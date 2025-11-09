"""
Analyze generated mockup against GitHub repository and create Jira tickets
"""
import re
from typing import List, Dict, Optional
from nemotron_client import call_nvidia_nemotron


def analyze_mockup_vs_repo(mockup_html: str, repo_data: dict, github_repo_url: str) -> List[Dict]:
    """
    Compare generated mockup with repository and identify required changes.
    Creates structured tickets with difficulty, priority, description, and acceptance criteria.
    
    Args:
        mockup_html: Generated HTML mockup content
        repo_data: Repository analysis data from analyze_repo_for_mockup
        github_repo_url: GitHub repository URL
    
    Returns:
        List of ticket dictionaries with difficulty, priority, description, and acceptance_criteria
    """
    repo_info = repo_data.get("repo_info", {})
    readme = repo_data.get("readme", "")
    relevant_files = repo_data.get("relevant_files", {})
    
    # Build repository context summary
    repo_context = []
    repo_context.append(f"Repository: {repo_info.get('name', 'Unknown')}")
    if repo_info.get('description'):
        repo_context.append(f"Description: {repo_info.get('description')}")
    if repo_info.get('language'):
        repo_context.append(f"Language: {repo_info.get('language')}")
    if repo_info.get('topics'):
        repo_context.append(f"Topics: {', '.join(repo_info.get('topics', []))}")
    
    # Summarize relevant files
    file_summary = []
    for file_path, content in list(relevant_files.items())[:10]:  # Limit to 10 files
        file_summary.append(f"{file_path}: {len(content)} chars")
    
    # Truncate mockup HTML for analysis (keep structure and key elements)
    mockup_preview = mockup_html[:5000] if len(mockup_html) > 5000 else mockup_html
    
    # Create analysis prompt
    analysis_prompt = f"""You are an expert product manager and technical lead. Analyze the differences between a generated mockup and an existing GitHub repository to identify what needs to be implemented or changed.

Repository Context:
{chr(10).join(repo_context)}

Repository Files Summary:
{chr(10).join(file_summary[:10])}

Generated Mockup HTML (preview):
{mockup_preview}

Your task:
1. Compare the mockup design with the current repository state
2. Identify specific implementation tasks needed to bring the repository up to match the mockup
3. Break down tasks into logical, implementable tickets
4. Assign difficulty (1-10) and priority (1=High, 2=Medium, 3=Low) to each ticket
5. Create clear descriptions and acceptance criteria for each ticket

Return a JSON array of tickets. Each ticket should have:
- title: Short, descriptive title
- description: Detailed description of what needs to be done
- acceptance_criteria: List of specific, testable criteria
- difficulty: Number from 1-10 (1=easy, 10=very complex)
- priority: Number 1, 2, or 3 (1=High, 2=Medium, 3=Low)

Format your response as valid JSON only, no markdown or explanations:
[
  {{
    "title": "Ticket title",
    "description": "Detailed description",
    "acceptance_criteria": ["Criterion 1", "Criterion 2"],
    "difficulty": 5,
    "priority": 1
  }}
]"""
    
    system_message = """You are an expert at analyzing software requirements and creating detailed, actionable development tickets.
Your responses must be valid JSON arrays only, with no markdown formatting or explanations."""
    
    try:
        # Call Nemotron to analyze
        analysis_result = call_nvidia_nemotron(analysis_prompt, system_message)
        
        # Clean up the response
        if '<think>' in analysis_result:
            start_idx = analysis_result.find('<think>')
            end_idx = analysis_result.find('</think>') + len('</think>')
            analysis_result = analysis_result[:start_idx] + analysis_result[end_idx:]
            analysis_result = analysis_result.strip()
        
        # Remove markdown code blocks if present
        if '```json' in analysis_result:
            analysis_result = analysis_result.split('```json')[1].split('```')[0].strip()
        elif '```' in analysis_result:
            analysis_result = analysis_result.split('```')[1].split('```')[0].strip()
        
        # Parse JSON - try to extract JSON from response
        import json
        
        # Try to find JSON array in the response
        json_start = analysis_result.find('[')
        json_end = analysis_result.rfind(']') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = analysis_result[json_start:json_end]
        else:
            json_str = analysis_result
        
        try:
            tickets = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from Nemotron response: {str(e)}")
            print(f"Response preview: {analysis_result[:500]}")
            # Fallback to single generic ticket
            return [{
                'title': 'Implement mockup design',
                'description': f'Implement the generated mockup design in the repository. Review the mockup HTML and update the codebase accordingly.',
                'acceptance_criteria': [
                    'Mockup design is implemented in the repository',
                    'Code matches the mockup structure and styling',
                    'All components from mockup are present'
                ],
                'difficulty': 5,
                'priority': 1
            }]
        
        # Validate and clean tickets
        validated_tickets = []
        for ticket in tickets:
            if isinstance(ticket, dict):
                try:
                    validated_ticket = {
                        'title': str(ticket.get('title', 'Untitled Task')).strip(),
                        'description': str(ticket.get('description', '')).strip(),
                        'acceptance_criteria': [
                            str(c).strip() 
                            for c in ticket.get('acceptance_criteria', [])
                            if c
                        ] if isinstance(ticket.get('acceptance_criteria'), list) else [],
                        'difficulty': max(1, min(10, int(ticket.get('difficulty', 5)))),
                        'priority': max(1, min(3, int(ticket.get('priority', 2))))
                    }
                    if validated_ticket['title']:  # Only add if title is not empty
                        validated_tickets.append(validated_ticket)
                except (ValueError, TypeError) as e:
                    print(f"Error validating ticket: {str(e)}")
                    continue
        
        if not validated_tickets:
            # Fallback if no valid tickets
            return [{
                'title': 'Implement mockup design',
                'description': f'Implement the generated mockup design in the repository.',
                'acceptance_criteria': [
                    'Mockup design is implemented',
                    'Code matches the mockup structure'
                ],
                'difficulty': 5,
                'priority': 1
            }]
        
        return validated_tickets
    
    except Exception as e:
        print(f"Error analyzing mockup vs repo: {str(e)}")
        # Fallback: Create a single generic ticket
        return [{
            'title': 'Implement mockup design',
            'description': f'Implement the generated mockup design in the repository. Review the mockup HTML and update the codebase accordingly.',
            'acceptance_criteria': [
                'Mockup design is implemented in the repository',
                'Code matches the mockup structure and styling',
                'All components from mockup are present'
            ],
            'difficulty': 5,
            'priority': 1
        }]


def create_tickets_from_analysis(tickets: List[Dict], github_repo_url: str, mockup_id: str) -> List[Dict]:
    """
    Create Jira tickets from analysis results
    
    Args:
        tickets: List of ticket dictionaries from analyze_mockup_vs_repo
        github_repo_url: GitHub repository URL
        mockup_id: Mockup ID for reference
    
    Returns:
        List of ticket creation results
    """
    try:
        from jira_integration import create_enhanced_jira_ticket
    except ImportError:
        print("Error importing jira_integration module")
        return [{
            'success': False,
            'error': 'Jira integration not available',
            'ticket': ticket
        } for ticket in tickets]
    
    results = []
    for ticket in tickets:
        try:
            result = create_enhanced_jira_ticket(
                title=ticket['title'],
                description=ticket['description'],
                acceptance_criteria=ticket['acceptance_criteria'],
                difficulty=ticket['difficulty'],
                priority=ticket['priority'],
                github_repo_url=github_repo_url,
                mockup_id=mockup_id
            )
            # Add ticket title to result for reference
            result['title'] = ticket['title']
            results.append(result)
        except Exception as e:
            print(f"Error creating ticket '{ticket.get('title', 'Unknown')}': {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'success': False,
                'error': str(e),
                'ticket': ticket,
                'title': ticket.get('title', 'Unknown')
            })
    
    return results


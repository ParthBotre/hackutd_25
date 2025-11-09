"""
Repository-aware mockup generator - core functionality without MCP decorators
This module provides the core functions that can be used by both MCP server and Flask backend
"""
import re
from typing import Optional
from github_integration import analyze_repo_for_mockup
from nemotron_client import call_nvidia_nemotron


def parse_github_url(repo_url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse GitHub URL to extract owner and repo name
    
    Args:
        repo_url: GitHub repository URL
    
    Returns:
        Tuple of (owner, repo_name) or (None, None) if invalid
    """
    # Handle various GitHub URL formats
    patterns = [
        r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?$",  # github.com/owner/repo
        r"([^/]+)/([^/]+?)(?:\.git)?$",  # owner/repo
    ]
    
    for pattern in patterns:
        match = re.search(pattern, repo_url)
        if match:
            owner = match.group(1)
            repo = match.group(2).rstrip('/')
            return owner, repo
    
    return None, None


def enhance_prompt_with_repo_context(user_request: str, repo_data: dict) -> str:
    """
    Enhance mockup request with repository context using Nemotron
    
    Args:
        user_request: Original user request for mockup
        repo_data: Repository analysis data
    
    Returns:
        Enhanced prompt with repository context
    """
    repo_info = repo_data.get("repo_info", {})
    readme = repo_data.get("readme", "")
    relevant_files = repo_data.get("relevant_files", {})
    
    # Build context from repository
    context_parts = []
    
    # Add repository information
    if repo_info.get("description"):
        context_parts.append(f"Repository Description: {repo_info['description']}")
    if repo_info.get("language"):
        context_parts.append(f"Primary Language: {repo_info['language']}")
    if repo_info.get("topics"):
        context_parts.append(f"Topics: {', '.join(repo_info['topics'])}")
    
    # Add README if available
    if readme:
        # Truncate README if too long
        readme_preview = readme[:2000] if len(readme) > 2000 else readme
        context_parts.append(f"\nREADME:\n{readme_preview}")
    
    # Add relevant file contents (prioritize key files)
    key_files = ["package.json", "requirements.txt", "README.md", "*.json"]
    file_contents = []
    
    for file_path, content in relevant_files.items():
        # Prioritize key files
        is_key_file = any(key_file in file_path for key_file in key_files)
        
        if is_key_file or len(file_contents) < 5:
            # Truncate file content if too long
            content_preview = content[:1000] if len(content) > 1000 else content
            file_contents.append(f"\n{file_path}:\n{content_preview}")
    
    if file_contents:
        context_parts.append("\nRelevant Files:")
        context_parts.extend(file_contents[:5])  # Limit to 5 files
    
    # Build context string
    repo_context = "\n".join(context_parts)
    
    # Create prompt for Nemotron to enhance the request
    enhancement_prompt = f"""You are an expert product manager and developer. Analyze the following repository information and user request, then create an enhanced, detailed mockup specification that incorporates the repository's context, technology stack, and existing patterns.

Repository Context:
{repo_context}

Original User Request:
{user_request}

Based on the repository information above, enhance the mockup request to:
1. Align with the repository's technology stack and patterns
2. Match the project's style and conventions
3. Incorporate relevant design patterns from the codebase
4. Ensure consistency with existing components and structure
5. Add specific technical details relevant to the project

Provide an enhanced, detailed mockup specification that the user would want, incorporating all relevant repository context. Be specific about:
- Technology stack to use (based on package.json, requirements.txt, etc.)
- Design patterns and components from the repo
- Color schemes and styling approaches
- Component structure and organization
- Any specific libraries or frameworks to consider

Return ONLY the enhanced mockup specification, no explanations or markdown formatting."""
    
    # Call Nemotron to enhance the prompt
    system_message = """You are an expert at analyzing codebases and creating detailed product specifications. 
Your task is to enhance user requests with relevant repository context to create better mockups.
Return only the enhanced specification text."""
    
    try:
        enhanced_prompt = call_nvidia_nemotron(enhancement_prompt, system_message)
        
        # Clean up the response
        if '<think>' in enhanced_prompt:
            start_idx = enhanced_prompt.find('<think>')
            end_idx = enhanced_prompt.find('</think>') + len('</think>')
            enhanced_prompt = enhanced_prompt[:start_idx] + enhanced_prompt[end_idx:]
            enhanced_prompt = enhanced_prompt.strip()
        
        # Remove markdown code blocks if present
        if '```' in enhanced_prompt:
            enhanced_prompt = re.sub(r'```[^`]*```', '', enhanced_prompt, flags=re.DOTALL)
            enhanced_prompt = enhanced_prompt.strip()
        
        return enhanced_prompt
    except Exception as e:
        print(f"Error enhancing prompt with Nemotron: {str(e)}")
        # Fallback to basic enhancement
        return f"""{user_request}

Repository Context:
- Project: {repo_info.get('name', 'Unknown')}
- Description: {repo_info.get('description', 'N/A')}
- Language: {repo_info.get('language', 'N/A')}
- Technologies: {', '.join(repo_info.get('topics', []))}

Please ensure the mockup aligns with this project's context and technology stack."""


def generate_mockup_from_repo(
    github_repo_url: str,
    mockup_request: str,
    github_token: Optional[str] = None
) -> str:
    """
    Generate a mockup by analyzing a GitHub repository and enhancing the request with repository context.
    
    Args:
        github_repo_url: GitHub repository URL (e.g., 'https://github.com/owner/repo' or 'owner/repo')
        mockup_request: User's original mockup request/description
        github_token: Optional GitHub personal access token (uses GITHUB_TOKEN env var if not provided)
    
    Returns:
        Generated HTML mockup content
    """
    try:
        # Parse GitHub URL
        owner, repo_name = parse_github_url(github_repo_url)
        
        if not owner or not repo_name:
            raise ValueError(f"Invalid GitHub repository URL: {github_repo_url}. Expected format: 'https://github.com/owner/repo' or 'owner/repo'")
        
        print(f"Analyzing repository: {owner}/{repo_name}")
        
        # Analyze repository
        repo_data = analyze_repo_for_mockup(owner, repo_name, mockup_request, github_token)
        
        print(f"Repository analyzed. Found {len(repo_data['relevant_files'])} relevant files.")
        
        # Enhance prompt with repository context
        enhanced_prompt = enhance_prompt_with_repo_context(mockup_request, repo_data)
        
        print(f"Enhanced prompt generated (length: {len(enhanced_prompt)} characters)")
        
        # Generate mockup using Nemotron
        system_message = """You are an expert UI/UX designer and frontend developer. Generate complete, production-ready HTML mockups based on user requirements.

Your mockups should:
1. Be fully self-contained with inline CSS (no external dependencies)
2. Use modern, professional design principles
3. Include responsive design
4. Use a cohesive color scheme
5. Include placeholder content that makes sense for the use case
6. Be visually appealing and suitable for stakeholder presentations
7. Include semantic HTML5 elements
8. Use modern CSS features (flexbox, grid, gradients, shadows, etc.)
9. Align with the technology stack and patterns specified in the request

Return ONLY the complete HTML code, no explanations or markdown formatting."""
        
        html_content = call_nvidia_nemotron(enhanced_prompt, system_message)
        
        # Clean up the response
        if '<think>' in html_content:
            start_idx = html_content.find('<think>')
            end_idx = html_content.find('</think>') + len('</think>')
            html_content = html_content[:start_idx] + html_content[end_idx:]
            html_content = html_content.strip()
        
        # Remove markdown code blocks if present
        if '```html' in html_content:
            html_content = html_content.split('```html')[1].split('```')[0].strip()
        elif '```' in html_content:
            html_content = html_content.split('```')[1].split('```')[0].strip()
        
        return html_content
    
    except Exception as e:
        error_message = f"Error generating mockup from repository: {str(e)}"
        print(error_message)
        raise Exception(error_message)


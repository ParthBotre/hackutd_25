import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import urllib3
from pathlib import Path
from typing import List

# 🔇 Disable only the InsecureRequestWarning that verify=False triggers
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
# Also try default location
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL", "https://hack-utd-automations.atlassian.net")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_projects(max_results: int = 50):
    """Get all projects from Jira"""
    projects = []
    start_at = 0
    
    while True:
        params = {
            "maxResults": max_results,
            "startAt": start_at,
        }
        
        resp = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/project/search",
            headers=headers,
            auth=auth,
            params=params,
            verify=False,  # 👈 ignore SSL
        )
        
        resp.raise_for_status()
        data = resp.json()
        projects.extend(data.get("values", []))
        
        if data.get("isLast", True):
            break
            
        start_at = data["startAt"] + data["maxResults"]
    
    return projects


def get_board_issues(board_id: int = 1, max_results: int = 100):
    """
    Get all issues from a Jira board using the Agile API.
    
    Args:
        board_id: The ID of the board (default: 1 for the KAN board)
        max_results: Number of results per page (max 100)
    
    Returns:
        List of all issues from the board
    """
    issues = []
    start_at = 0
    
    while True:
        params = {
            "maxResults": max_results,
            "startAt": start_at,
            "fields": "id,key,summary,status,issuetype,assignee,priority,created,updated"  # Include relevant fields
        }
        
        resp = requests.get(
            f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/issue",
            headers=headers,
            auth=auth,
            params=params,
            verify=False,  # 👈 ignore SSL
        )
        
        resp.raise_for_status()
        data = resp.json()
        page_issues = data.get("issues", [])
        issues.extend(page_issues)
        
        # Check if this is the last page
        if data.get("isLast", True) or len(page_issues) == 0:
            break
            
        start_at = data["startAt"] + data["maxResults"]
    
    return issues


def validate_jira_credentials() -> bool:
    """
    Validate that Jira credentials are configured
    
    Returns:
        True if credentials are valid, False otherwise
    """
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        return False
    
    try:
        # Test connection by fetching projects
        resp = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/myself",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        return resp.status_code == 200
    except Exception:
        return False


def create_enhanced_jira_ticket(
    title: str,
    description: str,
    acceptance_criteria: List[str],
    difficulty: int,
    priority: int,
    github_repo_url: str = "",
    mockup_id: str = "",
    project_key: str = "SM",
    issue_type: str = "Task"
) -> dict:
    """
    Create an enhanced Jira ticket with difficulty, priority, description, and acceptance criteria.
    
    Args:
        title: Ticket title/summary
        description: Detailed description
        acceptance_criteria: List of acceptance criteria strings
        difficulty: Difficulty level (1-10)
        priority: Priority level (1=High, 2=Medium, 3=Low)
        github_repo_url: GitHub repository URL (optional)
        mockup_id: Mockup ID for reference (optional)
        project_key: Jira project key (default: "KAN")
        issue_type: Issue type (default: "Task")
    
    Returns:
        Dictionary with success status and ticket information
    """
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be set in environment variables")
    
    if not validate_jira_credentials():
        raise ValueError("Invalid Jira credentials. Please check JIRA_EMAIL and JIRA_API_TOKEN")
    
    # Map priority numbers to Jira priority names
    # Ensure priority is within valid range
    priority = max(1, min(3, priority))
    priority_map = {
        1: "Highest",
        2: "High", 
        3: "Medium"
    }
    priority_name = priority_map.get(priority, "Medium")
    
    # Ensure difficulty is within valid range
    difficulty = max(1, min(10, difficulty))
    
    # Build description content
    description_content = []
    
    # Add main description
    description_content.append({
        "type": "heading",
        "attrs": {"level": 2},
        "content": [{"type": "text", "text": "Description"}]
    })
    description_content.append({
        "type": "paragraph",
        "content": [{"type": "text", "text": description}]
    })
    
    # Add acceptance criteria
    if acceptance_criteria:
        description_content.append({
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "Acceptance Criteria"}]
        })
        criteria_list = []
        for criterion in acceptance_criteria:
            criteria_list.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": criterion}]
                }]
            })
        description_content.append({
            "type": "bulletList",
            "content": criteria_list
        })
    
    # Add metadata
    description_content.append({
        "type": "heading",
        "attrs": {"level": 2},
        "content": [{"type": "text", "text": "Metadata"}]
    })
    
    metadata_items = []
    if github_repo_url:
        metadata_items.append({
            "type": "listItem",
            "content": [{
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "GitHub Repository: ", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": github_repo_url}
                ]
            }]
        })
    if mockup_id:
        metadata_items.append({
            "type": "listItem",
            "content": [{
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Mockup ID: ", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": mockup_id}
                ]
            }]
        })
    metadata_items.append({
        "type": "listItem",
        "content": [{
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Difficulty: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": f"{difficulty}/10"}
            ]
        }]
    })
    
    if metadata_items:
        description_content.append({
            "type": "bulletList",
            "content": metadata_items
        })
    
    # Build payload
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": description_content
            },
            "issuetype": {
                "name": issue_type
            },
            "priority": {
                "name": priority_name
            }
        }
    }
    
    # Add custom field for difficulty if available (some Jira instances have this)
    # For now, we'll include it in the description
    
    try:
        response = requests.post(
            f"{JIRA_BASE_URL}/rest/api/3/issue",
            headers=headers,
            auth=auth,
            json=payload,
            verify=False
        )
        
        response.raise_for_status()
        created_issue = response.json()
        
        return {
            "success": True,
            "issue_key": created_issue.get("key"),
            "issue_id": created_issue.get("id"),
            "issue_url": f"{JIRA_BASE_URL}/browse/{created_issue.get('key')}",
            "title": title,
            "difficulty": difficulty,
            "priority": priority
        }
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        error_details = None
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                if "errorMessages" in error_detail:
                    error_messages = error_detail.get("errorMessages", [])
                    error_message = "; ".join(error_messages) if error_messages else str(e)
                elif "errors" in error_detail:
                    errors = error_detail.get("errors", {})
                    error_message = "; ".join([f"{k}: {v}" for k, v in errors.items()])
                elif "message" in error_detail:
                    error_message = error_detail.get("message", str(e))
                else:
                    error_message = str(error_detail)
                
                error_details = error_detail
            except Exception as json_error:
                error_message = e.response.text or str(e)
        
        print(f"Jira API Error: {error_message}")
        if error_details:
            print(f"Error details: {error_details}")
        
        return {
            "success": False,
            "error": error_message,
            "error_details": error_details
        }


def create_jira_ticket(mockup_data, project_key="SM", issue_type="Task"):
    """
    Create a new Jira ticket with mockup information.
    
    Args:
        mockup_data: Dictionary containing mockup information (id, project_name, prompt, etc.)
        project_key: Jira project key (default: "KAN")
        issue_type: Type of issue to create (default: "Task")
    
    Returns:
        Dictionary with success status and ticket information
    """
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN must be set in environment variables")
    
    # Hardcoded ticket data for now
    # TODO: Make this configurable or use mockup_data more extensively
    summary = f"Mockup: {mockup_data.get('project_name', 'Untitled Project')}"
    
    # Create description from mockup data using Atlassian Document Format (ADF)
    # Build ADF content structure
    description_content = []
    
    # Add heading
    description_content.append({
        "type": "heading",
        "attrs": {"level": 2},
        "content": [{"type": "text", "text": "Mockup Submission"}]
    })
    
    # Add project name
    description_content.append({
        "type": "paragraph",
        "content": [
            {"type": "text", "text": "Project Name: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": mockup_data.get('project_name', 'N/A')}
        ]
    })
    
    # Add mockup ID
    description_content.append({
        "type": "paragraph",
        "content": [
            {"type": "text", "text": "Mockup ID: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": mockup_data.get('id', 'N/A')}
        ]
    })
    
    # Add created date
    description_content.append({
        "type": "paragraph",
        "content": [
            {"type": "text", "text": "Created At: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": mockup_data.get('created_at', 'N/A')}
        ]
    })
    
    # Add prompt heading
    description_content.append({
        "type": "heading",
        "attrs": {"level": 3},
        "content": [{"type": "text", "text": "Original Prompt"}]
    })
    
    # Add prompt text
    prompt_text = mockup_data.get('prompt', 'No prompt provided')
    description_content.append({
        "type": "paragraph",
        "content": [{"type": "text", "text": prompt_text}]
    })
    
    # Add details heading
    description_content.append({
        "type": "heading",
        "attrs": {"level": 3},
        "content": [{"type": "text", "text": "Mockup Details"}]
    })
    
    # Add details list
    description_content.append({
        "type": "bulletList",
        "content": [
            {
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": f"HTML File: {mockup_data.get('html_filename', 'N/A')}"}
                    ]
                }]
            },
            {
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": f"Screenshot: {mockup_data.get('screenshot_filename', 'N/A')}"}
                    ]
                }]
            }
        ]
    })
    
    # Add footer
    description_content.append({
        "type": "paragraph",
        "content": [{"type": "text", "text": "This mockup was generated and submitted from the PM Mockup Generator application."}]
    })
    
    # Payload for creating the issue
    # Try using project key first (most common approach)
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": description_content
            },
            "issuetype": {
                "name": issue_type
            }
        }
    }
    
    try:
        response = requests.post(
            f"{JIRA_BASE_URL}/rest/api/3/issue",
            headers=headers,
            auth=auth,
            json=payload,
            verify=False
        )
        
        response.raise_for_status()
        created_issue = response.json()
        
        return {
            "success": True,
            "issue_key": created_issue.get("key"),
            "issue_id": created_issue.get("id"),
            "issue_url": f"{JIRA_BASE_URL}/browse/{created_issue.get('key')}"
        }
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        error_details = None
        
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                # Jira API returns errors in different formats
                if "errorMessages" in error_detail:
                    error_messages = error_detail.get("errorMessages", [])
                    error_message = "; ".join(error_messages) if error_messages else str(e)
                elif "errors" in error_detail:
                    errors = error_detail.get("errors", {})
                    error_message = "; ".join([f"{k}: {v}" for k, v in errors.items()])
                elif "message" in error_detail:
                    error_message = error_detail.get("message", str(e))
                else:
                    error_message = str(error_detail)
                
                error_details = error_detail
            except Exception as json_error:
                # If response is not JSON, get text
                error_message = e.response.text or str(e)
        
        # Log the full error for debugging
        print(f"Jira API Error: {error_message}")
        if error_details:
            print(f"Error details: {error_details}")
        
        return {
            "success": False,
            "error": error_message,
            "error_details": error_details
        }


def test_jira_connection() -> dict:
    """
    Test Jira connection and return status
    
    Returns:
        Dictionary with connection status and details
    """
    result = {
        "connected": False,
        "error": None,
        "base_url": JIRA_BASE_URL,
        "email_configured": bool(JIRA_EMAIL),
        "token_configured": bool(JIRA_API_TOKEN)
    }
    
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        result["error"] = "Jira credentials not configured"
        return result
    
    try:
        # Test connection
        resp = requests.get(
            f"{JIRA_BASE_URL}/rest/api/3/myself",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        if resp.status_code == 200:
            result["connected"] = True
            user_data = resp.json()
            result["user"] = user_data.get("displayName", "Unknown")
        else:
            result["error"] = f"Authentication failed with status {resp.status_code}"
    except Exception as e:
        result["error"] = str(e)
    
    return result


if __name__ == "__main__":
    # Test the functions
    print("=" * 80)
    print("Jira Integration Test")
    print("=" * 80)
    print()
    
    # Test connection
    print("1. Testing Jira connection...")
    conn_result = test_jira_connection()
    if conn_result["connected"]:
        print(f"   ✓ Connected to Jira as: {conn_result.get('user')}")
        print(f"   Base URL: {conn_result['base_url']}")
    else:
        print(f"   ✗ Connection failed: {conn_result.get('error')}")
        print(f"   Email configured: {conn_result['email_configured']}")
        print(f"   Token configured: {conn_result['token_configured']}")
    print()
    
    if conn_result["connected"]:
        print("2. Fetching all tickets from board 1 (KAN)...")
        try:
            tickets = get_board_issues(board_id=1)
            print(f"   ✓ Found {len(tickets)} tickets")
            print()
            print("-" * 80)
            
            for ticket in tickets[:5]:  # Show first 5
                key = ticket.get("key", "N/A")
                fields = ticket.get("fields", {})
                summary = fields.get("summary", "No summary")
                status = fields.get("status", {}).get("name", "Unknown")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown")
                
                print(f"{key}: {summary}")
                print(f"  Type: {issue_type} | Status: {status}")
                print()
            
            if len(tickets) > 5:
                print(f"... and {len(tickets) - 5} more tickets")
        except Exception as e:
            print(f"   ✗ Error fetching tickets: {str(e)}")
    
    print()
    print("=" * 80)


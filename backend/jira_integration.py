import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import urllib3
from pathlib import Path

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


def create_jira_ticket(mockup_data, project_key="KAN", issue_type="Task"):
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


if __name__ == "__main__":
    # Test the functions
    print("Fetching all tickets from board 1 (KAN)...")
    tickets = get_board_issues(board_id=1)
    print(f"\nFound {len(tickets)} tickets:")
    print("-" * 80)
    
    for ticket in tickets:
        key = ticket.get("key", "N/A")
        fields = ticket.get("fields", {})
        summary = fields.get("summary", "No summary")
        status = fields.get("status", {}).get("name", "Unknown")
        issue_type = fields.get("issuetype", {}).get("name", "Unknown")
        
        print(f"{key}: {summary}")
        print(f"  Type: {issue_type} | Status: {status}")
        print()


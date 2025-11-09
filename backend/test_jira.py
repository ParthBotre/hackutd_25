"""
Test script to verify Jira integration and credentials
Run this to diagnose Jira connection issues
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from jira_integration import get_projects, create_jira_ticket, JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()

def test_jira_connection():
    """Test Jira connection and list available projects"""
    print("=" * 60)
    print("Jira Connection Test")
    print("=" * 60)
    print()
    
    # Check credentials
    print("1. Checking credentials...")
    print(f"   JIRA_BASE_URL: {JIRA_BASE_URL}")
    print(f"   JIRA_EMAIL: {JIRA_EMAIL if JIRA_EMAIL else '[NOT SET]'}")
    print(f"   JIRA_API_TOKEN: {'[SET]' if JIRA_API_TOKEN else '[NOT SET]'}")
    print()
    
    if not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("[ERROR] JIRA_EMAIL and JIRA_API_TOKEN must be set in backend/.env")
        print()
        print("Add these lines to backend/.env:")
        print("JIRA_BASE_URL=https://hack-utd-automations.atlassian.net")
        print("JIRA_EMAIL=your-email@example.com")
        print("JIRA_API_TOKEN=your-api-token")
        return False
    
    # Test getting projects
    print("2. Testing connection to Jira...")
    try:
        projects = get_projects()
        print(f"   [OK] Successfully connected to Jira!")
        print(f"   Found {len(projects)} projects:")
        print()
        
        for project in projects:
            print(f"   - Key: {project.get('key', 'N/A')}, ID: {project.get('id', 'N/A')}, Name: {project.get('name', 'N/A')}")
        print()
        
        # Check if KAN project exists
        kan_project = next((p for p in projects if p.get('key') == 'KAN'), None)
        if kan_project:
            print(f"   [OK] Project 'KAN' found:")
            print(f"        Name: {kan_project.get('name')}")
            print(f"        ID: {kan_project.get('id')}")
            print(f"        Key: {kan_project.get('key')}")
        else:
            print(f"   [WARNING] Project 'KAN' not found!")
            print(f"   Available project keys: {', '.join([p.get('key') for p in projects])}")
        print()
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] Failed to connect to Jira")
        print(f"   Error: {str(e)}")
        print()
        return False

def test_create_ticket():
    """Test creating a test ticket"""
    print("3. Testing ticket creation...")
    print()
    
    # Test data
    test_mockup_data = {
        'id': 'test_123',
        'project_name': 'Test Project',
        'prompt': 'This is a test prompt',
        'created_at': '2024-01-01T00:00:00',
        'html_filename': 'test.html',
        'screenshot_filename': 'test.png'
    }
    
    try:
        result = create_jira_ticket(
            test_mockup_data,
            project_key="KAN",
            issue_type="Task"
        )
        
        if result.get('success'):
            print(f"   [OK] Successfully created test ticket!")
            print(f"   Issue Key: {result.get('issue_key')}")
            print(f"   Issue URL: {result.get('issue_url')}")
        else:
            print(f"   [ERROR] Failed to create ticket")
            print(f"   Error: {result.get('error')}")
            if result.get('error_details'):
                print(f"   Details: {result.get('error_details')}")
        print()
        
    except Exception as e:
        print(f"   [ERROR] {str(e)}")
        print()

if __name__ == "__main__":
    if test_jira_connection():
        # Uncomment the line below to test creating a ticket
        # test_create_ticket()
        print("=" * 60)
        print("Test complete!")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Fix the errors above and try again")
        print("=" * 60)


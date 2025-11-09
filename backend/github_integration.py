"""
GitHub integration module for fetching repository information
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional
import base64

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_BASE = "https://api.github.com"


def get_repo_contents(repo_owner: str, repo_name: str, path: str = "", token: Optional[str] = None) -> List[Dict]:
    """
    Fetch repository contents from GitHub API
    
    Args:
        repo_owner: Repository owner (username or organization)
        repo_name: Repository name
        path: Path within repository (default: root)
        token: GitHub personal access token (optional, uses env var if not provided)
    
    Returns:
        List of file/directory information
    """
    token = token or GITHUB_TOKEN
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/contents/{path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repo contents: {str(e)}")
        raise Exception(f"Failed to fetch repository contents: {str(e)}")


def get_file_content(repo_owner: str, repo_name: str, file_path: str, token: Optional[str] = None) -> str:
    """
    Fetch file content from GitHub repository
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        file_path: Path to file in repository
        token: GitHub personal access token (optional)
    
    Returns:
        File content as string
    """
    token = token or GITHUB_TOKEN
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        file_data = response.json()
        
        # Decode base64 content
        if file_data.get("encoding") == "base64":
            content = base64.b64decode(file_data["content"]).decode("utf-8")
            return content
        else:
            return file_data.get("content", "")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching file content: {str(e)}")
        raise Exception(f"Failed to fetch file content: {str(e)}")


def get_repo_readme(repo_owner: str, repo_name: str, token: Optional[str] = None) -> Optional[str]:
    """
    Fetch README file from repository
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        token: GitHub personal access token (optional)
    
    Returns:
        README content or None if not found
    """
    readme_variants = ["README.md", "README.txt", "README", "readme.md"]
    
    for readme_name in readme_variants:
        try:
            content = get_file_content(repo_owner, repo_name, readme_name, token)
            return content
        except:
            continue
    
    return None


def get_repo_info(repo_owner: str, repo_name: str, token: Optional[str] = None) -> Dict:
    """
    Get repository information and key files
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        token: GitHub personal access token (optional)
    
    Returns:
        Dictionary with repository information
    """
    token = token or GITHUB_TOKEN
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        repo_data = response.json()
        
        return {
            "name": repo_data.get("name"),
            "description": repo_data.get("description"),
            "language": repo_data.get("language"),
            "topics": repo_data.get("topics", []),
            "default_branch": repo_data.get("default_branch"),
            "url": repo_data.get("html_url"),
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repo info: {str(e)}")
        raise Exception(f"Failed to fetch repository information: {str(e)}")


def get_relevant_files(repo_owner: str, repo_name: str, file_patterns: List[str] = None, max_files: int = 10, token: Optional[str] = None) -> Dict[str, str]:
    """
    Get relevant files from repository based on patterns
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        file_patterns: List of file patterns to search for (e.g., ['*.json', 'package.json', '*.md'])
        max_files: Maximum number of files to return
        token: GitHub personal access token (optional)
    
    Returns:
        Dictionary mapping file paths to content
    """
    if file_patterns is None:
        file_patterns = [
            "package.json", "package-lock.json", "requirements.txt",
            "README.md", "README.txt", "*.md",
            "*.json", "*.yaml", "*.yml",
            "*.tsx", "*.jsx", "*.ts", "*.js",
            "*.css", "*.scss", "*.html"
        ]
    
    relevant_files = {}
    token = token or GITHUB_TOKEN
    
    def search_directory(path: str = "", depth: int = 0, max_depth: int = 3):
        """Recursively search directory for relevant files"""
        if depth > max_depth or len(relevant_files) >= max_files:
            return
        
        try:
            contents = get_repo_contents(repo_owner, repo_name, path, token)
            
            for item in contents:
                if len(relevant_files) >= max_files:
                    break
                
                item_path = item.get("path", "")
                item_type = item.get("type", "")
                
                if item_type == "file":
                    # Check if file matches patterns
                    for pattern in file_patterns:
                        if pattern.startswith("*."):
                            # Extension match
                            if item_path.endswith(pattern[1:]):
                                try:
                                    content = get_file_content(repo_owner, repo_name, item_path, token)
                                    relevant_files[item_path] = content
                                    break
                                except:
                                    continue
                        elif item_path.endswith(pattern) or item_path == pattern:
                            # Exact match
                            try:
                                content = get_file_content(repo_owner, repo_name, item_path, token)
                                relevant_files[item_path] = content
                                break
                            except:
                                continue
                
                elif item_type == "dir" and depth < max_depth:
                    # Skip common ignored directories
                    if item_path.split("/")[-1] not in [".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"]:
                        search_directory(item_path, depth + 1, max_depth)
        
        except Exception as e:
            print(f"Error searching directory {path}: {str(e)}")
    
    # Start search from root
    search_directory()
    
    return relevant_files


def analyze_repo_for_mockup(repo_owner: str, repo_name: str, user_request: str, token: Optional[str] = None) -> Dict:
    """
    Analyze repository and extract information relevant to mockup generation
    
    Args:
        repo_owner: Repository owner
        repo_name: Repository name
        user_request: Original user request for mockup
        token: GitHub personal access token (optional)
    
    Returns:
        Dictionary with analyzed repository information and enhanced prompt
    """
    try:
        # Get repository info
        repo_info = get_repo_info(repo_owner, repo_name, token)
        
        # Get README
        readme = get_repo_readme(repo_owner, repo_name, token)
        
        # Get relevant files
        relevant_files = get_relevant_files(
            repo_owner, 
            repo_name, 
            file_patterns=[
                "package.json", "requirements.txt", "README.md",
                "*.json", "*.md", "*.yaml", "*.yml",
                "*.tsx", "*.jsx", "*.ts", "*.js",
                "*.css", "*.html"
            ],
            max_files=15,
            token=token
        )
        
        return {
            "repo_info": repo_info,
            "readme": readme,
            "relevant_files": relevant_files,
            "user_request": user_request
        }
    
    except Exception as e:
        print(f"Error analyzing repository: {str(e)}")
        raise Exception(f"Failed to analyze repository: {str(e)}")


if __name__ == "__main__":
    # Test the functions
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python github_integration.py <owner> <repo>")
        sys.exit(1)
    
    owner = sys.argv[1]
    repo = sys.argv[2]
    
    print(f"Analyzing repository: {owner}/{repo}")
    result = analyze_repo_for_mockup(owner, repo, "Test mockup request")
    print(f"Repository info: {result['repo_info']}")
    print(f"README found: {bool(result['readme'])}")
    print(f"Relevant files found: {len(result['relevant_files'])}")


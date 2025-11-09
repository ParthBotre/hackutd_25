"""
MCP Server for GitHub-aware mockup generation using fastmcp and Nemotron
"""
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
from fastmcp import FastMCP
from repo_mockup_generator import generate_mockup_from_repo, parse_github_url
from github_integration import analyze_repo_for_mockup

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
load_dotenv()

# Initialize MCP server
mcp = FastMCP("GitHub-Aware Mockup Generator")


@mcp.tool()
def generate_mockup_from_repo_mcp(
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
    return generate_mockup_from_repo(github_repo_url, mockup_request, github_token)


@mcp.tool()
def analyze_repository_mcp(github_repo_url: str, github_token: Optional[str] = None) -> dict:
    """
    Analyze a GitHub repository and return information about its structure, technologies, and context.
    
    Args:
        github_repo_url: GitHub repository URL (e.g., 'https://github.com/owner/repo' or 'owner/repo')
        github_token: Optional GitHub personal access token (uses GITHUB_TOKEN env var if not provided)
    
    Returns:
        Dictionary with repository analysis information
    """
    try:
        # Parse GitHub URL
        owner, repo_name = parse_github_url(github_repo_url)
        
        if not owner or not repo_name:
            raise ValueError(f"Invalid GitHub repository URL: {github_repo_url}")
        
        # Analyze repository
        repo_data = analyze_repo_for_mockup(owner, repo_name, "Analysis request", github_token)
        
        return {
            "success": True,
            "repo_info": repo_data["repo_info"],
            "readme_available": bool(repo_data["readme"]),
            "relevant_files_count": len(repo_data["relevant_files"]),
            "relevant_files": list(repo_data["relevant_files"].keys())
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Run MCP server
    mcp.run()


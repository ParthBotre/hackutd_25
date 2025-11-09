# MCP Server for GitHub-Aware Mockup Generation

This MCP (Model Context Protocol) server enables GitHub repository-aware mockup generation using fastmcp and NVIDIA Nemotron.

## Overview

The MCP server analyzes GitHub repositories to understand their context, technology stack, and patterns, then enhances mockup generation requests to align with the repository's existing codebase.

## Architecture

### Components

1. **`github_integration.py`** - GitHub API integration for fetching repository information
2. **`repo_mockup_generator.py`** - Core logic for analyzing repos and generating context-aware mockups
3. **`mcp_server.py`** - FastMCP server that exposes tools for MCP clients
4. **`nemotron_client.py`** - NVIDIA Nemotron API client
5. **`app.py`** - Flask backend integration (optional GitHub repo URL parameter)

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add to `backend/.env`:

```env
# Required
NVIDIA_API_KEY=your_nvidia_api_key

# Optional (for private repos or higher rate limits)
GITHUB_TOKEN=your_github_personal_access_token
```

**Getting a GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Generate a new token with `repo` scope (for private repos) or `public_repo` scope (for public repos only)
3. Add it to your `.env` file

### 3. Run the MCP Server

**Standalone MCP Server:**
```bash
python mcp_server.py
```

The server will run on stdio by default (for MCP client integration).

**Integrated with Flask Backend:**
The Flask backend automatically uses the repo-aware generator when a `github_repo_url` is provided in the request.

## Usage

### Via Flask API

Send a POST request to `/api/generate-mockup` with an optional `github_repo_url`:

```json
{
  "prompt": "Create a dashboard for user management",
  "project_name": "User Dashboard",
  "github_repo_url": "https://github.com/owner/repo"
}
```

### Via MCP Server (FastMCP)

The MCP server exposes two tools:

#### 1. `generate_mockup_from_repo_mcp`

Generate a mockup with repository context:

```python
# Example MCP client call
result = mcp_client.call_tool(
    "generate_mockup_from_repo_mcp",
    {
        "github_repo_url": "https://github.com/owner/repo",
        "mockup_request": "Create a login page",
        "github_token": "optional_token"  # Optional
    }
)
```

#### 2. `analyze_repository_mcp`

Analyze a repository without generating a mockup:

```python
# Example MCP client call
result = mcp_client.call_tool(
    "analyze_repository_mcp",
    {
        "github_repo_url": "https://github.com/owner/repo",
        "github_token": "optional_token"  # Optional
    }
)
```

## How It Works

1. **Repository Analysis**: 
   - Fetches repository metadata (description, language, topics)
   - Retrieves README file
   - Finds and reads relevant files (package.json, requirements.txt, config files, etc.)

2. **Context Enhancement**:
   - Uses Nemotron to analyze repository context
   - Enhances the user's mockup request with repository-specific details
   - Incorporates technology stack, design patterns, and conventions

3. **Mockup Generation**:
   - Generates HTML mockup using the enhanced prompt
   - Aligns with repository's technology stack and patterns
   - Returns production-ready HTML code

## Repository URL Formats

The following URL formats are supported:

- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `owner/repo`
- `owner/repo.git`

## File Analysis

The system prioritizes these files for context:

- `package.json` (Node.js projects)
- `requirements.txt` (Python projects)
- `README.md` / `README.txt`
- Configuration files (`*.json`, `*.yaml`, `*.yml`)
- Source files (`*.tsx`, `*.jsx`, `*.ts`, `*.js`, `*.css`, `*.html`)

## Error Handling

- If GitHub integration fails, the system falls back to standard mockup generation
- Invalid repository URLs return clear error messages
- Missing GitHub token works for public repositories (with rate limits)

## Rate Limits

- **Without GitHub Token**: 60 requests/hour for public repos
- **With GitHub Token**: 5,000 requests/hour

For private repositories, a GitHub token is required.

## Example Workflow

1. User provides: "Create a user profile page" + GitHub repo URL
2. System analyzes the repository:
   - Finds it's a React/TypeScript project
   - Identifies existing component patterns
   - Reads styling approach from CSS files
3. System enhances prompt:
   - "Create a user profile page using React/TypeScript patterns, matching the existing component structure and styling approach from the repository"
4. System generates mockup aligned with repository context

## Integration with Frontend

The frontend can optionally include a GitHub repository URL field in the mockup generation form. When provided, the backend will automatically use repository context to enhance the mockup.

## Troubleshooting

### "Invalid GitHub repository URL"
- Check the URL format
- Ensure the repository exists and is accessible
- For private repos, ensure GITHUB_TOKEN is set

### "Failed to fetch repository contents"
- Check internet connection
- Verify repository is public or token has correct permissions
- Check GitHub API status

### "Rate limit exceeded"
- Add GITHUB_TOKEN to increase rate limits
- Wait for rate limit to reset (usually 1 hour)

## Development

### Testing the MCP Server

```bash
# Test repository analysis
python -c "from github_integration import analyze_repo_for_mockup; print(analyze_repo_for_mockup('owner', 'repo', 'test request'))"

# Test mockup generation
python -c "from repo_mockup_generator import generate_mockup_from_repo; print(generate_mockup_from_repo('owner/repo', 'test request'))"
```

### Running MCP Server Standalone

```bash
python mcp_server.py
```

The server will listen on stdio for MCP protocol messages.

## License

Same as the main project.


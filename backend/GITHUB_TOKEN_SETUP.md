# GitHub Token Setup Guide

## Do You Need a GitHub Token?

### ✅ **Required If:**
- You want to access **private repositories**
- You need more than 60 requests/hour (rate limits)

### ⚠️ **Optional If:**
- You're only using **public repositories**
- You don't mind the 60 requests/hour limit
- You're just testing the functionality

## How to Create a GitHub Personal Access Token

### Step 1: Go to GitHub Settings
1. Go to https://github.com/settings/tokens
2. Or: Click your profile → Settings → Developer settings → Personal access tokens → Tokens (classic)

### Step 2: Generate New Token
1. Click **"Generate new token"** → **"Generate new token (classic)"**
2. Give it a name (e.g., "Mockup Generator")
3. Set expiration (choose based on your needs)
4. Select scopes:
   - **For public repos only**: Check `public_repo`
   - **For private repos**: Check `repo` (includes public_repo)
5. Click **"Generate token"**

### Step 3: Copy the Token
⚠️ **Important**: Copy the token immediately - you won't be able to see it again!

### Step 4: Add to .env File
Add the token to your `backend/.env` file:

```env
GITHUB_TOKEN=ghp_your_token_here
```

**Important Notes:**
- Don't include quotes around the token
- Don't add spaces around the `=` sign
- Keep the token secret - never commit it to Git

## Testing Your Token

### Test 1: Check if token is loaded
```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Token set:', bool(os.getenv('GITHUB_TOKEN')))"
```

### Test 2: Test repository access
```bash
cd backend
python github_integration.py owner repo_name
```

Replace `owner` and `repo_name` with a real repository.

## Troubleshooting

### "401 Unauthorized" Error
- Check that your token is correctly set in `.env`
- Verify the token hasn't expired
- Ensure the token has the correct scopes (`repo` for private repos)

### "403 Forbidden" or Rate Limit Errors
- Without token: You've hit the 60 requests/hour limit
- With token: Check if token has correct permissions
- Wait for rate limit to reset (usually 1 hour)

### "404 Not Found" for Private Repo
- Ensure you're using a token with `repo` scope
- Verify you have access to the repository
- Check the repository URL is correct

## Security Best Practices

1. **Never commit tokens to Git**
   - Add `.env` to `.gitignore`
   - Use environment variables in production

2. **Use minimal scopes**
   - Only grant the minimum permissions needed
   - `public_repo` for public repos only
   - `repo` only if you need private repo access

3. **Set expiration dates**
   - Don't create tokens that never expire
   - Rotate tokens regularly

4. **Revoke unused tokens**
   - Delete tokens you're no longer using
   - Revoke compromised tokens immediately

## Example .env File

```env
# NVIDIA API Key (required)
NVIDIA_API_KEY=your_nvidia_api_key_here

# GitHub Token (optional - for private repos or higher rate limits)
GITHUB_TOKEN=ghp_your_github_token_here

# Jira Credentials (optional - for Jira integration)
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_token_here
```

## Rate Limits Reference

| Scenario | Rate Limit |
|----------|------------|
| No token (public repos) | 60 requests/hour |
| With token (authenticated) | 5,000 requests/hour |
| Private repos | Requires token |

## Need Help?

If you're having issues:
1. Check that your `.env` file is in the `backend/` directory
2. Verify the token format (should start with `ghp_`)
3. Test with a public repository first
4. Check GitHub API status: https://www.githubstatus.com/


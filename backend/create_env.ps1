# Prompt the user for environment variable values
$NVIDIA_API_KEY = Read-Host "Enter NVIDIA_API_KEY"
$NVIDIA_API_URL = Read-Host "Enter NVIDIA_API_URL"

$JIRA_API_TOKEN = Read-Host "Enter JIRA_API_TOKEN"
$JIRA_EMAIL = Read-Host "Enter JIRA_EMAIL"
$JIRA_BASE_URL = Read-Host "Enter JIRA_BASE_URL"

$GITHUB_TOKEN = Read-Host "Enter GITHUB_TOKEN"

# Define the content for the .env file
$envContent = @"
NVIDIA_API_KEY=$NVIDIA_API_KEY
NVIDIA_API_URL=$NVIDIA_API_URL

JIRA_API_TOKEN=$JIRA_API_TOKEN
JIRA_EMAIL=$JIRA_EMAIL
JIRA_BASE_URL=$JIRA_BASE_URL

GITHUB_TOKEN=$GITHUB_TOKEN

FLASK_ENV=development
FLASK_DEBUG=True
"@

# Write the content to .env (overwrites if it exists)
$envContent | Set-Content -Path ".env" -Encoding UTF8

Write-Host ".env file created successfully."

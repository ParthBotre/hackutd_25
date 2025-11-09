# Jira Integration - Quick Start Guide

## ⚡ Quick Setup (2 minutes)

### 1. Configure Credentials
Edit `backend/.env`:
```env
JIRA_BASE_URL=https://hack-utd-automations.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
```

### 2. Test Connection
```bash
cd backend
python jira_integration.py
```

Expected output:
```
✓ Connected to Jira as: Your Name
✓ Found 15 tickets
```

---

## 🎯 Usage

### Test Connection (API)
```bash
curl http://localhost:5001/api/jira/test
```

### Submit Mockup to Jira
```bash
curl -X POST http://localhost:5001/api/mockups/{mockup_id}/submit \
  -H "Content-Type: application/json" \
  -d '{"github_repo_url": "https://github.com/owner/repo.git"}'
```

---

## 📝 What Gets Created

Each mockup submission creates **multiple Jira tickets** with:

- ✅ **Title**: Short, actionable description
- ✅ **Description**: Detailed requirements
- ✅ **Acceptance Criteria**: Testable conditions
- ✅ **Difficulty**: 1-10 rating
- ✅ **Priority**: High/Medium/Low
- ✅ **Metadata**: GitHub URL, mockup ID

---

## 🔍 Troubleshooting

### Connection Fails
```bash
# Check if credentials are loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv('backend/.env'); print('Email:', os.getenv('JIRA_EMAIL')); print('Token:', 'SET' if os.getenv('JIRA_API_TOKEN') else 'NOT SET')"
```

### Invalid Credentials
1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Create new API token
3. Copy to `.env` file

### Project Key Error
- Default project is now "SM" (Scrum Management)
- Board URL: https://hack-utd-automations.atlassian.net/jira/core/projects/SM/board
- Verify project exists in your Jira workspace
- Or change `project_key` parameter when calling the function

---

## 📊 Example Response

```json
{
  "success": true,
  "message": "Created 3 ticket(s) in Jira",
  "tickets_created": 3,
  "tickets": [
    {
      "title": "Implement login form",
      "issue_key": "KAN-123",
      "issue_url": "https://hack-utd-automations.atlassian.net/browse/KAN-123",
      "difficulty": 5,
      "priority": 1,
      "success": true
    }
  ]
}
```

---

## ✅ Status: READY TO USE

All fixes applied, code is production-ready!


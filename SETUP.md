# PM Genie - Quick Setup Guide

**⚡ Get up and running in 5 minutes!**

## Prerequisites Checklist
- [ ] Python 3.8+ (`python --version`)
- [ ] Node.js 16+ (`node --version`)
- [ ] NVIDIA API Key from https://build.nvidia.com/

## 🚀 Quick Setup (5 Steps)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackutd_25
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Create a file named .env in the backend directory with:
```

**backend/.env file contents:**
```env
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions

# Optional: GitHub Integration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO_URL=https://github.com/your-username/your-repo

# Optional: JIRA Integration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token_here
```

**⚠️ Important:**
- NO quotes around values
- NO spaces around `=`
- File must be named exactly `.env`

```bash
# Start backend server
python app.py
```

✅ **Verify**: Should see "Running on http://127.0.0.1:5001"

### 3. Frontend Setup (New Terminal)
```bash
# Open NEW terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

✅ **Verify**: Browser opens to http://localhost:3000

## ✅ You're Done!

Both servers should be running:
- **Backend**: http://127.0.0.1:5001 
- **Frontend**: http://localhost:3000

## 🎮 Quick Feature Tour

### 1. Chat with AI
- Ask questions: "What are good features for a login page?"
- Get JIRA info: "How many tickets are in progress?"
- Load context: "fetch readme"

### 2. Generate Mockup
1. Say: "Create a dashboard for a banking app"
2. Review AI suggestions
3. Confirm: "yes, proceed"
4. Wait ~20 seconds
5. View your mockup!

### 3. View JIRA Board
- Click "JIRA Board" button
- See all tickets organized by status
- Filter and search tickets

### 4. Create JIRA Tickets
- After generating mockup, click "Create JIRA Tickets"
- AI analyzes mockup and creates detailed tickets
- View tickets with difficulty scores and priorities

## 🐛 Common Issues

**Backend won't start?**
- Check virtual environment is activated: `(venv)` in prompt
- Verify .env file exists in backend directory
- Test: Visit http://127.0.0.1:5001/api/health

**Frontend won't connect?**
- Make sure backend is running on port 5001
- Check browser console (F12) for errors
- Hard refresh: Ctrl+Shift+R

**API Key issues?**
- Verify no quotes in .env file
- Check key is valid at https://build.nvidia.com/
- Restart backend after changing .env

## 🔗 More Help

- Full documentation: See [README.md](README.md)
- GitHub token setup: See `backend/GITHUB_TOKEN_SETUP.md`
- JIRA setup: See `backend/test_jira.py`

## 📋 Environment Variables Reference

### Required
- `NVIDIA_API_KEY` - Your NVIDIA API key

### Optional
- `GITHUB_TOKEN` - For private repos or higher rate limits
- `GITHUB_REPO_URL` - Your repository URL for context
- `JIRA_BASE_URL` - Your Atlassian instance URL
- `JIRA_EMAIL` - Your Atlassian account email
- `JIRA_API_TOKEN` - Your JIRA API token

## 🎯 Next Steps

1. Generate your first mockup
2. Try the JIRA integration
3. Load your GitHub README for context-aware suggestions
4. Explore the markdown chat features
5. Create implementation tickets from mockups

---

**Need more details?** Check out the [full README](README.md) for comprehensive documentation!

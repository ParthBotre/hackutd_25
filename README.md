# PM Mockup Generator 🎨

An AI-powered mockup generation dashboard for Product Managers, powered by NVIDIA Nemotron. This application allows PMs to generate HTML mockups from natural language prompts, edit them with AI assistance, view past projects, and iterate before passing to developers.

## 🏆 HackUTD Challenge Integration

### PNC Challenge: AI-Powered Productivity for Product Managers
This solution supports Product Managers in the **Prototyping & Testing** phase by:
- Generating wireframes and mockups instantly from natural language descriptions
- Enabling rapid iteration with AI-assisted refinement
- Facilitating stakeholder feedback collection
- Accelerating speed to market by reducing manual design work

### NVIDIA Challenge: Intelligent Agents with Multi-Step Workflows
This project demonstrates:
- **Reasoning beyond single-prompt conversation**: The AI understands context and generates complete, production-ready HTML mockups
- **Workflow orchestration**: Multi-step process from prompt → generation → feedback → refinement
- **Tool integration**: Integration with NVIDIA Nemotron API through Brev for rate limit management
- **Practical value**: Real-world application solving PM productivity challenges

## ✨ Features

- 🤖 **AI-Powered Generation**: Leverages NVIDIA Nemotron for intelligent mockup creation
- 🔗 **GitHub Integration**: Analyze repositories and generate context-aware mockups
- 📋 **Jira Integration**: Automatically create development tickets from mockups
- ⚡ **Instant Preview**: Real-time HTML rendering with iframe preview
- ✏️ **AI-Powered HTML Editor**: Edit HTML with natural language instructions using AI Assistant
- 💾 **SQLite Database**: Persistent storage for all mockups and edits
- 📚 **Past Projects**: View and revisit all your previously generated mockups
- 🔄 **Auto-Save**: AI edits are automatically saved to the database
- 🔄 **AI Refinement**: Refine mockups with AI assistance
- 📥 **Export Ready**: Download HTML files to share with development teams
- 🎨 **Modern UI**: Beautiful, responsive dashboard built with React
- 🔍 **Code Editor**: Direct HTML editing with syntax highlighting
- 🎯 **Smart Ticket Generation**: Compare mockups with repos and create prioritized Jira tickets
- 🔧 **MCP Server**: Model Context Protocol server for GitHub-aware mockup generation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  - Dashboard: Prompt input, past projects list              │
│  - MockupViewer: Preview, code editor, AI editor assistant  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Backend (Flask)                            │
│  - API endpoints for generation & editing                    │
│  - HTML to image conversion                                  │
│  - SQLite database for persistent storage                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ API Calls
                     │
┌────────────────────▼────────────────────────────────────────┐
│              NVIDIA Nemotron API                             │
│  - Natural language to HTML conversion                       │
│  - HTML editing with natural language instructions           │
│  - Mockup refinement                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ 
- Node.js 16+
- npm or yarn
- Git (for cloning the repository)
- NVIDIA API Key (get from [NVIDIA API Catalog](https://build.nvidia.com/))
- GitHub Personal Access Token (optional, for private repos or higher rate limits)
- Jira credentials (optional, for Jira integration)

### Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd hackutd_25

# Or if you have the repository URL:
git clone https://github.com/your-username/hackutd_25.git
cd hackutd_25
```

**Note**: Replace `<repository-url>` with the actual repository URL.

### Backend Setup

#### Step 1: Navigate to Backend Directory

**Windows (PowerShell or Command Prompt):**
```powershell
cd backend
```

**Mac/Linux:**
```bash
cd backend
```

#### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

#### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

**✅ Verification**: You should see `(venv)` at the beginning of your command prompt.

#### Step 4: Install Dependencies

**Important**: Make sure your virtual environment is activated (you should see `(venv)` in your prompt).

```bash
pip install -r requirements.txt
```

**✅ Verification**: You should see "Successfully installed" messages. If you get errors, check:
- Python version is 3.8+ (`python --version`)
- Virtual environment is activated
- You have internet connection

#### Step 5: Configure Environment Variables

**Option A: Manual Creation (Recommended)**

1. Create a file named `.env` in the `backend` directory
2. Add the following content (replace placeholders with your actual values):

```env
# Required: NVIDIA API Key for mockup generation
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions

# Optional: GitHub Token (for private repos or higher rate limits)
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=your_github_token_here

# Optional: Jira Integration (for submitting mockups to Jira)
# Get from: https://id.atlassian.com/manage-profile/security/api-tokens
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your_jira_api_token_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

**⚠️ CRITICAL**: 
- Do NOT put quotes around the API key values
- Do NOT add spaces around the `=` sign
- The file must be named exactly `.env` (not `.env.txt` or `env`)
- Never commit the `.env` file to Git (it should be in `.gitignore`)

**Option B: Use PowerShell Script (Windows Only)**

```powershell
.\create_env.ps1
```

Or use the setup script:
```powershell
.\setup_env.ps1
```

Then edit the `.env` file it creates and add your actual API keys.

**✅ Verification**: 
- Check that `.env` file exists in `backend` directory
- Verify the NVIDIA_API_KEY is set (without quotes)
- Get your NVIDIA API key from: https://build.nvidia.com/
- GitHub token is optional (see `backend/GITHUB_TOKEN_SETUP.md` for details)
- Jira credentials are optional (only needed if using Jira integration)

#### Step 6: Run the Backend Server

**Make sure your virtual environment is activated** (you should see `(venv)` in your prompt).

```bash
python app.py
```

**✅ Expected Output:**
```
✅ NVIDIA_API_KEY loaded (length: XX characters)
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server...
 * Running on http://127.0.0.1:5001
Press CTRL+C to quit
```

**✅ Verification Steps:**
1. You should see "✅ NVIDIA_API_KEY loaded" message (not a warning)
2. Server should say "Running on http://127.0.0.1:5001"
3. Open a browser and visit: `http://127.0.0.1:5001/api/health`
   - You should see: `{"status": "healthy", "message": "PM Mockup Generator API is running"}`
4. The `data/mockups.db` file will be created automatically on first run

**⚠️ Common Issues:**
- If you see "⚠️ NVIDIA_API_KEY is empty or not set": Check your `.env` file exists and has the correct format
- If port 5001 is already in use: Stop other Flask processes or change the port in `app.py`
- If you get import errors: Make sure virtual environment is activated and dependencies are installed

**Keep this terminal window open** - the server needs to keep running!

### Frontend Setup

**⚠️ IMPORTANT**: Open a **NEW terminal window** for the frontend. Keep the backend terminal running!

#### Step 1: Navigate to Frontend Directory

**Windows (PowerShell or Command Prompt):**
```powershell
cd frontend
```

**Mac/Linux:**
```bash
cd frontend
```

**Note**: If you're in the `backend` directory, go back first:
```bash
cd ..
cd frontend
```

#### Step 2: Install Dependencies

```bash
npm install
```

**✅ Verification**: You should see:
- "up to date" or "added X packages" messages
- No critical errors (warnings about vulnerabilities are okay)

**⏱️ This may take 2-5 minutes** depending on your internet speed.

#### Step 3: Configure API URL (Optional)

If your backend is running on a different port or URL, create a `.env` file in the `frontend` directory:

```env
REACT_APP_API_URL=http://localhost:5001
```

**Note**: If you don't create this file, it defaults to `http://localhost:5001`. Only create it if you need to change the backend URL.

#### Step 4: Start the Development Server

```bash
npm start
```

**✅ Expected Output:**
```
Compiling...
Compiled successfully!

You can now view pm-mockup-generator in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
```

**✅ Verification Steps:**
1. Your browser should automatically open to `http://localhost:3000`
2. If not, manually open: `http://localhost:3000`
3. You should see the PM Mockup Generator dashboard
4. Check the browser console (F12) for any errors
5. Try generating a mockup to verify backend connection

**⚠️ Common Issues:**
- If port 3000 is already in use: The terminal will ask if you want to use a different port (press Y)
- If you see "Cannot connect to backend": 
  - Make sure backend is running on port 5001
  - Verify backend URL in `frontend/.env` (if you created one) matches your backend
  - Check browser console (F12) for specific error messages
  - Test backend directly: `http://127.0.0.1:5001/api/health`
- If npm install fails: Try deleting `node_modules` folder and `package-lock.json`, then run `npm install` again

**Keep this terminal window open** - the frontend server needs to keep running!

## 🚀 Quick Start Summary

**You need TWO terminal windows running simultaneously:**

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python app.py
```
✅ Should show: "Running on http://127.0.0.1:5001"

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```
✅ Should open browser to: http://localhost:3000

**Both servers must be running for the app to work!**

**Note**: All API calls use full URLs with port numbers (`http://localhost:5001/api/...`) for better portability. You can customize the backend URL by creating a `frontend/.env` file with `REACT_APP_API_URL=your_backend_url`.

## ✅ Pre-Flight Checklist

Before starting, verify you have everything:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] NVIDIA API key obtained from https://build.nvidia.com/
- [ ] Two terminal windows ready (one for backend, one for frontend)

## 🔍 Troubleshooting Guide

### Backend Won't Start

**Problem**: `python app.py` fails or shows errors

**Solutions**:
1. ✅ Check virtual environment is activated - you should see `(venv)` in your prompt
2. ✅ Verify Python version: `python --version` (should be 3.8+)
3. ✅ Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
4. ✅ Check if port 5001 is in use: `netstat -ano | findstr :5001` (Windows) or `lsof -i :5001` (Mac/Linux)
5. ✅ Make sure you're in the `backend` directory when running `python app.py`

### API Key Not Working

**Problem**: See "⚠️ NVIDIA_API_KEY is empty or not set" or "401 Unauthorized"

**Solutions**:
1. ✅ Verify `.env` file exists in `backend` directory (not root directory)
2. ✅ Check `.env` file format:
   ```
   ✅ CORRECT: NVIDIA_API_KEY=nvapi-abc123...
   ❌ WRONG:   NVIDIA_API_KEY="nvapi-abc123..."
   ❌ WRONG:   NVIDIA_API_KEY = nvapi-abc123...
   ```
3. ✅ Restart Flask server after creating/editing `.env` file
4. ✅ Test API key: Visit `http://127.0.0.1:5001/api/debug/api-key` in browser
5. ✅ Verify API key is valid at https://build.nvidia.com/

### Frontend Won't Connect to Backend

**Problem**: Frontend shows "Cannot connect to backend" or API calls fail

**Solutions**:
1. ✅ Verify backend is running: Visit `http://127.0.0.1:5001/api/health`
2. ✅ Check API URL configuration:
   - If `frontend/.env` exists, verify `REACT_APP_API_URL=http://localhost:5001`
   - Default is `http://localhost:5001` (no .env needed)
   - Make sure port matches your backend port
3. ✅ Restart frontend server after changing `.env` file (React needs restart for env changes)
4. ✅ Check browser console (F12) for specific error messages
   - Look for CORS errors or network errors
   - Check Network tab to see if requests are going to correct URL
5. ✅ Verify both servers are running simultaneously
6. ✅ Test API directly: Open `http://localhost:5001/api/health` in browser

### Database Issues

**Problem**: Edits not saving or projects not appearing

**Solutions**:
1. ✅ Check `backend/data/mockups.db` file exists
2. ✅ Verify file permissions (should be writable)
3. ✅ Restart backend server to reinitialize database connection
4. ✅ Check backend console for SQLite errors

### Port Already in Use

**Problem**: "Address already in use" error

**Solutions**:
- **Backend (port 5001)**: 
  - Find process: `netstat -ano | findstr :5001` (Windows) or `lsof -i :5001` (Mac/Linux)
  - Kill process or change port in `app.py` line 729: `app.run(debug=True, port=5002, ...)`
- **Frontend (port 3000)**:
  - Terminal will prompt to use different port - press `Y`
  - Or manually: `PORT=3001 npm start`

## 📖 Usage Guide

### 1. Generate a Mockup

1. Open the dashboard at `http://localhost:3000`
2. Enter a project name (optional)
3. Describe your desired mockup in the prompt field. Be specific about:
   - Layout requirements
   - Features to include
   - Visual style preferences
   - Target audience
4. Click "Generate Mockup"
5. Wait for AI to generate your mockup (15-30 seconds)

**Example Prompts**:
- "Create a modern landing page for a fintech SaaS product with a hero section, features grid, and pricing table"
- "Design a dashboard for a project management tool with sidebar navigation, task cards, and progress charts"
- "Build a product page for an e-commerce site with image gallery, product details, and add to cart button"

### 2. View and Edit Mockups

1. **Preview Tab**: View the rendered HTML mockup in real-time
2. **HTML Code Tab**: View and copy the HTML source code
3. **Edit with AI Tab**: 
   - Edit HTML directly in the code editor
   - Use the AI Editor Assistant (right sidebar) to make changes with natural language
   - Examples: "Change the background color to blue", "Make the heading larger", "Add rounded corners to buttons"
   - AI edits are automatically saved to the database
   - Manual edits can be saved with the "Save Changes" button

### 3. View Past Projects

1. All generated mockups appear in the "Past Projects" section (right sidebar on dashboard)
2. Click any project card to view and edit it again
3. Your edits are persisted in the SQLite database

### 4. Refine with AI

1. Click "Refine with AI" button in the header
2. The AI will generate an improved version of the current mockup
3. Review and continue editing as needed

### 5. Export for Development

1. Once satisfied with the mockup, click "Download HTML"
2. Share the HTML file with your development team
3. Developers can use it as a reference for implementation

### 6. GitHub Repository Integration

1. When generating a mockup, optionally provide a GitHub repository URL
2. The system will analyze the repository to understand:
   - Technology stack (from package.json, requirements.txt, etc.)
   - Existing design patterns and components
   - Code structure and conventions
3. The mockup will be enhanced to align with your repository's context
4. This creates more relevant mockups that match your existing codebase

### 7. Submit to Jira

1. After generating a mockup, click the "Submit" button
2. The system will:
   - Compare the mockup with your GitHub repository
   - Identify required changes and implementation tasks
   - Create multiple Jira tickets with:
     - Difficulty scores (1-10)
     - Priority levels (High, Medium, Low)
     - Detailed descriptions
     - Acceptance criteria
3. View all created tickets with their details and links

## 🛠️ API Endpoints

### Health Check
```
GET /api/health
```
Returns API health status.

### Debug API Key
```
GET /api/debug/api-key
```
Returns API key status (without exposing the key).

### Generate Mockup
```
POST /api/generate-mockup
Content-Type: application/json

{
  "prompt": "Description of the mockup",
  "project_name": "Optional project name",
  "github_repo_url": "https://github.com/owner/repo"  // Optional: for context-aware generation
}
```

**Note**: If `github_repo_url` is provided, the system will analyze the repository and enhance the mockup to align with the repository's technology stack and patterns.

### List All Mockups
```
GET /api/mockups?limit=10&include_html=false
```
Returns list of all mockups stored in database.

### Get Single Mockup
```
GET /api/mockups/{mockup_id}?include_html=true
```
Returns mockup metadata and optionally HTML content.

### Get Mockup HTML
```
GET /api/mockups/{mockup_id}/html
```
Returns HTML file directly.

### Get Mockup Screenshot
```
GET /api/mockups/{mockup_id}/screenshot
```
Returns screenshot image.

### Update Mockup HTML
```
PUT /api/mockups/{mockup_id}/update
Content-Type: application/json

{
  "html_content": "Updated HTML content"
}
```
Updates the HTML content in the database and regenerates screenshot.

### Edit HTML with AI
```
POST /api/edit-html
Content-Type: application/json

{
  "html_content": "Original HTML",
  "instruction": "Change the background color to blue"
}
```
Uses AI to edit HTML based on natural language instruction.

### Refine Mockup
```
POST /api/refine-mockup
Content-Type: application/json

{
  "original_html": "Original HTML content",
  "feedback": ["Feedback item 1", "Feedback item 2"]
}
```
Refines mockup based on feedback.

### Submit Mockup to Jira
```
POST /api/mockups/{mockup_id}/submit
```

Analyzes the mockup against the GitHub repository and creates multiple Jira tickets with:
- Difficulty scores (1-10)
- Priority levels (High, Medium, Low)
- Detailed descriptions
- Acceptance criteria

**Response:**
```json
{
  "success": true,
  "message": "Created 3 ticket(s) in Jira",
  "tickets_created": 3,
  "tickets_failed": 0,
  "tickets": [
    {
      "title": "Implement user dashboard component",
      "issue_key": "KAN-10",
      "issue_url": "https://...",
      "difficulty": 5,
      "priority": 1,
      "success": true
    }
  ]
}
```

## 🔧 Configuration

### NVIDIA Nemotron Configuration

The application uses NVIDIA's `nvidia/llama-3.3-nemotron-super-49b-v1.5` model. To configure:

1. Sign up at [NVIDIA API Catalog](https://build.nvidia.com/)
2. Generate an API key
3. Add to `backend/.env`:
   ```env
   NVIDIA_API_KEY=your_actual_api_key_here
   NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
   ```
4. **Important**: Remove any quotes around the API key value
5. Restart the Flask server after creating/updating the `.env` file

### GitHub Integration (Optional)

For GitHub repository analysis and context-aware mockups:

1. Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope (for private repos) or `public_repo` scope (for public repos)
3. Add to `backend/.env`:
   ```env
   GITHUB_TOKEN=ghp_your_token_here
   ```
4. **Note**: Without a token, you can still use public repositories (with 60 requests/hour limit)
5. See `backend/GITHUB_TOKEN_SETUP.md` for detailed instructions

### Jira Integration (Optional)

For submitting mockups to Jira and creating development tickets:

1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create an API token
3. Add to `backend/.env`:
   ```env
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your_jira_api_token_here
   ```
4. The system will create tickets in the "KAN" project by default (configurable in code)
5. See `backend/test_jira.py` to test your Jira connection

**Windows Users**: You can use `create_env.ps1` or `setup_env.ps1` script to create the `.env` file template.

### Customization

- **Model parameters**: Edit `temperature` and `max_tokens` in `app.py`
- **Screenshot size**: Modify `size` parameter in `hti.screenshot()` calls
- **UI theme**: Update CSS files in `frontend/src/components/`

## 📁 Project Structure

```
hackutd_25/
├── backend/
│   ├── app.py                      # Flask backend with API endpoints
│   ├── requirements.txt             # Python dependencies
│   ├── setup_env.ps1               # Windows PowerShell script to create .env
│   ├── create_env.ps1              # Alternative env creation script
│   ├── .env                        # Environment variables (create this, not in repo)
│   ├── nemotron_client.py          # NVIDIA Nemotron API client
│   ├── github_integration.py       # GitHub API integration
│   ├── jira_integration.py         # Jira API integration
│   ├── repo_mockup_generator.py    # Repository-aware mockup generator
│   ├── mockup_analyzer.py          # Mockup vs repo comparison and ticket generation
│   ├── mcp_server.py               # MCP server for GitHub-aware generation
│   ├── test_jira.py                # Jira connection test script
│   ├── GITHUB_TOKEN_SETUP.md       # GitHub token setup guide
│   ├── MCP_SERVER_README.md        # MCP server documentation
│   ├── data/
│   │   └── mockups.db              # SQLite database (auto-created)
│   └── mockups/                    # Generated HTML files storage
├── frontend/
│   ├── public/
│   │   └── index.html              # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.js        # Main dashboard with past projects
│   │   │   ├── Dashboard.css
│   │   │   ├── MockupViewer.js     # Mockup viewer with AI editor
│   │   │   └── MockupViewer.css
│   │   ├── config/
│   │   │   └── api.js              # API endpoint configuration
│   │   ├── App.js                  # Root component
│   │   ├── App.css
│   │   ├── index.js                # React entry point
│   │   └── index.css
│   └── package.json                # Node dependencies
├── README.md                       # This file
└── SETUP.md                        # Quick setup guide
```

## 🎯 Use Cases

1. **Rapid Prototyping**: Quickly generate mockups for stakeholder meetings
2. **A/B Testing**: Generate multiple versions to test with users
3. **Client Presentations**: Create professional mockups for proposals
4. **Developer Handoff**: Provide clear visual references to development teams
5. **Sprint Planning**: Visualize features before sprint commitment
6. **Stakeholder Alignment**: Get feedback early in the design process

## 🚧 Additional Troubleshooting

> **📌 For comprehensive troubleshooting, see the [Troubleshooting Guide](#-troubleshooting-guide) section above.**

### Quick Fixes

**Mockup preview not loading**
- Check browser console (F12) for errors
- Ensure iframe sandbox permissions are correct
- Try hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)

**AI edits not working**
- Verify backend console shows "✅ NVIDIA_API_KEY loaded"
- Check API key has credits available at https://build.nvidia.com/
- Review backend console for detailed error messages
- Test API endpoint: `http://127.0.0.1:5001/api/debug/api-key`

**Projects not showing in Past Projects**
- Verify `backend/data/mockups.db` file exists
- Check backend console for database errors
- Try refreshing the dashboard page
- Verify you've generated at least one mockup

## 🔐 Security Notes

- **Never commit your `.env` file to version control** - it contains sensitive API keys
- Keep your API keys confidential:
  - NVIDIA API key
  - GitHub token (if using)
  - Jira credentials (if using)
- The HTML preview uses iframe sandboxing for security
- All data is stored locally in SQLite database (`backend/data/mockups.db`)
- For production deployment:
  - Migrate to a cloud database (PostgreSQL, MySQL, etc.)
  - Use environment variables or secret management services
  - Enable HTTPS for all API communications
  - Implement proper authentication and authorization

## 🌟 Features & Enhancements

### ✅ Implemented Features

- [x] Database integration for persistent storage (SQLite)
- [x] Past projects viewing
- [x] AI-powered HTML editing
- [x] GitHub repository integration
- [x] Context-aware mockup generation
- [x] Jira integration for ticket creation
- [x] Smart ticket generation with difficulty and priority
- [x] MCP server for GitHub-aware mockup generation
- [x] Mockup vs repository comparison
- [x] Automated acceptance criteria generation

### 🚧 Future Enhancements

- [ ] User authentication and project management
- [ ] Version control for mockup iterations
- [ ] Collaborative editing features
- [ ] Export to Figma/Sketch
- [ ] Mobile app support
- [ ] Real-time collaboration
- [ ] Template library
- [ ] AI-powered A/B test suggestions
- [ ] Cloud database migration for production
- [ ] Custom Jira project selection
- [ ] GitHub webhook integration
- [ ] Automated PR creation from mockups

## 📄 License

This project was created for HackUTD 2025.

## 🙏 Acknowledgments

- **NVIDIA** for providing the Nemotron AI model
- **PNC** for sponsoring the Product Manager productivity challenge
- **HackUTD** for organizing the hackathon
- **Brev** for rate limit management infrastructure

## 📞 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the API documentation
3. Check Flask and React console logs
4. Refer to NVIDIA API documentation
5. Check `backend/GITHUB_TOKEN_SETUP.md` for GitHub integration help
6. Check `backend/MCP_SERVER_README.md` for MCP server documentation
7. Run `python backend/test_jira.py` to test Jira connection

## 🔗 Additional Resources

- **GitHub Integration**: See `backend/GITHUB_TOKEN_SETUP.md`
- **MCP Server**: See `backend/MCP_SERVER_README.md`
- **Quick Setup**: See `SETUP.md` for a condensed setup guide
- **Jira Testing**: Run `python backend/test_jira.py` to verify Jira connection

## 📝 Quick Setup Checklist

After cloning the repository:

- [ ] Install Python 3.8+ and Node.js 16+
- [ ] Create virtual environment: `python -m venv backend/venv`
- [ ] Activate virtual environment
- [ ] Install backend dependencies: `pip install -r backend/requirements.txt`
- [ ] Install frontend dependencies: `npm install` (in frontend directory)
- [ ] Create `backend/.env` file with NVIDIA_API_KEY
- [ ] (Optional) Add GITHUB_TOKEN to `.env` for GitHub integration
- [ ] (Optional) Add Jira credentials to `.env` for Jira integration
- [ ] Start backend: `python backend/app.py`
- [ ] Start frontend: `npm start` (in frontend directory)
- [ ] Open http://localhost:3000 in your browser

---

Built with ❤️ for HackUTD 2025


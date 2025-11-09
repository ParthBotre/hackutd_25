# 🪟 Windows Setup Guide

## Prerequisites

1. **Python 3.8+**: Download from https://python.org
   - ✅ Check "Add Python to PATH" during installation!
2. **Node.js 16+**: Download from https://nodejs.org
3. **Git**: Download from https://git-scm.com

---

## ⚡ Quick Setup for Windows

### Step 1: Get Your NVIDIA API Key

1. Go to https://build.nvidia.com/
2. Sign in and get your API key
3. Copy the key (starts with `nvapi-...`)

### Step 2: Setup Backend

Open **Command Prompt** or **PowerShell**:

```cmd
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (you'll need to edit this!)
type nul > .env
```

Now **edit the `.env` file** in `backend` folder with Notepad:
```
NVIDIA_API_KEY=your_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
FLASK_ENV=development
FLASK_DEBUG=True
```

**Start backend:**
```cmd
python app.py
```

Leave this window open! Backend runs on http://localhost:5001

---

### Step 3: Setup Frontend

Open a **NEW** Command Prompt or PowerShell window:

```cmd
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

Frontend will automatically open at http://localhost:3000

---

## 🔧 Key Differences from Mac/Linux

### 1. **Virtual Environment Activation**
- **Windows:** `venv\Scripts\activate`
- **Mac/Linux:** `source venv/bin/activate`

### 2. **Path Separators**
- **Windows:** Backslashes `\`
- **Mac/Linux:** Forward slashes `/`

### 3. **Shell Scripts Don't Work**
- ❌ `setup.sh` won't work on Windows
- ❌ `start_all.sh` won't work on Windows
- ✅ Use the commands above instead
- ✅ Or use PowerShell scripts (if you want to create them)

### 4. **Creating .env File**
- **Windows:** `type nul > .env` or just create in Notepad
- **Mac/Linux:** `cat > .env << 'EOF'`

### 5. **Environment Variables**
- Same `.env` file works on both!
- No changes needed to the `.env` content

---

## 📝 Step-by-Step (Detailed)

### Backend Setup

```powershell
# Navigate to backend
cd C:\path\to\hackutd_25\backend

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# You should see (venv) in your prompt

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Create .env file
notepad .env
```

In Notepad, paste:
```
NVIDIA_API_KEY=nvapi-your-key-here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
FLASK_ENV=development
FLASK_DEBUG=True
```

Save and close.

Start backend:
```powershell
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5001
```

---

### Frontend Setup

Open a **new** PowerShell/Command Prompt:

```powershell
# Navigate to frontend
cd C:\path\to\hackutd_25\frontend

# Install dependencies (takes a few minutes)
npm install

# Start development server
npm start
```

Browser should automatically open to http://localhost:3000

---

## 🐛 Windows-Specific Troubleshooting

### "python is not recognized"
- **Fix:** Reinstall Python and check "Add to PATH"
- **Or:** Use `py` instead of `python`

### "npm is not recognized"
- **Fix:** Reinstall Node.js
- **Restart** your terminal after installation

### "Activate.ps1 cannot be loaded"
PowerShell execution policy issue:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating venv again.

### Port 5000 or 5001 in use
Check what's using the port:
```powershell
netstat -ano | findstr :5001
```
Kill the process:
```powershell
taskkill /PID <process_id> /F
```

### Port 3000 in use
```powershell
netstat -ano | findstr :3000
taskkill /PID <process_id> /F
```

---

## 🚀 Starting the App (After First Setup)

### Terminal 1 - Backend:
```cmd
cd backend
venv\Scripts\activate
python app.py
```

### Terminal 2 - Frontend:
```cmd
cd frontend
npm start
```

---

## 💡 Windows PowerShell Tips

### Create a startup script (Optional)

**`start-backend.ps1`:**
```powershell
Set-Location backend
.\venv\Scripts\Activate.ps1
python app.py
```

**`start-frontend.ps1`:**
```powershell
Set-Location frontend
npm start
```

Run them:
```powershell
.\start-backend.ps1
.\start-frontend.ps1
```

---

## 🔄 Git Commands (Same on Windows!)

Git commands are the same:
```bash
git clone https://github.com/ParthBotre/hackutd_25.git
git add .
git commit -m "message"
git push
```

---

## ✅ Verification Checklist

- [ ] Python installed and in PATH
- [ ] Node.js installed and in PATH
- [ ] Git installed
- [ ] Backend virtual environment created
- [ ] Dependencies installed (Python & Node)
- [ ] `.env` file created with API key
- [ ] Backend running on port 5001
- [ ] Frontend running on port 3000
- [ ] Browser opens to http://localhost:3000
- [ ] Can generate mockups successfully

---

## 🎯 Quick Reference

| Task | Windows Command | Mac/Linux Command |
|------|----------------|-------------------|
| Create venv | `python -m venv venv` | `python3 -m venv venv` |
| Activate venv | `venv\Scripts\activate` | `source venv/bin/activate` |
| Deactivate venv | `deactivate` | `deactivate` |
| Create .env | `type nul > .env` | `touch .env` |
| Python command | `python` | `python3` |
| Path separator | `\` | `/` |

---

## 📚 Additional Resources

- **Python on Windows:** https://docs.python.org/3/using/windows.html
- **Node.js on Windows:** https://nodejs.org/en/download/
- **PowerShell Basics:** https://learn.microsoft.com/en-us/powershell/

---

## 🆘 Need Help?

If you're stuck:
1. Make sure all prerequisites are installed
2. Restart your terminal/Command Prompt
3. Check that `.env` has your actual API key
4. Verify ports 5001 and 3000 are available
5. Check the backend terminal for error messages

---

**Built for HackUTD 2025** 🚀


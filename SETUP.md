# Quick Setup Guide

## 🚀 Fast Start (5 minutes)

### Step 1: Get Your NVIDIA API Key

1. Go to https://build.nvidia.com/
2. Sign in or create an account
3. Navigate to the API Catalog
4. Find "Nemotron-4-340B-Instruct" 
5. Click "Get API Key"
6. Copy your API key

### Step 2: Setup Backend

Open a terminal and run:

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOL
NVIDIA_API_KEY=YOUR_API_KEY_HERE
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions
FLASK_ENV=development
FLASK_DEBUG=True
EOL

# Replace YOUR_API_KEY_HERE with your actual API key
# You can edit the .env file with: nano .env or vim .env

# Start backend
python app.py
```

Backend should now be running on http://localhost:5000

### Step 3: Setup Frontend

Open a **new terminal** (keep backend running) and run:

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

Frontend should now be running on http://localhost:3000 and automatically open in your browser!

## ✅ Verify Installation

1. Open http://localhost:3000 in your browser
2. You should see the PM Mockup Generator dashboard
3. Enter a test prompt: "Create a simple landing page with a header and call-to-action button"
4. Click "Generate Mockup"
5. Wait 15-30 seconds for the AI to generate your mockup

## 🐛 Common Issues

### "NVIDIA_API_KEY not found"
Make sure you:
1. Created the `.env` file in the `backend` directory
2. Added your actual API key (not `YOUR_API_KEY_HERE`)
3. Restarted the Flask server after creating `.env`

### "Module not found" errors
Run these commands in the backend directory:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend won't start
Try:
```bash
rm -rf node_modules package-lock.json
npm install
npm start
```

### Port already in use
If port 5000 or 3000 is busy, you can change ports:
- Backend: Edit `app.run(port=5001)` in `app.py`
- Frontend: Set `PORT=3001` before running `npm start`

## 📚 Next Steps

- Read the full README.md for detailed documentation
- Try the example prompts in the dashboard
- Experiment with different mockup descriptions
- Share with your team for feedback!

## 💡 Tips for Best Results

1. **Be specific** in your prompts - mention colors, layout, features
2. **Start simple** - test with basic layouts first
3. **Iterate** - use the feedback system to refine mockups
4. **Export early** - download HTML to review offline

## 🎯 Example Workflow

1. Generate initial mockup with prompt
2. Preview in the viewer
3. Collect feedback from stakeholders
4. Click "Refine with AI" to improve based on feedback
5. Download final HTML to share with developers

Happy mockup generating! 🎨✨


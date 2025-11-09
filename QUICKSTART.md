# ⚡ Quick Start - Get Running in 5 Minutes

## Prerequisites Check

```bash
# Check Python (need 3.8+)
python3 --version

# Check Node.js (need 16+)
node --version

# Check npm
npm --version
```

If any are missing, install them first!

## Option 1: Automated Setup (Recommended)

### macOS/Linux:

```bash
# 1. Setup backend
cd backend
./setup.sh
# Edit .env file and add your NVIDIA API key
nano .env  # or use any text editor

# 2. Setup frontend (open new terminal)
cd frontend
./setup.sh

# 3. Start everything (open new terminal from project root)
./start_all.sh
```

### Windows:

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Create .env file and add NVIDIA_API_KEY
python app.py

# Frontend (new terminal)
cd frontend
npm install
npm start
```

## Option 2: Manual Setup

### Backend (Terminal 1):

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo 'NVIDIA_API_KEY=your_key_here' > .env
echo 'NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions' >> .env
echo 'FLASK_ENV=development' >> .env
echo 'FLASK_DEBUG=True' >> .env

# Edit .env and add your actual API key
nano .env

# Start backend
python app.py
```

### Frontend (Terminal 2):

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm start
```

## Getting Your NVIDIA API Key

1. Go to https://build.nvidia.com/
2. Sign in / Sign up
3. Find "Nemotron-4-340B-Instruct"
4. Click "Get API Key"
5. Copy the key
6. Paste it in `backend/.env`

## Verify It's Working

1. Open http://localhost:3000
2. You should see the PM Mockup Generator dashboard
3. Try this test prompt:
   ```
   Create a simple landing page with a hero section, feature cards, and a call-to-action button
   ```
4. Click "Generate Mockup"
5. Wait 30 seconds
6. You should see a beautiful mockup!

## Troubleshooting

### "Cannot connect to backend"
- Make sure backend is running on port 5000
- Check for errors in the backend terminal

### "NVIDIA API error"
- Verify your API key in `.env`
- Check you have API credits at https://build.nvidia.com/
- Restart the backend after changing `.env`

### "Module not found" (Python)
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "Module not found" (Node)
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Check what's using port 5000
lsof -i :5000
# Kill it or change port in app.py

# Check what's using port 3000
lsof -i :3000
# Kill it or set PORT=3001 before npm start
```

## 🎯 First Steps After Setup

1. **Test basic generation**: Use simple prompts first
2. **Explore examples**: Click example prompts in the dashboard
3. **Try feedback system**: Generate a mockup, add feedback, refine it
4. **Export HTML**: Download and view the generated HTML
5. **Read the docs**: Check README.md for detailed info

## 🚀 You're Ready!

Now you can:
- Generate professional mockups in seconds
- Collect stakeholder feedback
- Iterate with AI refinement
- Export for development

Check out `DEMO_SCRIPT.md` for demo ideas and `PITCH.md` for the full story!

---

**Need help?** Check the full README.md or troubleshooting section above.

**Ready to demo?** Check out DEMO_SCRIPT.md for the perfect pitch!


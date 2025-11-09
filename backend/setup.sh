#!/bin/bash

echo "🚀 PM Mockup Generator - Backend Setup"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

echo "✅ pip upgraded"
echo ""

# Install requirements
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOL'
# NVIDIA Nemotron API Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1/chat/completions

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
EOL
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your NVIDIA API key!"
    echo "   Get your API key from: https://build.nvidia.com/"
    echo ""
else
    echo "ℹ️  .env file already exists, skipping creation"
    echo ""
fi

# Create mockups directory
mkdir -p mockups
echo "✅ Mockups directory created"
echo ""

echo "🎉 Backend setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file and add your NVIDIA API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python app.py"
echo ""
echo "The backend will start on http://localhost:5000"


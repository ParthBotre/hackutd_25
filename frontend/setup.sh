#!/bin/bash

echo "🚀 PM Mockup Generator - Frontend Setup"
echo "======================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Node.js found: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm found: $(npm --version)"
echo ""

# Install dependencies
echo "📥 Installing Node.js dependencies..."
echo "   (This may take a few minutes...)"
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed"
echo ""

echo "🎉 Frontend setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure the backend is running on http://localhost:5000"
echo "2. Run: npm start"
echo ""
echo "The frontend will start on http://localhost:3000"


#!/bin/bash

echo "🚀 Starting PM Mockup Generator"
echo "================================"
echo ""

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Check if backend is already running
if check_port 5000; then
    echo "⚠️  Backend already running on port 5000"
else
    echo "🔧 Starting backend..."
    cd backend
    source venv/bin/activate 2>/dev/null || . venv/bin/activate
    python app.py &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started (PID: $BACKEND_PID)"
fi

echo ""
sleep 2

# Check if frontend is already running
if check_port 3000; then
    echo "⚠️  Frontend already running on port 3000"
else
    echo "🎨 Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
fi

echo ""
echo "🎉 PM Mockup Generator is starting!"
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait


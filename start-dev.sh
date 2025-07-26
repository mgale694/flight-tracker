#!/bin/bash

# Flight Tracker Development Startup Script

echo "🚀 Starting Flight Tracker Development Environment"
echo "=================================================="

# Check if required directories exist
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: backend or frontend directory not found"
    echo "Please run this script from the flight-tracker root directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Function to start backend
start_backend() {
    echo "🔧 Starting FastAPI Backend..."
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Start backend
    echo "🚀 Starting backend on port 8000..."
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend started successfully
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    else
        echo "❌ Backend failed to start"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    echo "🔧 Starting React Frontend..."
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend
    echo "🚀 Starting frontend on port 5173..."
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    # Wait a moment for frontend to start
    sleep 3
    
    # Check if frontend started successfully
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
    else
        echo "❌ Frontend failed to start"
        exit 1
    fi
}

# Check ports
echo "🔍 Checking ports..."
if ! check_port 8000; then
    echo "Please stop the service using port 8000 and try again"
    exit 1
fi

if ! check_port 5173; then
    echo "Please stop the service using port 5173 and try again"
    exit 1
fi

# Start services
start_backend
start_frontend

echo ""
echo "🎉 Flight Tracker Development Environment Started!"
echo "=================================================="
echo "📡 Backend API: http://localhost:8000"
echo "📺 Frontend:    http://localhost:5173"
echo "📖 API Docs:    http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend stopped"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "✅ Frontend stopped"
    fi
    
    echo "👋 Development environment stopped"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait

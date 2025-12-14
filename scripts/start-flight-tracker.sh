#!/bin/bash

# Start both Backend and Frontend for Flight Tracker

echo "🚀 Starting Flight Tracker System"
echo "=================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

# Function to get local IP
get_local_ip() {
    local ip=$(ipconfig getifaddr en0 2>/dev/null)
    if [ -z "$ip" ]; then
        ip=$(hostname)
    fi
    echo "$ip"
}

LOCAL_IP=$(get_local_ip)

echo "📋 Pre-flight Checks"
echo "-------------------"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python 3 found"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi
echo "✅ Node.js found"

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use (Backend)"
    read -p "Kill the process? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null
        echo "✅ Port 8000 freed"
    else
        echo "❌ Cannot start backend on port 8000"
        exit 1
    fi
fi

if check_port 5173; then
    echo "⚠️  Port 5173 is already in use (Frontend)"
    read -p "Kill the process? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:5173 | xargs kill -9 2>/dev/null
        echo "✅ Port 5173 freed"
    else
        echo "❌ Cannot start frontend on port 5173"
        exit 1
    fi
fi

echo ""
echo "🔧 Setting up Backend"
echo "--------------------"

# Navigate to backend
cd "$PROJECT_ROOT/src/backend"

# Activate virtual environment
echo "🔧 Activating uvve virtual environment (flight-tracker)..."
uvve activate flight-tracker

# Install backend dependencies
echo "📥 Installing backend dependencies..."
uv pip install -q -r requirements.txt

echo "✅ Backend setup complete"
echo ""

# Start backend in background
echo "🌐 Starting Backend API..."
python main.py > /tmp/flight-tracker-backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if check_port 8000; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs: /tmp/flight-tracker-backend.log"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done

echo ""
echo "🔧 Setting up Frontend"
echo "---------------------"

# Navigate to frontend
cd "$PROJECT_ROOT/src/frontend"

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"
echo ""

# Start frontend in background
echo "🌐 Starting Frontend Dev Server..."
npm run dev > /tmp/flight-tracker-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
for i in {1..30}; do
    if check_port 5173; then
        echo "✅ Frontend is ready!"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start. Check logs: /tmp/flight-tracker-frontend.log"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        exit 1
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Flight Tracker is now running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}🔹 Backend API${NC}"
echo "   Local:   http://localhost:8000"
echo "   Network: http://$LOCAL_IP:8000"
echo "   Docs:    http://localhost:8000/docs"
echo ""
echo -e "${BLUE}🔹 Frontend Dashboard${NC}"
echo "   Local:   http://localhost:5173"
echo "   Network: http://$LOCAL_IP:5173"
echo ""
echo -e "${YELLOW}📊 Process IDs${NC}"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}📝 Logs${NC}"
echo "   Backend:  /tmp/flight-tracker-backend.log"
echo "   Frontend: /tmp/flight-tracker-frontend.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Flight Tracker..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    deactivate 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running and show logs
echo "📋 Showing combined logs (Ctrl+C to stop):"
echo "-------------------------------------------"
tail -f /tmp/flight-tracker-backend.log /tmp/flight-tracker-frontend.log

#!/bin/bash

# All-in-One Flight Tracker for Raspberry Pi
# Starts backend API, frontend web server, and e-ink display client

set -e  # Exit on error

echo "✈️  Flight Tracker - Raspberry Pi Complete System"
echo "=================================================="
echo ""

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get local IP address
get_local_ip() {
    # Try different methods to get IP
    local ip=$(hostname -I | awk '{print $1}')
    if [ -z "$ip" ]; then
        ip=$(ip route get 1 | awk '{print $7;exit}')
    fi
    if [ -z "$ip" ]; then
        ip="localhost"
    fi
    echo "$ip"
}

LOCAL_IP=$(get_local_ip)

echo "📋 Pre-flight Checks"
echo "-------------------"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 found${NC}"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    echo "Install with: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi
echo -e "${GREEN}✅ Node.js found${NC}"

echo ""
echo "🔧 Setting up Backend"
echo "--------------------"

cd "$PROJECT_ROOT/src/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
pip install -q -r requirements.txt

# Update backend config to bind to all interfaces
if [ -f "config.toml" ]; then
    echo "✅ Backend config found"
else
    echo -e "${RED}❌ Backend config.toml not found${NC}"
    exit 1
fi

# Start backend in background
echo "🌐 Starting Backend API..."
python main.py > /tmp/flight-tracker-backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start. Check logs: /tmp/flight-tracker-backend.log${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
done

echo ""
echo "🔧 Setting up Frontend"
echo "---------------------"

cd "$PROJECT_ROOT/src/frontend"

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"

# Build frontend for production
echo "🏗️  Building frontend..."
npm run build

# Serve frontend with a simple HTTP server
echo "🌐 Starting Frontend Web Server..."
npx serve -s dist -l 5173 > /tmp/flight-tracker-frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
sleep 3

echo ""
echo "🔧 Setting up E-ink Display Client"
echo "----------------------------------"

cd "$PROJECT_ROOT/src/raspi"

# Update raspi config to use localhost backend
if [ -f "config.toml" ]; then
    # Update API URL to localhost since everything runs on Pi
    sed -i 's|api_url = .*|api_url = "http://localhost:8000"|g' config.toml
    echo "✅ Raspi config updated to use local backend"
else
    echo -e "${RED}❌ Raspi config.toml not found${NC}"
    exit 1
fi

# Install raspi dependencies
echo "📥 Installing raspi dependencies..."
pip install -q -r requirements.txt

# Install Pi hardware packages if on Raspberry Pi
if [ -f "requirements-pi.txt" ] && command -v raspi-config &> /dev/null; then
    echo "📦 Installing Raspberry Pi hardware packages..."
    pip install -q -r requirements-pi.txt || echo "⚠️  Some hardware packages may need system install"
fi

# Start raspi client in background
echo "🖥️  Starting E-ink Display Client..."
python3 agent.py > /tmp/flight-tracker-raspi.log 2>&1 &
RASPI_PID=$!
echo -e "${GREEN}✅ E-ink Display Client started (PID: $RASPI_PID)${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Flight Tracker is now running on Raspberry Pi!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}🔹 Access from your laptop/phone:${NC}"
echo ""
echo -e "${YELLOW}   Frontend Dashboard:${NC}"
echo "   http://$LOCAL_IP:5173"
echo ""
echo -e "${YELLOW}   Backend API:${NC}"
echo "   http://$LOCAL_IP:8000"
echo "   http://$LOCAL_IP:8000/docs (API Documentation)"
echo ""
echo -e "${BLUE}🔹 E-ink Display:${NC}"
echo "   Running on Raspberry Pi hardware"
echo "   Check display for flight information"
echo ""
echo -e "${YELLOW}📊 Process IDs:${NC}"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo "   Display:  $RASPI_PID"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "   Backend:  /tmp/flight-tracker-backend.log"
echo "   Frontend: /tmp/flight-tracker-frontend.log"
echo "   Display:  /tmp/flight-tracker-raspi.log"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}💡 To configure settings:${NC}"
echo "   1. Open http://$LOCAL_IP:5173/settings in your browser"
echo "   2. Update your location and preferences"
echo "   3. Changes will apply immediately to the display"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping Flight Tracker..."
    kill $BACKEND_PID $FRONTEND_PID $RASPI_PID 2>/dev/null
    deactivate 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Keep script running and show logs
echo "📋 Showing combined logs (Ctrl+C to stop):"
echo "-------------------------------------------"
tail -f /tmp/flight-tracker-backend.log /tmp/flight-tracker-frontend.log /tmp/flight-tracker-raspi.log

#!/bin/bash

# Flight Tracker Startup Script
# Starts backend API, frontend with network hosting, and optionally raspi client

set -e  # Exit on any error

# Configuration
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/src/backend" && pwd)"
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/src/frontend/react" && pwd)"
RASPI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/src/raspi" && pwd)"

# Default ports and host
BACKEND_PORT=8000
FRONTEND_PORT=5173
FRONTEND_HOST="0.0.0.0"  # Allow external access
BACKEND_HOST="0.0.0.0"   # Allow external access

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# PID file locations
PIDS_DIR="/tmp/flight_tracker_pids"
mkdir -p "$PIDS_DIR"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process by PID file
kill_by_pidfile() {
    local pidfile=$1
    local service_name=$2
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if ps -p $pid > /dev/null 2>&1; then
            print_warning "Stopping existing $service_name (PID: $pid)"
            kill $pid
            sleep 2
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid
            fi
        fi
        rm -f "$pidfile"
    fi
}

# Function to setup all dependencies
setup_dependencies() {
    print_status "Setting up Flight Tracker dependencies..."
    
    # Check system prerequisites
    print_status "Checking system prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed. Please install Python3 first."
        print_status "On Raspberry Pi: sudo apt update && sudo apt install python3 python3-pip python3-venv -y"
        exit 1
    fi
    
    # Check if python3-venv is available
    if ! python3 -c "import venv" 2>/dev/null; then
        print_error "python3-venv module is not available. Please install it."
        print_status "On Raspberry Pi: sudo apt install python3-venv"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install Node.js and npm first."
        print_status "On Raspberry Pi: "
        print_status "  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
        print_status "  sudo apt-get install -y nodejs"
        exit 1
    fi
    
    print_success "System prerequisites check passed!"
    
    # Setup backend dependencies
    print_status "Setting up backend dependencies..."
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        if ! python3 -m venv venv; then
            print_error "Failed to create virtual environment. Check if python3-venv is installed."
            print_status "Try: sudo apt install python3-venv"
            exit 1
        fi
    fi
    
    # Check if virtual environment was created successfully
    if [ ! -f "venv/bin/activate" ]; then
        print_error "Virtual environment creation failed or incomplete."
        print_status "Removing incomplete venv and trying again..."
        rm -rf venv
        if ! python3 -m venv venv; then
            print_error "Failed to create virtual environment on second attempt."
            exit 1
        fi
    fi
    
    # Activate and install dependencies
    print_status "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        if ! pip install --upgrade pip; then
            print_warning "Failed to upgrade pip, continuing with current version..."
        fi
        if ! pip install -r requirements.txt; then
            print_error "Failed to install Python dependencies"
            exit 1
        fi
    fi
    
    # Setup frontend dependencies
    print_status "Setting up frontend dependencies..."
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    if [ ! -d "node_modules" ] || [ ! -f "package-lock.json" ]; then
        print_status "Installing Node.js dependencies..."
        if ! npm install; then
            print_error "Failed to install Node.js dependencies"
            exit 1
        fi
    else
        print_status "Node.js dependencies already installed"
    fi
    
    print_success "All dependencies installed successfully!"
    print_status "You can now run: $0 start"
}

# Function to start the backend
start_backend() {
    print_status "Starting Flight Tracker Backend..."
    
    # Check if backend port is already in use
    if check_port $BACKEND_PORT; then
        print_warning "Port $BACKEND_PORT is already in use. Attempting to stop existing service..."
        kill_by_pidfile "$PIDS_DIR/backend.pid" "backend"
        sleep 2
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists and create if needed
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment for backend..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        print_status "Installing/updating backend dependencies..."
        pip install -r requirements.txt
    fi
    
    # Start backend in background
    print_status "Starting backend process..."
    nohup ./venv/bin/python main.py --host $BACKEND_HOST --port $BACKEND_PORT > /tmp/flight_tracker_backend.log 2>&1 &
    local backend_pid=$!
    echo $backend_pid > "$PIDS_DIR/backend.pid"
    
    # Give the process a moment to start
    sleep 2
    
    # Check if the process is still running
    if ! kill -0 $backend_pid 2>/dev/null; then
        print_error "Backend process crashed immediately. Log output:"
        echo "----------------------------------------"
        cat /tmp/flight_tracker_backend.log
        echo "----------------------------------------"
        exit 1
    fi
    
    # Wait for backend to start responding
    print_status "Waiting for backend to start responding..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        # Check if process is still running
        if ! kill -0 $backend_pid 2>/dev/null; then
            print_error "Backend process died during startup. Log output:"
            echo "----------------------------------------"
            cat /tmp/flight_tracker_backend.log
            echo "----------------------------------------"
            exit 1
        fi
        
        # Check if backend is responding
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            print_success "Backend started successfully on http://$BACKEND_HOST:$BACKEND_PORT"
            return 0
        fi
        
        sleep 1
        ((attempts++))
        
        # Show progress every 5 seconds
        if [ $((attempts % 5)) -eq 0 ]; then
            print_status "Still waiting for backend... (${attempts}/${max_attempts})"
        fi
    done
    
    print_error "Backend failed to start responding after $max_attempts seconds"
    print_status "Backend log output:"
    echo "----------------------------------------"
    cat /tmp/flight_tracker_backend.log
    echo "----------------------------------------"
    exit 1
}

# Function to start the frontend
start_frontend() {
    print_status "Starting React Frontend..."
    
    # Check if frontend port is already in use
    if check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use. Attempting to stop existing service..."
        kill_by_pidfile "$PIDS_DIR/frontend.pid" "frontend"
        sleep 2
    fi
    
    # Check if Node.js is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        exit 1
    fi
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Update API base URL in frontend to use network-accessible backend
    print_status "Configuring frontend for network access..."
    
    # Start frontend in background with network host
    nohup npm run dev -- --host $FRONTEND_HOST --port $FRONTEND_PORT > /tmp/flight_tracker_frontend.log 2>&1 &
    echo $! > "$PIDS_DIR/frontend.pid"
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            print_success "Frontend started successfully on http://$FRONTEND_HOST:$FRONTEND_PORT"
            return 0
        fi
        sleep 1
        ((attempts++))
    done
    
    print_error "Frontend failed to start after $max_attempts seconds"
    cat /tmp/flight_tracker_frontend.log
    exit 1
}

# Function to test raspi client
test_raspi() {
    print_status "Testing Raspi API Client..."
    
    if [ ! -d "$RASPI_DIR" ]; then
        print_error "Raspi directory not found: $RASPI_DIR"
        return 1
    fi
    
    cd "$RASPI_DIR"
    
    if python3 api_simple.py > /tmp/flight_tracker_raspi_test.log 2>&1; then
        print_success "Raspi API client test passed"
        cat /tmp/flight_tracker_raspi_test.log
    else
        print_warning "Raspi API client test failed"
        cat /tmp/flight_tracker_raspi_test.log
    fi
}

# Function to show status
show_status() {
    print_status "Flight Tracker System Status:"
    echo
    
    # Backend status
    if [ -f "$PIDS_DIR/backend.pid" ] && ps -p $(cat "$PIDS_DIR/backend.pid") > /dev/null 2>&1; then
        print_success "✅ Backend: Running (PID: $(cat "$PIDS_DIR/backend.pid"))"
        echo "   URL: http://$BACKEND_HOST:$BACKEND_PORT"
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo "   Health: OK"
        else
            echo "   Health: NOT RESPONDING"
        fi
    else
        print_error "❌ Backend: Not running"
    fi
    
    echo
    
    # Frontend status
    if [ -f "$PIDS_DIR/frontend.pid" ] && ps -p $(cat "$PIDS_DIR/frontend.pid") > /dev/null 2>&1; then
        print_success "✅ Frontend: Running (PID: $(cat "$PIDS_DIR/frontend.pid"))"
        echo "   URL: http://$FRONTEND_HOST:$FRONTEND_PORT"
    else
        print_error "❌ Frontend: Not running"
    fi
    
    echo
    echo "Network URLs (accessible from other machines):"
    
    # Get local IP address
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
    if [ -n "$LOCAL_IP" ]; then
        echo "   Backend:  http://$LOCAL_IP:$BACKEND_PORT"
        echo "   Frontend: http://$LOCAL_IP:$FRONTEND_PORT"
    else
        echo "   Could not determine local IP address"
    fi
}

# Function to stop all services
stop_all() {
    print_status "Stopping all Flight Tracker services..."
    
    kill_by_pidfile "$PIDS_DIR/backend.pid" "backend"
    kill_by_pidfile "$PIDS_DIR/frontend.pid" "frontend"
    
    print_success "All services stopped"
}

# Function to show help
show_help() {
    echo "Flight Tracker Startup Script"
    echo
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  setup      Install all dependencies (run this first on new systems)"
    echo "  start      Start backend and frontend services"
    echo "  stop       Stop all running services"
    echo "  restart    Restart all services"
    echo "  status     Show status of all services"
    echo "  test       Test the raspi client"
    echo "  logs       Show recent logs"
    echo "  debug      Show detailed backend debug information"
    echo "  reset      Remove all installed dependencies and reset environment"
    echo "  help       Show this help message"
    echo
    echo "First Time Setup:"
    echo "  1. Run: $0 setup"
    echo "  2. Run: $0 start"
    echo
    echo "Troubleshooting:"
    echo "  If you encounter issues, try: $0 reset"
    echo "  Then run setup and start again"
    echo
    echo "Network Access:"
    echo "  Services will be accessible from other machines on the network"
    echo "  Backend:  http://YOUR_IP:$BACKEND_PORT"
    echo "  Frontend: http://YOUR_IP:$FRONTEND_PORT"
    echo
    echo "Environment Variables:"
    echo "  BACKEND_PORT   Backend port (default: $BACKEND_PORT)"
    echo "  FRONTEND_PORT  Frontend port (default: $FRONTEND_PORT)"
    echo "  BACKEND_HOST   Backend host (default: $BACKEND_HOST)"
    echo "  FRONTEND_HOST  Frontend host (default: $FRONTEND_HOST)"
}

# Function to show logs
show_logs() {
    print_status "Recent Backend Logs:"
    if [ -f "/tmp/flight_tracker_backend.log" ]; then
        tail -20 /tmp/flight_tracker_backend.log
    else
        echo "No backend logs found"
    fi
    
    echo
    print_status "Recent Frontend Logs:"
    if [ -f "/tmp/flight_tracker_frontend.log" ]; then
        tail -20 /tmp/flight_tracker_frontend.log
    else
        echo "No frontend logs found"
    fi
}

# Function to show debug information
show_debug() {
    print_status "=== BACKEND DEBUG INFORMATION ==="
    echo
    
    print_status "Backend Directory Check:"
    if [ -d "$BACKEND_DIR" ]; then
        echo "✓ Backend directory exists: $BACKEND_DIR"
        ls -la "$BACKEND_DIR"
    else
        echo "✗ Backend directory not found: $BACKEND_DIR"
        return 1
    fi
    
    echo
    print_status "Python Environment Check:"
    cd "$BACKEND_DIR"
    if [ -d "venv" ]; then
        echo "✓ Virtual environment exists"
        source venv/bin/activate
        echo "Python version: $(python --version)"
        echo "Python path: $(which python)"
        if [ -f "requirements.txt" ]; then
            echo "Checking installed packages against requirements:"
            pip check
        fi
    else
        echo "✗ Virtual environment not found"
    fi
    
    echo
    print_status "Configuration Check:"
    if [ -f "config.toml" ]; then
        echo "✓ Config file exists"
        echo "Config contents:"
        cat config.toml
    else
        echo "✗ Config file not found"
    fi
    
    echo
    print_status "Network Check:"
    echo "Backend host: $BACKEND_HOST"
    echo "Backend port: $BACKEND_PORT"
    if check_port $BACKEND_PORT; then
        echo "⚠ Port $BACKEND_PORT is already in use"
        echo "Processes using port $BACKEND_PORT:"
        lsof -i :$BACKEND_PORT || echo "Unable to check processes (lsof not available)"
    else
        echo "✓ Port $BACKEND_PORT is available"
    fi
    
    echo
    print_status "Recent Backend Logs:"
    if [ -f "/tmp/flight_tracker_backend.log" ]; then
        echo "Last 50 lines of backend log:"
        echo "----------------------------------------"
        tail -50 /tmp/flight_tracker_backend.log
        echo "----------------------------------------"
    else
        echo "No backend logs found"
    fi
    
    echo
    print_status "Manual Test Command:"
    echo "To manually test the backend, run:"
    echo "cd $BACKEND_DIR"
    echo "source venv/bin/activate"
    echo "python main.py --host $BACKEND_HOST --port $BACKEND_PORT"
}

# Function to reset environment
reset_environment() {
    print_status "=== RESETTING FLIGHT TRACKER ENVIRONMENT ==="
    echo
    print_warning "This will remove all installed dependencies and reset the environment."
    print_warning "You will need to run 'setup' again before using the Flight Tracker."
    echo
    
    # Ask for confirmation
    read -p "Are you sure you want to reset the environment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Reset cancelled."
        return 0
    fi
    
    # Stop all services first
    print_status "Stopping all services..."
    stop_all
    
    # Remove backend virtual environment
    print_status "Removing backend Python virtual environment..."
    if [ -d "$BACKEND_DIR/venv" ]; then
        rm -rf "$BACKEND_DIR/venv"
        print_success "✓ Backend virtual environment removed"
    else
        echo "  No backend virtual environment found"
    fi
    
    # Remove frontend node_modules
    print_status "Removing frontend Node.js dependencies..."
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        rm -rf "$FRONTEND_DIR/node_modules"
        print_success "✓ Frontend node_modules removed"
    else
        echo "  No frontend node_modules found"
    fi
    
    # Remove package-lock.json
    if [ -f "$FRONTEND_DIR/package-lock.json" ]; then
        rm -f "$FRONTEND_DIR/package-lock.json"
        print_success "✓ Frontend package-lock.json removed"
    fi
    
    # Remove log files
    print_status "Cleaning up log files..."
    rm -f /tmp/flight_tracker_backend.log
    rm -f /tmp/flight_tracker_frontend.log
    print_success "✓ Log files cleaned"
    
    # Remove PID files
    print_status "Cleaning up PID files..."
    rm -f "$PIDS_DIR"/*.pid
    print_success "✓ PID files cleaned"
    
    # Remove any Python cache files
    print_status "Removing Python cache files..."
    find "$BACKEND_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$BACKEND_DIR" -name "*.pyc" -type f -delete 2>/dev/null || true
    print_success "✓ Python cache files removed"
    
    echo
    print_success "=== ENVIRONMENT RESET COMPLETE ==="
    print_status "To reinstall dependencies, run: $0 setup"
    print_status "To start services, run: $0 start"
}

# Main script logic
case "${1:-start}" in
    "setup")
        setup_dependencies
        ;;
    "start")
        print_status "Starting Flight Tracker System..."
        start_backend
        start_frontend
        echo
        show_status
        echo
        print_status "To test the Raspi client, run: $0 test"
        print_status "To check status, run: $0 status"
        print_status "To stop all services, run: $0 stop"
        ;;
    "stop")
        stop_all
        ;;
    "restart")
        stop_all
        sleep 2
        start_backend
        start_frontend
        show_status
        ;;
    "status")
        show_status
        ;;
    "test")
        test_raspi
        ;;
    "logs")
        show_logs
        ;;
    "debug")
        show_debug
        ;;
    "reset")
        reset_environment
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

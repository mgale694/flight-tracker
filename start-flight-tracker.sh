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
YIGHLIGHT='\033[1;33m'
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
    echo -e "${YIGHLIGHT}[WARNING]${NC} $1"
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
    
    # Optimize for Raspberry Pi memory constraints
    print_status "Configuring memory settings for Raspberry Pi..."
    export NODE_OPTIONS="--max-old-space-size=1024"
    
    # Increase swap if available (helps with npm install)
    if command -v free &> /dev/null; then
        local mem_info=$(free -m)
        print_status "Current memory status:"
        echo "$mem_info"
    fi
    
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
    print_status "Setting up simple frontend (no Node.js dependencies needed)..."
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Clean up any existing Node.js artifacts
    if [ -d "node_modules" ]; then
        print_status "Removing old Node.js dependencies..."
        rm -rf node_modules package-lock.json
    fi
    
    print_success "Simple frontend setup complete!"
    
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
        pip install -q -r requirements.txt
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
        
        # Check if there are any error messages in the log
        if [ -f "/tmp/flight_tracker_backend.log" ] && [ -s "/tmp/flight_tracker_backend.log" ]; then
            # Check for common error patterns
            if grep -q -i "error\|exception\|traceback\|failed\|could not" /tmp/flight_tracker_backend.log; then
                print_error "Backend encountered errors during startup. Log output:"
                echo "----------------------------------------"
                cat /tmp/flight_tracker_backend.log
                echo "----------------------------------------"
                exit 1
            fi
        fi
        
        # Check if backend is responding (try multiple methods)
        local health_check_success=false
        
        # Method 1: Try curl if available
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
                health_check_success=true
            fi
        # Method 2: Try wget if curl not available
        elif command -v wget &> /dev/null; then
            if wget -q --timeout=2 --tries=1 -O /dev/null http://localhost:$BACKEND_PORT/health 2>/dev/null; then
                health_check_success=true
            fi
        # Method 3: Try netcat/nc if available
        elif command -v nc &> /dev/null; then
            if echo "" | nc -w 2 localhost $BACKEND_PORT > /dev/null 2>&1; then
                health_check_success=true
            fi
        fi
        
        if [ "$health_check_success" = true ]; then
            print_success "Backend started successfully on http://$BACKEND_HOST:$BACKEND_PORT"
            return 0
        fi
        
        sleep 1
        ((attempts++))
        
        # Show progress every 5 seconds with more detail
        if [ $((attempts % 5)) -eq 0 ]; then
            print_status "Still waiting for backend... (${attempts}/${max_attempts})"
            if [ -f "/tmp/flight_tracker_backend.log" ]; then
                echo "Recent log output:"
                tail -3 /tmp/flight_tracker_backend.log 2>/dev/null || echo "No recent log output"
            fi
        fi
    done
    
    print_error "Backend failed to start responding after $max_attempts seconds"
    print_status "Final backend log output:"
    echo "----------------------------------------"
    if [ -f "/tmp/flight_tracker_backend.log" ]; then
        cat /tmp/flight_tracker_backend.log
    else
        echo "No log file found at /tmp/flight_tracker_backend.log"
    fi
    echo "----------------------------------------"
    
    print_status "Process status:"
    if kill -0 $backend_pid 2>/dev/null; then
        echo "Backend process (PID: $backend_pid) is still running"
    else
        echo "Backend process (PID: $backend_pid) has terminated"
    fi
    
    print_status "Network diagnostics:"
    echo "Checking if port $BACKEND_PORT is listening..."
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep ":$BACKEND_PORT " || echo "Port $BACKEND_PORT is not listening"
    elif command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null | grep ":$BACKEND_PORT " || echo "Port $BACKEND_PORT is not listening"
    else
        echo "Unable to check port status (netstat/ss not available)"
    fi
    
    exit 1
}

# Function to start the frontend
start_frontend() {
    print_status "Starting Simple Frontend..."
    
    # Check if frontend port is already in use
    if check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use. Attempting to stop existing service..."
        kill_by_pidfile "$PIDS_DIR/frontend.pid" "frontend"
        sleep 2
    fi
    
    # Check if frontend directory exists
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Remove any existing node_modules to avoid confusion
    if [ -d "node_modules" ]; then
        print_status "Removing old Node.js dependencies (no longer needed)..."
        rm -rf node_modules package-lock.json
    fi
    
    # Start simple HTTP server using Python (no Node.js dependencies needed)
    print_status "Starting Python HTTP server for simple frontend..."
    nohup python3 -m http.server $FRONTEND_PORT > /tmp/flight_tracker_frontend.log 2>&1 &
    local frontend_pid=$!
    echo $frontend_pid > "$PIDS_DIR/frontend.pid"
    
    # Give the process time to build and start (TypeScript compilation takes time)
    sleep 5
    
    # Check if the process is still running
    if ! kill -0 $frontend_pid 2>/dev/null; then
        print_error "Frontend process crashed during startup. Log output:"
        echo "----------------------------------------"
        cat /tmp/flight_tracker_frontend.log
        echo "----------------------------------------"
        exit 1
    fi
    
    # Wait for frontend to start
    print_status "Waiting for frontend to start responding..."
    local attempts=0
    local max_attempts=45  # TypeScript compilation + server startup
    
    while [ $attempts -lt $max_attempts ]; do
        # Check if process is still running
        if ! kill -0 $frontend_pid 2>/dev/null; then
            print_error "Frontend process died during startup. Log output:"
            echo "----------------------------------------"
            cat /tmp/flight_tracker_frontend.log
            echo "----------------------------------------"
            exit 1
        fi
        
        # Check if there are any error messages in the log
        if [ -f "/tmp/flight_tracker_frontend.log" ] && [ -s "/tmp/flight_tracker_frontend.log" ]; then
            # Check for common error patterns (but not "Illegal instruction" since we removed Vite)
            if grep -q -i "error.*failed\|exception\|cannot resolve\|port.*already in use\|compilation.*failed" /tmp/flight_tracker_frontend.log; then
                print_error "Frontend encountered errors during startup. Log output:"
                echo "----------------------------------------"
                cat /tmp/flight_tracker_frontend.log
                echo "----------------------------------------"
                exit 1
            fi
        fi
        
        # Check if frontend is responding
        local health_check_success=false
        
        # Try multiple methods to check if frontend is responding
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 2 http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
                health_check_success=true
            fi
        elif command -v wget &> /dev/null; then
            if wget -q --timeout=2 --tries=1 -O /dev/null http://localhost:$FRONTEND_PORT 2>/dev/null; then
                health_check_success=true
            fi
        elif command -v nc &> /dev/null; then
            if echo "" | nc -w 2 localhost $FRONTEND_PORT > /dev/null 2>&1; then
                health_check_success=true
            fi
        fi
        
        if [ "$health_check_success" = true ]; then
            print_success "Simple Frontend started successfully on http://$FRONTEND_HOST:$FRONTEND_PORT"
            print_status "Access your flight tracker at: http://$(hostname -I | awk '{print $1}'):$FRONTEND_PORT"
            return 0
        fi
        
        sleep 1
        ((attempts++))
        
        # Show progress every 10 seconds
        if [ $((attempts % 10)) -eq 0 ]; then
            print_status "Still waiting for frontend... (${attempts}/${max_attempts})"
            if [ -f "/tmp/flight_tracker_frontend.log" ]; then
                echo "Recent log output:"
                tail -3 /tmp/flight_tracker_frontend.log 2>/dev/null || echo "No recent log output"
            fi
        fi
    done
    
    print_error "Frontend failed to start responding after $max_attempts seconds"
    print_status "Final frontend log output:"
    echo "----------------------------------------"
    if [ -f "/tmp/flight_tracker_frontend.log" ]; then
        cat /tmp/flight_tracker_frontend.log
    else
        echo "No log file found at /tmp/flight_tracker_frontend.log"
    fi
    echo "----------------------------------------"
    
    print_status "Process status:"
    if kill -0 $frontend_pid 2>/dev/null; then
        echo "Frontend process (PID: $frontend_pid) is still running"
    else
        echo "Frontend process (PID: $frontend_pid) has terminated"
    fi
    
    print_status "Network diagnostics:"
    echo "Checking if port $FRONTEND_PORT is listening..."
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep ":$FRONTEND_PORT " || echo "Port $FRONTEND_PORT is not listening"
    elif command -v ss &> /dev/null; then
        ss -tlnp 2>/dev/null | grep ":$FRONTEND_PORT " || echo "Port $FRONTEND_PORT is not listening"
    else
        echo "Unable to check port status (netstat/ss not available)"
    fi
    
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
    local backend_running=false
    local backend_pid=""
    
    # First check if we have a valid PID file
    if [ -f "$PIDS_DIR/backend.pid" ] && ps -p $(cat "$PIDS_DIR/backend.pid") > /dev/null 2>&1; then
        backend_running=true
        backend_pid=$(cat "$PIDS_DIR/backend.pid")
    # If no PID file, check if backend is responding on the port
    elif curl -s --connect-timeout 3 http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
        backend_running=true
        backend_pid="unknown (not tracked by script)"
    fi
    
    if [ "$backend_running" = true ]; then
        print_success "✅ Backend: Running (PID: $backend_pid)"
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
    echo "  quick-debug Run a quick backend test and show immediate results"
    echo "  frontend-debug Run a quick frontend test and show immediate results"
    echo "  reset      Remove all installed dependencies and reset environment"
    echo "  swap       Help increase swap space for memory-constrained systems"
    echo "  minimal-frontend  Setup minimal frontend for low-memory systems"
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

# Function for quick debug test
quick_debug() {
    print_status "=== QUICK BACKEND DEBUG TEST ==="
    echo
    
    # Check if we're in the right directory
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found: $BACKEND_DIR"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check virtual environment
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run: $0 setup"
        return 1
    fi
    
    print_status "Testing backend startup directly..."
    source venv/bin/activate
    
    # Try to run the backend for 10 seconds and capture output
    timeout 10 python main.py --host $BACKEND_HOST --port $BACKEND_PORT 2>&1 | tee /tmp/quick_debug.log &
    local test_pid=$!
    
    sleep 3
    
    # Check if it's running
    if kill -0 $test_pid 2>/dev/null; then
        print_status "Backend process started, testing health endpoint..."
        
        # Test health endpoint
        local health_result=""
        if command -v curl &> /dev/null; then
            health_result=$(curl -s --connect-timeout 3 http://localhost:$BACKEND_PORT/health 2>&1)
        elif command -v wget &> /dev/null; then
            health_result=$(wget -q --timeout=3 --tries=1 -O - http://localhost:$BACKEND_PORT/health 2>&1)
        fi
        
        if [ -n "$health_result" ]; then
            print_success "✓ Backend is responding!"
            echo "Health response: $health_result"
        else
            print_warning "Backend started but not responding to health checks"
        fi
        
        # Kill the test process
        kill $test_pid 2>/dev/null
        wait $test_pid 2>/dev/null
    else
        print_error "Backend process failed to start"
    fi
    
    echo
    print_status "Backend output during test:"
    echo "----------------------------------------"
    cat /tmp/quick_debug.log 2>/dev/null || echo "No output captured"
    echo "----------------------------------------"
    
    # Clean up
    rm -f /tmp/quick_debug.log
}

# Function for quick frontend debug test
frontend_debug() {
    print_status "=== QUICK FRONTEND DEBUG TEST ==="
    echo
    
    # Check if we're in the right directory
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "Node modules not found. Run: $0 setup"
        return 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        return 1
    fi
    
    print_status "Testing frontend startup directly..."
    
    # Check package.json for dev script
    if [ -f "package.json" ]; then
        echo "Package.json dev script:"
        grep -A 2 -B 2 '"dev"' package.json || echo "No dev script found"
    fi
    
    # Try to run the frontend for 20 seconds and capture output
    timeout 20 npm run dev 2>&1 | tee /tmp/frontend_quick_debug.log &
    local test_pid=$!
    
    sleep 5
    
    # Check if it's running
    if kill -0 $test_pid 2>/dev/null; then
        print_status "Frontend process started, testing accessibility..."
        
        # Test frontend endpoint
        local frontend_result=""
        if command -v curl &> /dev/null; then
            frontend_result=$(curl -s --connect-timeout 5 http://localhost:$FRONTEND_PORT 2>&1)
        elif command -v wget &> /dev/null; then
            frontend_result=$(wget -q --timeout=5 --tries=1 -O - http://localhost:$FRONTEND_PORT 2>&1)
        fi
        
        if echo "$frontend_result" | grep -q -i "html\|<!doctype\|<title\|react"; then
            print_success "✓ Frontend is responding with HTML content!"
        elif [ -n "$frontend_result" ]; then
            print_warning "Frontend responding but content may be unexpected"
            echo "Response preview: ${frontend_result:0:200}..."
        else
            print_warning "Frontend started but not responding to HTTP requests"
        fi
        
        # Kill the test process
        kill $test_pid 2>/dev/null
        wait $test_pid 2>/dev/null
    else
        print_error "Frontend process failed to start"
    fi
    
    echo
    print_status "Frontend output during test:"
    echo "----------------------------------------"
    cat /tmp/frontend_quick_debug.log 2>/dev/null || echo "No output captured"
    echo "----------------------------------------"
    
    # Clean up
    rm -f /tmp/frontend_quick_debug.log
}

# Function to create a lightweight package.json for memory-constrained systems
create_lightweight_frontend() {
    local frontend_dir="$1"
    print_status "Creating lightweight frontend setup for Raspberry Pi..."
    
    cd "$frontend_dir"
    
    # Backup original package.json
    if [ -f "package.json" ]; then
        cp package.json package.json.full
    fi
    
    # Create minimal package.json for Raspberry Pi
    cat > package.json.minimal << 'EOF'
{
  "name": "frontend-minimal",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "python3 -m http.server 5173 --directory dist",
    "build": "echo 'Building with minimal setup...' && mkdir -p dist && cp -r public/* dist/ 2>/dev/null || true",
    "serve": "python3 -m http.server 5173 --directory dist"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
EOF
    
    print_status "Lightweight package.json created. Use 'mv package.json.minimal package.json' if needed."
}

# Function to setup minimal frontend only
setup_minimal_frontend() {
    print_status "Setting up minimal frontend for Raspberry Pi..."
    
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found: $FRONTEND_DIR"
        exit 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Create the lightweight package.json
    create_lightweight_frontend "$FRONTEND_DIR"
    
    # Use the minimal version
    if [ -f "package.json.minimal" ]; then
        mv package.json package.json.full 2>/dev/null || true
        mv package.json.minimal package.json
        print_success "Minimal frontend configuration created"
    fi
    
    # Try to install minimal dependencies
    export NODE_OPTIONS="--max-old-space-size=512"
    if npm install --no-optional; then
        print_success "Minimal frontend dependencies installed"
    else
        print_warning "Even minimal install failed, will use Python HTTP server only"
    fi
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

# Function to help increase swap space on Raspberry Pi
increase_swap() {
    print_status "Helping increase swap space for npm install..."
    
    if [ ! -f "/etc/dphys-swapfile" ]; then
        print_error "dphys-swapfile not found. Installing..."
        sudo apt update && sudo apt install -y dphys-swapfile
    fi
    
    print_status "Current swap configuration:"
    free -h
    
    print_status "To increase swap space, run these commands:"
    echo "  sudo dphys-swapfile swapoff"
    echo "  sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=1024/' /etc/dphys-swapfile"
    echo "  sudo dphys-swapfile setup"
    echo "  sudo dphys-swapfile swapon"
    echo ""
    echo "Then run: $0 setup"
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
    "quick-debug")
        quick_debug
        ;;
    "frontend-debug")
        frontend_debug
        ;;
    "reset")
        reset_environment
        ;;
    "swap")
        increase_swap
        ;;
    "minimal-frontend")
        setup_minimal_frontend
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

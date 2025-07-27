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
    
    # Start backend in background
    cd "$BACKEND_DIR"
    nohup python3 main.py --host $BACKEND_HOST --port $BACKEND_PORT > /tmp/flight_tracker_backend.log 2>&1 &
    echo $! > "$PIDS_DIR/backend.pid"
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            print_success "Backend started successfully on http://$BACKEND_HOST:$BACKEND_PORT"
            return 0
        fi
        sleep 1
        ((attempts++))
    done
    
    print_error "Backend failed to start after $max_attempts seconds"
    cat /tmp/flight_tracker_backend.log
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
    echo "  start      Start backend and frontend services"
    echo "  stop       Stop all running services"
    echo "  restart    Restart all services"
    echo "  status     Show status of all services"
    echo "  test       Test the raspi client"
    echo "  logs       Show recent logs"
    echo "  help       Show this help message"
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

# Main script logic
case "${1:-start}" in
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
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

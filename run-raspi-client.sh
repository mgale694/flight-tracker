#!/bin/bash

# Flight Tracker Raspi Client Runner
# For running the raspi client against a remote backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Default backend URL
BACKEND_URL="http://localhost:8000"
RASPI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/src/raspi" && pwd)"

# Function to show help
show_help() {
    echo "Flight Tracker Raspi Client Runner"
    echo
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo
    echo "Commands:"
    echo "  test       Test connection to backend (default)"
    echo "  poll       Start continuous polling mode"
    echo "  config     Show backend configuration"
    echo "  health     Check backend health"
    echo "  help       Show this help message"
    echo
    echo "Options:"
    echo "  -u, --url URL    Backend URL (default: $BACKEND_URL)"
    echo "  -i, --interval N Polling interval in seconds (default: 3)"
    echo
    echo "Examples:"
    echo "  $0 test"
    echo "  $0 -u http://192.168.0.102:8000 test"
    echo "  $0 -u http://192.168.0.102:8000 poll"
    echo "  $0 --url http://192.168.0.102:8000 --interval 5 poll"
}

# Function to test backend connection
test_backend() {
    print_status "Testing connection to backend: $BACKEND_URL"
    
    cd "$RASPI_DIR"
    
    # Create a temporary test script
    cat > /tmp/raspi_test.py << EOF
import sys
sys.path.append("$RASPI_DIR")
from api_simple import SimpleFlightTrackerAPI

api = SimpleFlightTrackerAPI("$BACKEND_URL")

try:
    # Test health
    health = api.health_check()
    print(f"✅ Health check: {health['status']}")
    
    # Test config
    config = api.get_config()
    print(f"✅ Config: {config['main']['address']}")
    
    # Test flights
    flights = api.get_flights()
    print(f"✅ Flights: {len(flights.get('flights', []))} flights at {flights.get('location', 'unknown')}")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
EOF
    
    python3 /tmp/raspi_test.py
    rm /tmp/raspi_test.py
}

# Function to start continuous polling
start_polling() {
    local interval=${1:-3}
    
    print_status "Starting continuous polling mode (interval: ${interval}s)"
    print_status "Backend: $BACKEND_URL"
    print_status "Press Ctrl+C to stop"
    echo
    
    cd "$RASPI_DIR"
    
    # Create a polling script
    cat > /tmp/raspi_poll.py << EOF
import sys
import time
import signal
sys.path.append("$RASPI_DIR")
from api_simple import SimpleFlightTrackerAPI

api = SimpleFlightTrackerAPI("$BACKEND_URL")
running = True

def signal_handler(sig, frame):
    global running
    print("\n\n🛑 Stopping polling...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

print("🚀 Starting flight polling...")
print(f"Backend: $BACKEND_URL")
print(f"Interval: ${interval}s")
print("Press Ctrl+C to stop\n")

poll_count = 0

while running:
    try:
        poll_count += 1
        flights = api.get_flights()
        flight_list = flights.get('flights', [])
        location = flights.get('location', 'unknown')
        timestamp = flights.get('timestamp', 0)
        
        print(f"[{poll_count:04d}] {len(flight_list)} flights at {location} (ts: {timestamp:.0f})")
        
        if flight_list:
            for i, flight in enumerate(flight_list[:3]):  # Show first 3 flights
                callsign = flight.get('callsign', 'N/A')
                altitude = flight.get('altitude', 'N/A')
                speed = flight.get('speed', 'N/A')
                print(f"  └─ {callsign}: {altitude}ft, {speed}kts")
        
        time.sleep($interval)
        
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(f"❌ Polling error: {e}")
        time.sleep($interval)

print("\n✅ Polling stopped")
EOF
    
    python3 /tmp/raspi_poll.py
    rm /tmp/raspi_poll.py
}

# Function to show config
show_config() {
    print_status "Fetching backend configuration..."
    
    cd "$RASPI_DIR"
    
    cat > /tmp/raspi_config.py << EOF
import sys
import json
sys.path.append("$RASPI_DIR")
from api_simple import SimpleFlightTrackerAPI

api = SimpleFlightTrackerAPI("$BACKEND_URL")

try:
    config = api.get_config()
    print(json.dumps(config, indent=2))
except Exception as e:
    print(f"❌ Error fetching config: {e}")
    sys.exit(1)
EOF
    
    python3 /tmp/raspi_config.py
    rm /tmp/raspi_config.py
}

# Function to check health
check_health() {
    print_status "Checking backend health..."
    
    cd "$RASPI_DIR"
    
    cat > /tmp/raspi_health.py << EOF
import sys
import json
sys.path.append("$RASPI_DIR")
from api_simple import SimpleFlightTrackerAPI

api = SimpleFlightTrackerAPI("$BACKEND_URL")

try:
    health = api.health_check()
    print(json.dumps(health, indent=2))
    
    if health.get('status') == 'healthy':
        print("\n✅ Backend is healthy")
    else:
        print("\n⚠️ Backend health check failed")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Health check failed: {e}")
    sys.exit(1)
EOF
    
    python3 /tmp/raspi_health.py
    rm /tmp/raspi_health.py
}

# Parse command line arguments
COMMAND="test"
INTERVAL=3

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            BACKEND_URL="$2"
            shift 2
            ;;
        -i|--interval)
            INTERVAL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        test|poll|config|health|help)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check if raspi directory exists
if [ ! -d "$RASPI_DIR" ]; then
    print_error "Raspi directory not found: $RASPI_DIR"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed or not in PATH"
    exit 1
fi

# Execute the requested command
case "$COMMAND" in
    "test")
        test_backend
        ;;
    "poll")
        start_polling "$INTERVAL"
        ;;
    "config")
        show_config
        ;;
    "health")
        check_health
        ;;
    "help")
        show_help
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

# Flight Tracker Startup Scripts

This directory contains shell scripts to easily start and manage the Flight Tracker system components.

## 🚀 Quick Start

### Start All Services (Main Script)

```bash
# Start backend and frontend with network access
./start-flight-tracker.sh start

# Check status
./start-flight-tracker.sh status

# Stop all services
./start-flight-tracker.sh stop
```

### Run Raspi Client (Remote Machine)

```bash
# Test connection to local backend
./run-raspi-client.sh test

# Connect to remote backend
./run-raspi-client.sh -u http://192.168.0.102:8000 test

# Start continuous polling
./run-raspi-client.sh -u http://192.168.0.102:8000 poll
```

## 📋 Scripts Overview

### `start-flight-tracker.sh`

**Main startup script for the complete system**

**Commands:**

- `start` - Start backend and frontend services
- `stop` - Stop all running services
- `restart` - Restart all services
- `status` - Show status of all services
- `test` - Test the raspi client
- `logs` - Show recent logs
- `help` - Show help message

**Features:**

- ✅ Starts backend with network access (`0.0.0.0`)
- ✅ Starts frontend with network access (`0.0.0.0`)
- ✅ Automatic port conflict detection and resolution
- ✅ Health checks for all services
- ✅ Shows network URLs for external access
- ✅ PID file management for clean shutdowns
- ✅ Colored output and status reporting

**Environment Variables:**

```bash
export BACKEND_PORT=8000      # Backend port
export FRONTEND_PORT=5173     # Frontend port
export BACKEND_HOST=0.0.0.0   # Backend host
export FRONTEND_HOST=0.0.0.0  # Frontend host
```

### `run-raspi-client.sh`

**Dedicated script for running raspi clients**

**Commands:**

- `test` - Test connection to backend (default)
- `poll` - Start continuous polling mode
- `config` - Show backend configuration
- `health` - Check backend health
- `help` - Show help message

**Options:**

- `-u, --url URL` - Backend URL (default: http://localhost:8000)
- `-i, --interval N` - Polling interval in seconds (default: 3)

**Features:**

- ✅ Connection testing and validation
- ✅ Continuous polling with real-time output
- ✅ Configuration and health checking
- ✅ Graceful shutdown with Ctrl+C
- ✅ Error handling and retry logic

## 🌐 Network Access

Both scripts configure services for network access by default:

**Default URLs:**

- Backend: `http://0.0.0.0:8000`
- Frontend: `http://0.0.0.0:5173`

**External Access:**
When you run `./start-flight-tracker.sh start`, it will show your network IP:

```
Network URLs (accessible from other machines):
   Backend:  http://192.168.0.102:8000
   Frontend: http://192.168.0.102:5173
```

## 🔧 Usage Examples

### Start the complete system

```bash
./start-flight-tracker.sh start
```

### Check if everything is running

```bash
./start-flight-tracker.sh status
```

### Test raspi client against local backend

```bash
./run-raspi-client.sh test
```

### Connect raspi client to remote backend

```bash
./run-raspi-client.sh -u http://192.168.0.102:8000 test
```

### Start continuous polling from raspi

```bash
./run-raspi-client.sh -u http://192.168.0.102:8000 --interval 5 poll
```

### View recent logs

```bash
./start-flight-tracker.sh logs
```

### Stop everything

```bash
./start-flight-tracker.sh stop
```

## 📁 File Locations

**Log Files:**

- Backend: `/tmp/flight_tracker_backend.log`
- Frontend: `/tmp/flight_tracker_frontend.log`
- Raspi Test: `/tmp/flight_tracker_raspi_test.log`

**PID Files:**

- Backend: `/tmp/flight_tracker_pids/backend.pid`
- Frontend: `/tmp/flight_tracker_pids/frontend.pid`

## 🛠️ Troubleshooting

### Port conflicts

```bash
# Check what's using a port
lsof -i :8000

# Kill process on port
sudo kill $(lsof -t -i:8000)
```

### Service won't start

```bash
# Check logs
./start-flight-tracker.sh logs

# Try manual start
cd src/backend && python3 main.py --host 0.0.0.0 --port 8000
cd src/frontend/react && npm run dev -- --host 0.0.0.0 --port 5173
```

### Raspi client can't connect

```bash
# Test network connectivity
curl http://192.168.0.102:8000/health

# Check firewall settings
# Ensure ports 8000 and 5173 are open
```

## 🔒 Security Notes

- Services bind to `0.0.0.0` for network access
- Ensure your firewall allows connections on ports 8000 and 5173
- Consider using a reverse proxy (nginx) for production deployments
- No authentication is currently implemented - add if needed for production

## 🚀 Production Deployment

For production use, consider:

1. **Reverse Proxy**: Use nginx to proxy requests
2. **SSL/TLS**: Add HTTPS support
3. **Environment Variables**: Use proper environment configuration
4. **Process Management**: Use systemd or supervisor
5. **Monitoring**: Add health checks and alerting

## 📱 Mobile Access

The frontend is accessible from mobile devices when using network hosting:

- Visit `http://YOUR_IP:5173` from any device on the same network
- The React app is responsive and works on mobile browsers

---

**Created:** July 27, 2025
**Compatible with:** macOS, Linux
**Requirements:** Python 3.x, Node.js/npm, curl

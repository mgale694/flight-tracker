# 🚀 Quick Start Guide - Flight Tracker

Get your Flight Tracker system up and running in minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- `uvve` virtual environment manager (custom)
- `uv` package manager
- Internet connection (for FlightRadar24 API)

**Note:** Make sure you have a `flight-tracker` virtual environment set up with uvve before running the scripts.

## Option 1: Start Everything (Recommended)

Use the all-in-one startup script:

```bash
./scripts/start-flight-tracker.sh
```

This will:

1. ✅ Check prerequisites
2. ✅ Activate uvve virtual environment (flight-tracker)
3. ✅ Install backend dependencies with `uv pip`
4. ✅ Start backend API on port 8000
5. ✅ Install frontend dependencies
6. ✅ Start frontend on port 5173
7. ✅ Display all URLs and process info

**Press Ctrl+C to stop all services**

## Option 2: Start Services Separately

### Start Backend Only

```bash
./scripts/start-backend.sh
```

Access at: http://localhost:8000  
API Docs: http://localhost:8000/docs

### Start Frontend Only

```bash
./scripts/start-frontend.sh
```

Access at: http://localhost:5173

## First Time Setup

### 1. Configure Your Location

Edit `src/backend/config.toml`:

```toml
[main]
address = "Your City, Country"  # Change this!
search_radius_meters = 3000
max_flights = 20
```

Or update via the web UI Settings page after starting.

### 2. Verify Installation

**Backend Health Check:**

```bash
curl http://localhost:8000/api/health
```

**Frontend:**
Open http://localhost:5173 in your browser

## Usage

### Web Dashboard

1. Open http://localhost:5173
2. View the **Tracker** page for:
   - E-ink display simulator
   - Flight board with live data
   - Configuration settings
3. Check **Activities** page for system logs

### API Access

**Get Flights:**

```bash
curl http://localhost:8000/api/flights
```

**Update Config:**

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"address": "New York, NY", "search_radius_meters": 5000}'
```

**View Activities:**

```bash
curl http://localhost:8000/api/activities
```

## Troubleshooting

### Port Already in Use

**Backend (8000):**

```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (5173):**

```bash
lsof -ti:5173 | xargs kill -9
```

### No Flights Detected

1. Check your location is correct in Settings
2. Increase search radius (try 5000-10000 meters)
3. Verify FlightRadar24 API is accessible
4. Check Activity Logs for errors

### Backend Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check logs
tail -f /tmp/flight-tracker-backend.log
```

### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 18+

# Check logs
tail -f /tmp/flight-tracker-frontend.log

# Reinstall dependencies
cd src/frontend
rm -rf node_modules
npm install
```

## Network Access

To access from other devices on your network:

**Backend:**

```
http://<your-ip>:8000
```

**Frontend:**

```
http://<your-ip>:5173
```

Find your IP:

```bash
# macOS/Linux
ifconfig | grep "inet "

# Or
ipconfig getifaddr en0
```

## Stopping Services

**If using start-flight-tracker.sh:**

- Press `Ctrl+C` in the terminal

**If started separately:**

```bash
# Kill backend
pkill -f "python main.py"

# Kill frontend
pkill -f "vite"
```

## Next Steps

1. ✅ Start the system
2. ✅ Configure your location
3. ✅ Watch for flights on the dashboard
4. ✅ Monitor activity logs
5. 🎯 Deploy to Raspberry Pi (Phase 3)

## Development

**Backend changes:** Auto-reload enabled with `--reload` flag

**Frontend changes:** Hot Module Replacement (HMR) enabled by Vite

## Production Deployment

**Backend:**

```bash
cd src/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd src/frontend
npm run build
# Serve dist/ folder with any static server
```

## Support

- Backend docs: `src/backend/README.md`
- Frontend docs: `src/frontend/README.md`
- Architecture: `src/backend/ARCHITECTURE.md`
- Project plan: `docs/PLAN.md`

---

**Enjoy tracking flights! ✈️**

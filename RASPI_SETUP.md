# Flight Tracker - Raspberry Pi Complete Setup

Run the complete Flight Tracker system on your Raspberry Pi with backend API, web frontend, and e-ink display!

## Quick Start

### On Your Raspberry Pi

1. **Clone the repository:**

   ```bash
   cd ~
   git clone https://github.com/yourusername/flight-tracker.git
   cd flight-tracker
   ```

2. **Run the all-in-one startup script:**

   ```bash
   ./scripts/start-raspi-all.sh
   ```

3. **Access from your laptop:**
   - Frontend: `http://<raspberry-pi-ip>:5173`
   - Backend API: `http://<raspberry-pi-ip>:8000`
   - Settings: `http://<raspberry-pi-ip>:5173/settings`

The script will show you the exact URL when it starts!

## What Gets Started

The `start-raspi-all.sh` script launches:

1. **Backend API** (port 8000) - Flight tracking and configuration
2. **Frontend Web Server** (port 5173) - Dashboard and settings interface
3. **E-ink Display Client** - Shows flights on the hardware display

All three components run on the Raspberry Pi and are accessible from any device on your network!

## Configuration

### First Time Setup

When you first run the system:

1. Open `http://<raspberry-pi-ip>:5173/settings` in your browser
2. Enter your location (address, postcode, etc.)
3. Adjust search radius and other settings
4. Click "Save Configuration"
5. Flights will appear on both the web dashboard and e-ink display!

### Files to Configure

- **Backend**: `src/backend/config.toml` - Main configuration
- **Raspi Client**: `src/raspi/config.toml` - Display settings (auto-configured by script)
- **Frontend**: Uses backend config via API

## Auto-Start on Boot (Optional)

To make the Flight Tracker start automatically when your Pi boots:

### Option 1: Systemd Service (Recommended)

```bash
# Copy service file
sudo cp scripts/flight-tracker.service /etc/systemd/system/

# Edit the service file to match your paths
sudo nano /etc/systemd/system/flight-tracker.service
# Update User and WorkingDirectory if needed

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable flight-tracker
sudo systemctl start flight-tracker

# Check status
sudo systemctl status flight-tracker

# View logs
sudo journalctl -u flight-tracker -f
```

### Option 2: rc.local

Add to `/etc/rc.local` (before `exit 0`):

```bash
su - pi -c "/home/pi/flight-tracker/scripts/start-raspi-all.sh" &
```

### Option 3: Crontab

```bash
crontab -e
# Add this line:
@reboot /home/pi/flight-tracker/scripts/start-raspi-all.sh
```

## Hardware Setup

See `src/raspi/README.md` for detailed hardware connection instructions for the Waveshare e-ink display.

### Quick Hardware Checklist

- [ ] Waveshare 2.13" V4 display connected to GPIO pins
- [ ] SPI enabled: `sudo raspi-config` → Interface Options → SPI → Enable
- [ ] Fonts installed: Copy a .ttf file to `src/raspi/ui/hw/libs/fonts/Font.ttc`
- [ ] Waveshare library: Download files to `src/raspi/ui/hw/libs/waveshare/`

## Network Access

### From Your Laptop

Once the Pi is running, access from any device on the same WiFi:

```
http://192.168.1.XX:5173        # Frontend (replace XX with your Pi's IP)
http://192.168.1.XX:5173/settings  # Settings page
http://192.168.1.XX:8000        # Backend API
http://192.168.1.XX:8000/docs   # API Documentation
```

To find your Pi's IP:

```bash
hostname -I
```

### Port Forwarding (Optional)

To access from outside your home network, set up port forwarding on your router:

- Forward external port → Pi IP:5173 (Frontend)
- Forward external port → Pi IP:8000 (Backend)

⚠️ **Security Note**: Consider setting up authentication if exposing to the internet!

## Troubleshooting

### Can't Access from Laptop

1. **Check Pi is on the same network:**

   ```bash
   # On Pi
   hostname -I
   # On laptop, try to ping it
   ping <pi-ip-address>
   ```

2. **Check firewall:**

   ```bash
   # On Pi, allow ports
   sudo ufw allow 8000
   sudo ufw allow 5173
   ```

3. **Check services are running:**
   ```bash
   # On Pi
   curl http://localhost:8000/api/health
   curl http://localhost:5173
   ```

### Display Not Working

The script will continue even if the display hardware isn't available. Check:

- SPI is enabled
- Waveshare library files are installed
- GPIO permissions: `sudo usermod -a -G spi,gpio pi`
- Run with sudo: `sudo ./scripts/start-raspi-all.sh`

### Backend/Frontend Issues

Check logs:

```bash
tail -f /tmp/flight-tracker-backend.log
tail -f /tmp/flight-tracker-frontend.log
tail -f /tmp/flight-tracker-raspi.log
```

### Stopping the Services

Press `Ctrl+C` in the terminal where you ran the script, or:

```bash
# Find and kill processes
pkill -f "python.*main.py"
pkill -f "python3.*agent.py"
pkill -f "npx serve"
```

## Architecture

```
Raspberry Pi
├── Backend API (port 8000)
│   ├── Fetches flights from FlightRadar24
│   ├── Manages configuration
│   └── Serves API endpoints
├── Frontend Web Server (port 5173)
│   ├── Dashboard view
│   ├── Settings interface
│   └── Activities log
└── E-ink Display Client
    ├── Connects to Backend API
    ├── Renders to e-ink display
    └── Shows boot screen & flights
```

All components communicate via the Backend API running on localhost.

## Advanced Configuration

### Change Ports

Edit `scripts/start-raspi-all.sh` to use different ports:

```bash
# Frontend port (default 5173)
npx serve -s dist -l 3000  # Change to port 3000

# Backend port (default 8000)
# Edit src/backend/main.py: uvicorn.run(app, host="0.0.0.0", port=9000)
```

### Use External Backend

If you want to run the backend elsewhere:

1. Edit `src/raspi/config.toml`:

   ```toml
   [main]
   api_url = "http://your-server:8000"
   ```

2. Skip backend startup in the script

### Development Mode

For development with hot-reload:

```bash
# Terminal 1 - Backend
cd src/backend
source venv/bin/activate
python main.py

# Terminal 2 - Frontend (dev mode)
cd src/frontend
npm run dev

# Terminal 3 - Display
cd src/raspi
python3 agent.py
```

## Requirements

- Raspberry Pi (any model with GPIO)
- Python 3.8+
- Node.js 18+
- Internet connection
- Waveshare 2.13" V4 e-ink display (optional)

## License

MIT License - See LICENSE file

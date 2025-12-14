# Flight Tracker - Raspberry Pi Complete Setup

Run the complete Flight Tracker system on your Raspberry Pi with backend API, web frontend, and e-ink display!

## Quick Start

### On Your Raspberry Pi

1. **Clone the repository:**

   ```bash
   cd ~
   git clone https://github.com/mgale694/flight-tracker.git
   cd flight-tracker
   ```

2. **Install Waveshare display libraries (first time only):**

   ```bash
   ./scripts/install-waveshare.sh
   sudo raspi-config  # Enable SPI: Interface Options → SPI → Enable
   sudo reboot
   ```

3. **Run the all-in-one startup script:**

   ```bash
   cd ~/flight-tracker
   ./scripts/start-raspi-all.sh
   ```

4. **Access from your laptop:**
   - Frontend: `http://<raspberry-pi-ip>:5173`
   - Backend API: `http://<raspberry-pi-ip>:8000`
   - Settings: `http://<raspberry-pi-ip>:5173/settings`

The script will show you the exact URL when it starts!

> **Note:** If you see "Display not initialized" warnings, that's normal before installing the Waveshare libraries. The backend and frontend will still work perfectly!

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

### Installing Display Libraries

**Option 1: Automated Install (Recommended)**

```bash
cd ~/flight-tracker
./scripts/install-waveshare.sh
```

This script will:
- Install system dependencies (RPi.GPIO, spidev, PIL)
- Download and install Waveshare EPD library
- Set up the correct file structure

**Option 2: Manual Install**

```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio python3-spidev python3-pil git

# Clone Waveshare library
cd ~/flight-tracker/src/raspi/ui/hw/libs
git clone --depth 1 https://github.com/waveshare/e-Paper.git waveshare-examples

# Copy required files
mkdir -p waveshare
cp waveshare-examples/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd2in13_V4.py waveshare/
cp waveshare-examples/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py waveshare/
touch waveshare/__init__.py

# Clean up
rm -rf waveshare-examples
```

**Enable SPI Interface:**

```bash
sudo raspi-config
# Navigate: Interface Options → SPI → Enable
sudo reboot
```

### Quick Hardware Checklist

- [ ] Waveshare 2.13" V4 display connected to GPIO pins (see wiring below)
- [ ] SPI enabled via `raspi-config`
- [ ] Waveshare library installed via `install-waveshare.sh`
- [ ] System rebooted after SPI enablement

### Display Wiring (Waveshare 2.13" V4)

| Display Pin | Raspberry Pi Pin | GPIO |
|-------------|------------------|------|
| VCC         | Pin 1            | 3.3V |
| GND         | Pin 6            | GND  |
| DIN         | Pin 19           | GPIO 10 (MOSI) |
| CLK         | Pin 23           | GPIO 11 (SCLK) |
| CS          | Pin 24           | GPIO 8 (CE0)   |
| DC          | Pin 22           | GPIO 25 |
| RST         | Pin 11           | GPIO 17 |
| BUSY        | Pin 18           | GPIO 24 |

See `src/raspi/README.md` for detailed hardware connection instructions.

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

### Display Shows "Display not initialized" Warning

This is **normal** before installing the Waveshare libraries! The backend and frontend will still work perfectly.

**To fix:**

1. **Install the libraries:**
   ```bash
   ./scripts/install-waveshare.sh
   ```

2. **Enable SPI:**
   ```bash
   sudo raspi-config
   # Navigate: Interface Options → SPI → Enable
   ```

3. **Reboot:**
   ```bash
   sudo reboot
   ```

4. **Run again:**
   ```bash
   ./scripts/start-raspi-all.sh
   ```

**Still not working? Check:**

- [ ] SPI is enabled: `lsmod | grep spi`
- [ ] Waveshare files exist: `ls src/raspi/ui/hw/libs/waveshare/epd2in13_V4.py`
- [ ] GPIO permissions: `sudo usermod -a -G spi,gpio pi` (then logout/login)
- [ ] Display is connected correctly (check wiring table above)
- [ ] Try with sudo: `sudo ./scripts/start-raspi-all.sh`

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

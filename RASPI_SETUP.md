# Flight Tracker - Raspberry Pi Setup

Run the complete Flight Tracker system on your Raspberry Pi with backend API, web frontend, and e-ink display!

## Prerequisites

- Raspberry Pi (any model with GPIO)
- Waveshare 2.13" V4 e-ink display (optional)
- Internet connection
- MicroSD card with Raspberry Pi OS

## Quick Start

```bash
# 1. Clone the repository
cd ~
git clone https://github.com/mgale694/flight-tracker.git
cd flight-tracker

# 2. Install GPIO system packages (for e-ink display)
sudo ./scripts/install-gpio-packages.sh

# 3. Enable SPI interface
sudo raspi-config
# Navigate: Interface Options → SPI → Enable → Reboot

# 4. Run everything!
./scripts/start-raspi-all.sh
```

Access from your laptop: The script will show you the URLs (e.g., `http://192.168.0.220:5173`)

## First Time Configuration

1. Open `http://<pi-ip>:5173/settings` in your browser
2. Enter your home address or postcode
3. Set search radius (5000-15000m recommended)
4. Save - flights will appear within seconds!

## What Gets Started

The `start-raspi-all.sh` script launches:

1. **Backend API** (port 8000) - Flight tracking and configuration
2. **Frontend Web Server** (port 5173) - Dashboard and settings interface
3. **E-ink Display Client** - Shows flights on the hardware display

All three components run on the Raspberry Pi and are accessible from any device on your network!

## What Gets Started

The `start-raspi-all.sh` script launches:

1. **Backend API** (port 8000) - Flight tracking and configuration
2. **Frontend Web Server** (port 5173) - Dashboard and settings interface
3. **E-ink Display Client** - Shows flights on the hardware display

All three components run on the Raspberry Pi and are accessible from any device on your network!

## Auto-Start on Boot

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

| Display Pin | Raspberry Pi Pin | GPIO           |
| ----------- | ---------------- | -------------- |
| VCC         | Pin 1            | 3.3V           |
| GND         | Pin 6            | GND            |
| DIN         | Pin 19           | GPIO 10 (MOSI) |
| CLK         | Pin 23           | GPIO 11 (SCLK) |
| CS          | Pin 24           | GPIO 8 (CE0)   |
| DC          | Pin 22           | GPIO 25        |
| RST         | Pin 11           | GPIO 17        |
| BUSY        | Pin 18           | GPIO 24        |

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

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for complete diagnostic guides.

### Quick Checks

**Can't access from laptop?**

- Check Pi's IP: `hostname -I`
- Ping from laptop: `ping <pi-ip>`
- Check services: `curl http://localhost:8000/api/health`

**Display not working?**

```bash
# Run diagnostic
./scripts/diagnose-display.sh

# If it shows missing packages:
sudo ./scripts/install-gpio-packages.sh
```

**View logs:**

```bash
tail -f /tmp/flight-tracker-raspi.log
tail -f /tmp/flight-tracker-backend.log
```

**Stop services:**

```bash
# Press Ctrl+C in terminal, or:
pkill -f "python.*main.py"
pkill -f "npx serve"
```

## What's Next?

- Configure your location in Settings
- Set up auto-start on boot (see Auto-Start section above)
- Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) if you have issues
- See main [README.md](README.md) for architecture details

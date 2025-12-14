# Flight Tracker - Raspberry Pi E-ink Display Client

This client displays real-time flight information on a Waveshare 2.13" V4 e-ink display connected to a Raspberry Pi.

## Features

- **Dual Mode Operation**:
  - **API Mode** (recommended): Connects to the backend API server
  - **Standalone Mode**: Uses FlightRadar24 API directly
- **E-ink Display**: Shows flight info on Waveshare 2.13" V4 (250x122 pixels)
- **Boot Sequence**: Fun ASCII art faces and phrases on startup
- **Startup Status**: Shows progress during system startup
- **Session Statistics**: Tracks flights detected and unique aircraft
- **Auto-rotation**: Cycles through multiple flights automatically
- **Remote Control**: Clear display and shutdown from web interface

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- Waveshare 2.13" V4 e-ink display (black and white)
- MicroSD card with Raspberry Pi OS
- Power supply for Raspberry Pi

## Software Requirements

### System Packages

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pil python3-numpy
sudo apt-get install -y python3-rpi.gpio python3-spidev
```

### Enable SPI Interface

```bash
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable
# Reboot after enabling
sudo reboot
```

### Python Dependencies

```bash
cd /path/to/flight-tracker/src/raspi
pip3 install -r requirements.txt
```

## Setup

### 1. Hardware Connection

Connect the Waveshare 2.13" V4 display to your Raspberry Pi:

| Display Pin | RPi Pin | Function     |
| ----------- | ------- | ------------ |
| VCC         | 3.3V    | Power        |
| GND         | GND     | Ground       |
| DIN         | GPIO 10 | SPI MOSI     |
| CLK         | GPIO 11 | SPI CLK      |
| CS          | GPIO 8  | SPI CE0      |
| DC          | GPIO 25 | Data/Command |
| RST         | GPIO 17 | Reset        |
| BUSY        | GPIO 24 | Busy         |

### 2. Install Waveshare Library

```bash
cd src/raspi/ui/hw/libs/waveshare
wget https://github.com/waveshare/e-Paper/raw/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd2in13_V4.py
wget https://github.com/waveshare/e-Paper/raw/master/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py
```

### 3. Install Font

```bash
cd src/raspi/ui/hw/libs/fonts
# Copy a system font or download one
cp /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf Font.ttc
```

### 4. Configure

Edit `config.toml`:

```toml
[main]
# API Mode (recommended)
api_url = "http://your-backend-server:8000"
use_backend_api = true

# OR Standalone Mode
# use_backend_api = false
# address = "Your Location"
# search_radius_meters = 3000

[ui]
boot_screen_duration = 10
flight_rotation_interval = 5
```

## Usage

### Run Manually

```bash
cd /path/to/flight-tracker/src/raspi
python3 agent.py
```

### Run as Service

Create `/etc/systemd/system/flight-tracker.service`:

```ini
[Unit]
Description=Flight Tracker E-ink Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/flight-tracker/src/raspi
ExecStart=/usr/bin/python3 /home/pi/flight-tracker/src/raspi/agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flight-tracker
sudo systemctl start flight-tracker
```

Check status:

```bash
sudo systemctl status flight-tracker
```

## Troubleshooting

### Display Not Working

1. **Check SPI is enabled**:

   ```bash
   ls /dev/spi*
   # Should see: /dev/spidev0.0 /dev/spidev0.1
   ```

2. **Check permissions**:

   ```bash
   sudo usermod -a -G spi,gpio pi
   # Logout and login again
   ```

3. **Run with sudo** (for testing):
   ```bash
   sudo python3 agent.py
   ```

### Cannot Connect to Backend

1. **Check backend is running**:

   ```bash
   curl http://your-backend:8000/api/health
   ```

2. **Check firewall**:

   ```bash
   # On backend server, allow port 8000
   sudo ufw allow 8000
   ```

3. **Use standalone mode** as fallback:
   ```toml
   [main]
   use_backend_api = false
   address = "London, UK"
   search_radius_meters = 5000
   ```

### Font Errors

If you see font errors, the code will fallback to system fonts automatically. To fix:

```bash
cd src/raspi/ui/hw/libs/fonts
cp /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf Font.ttc
```

## Display Layout

The display shows:

```
ATC: [callsign]  COUNT: [#]  TIMER: [time]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FROM: [origin airport]
AIRLINE: [airline name]
MODEL: [aircraft type]
REG: [registration]
[ORIGIN] -> [DESTINATION]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALT: [altitude] ft  SPD: [speed] kts  TIME: [time]
```

## Development Without Hardware

You can develop and test without a Raspberry Pi:

1. The code will detect missing hardware and continue
2. Check logs to see what would be displayed:

   ```bash
   tail -f flight_tracker.log
   ```

3. Use the web frontend for visualization

## Architecture

```
agent.py          # Main agent loop
├── tracker.py    # Flight tracking (API or standalone)
├── log.py        # Session statistics
├── faces.py      # Boot screen faces
├── utils.py      # Utility functions
└── ui/
    ├── display.py   # Display controller
    ├── view.py      # Screen rendering
    ├── fonts.py     # Font management
    └── hw/
        ├── base.py              # Base display class
        ├── waveshare213in_v4.py # Hardware driver
        └── libs/
            ├── waveshare/  # EPD library
            └── fonts/      # Font files
```

## License

MIT License - See LICENSE file

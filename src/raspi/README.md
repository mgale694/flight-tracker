# Raspberry Pi - Hardware Flight Tracker

Physical flight tracking implementation designed to run on Raspberry Pi with e-ink displays. This is the original hardware-focused version of the Flight Tracker system.

## 🚀 Features

- **Real-time Flight Tracking**: Direct FlightRadar24 API integration
- **E-ink Display Support**: Multiple display types and sizes supported
- **Voice Feedback**: Audio notifications for flight events (optional)
- **Boot Sequence**: Animated startup process with status updates
- **Hardware Integration**: GPIO control and hardware-specific optimizations
- **Standalone Operation**: Can run independently without backend service
- **Low Power**: Optimized for continuous operation on Raspberry Pi

## 🔧 Hardware Requirements

### Minimum Requirements

- **Raspberry Pi 3B+** or newer
- **MicroSD Card**: 16GB+ Class 10
- **Power Supply**: 5V 3A USB-C (Pi 4) or Micro-USB (Pi 3)
- **Internet Connection**: WiFi or Ethernet

### Supported E-ink Displays

- **Waveshare 2.13" V4**: 250x122 pixels (recommended)
- **Waveshare 1.54"**: 200x200 pixels
- **Inky pHAT**: 212x104 pixels
- **PimoroniInky**: Various sizes
- **Adafruit displays**: Multiple models
- **Custom displays**: Configurable drivers

### Optional Hardware

- **Speakers/Buzzer**: For voice feedback
- **LED indicators**: Status lights
- **Buttons**: Manual control inputs
- **RTC Module**: For accurate timekeeping

## 📁 Directory Structure

```
raspi/
├── tracker.py           # Main application entry point
├── config.toml          # Hardware configuration
├── agent.py             # Flight tracking agent
├── faces.py             # Boot screen ASCII art
├── log.py               # Logging utilities
├── voice.py             # Voice feedback system
├── utils.py             # Utility functions
├── ui/                  # Display interface
│   ├── display.py       # Main display controller
│   ├── fonts.py         # Font management
│   ├── view.py          # Display rendering
│   └── hw/              # Hardware drivers
│       ├── base.py      # Base display driver
│       ├── waveshare*.py # Waveshare drivers
│       ├── inky.py      # Inky display drivers
│       └── ...          # Additional hardware drivers
└── __pycache__/         # Python cache files
```

## 🛠️ Installation & Setup

### 1. Prepare Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install python3-pip python3-venv git -y

# Enable SPI for e-ink displays
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable
```

### 2. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd flight-tracker/src/raspi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Hardware

Edit `config.toml` for your hardware setup:

```toml
[main]
address = "Your Location Address"
search_radius_meters = 10000
max_flights = 20
max_elapsed_time = 1800

[ui]
boot_screen_duration = 10
scan_update_interval = 2
flight_display_duration = 5

[ui.display]
enabled = true
type = "waveshare213in_v4"  # Your display type
rotation = 0
color = "black"

[ui.font]
name = "DejaVuSansMono"
size_offset = 0

[logging]
level = "INFO"
path = "/tmp/flight_tracker.log"
```

### 4. Run Flight Tracker

```bash
# Start tracking
python tracker.py

# Run with debug output
python tracker.py --debug

# Run in background
nohup python tracker.py &
```

## 🖥️ Display System

### Display Types Configuration

The system automatically detects and configures supported displays:

```python
# In config.toml
[ui.display]
type = "waveshare213in_v4"    # Display driver name
rotation = 0                   # 0, 90, 180, 270 degrees
color = "black"               # "black", "red", "yellow"
```

### Supported Display Types

- `waveshare213in_v4` - Waveshare 2.13" V4 (250x122)
- `waveshare154inch` - Waveshare 1.54" (200x200)
- `inky` - Pimoroni Inky pHAT
- `oledhat` - OLED displays
- `lcdhat` - LCD displays

### Custom Display Drivers

To add new display support:

1. Create driver in `ui/hw/your_display.py`
2. Inherit from `BaseDisplay` class
3. Implement required methods
4. Add to display registry

## 🎨 Display Modes

### Boot Screen

- **ASCII Art Face**: Random selection from faces.py
- **Status Messages**: System initialization progress
- **Loading Animation**: Progress indicators
- **Duration**: Configurable boot screen time

### Flight Display

- **Flight Information**: Callsign, route, aircraft details
- **Session Stats**: Flight count, elapsed time
- **Real-time Updates**: Live position and altitude
- **Rotation**: Cycles through detected flights

### Error/Status Screens

- **No Flights**: When no aircraft detected
- **Connection Error**: API or network issues
- **System Status**: Health and diagnostic info

## 🔊 Voice Feedback (Optional)

### Text-to-Speech Integration

```python
# Enable in config.toml
[voice]
enabled = true
engine = "espeak"  # or "festival", "pico2wave"
volume = 0.8
```

### Voice Events

- **Flight Detection**: Announces new flights
- **System Status**: Startup and error messages
- **Periodic Updates**: Flight count announcements

## 📊 Data & Logging

### Flight Data Processing

- **FlightRadar24 API**: Real-time flight data
- **Filtering**: By distance, altitude, and relevance
- **Caching**: Temporary storage for performance
- **Enrichment**: Additional aircraft details

### Logging System

```python
# Logging configuration
[logging]
level = "INFO"          # DEBUG, INFO, WARNING, ERROR
path = "/tmp/flight_tracker.log"
max_size = "10MB"
```

### Log Types

- **System Events**: Startup, shutdown, errors
- **Flight Events**: Detection, updates, departures
- **Hardware Events**: Display updates, GPIO actions
- **API Events**: Network requests and responses

## ⚡ Performance Optimization

### Memory Management

- **Minimal Dependencies**: Lightweight Python packages
- **Efficient Data Structures**: Optimized for Pi hardware
- **Garbage Collection**: Automatic memory cleanup

### CPU Optimization

- **Async Operations**: Non-blocking API calls
- **Update Intervals**: Configurable refresh rates
- **Sleep Management**: Power-efficient scheduling

### Storage Optimization

- **Log Rotation**: Automatic old log cleanup
- **Temporary Files**: RAM-disk usage when possible
- **Cache Management**: Bounded memory usage

## 🔧 Troubleshooting

### Common Issues

#### Display Not Working

```bash
# Check SPI is enabled
ls /dev/spi*

# Test display connection
python -c "from ui.hw.waveshare213in_v4 import Waveshare213inV4; d=Waveshare213inV4(); d.test()"

# Check GPIO permissions
sudo usermod -a -G spi,gpio $USER
```

#### No Flights Detected

```bash
# Test internet connection
ping 8.8.8.8

# Check location configuration
grep address config.toml

# Verify API access
python -c "from FlightRadar24 import FlightRadar24API; print('API accessible')"
```

#### High CPU Usage

```bash
# Monitor processes
htop

# Check update intervals in config.toml
[ui]
scan_update_interval = 5  # Increase for less CPU usage
```

### Debug Mode

```bash
# Enable verbose logging
python tracker.py --debug

# Check system logs
tail -f /var/log/syslog | grep flight

# Monitor resource usage
iostat -x 1
```

## 🚀 Production Deployment

### Systemd Service

Create `/etc/systemd/system/flight-tracker.service`:

```ini
[Unit]
Description=Flight Tracker
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/flight-tracker/src/raspi
ExecStart=/home/pi/flight-tracker/src/raspi/venv/bin/python tracker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable flight-tracker
sudo systemctl start flight-tracker
sudo systemctl status flight-tracker
```

### Auto-start on Boot

Add to `/etc/rc.local`:

```bash
# Start flight tracker
cd /home/pi/flight-tracker/src/raspi
sudo -u pi ./venv/bin/python tracker.py &
```

### Remote Access

```bash
# SSH access for remote monitoring
ssh pi@your-pi-ip

# VNC for desktop access (optional)
sudo systemctl enable vncserver-x11-serviced
```

## 🔄 Integration with Backend

### Standalone Mode (Default)

Runs independently with direct API access

### Backend Integration Mode

Connect to centralized backend service:

```toml
[api]
backend_url = "http://your-backend:8000"
use_backend = true
```

Benefits:

- Centralized configuration
- Shared logging
- Remote monitoring
- Multi-device coordination

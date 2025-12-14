# 🔧 Troubleshooting Guide

Common issues and solutions for Flight Tracker.

## Table of Contents

- [Raspberry Pi Display Issues](#raspberry-pi-display-issues)
- [Backend Issues](#backend-issues)
- [Frontend Issues](#frontend-issues)
- [Network Issues](#network-issues)
- [General Issues](#general-issues)

---

## Raspberry Pi Display Issues

### Display Shows "Display not initialized" Warning

**Symptoms:**

```
ERROR - Cannot import Waveshare EPD module (missing Pi libraries): No module named 'spidev'
WARNING - Display not initialized, skipping render
```

**Cause:** GPIO/SPI packages not installed or not accessible to Python environment.

**Solution:**

```bash
# 1. Install system packages
sudo ./scripts/install-gpio-packages.sh

# 2. Verify installation
./scripts/test-display.sh

# 3. Restart system (recreates venv with correct settings)
./scripts/start-raspi-all.sh
```

**Why this happens:** Python virtual environments need `--system-site-packages` flag to access GPIO libraries.

### Display Shows "Failed to add edge detection"

**Symptoms:**

```
ERROR - Failed to initialize Waveshare hardware: Failed to add edge detection
WARNING - Falling back from lgpio: No module named 'lgpio'
```

**Cause:** Missing `lgpio` library (required by gpiozero on modern Raspberry Pi OS).

**Solution:**

```bash
sudo apt-get install python3-lgpio python3-rpi-lgpio
./scripts/start-raspi-all.sh
```

### Display Test Works But Full System Doesn't

**Symptoms:** `./scripts/test-display.sh` succeeds, but `./scripts/start-raspi-all.sh` fails.

**Cause:** Test uses system Python, but full system uses virtual environment.

**Solution:**

```bash
# The start script will automatically recreate venv with correct settings
./scripts/start-raspi-all.sh
```

If that doesn't work:

```bash
# Manually recreate venv
cd src/backend
rm -rf venv
cd ~/flight-tracker
./scripts/start-raspi-all.sh
```

### SPI Not Enabled

**Symptoms:**

```
ERROR - Hardware resources not available (SPI/GPIO not accessible)
```

**Solution:**

```bash
sudo raspi-config
# Navigate: Interface Options → SPI → Enable
sudo reboot
```

### Permission Denied on /dev/spidev\*

**Symptoms:** Display works with `sudo` but not without.

**Solution:**

```bash
# Add user to spi and gpio groups
sudo usermod -a -G spi,gpio $USER

# Logout and login (or reboot) for changes to take effect
sudo reboot
```

---

## Backend Issues

### FlightRadar24 API Returns Invalid Data

**Symptoms:**

```
FlightRadar24 API returned invalid data: list
WARNING - Invalid flight data received
```

**Cause:** API occasionally returns empty lists or unexpected formats.

**Solution:** This is expected behavior - the backend handles it gracefully. Flights will appear when aircraft are in range.

### "Address not found" or Geocoding Errors

**Symptoms:**

```
ERROR - Could not geocode address: [address]
```

**Solution:**

1. Check your internet connection
2. Try a different address format (postcode, city + country, etc.)
3. Use latitude/longitude directly in config.toml:
   ```toml
   latitude = 51.5074
   longitude = -0.1278
   ```

### Backend Won't Start

**Symptoms:**

```
❌ Backend failed to start. Check logs: /tmp/flight-tracker-backend.log
```

**Solution:**

```bash
# Check logs
tail -f /tmp/flight-tracker-backend.log

# Common fixes:
# 1. Port already in use
sudo lsof -i :8000
# Kill the process using port 8000

# 2. Missing dependencies
cd src/backend
source venv/bin/activate
pip install -r requirements.txt
```

---

## Frontend Issues

### Frontend Shows "Failed to fetch" Errors

**Symptoms:** Browser console shows:

```
Failed to load resource: net::ERR_BLOCKED_BY_CLIENT
GET http://localhost:8000/api/flights net::ERR_BLOCKED_BY_CLIENT
```

**Cause:** Frontend is trying to access `localhost:8000` from your laptop, but the backend is on the Raspberry Pi.

**Solution:** The start script now automatically configures this. Just restart:

```bash
./scripts/start-raspi-all.sh
```

The frontend will be rebuilt with the correct API URL (e.g., `http://192.168.0.220:8000`).

### Ad Blocker Blocking API Requests

**Symptoms:** `ERR_BLOCKED_BY_CLIENT` errors in browser console.

**Solution:** Disable ad blocker for your Pi's IP address, or whitelist:

- `http://<pi-ip>:8000`
- `http://<pi-ip>:5173`

### Frontend Won't Load

**Symptoms:** Blank page or build errors.

**Solution:**

```bash
# Rebuild frontend
cd src/frontend
npm install
npm run build

# Check Node.js version
node --version  # Should be 18+
```

---

## Network Issues

### Can't Access Frontend from Laptop

**Symptoms:** `http://<pi-ip>:5173` won't load.

**Check:**

1. **Pi and laptop on same network:**

   ```bash
   # On Pi
   hostname -I

   # On laptop
   ping <pi-ip>
   ```

2. **Firewall blocking ports:**

   ```bash
   # On Pi
   sudo ufw allow 8000
   sudo ufw allow 5173
   ```

3. **Services running:**
   ```bash
   # On Pi
   curl http://localhost:8000/api/health
   curl http://localhost:5173
   ```

### Finding Pi's IP Address

```bash
# On Pi
hostname -I

# Or
ip addr show | grep inet
```

---

## General Issues

### No Flights Detected

**Symptoms:** Dashboard shows "No flights detected" or count stays at 0.

**Possible causes:**

1. **No aircraft in range:**

   - Increase search radius in Settings
   - Check FlightRadar24 website to see if any aircraft are nearby

2. **Wrong location:**

   - Verify your location in Settings
   - Check latitude/longitude values

3. **API issues:**
   - Check backend logs: `tail -f /tmp/flight-tracker-backend.log`
   - Verify internet connection

### Services Won't Start

**Symptoms:** `start-raspi-all.sh` fails during setup.

**Solutions:**

1. **Python not found:**

   ```bash
   sudo apt-get install python3 python3-venv python3-pip
   ```

2. **Node.js not found:**

   ```bash
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **Port already in use:**
   ```bash
   # Kill existing processes
   pkill -f "python.*main.py"
   pkill -f "python.*agent.py"
   pkill -f "npx serve"
   ```

### "Module not found" Errors

**Symptoms:** Import errors in Python.

**Solution:**

```bash
# Backend
cd src/backend
source venv/bin/activate
pip install -r requirements.txt

# Raspberry Pi (if on Pi)
pip3 install -r src/raspi/requirements.txt
```

---

## Diagnostic Tools

### Display Diagnostic

Check display hardware and libraries:

```bash
./scripts/diagnose-display.sh
```

### Display Test

Test display without running full system:

```bash
./scripts/test-display.sh
```

### Check Logs

```bash
# Backend
tail -f /tmp/flight-tracker-backend.log

# Frontend
tail -f /tmp/flight-tracker-frontend.log

# Display client
tail -f /tmp/flight-tracker-raspi.log

# All together
tail -f /tmp/flight-tracker-*.log
```

### Verify Installation

```bash
# Python modules
python3 -c "import spidev; print('✅ spidev')"
python3 -c "import gpiozero; print('✅ gpiozero')"
python3 -c "import RPi.GPIO; print('✅ RPi.GPIO')"
python3 -c "import lgpio; print('✅ lgpio')"

# SPI enabled
lsmod | grep spi
ls -l /dev/spidev*

# Waveshare files
ls src/raspi/ui/hw/libs/waveshare/
```

---

## Still Need Help?

1. Check the logs for detailed error messages
2. Run diagnostic scripts: `diagnose-display.sh`, `test-display.sh`
3. Verify all requirements are met
4. Review the setup guides: [QUICKSTART.md](../QUICKSTART.md), [RASPI_SETUP.md](../RASPI_SETUP.md)
5. Check if similar issues exist in the project documentation

## Quick Reference Commands

```bash
# Raspberry Pi - Full system
./scripts/start-raspi-all.sh

# Desktop - Development
./scripts/start-flight-tracker.sh

# Test display only
./scripts/test-display.sh

# Diagnose issues
./scripts/diagnose-display.sh

# Install GPIO packages
sudo ./scripts/install-gpio-packages.sh

# Stop all services
pkill -f "python.*main.py"
pkill -f "python.*agent.py"
pkill -f "npx serve"
```

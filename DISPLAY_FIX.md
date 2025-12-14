# Raspberry Pi Display Setup - Quick Reference

## The Problem

You're seeing this error:

```
ERROR - Cannot import Waveshare EPD module (missing Pi libraries): No module named 'spidev'
WARNING - Display not initialized, skipping render
```

**Key insight:** The diagnostic script (`diagnose-display.sh`) may pass ✅ because it runs with system Python, but the flight tracker runs in a **virtual environment** that doesn't have the hardware packages installed yet!

## The Solution

Run these commands **on your Raspberry Pi**:

### Step 1: Run Diagnostic (Optional)

```bash
cd ~/flight-tracker
./scripts/diagnose-display.sh
```

This will tell you exactly what's missing.

### Step 2: Install Waveshare Libraries

```bash
cd ~/flight-tracker
./scripts/install-waveshare.sh
```

This script will:

- Install system packages (python3-spidev, python3-gpiozero, python3-rpi.gpio)
- Install Python packages (spidev, gpiozero, RPi.GPIO)
- Download Waveshare EPD library files
- Verify everything is installed correctly

### Step 3: Enable SPI Interface

```bash
sudo raspi-config
```

- Navigate to: **Interface Options** → **SPI** → **Enable**
- Exit and save

### Step 4: Test Display Hardware

**Before rebooting, test the display with a simple script:**

```bash
cd ~/flight-tracker
./scripts/test-display.sh
```

This will:

- Check all Python modules are available
- Test display initialization
- Render a test pattern to your e-ink display
- Verify everything works

If this test passes, your display is working! 🎉

### Step 5: Reboot (if test passed)

```bash
sudo reboot
```

### Step 6: Run Flight Tracker

```bash
cd ~/flight-tracker
./scripts/start-raspi-all.sh
```

The display warnings should be gone! ✅

## Manual Installation (If Script Fails)

If the automatic script doesn't work, try manual installation:

```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y python3-spidev python3-gpiozero python3-rpi.gpio python3-pil git

# Install Python packages
pip3 install spidev gpiozero RPi.GPIO Pillow --break-system-packages

# Clone Waveshare library
cd ~/flight-tracker/src/raspi/ui/hw/libs
git clone --depth 1 https://github.com/waveshare/e-Paper.git temp

# Copy files
mkdir -p waveshare
cp temp/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd2in13_V4.py waveshare/
cp temp/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py waveshare/
echo '"""Waveshare E-Paper Library"""' > waveshare/__init__.py

# Clean up
rm -rf temp

# Enable SPI
sudo raspi-config  # Interface Options → SPI → Enable
sudo reboot
```

## Verify Installation

After rebooting, verify everything works:

```bash
# Check Python modules
python3 -c "import spidev; print('✅ spidev OK')"
python3 -c "import gpiozero; print('✅ gpiozero OK')"
python3 -c "import RPi.GPIO; print('✅ RPi.GPIO OK')"

# Check SPI device
ls -l /dev/spidev*

# Check Waveshare files
ls ~/flight-tracker/src/raspi/ui/hw/libs/waveshare/

# Should see:
# __init__.py
# epd2in13_V4.py
# epdconfig.py
```

All checks should pass! ✅

## Common Issues

### "Permission denied" on /dev/spidev\*

Add your user to the spi and gpio groups:

```bash
sudo usermod -a -G spi,gpio $USER
```

Then **logout and login** (or reboot).

### "SPI not found"

Enable it via raspi-config:

```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

### Still seeing "Display not initialized"?

Try running with sudo:

```bash
sudo ./scripts/start-raspi-all.sh
```

If it works with sudo, it's a permission issue. Fix with:

```bash
sudo usermod -a -G spi,gpio $USER
# Then logout/login or reboot
```

## What Gets Installed

**System Packages:**

- `python3-spidev` - SPI interface for Python
- `python3-gpiozero` - GPIO control library
- `python3-rpi.gpio` - Alternative GPIO library
- `python3-pil` - Image processing (Pillow)

**Python Packages:**

- `spidev` - SPI communication
- `gpiozero` - GPIO pin control
- `RPi.GPIO` - GPIO access
- `Pillow` - Image manipulation

**Waveshare Files:**

- `epd2in13_V4.py` - Driver for 2.13" V4 display
- `epdconfig.py` - Hardware configuration

## Need Help?

Run the diagnostic script to see what's wrong:

```bash
./scripts/diagnose-display.sh
```

It will give you a detailed report of what's working and what needs fixing.

#!/bin/bash
# Diagnostic script to check Raspberry Pi display setup

echo "Flight Tracker Display Diagnostics"
echo "======================================"
echo ""

# Check if running on Pi
echo "System Check:"
if command -v raspi-config &> /dev/null; then
    echo "PASS: Running on Raspberry Pi"
else
    echo "FAIL: Not running on Raspberry Pi (raspi-config not found)"
fi
echo ""

# Check Python modules
echo "Python Module Check:"
python3 -c "import spidev; print('PASS: spidev module available')" 2>/dev/null || echo "FAIL: spidev module NOT available - Run: pip3 install spidev --break-system-packages"
python3 -c "import gpiozero; print('PASS: gpiozero module available')" 2>/dev/null || echo "FAIL: gpiozero module NOT available - Run: pip3 install gpiozero --break-system-packages"
python3 -c "import RPi.GPIO; print('PASS: RPi.GPIO module available')" 2>/dev/null || echo "FAIL: RPi.GPIO module NOT available - Run: pip3 install RPi.GPIO --break-system-packages"
python3 -c "import PIL; print('PASS: Pillow module available')" 2>/dev/null || echo "FAIL: Pillow module NOT available - Run: pip3 install Pillow"
echo ""

# Check SPI
echo "SPI Interface Check:"
if lsmod | grep -q spi_bcm2835; then
    echo "PASS: SPI kernel module loaded"
else
    echo "FAIL: SPI kernel module NOT loaded - Enable with: sudo raspi-config → Interface Options → SPI"
fi

if [ -e /dev/spidev0.0 ]; then
    echo "PASS: SPI device /dev/spidev0.0 exists"
    ls -lh /dev/spidev*
else
    echo "FAIL: SPI device NOT found - Enable with: sudo raspi-config → Interface Options → SPI"
fi
echo ""

# Check GPIO permissions
echo "Permission Check:"
if groups | grep -q spi; then
    echo "PASS: User is in 'spi' group"
else
    echo "FAIL: User NOT in 'spi' group - Run: sudo usermod -a -G spi $USER (then logout/login)"
fi

if groups | grep -q gpio; then
    echo "PASS: User is in 'gpio' group"
else
    echo "FAIL: User NOT in 'gpio' group - Run: sudo usermod -a -G gpio $USER (then logout/login)"
fi
echo ""

# Check Waveshare files
echo "Waveshare Library Check:"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
WAVESHARE_DIR="$PROJECT_ROOT/src/raspi/ui/hw/libs/waveshare"

if [ -f "$WAVESHARE_DIR/epd2in13_V4.py" ]; then
    echo "PASS: epd2in13_V4.py found"
else
    echo "FAIL: epd2in13_V4.py NOT found at: $WAVESHARE_DIR/"
fi

if [ -f "$WAVESHARE_DIR/epdconfig.py" ]; then
    echo "PASS: epdconfig.py found"
else
    echo "FAIL: epdconfig.py NOT found at: $WAVESHARE_DIR/"
fi

if [ -f "$WAVESHARE_DIR/__init__.py" ]; then
    echo "PASS: __init__.py found"
else
    echo "FAIL: __init__.py NOT found at: $WAVESHARE_DIR/"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary:"
echo ""

ALL_GOOD=true

# Check each requirement
python3 -c "import spidev" 2>/dev/null || ALL_GOOD=false
python3 -c "import gpiozero" 2>/dev/null || ALL_GOOD=false
[ -e /dev/spidev0.0 ] || ALL_GOOD=false
[ -f "$WAVESHARE_DIR/epd2in13_V4.py" ] || ALL_GOOD=false
[ -f "$WAVESHARE_DIR/epdconfig.py" ] || ALL_GOOD=false

if $ALL_GOOD; then
    echo "PASS: All checks passed! Display should work."
    echo ""
    echo "If you still see errors, try:"
    echo "  1. Reboot: sudo reboot"
    echo "  2. Run with sudo: sudo ./scripts/start-raspi-all.sh"
else
    echo "FAIL: Some checks failed. Please fix the issues above."
    echo ""
    echo "Quick fix - run the installer:"
    echo "  ./scripts/install-waveshare.sh"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

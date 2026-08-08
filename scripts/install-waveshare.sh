#!/bin/bash
# Install Waveshare E-ink Display Libraries for Raspberry Pi
# Run this on your Raspberry Pi

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LIBS_DIR="$PROJECT_ROOT/src/raspi/ui/hw/libs"

echo "Installing Waveshare E-Paper Display Libraries"
echo "=================================================="

# Check if running on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "WARNING: This doesn't appear to be a Raspberry Pi"
    echo "   The hardware drivers won't work on other systems"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install system dependencies unless the consolidated setup target already did it.
if [ "${SKIP_SYSTEM_PACKAGES:-0}" != "1" ]; then
    echo ""
    echo "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-spidev python3-gpiozero python3-lgpio python3-rpi-lgpio python3-dev python3-pil git
fi

# Create libs directory
mkdir -p "$LIBS_DIR"
cd "$LIBS_DIR"

if [ -f "waveshare/epd2in13_V4.py" ] && [ -f "waveshare/epdconfig.py" ]; then
    echo ""
    echo "PASS: Waveshare driver already installed"
    cd waveshare
else
    # Clone Waveshare examples temporarily
    echo ""
    echo "Downloading Waveshare libraries..."
    if [ -d "waveshare-examples" ]; then
        rm -rf waveshare-examples
    fi
    git clone --depth 1 https://github.com/waveshare/e-Paper.git waveshare-examples

    # Create waveshare library directory
    mkdir -p waveshare
    cd waveshare

    # Copy required files
    echo ""
    echo "Copying library files..."
    cp ../waveshare-examples/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd2in13_V4.py .
    cp ../waveshare-examples/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py .
fi

# Create __init__.py
cat > __init__.py << 'EOF'
"""
Waveshare E-Paper Display Library
Adapted from: https://github.com/waveshare/e-Paper
"""
EOF

# Clean up
cd ..
if [ -d "waveshare-examples" ]; then
    rm -rf waveshare-examples
fi

echo ""
echo "PASS: Waveshare libraries installed!"
echo ""
echo "Verifying installation..."
echo ""

# Check Python modules
python3 -c "import spidev; print('PASS: spidev module available')" 2>/dev/null || echo "FAIL: spidev module not found"
python3 -c "import gpiozero; print('PASS: gpiozero module available')" 2>/dev/null || echo "FAIL: gpiozero module not found"
python3 -c "import RPi.GPIO; print('PASS: RPi.GPIO module available')" 2>/dev/null || echo "FAIL: RPi.GPIO module not found"
python3 -c "import lgpio; print('PASS: lgpio module available')" 2>/dev/null || echo "FAIL: lgpio module not found"

echo ""

# Check Waveshare files
if [ -f "$LIBS_DIR/waveshare/epd2in13_V4.py" ] && [ -f "$LIBS_DIR/waveshare/epdconfig.py" ]; then
    echo "PASS: Waveshare EPD library files present"
    ls -lh "$LIBS_DIR/waveshare/"*.py
else
    echo "FAIL: Waveshare EPD library files missing!"
    echo "   Expected files:"
    echo "   - $LIBS_DIR/waveshare/epd2in13_V4.py"
    echo "   - $LIBS_DIR/waveshare/epdconfig.py"
fi

echo ""
echo "Next steps:"
if [ "${SKIP_SYSTEM_PACKAGES:-0}" = "1" ]; then
    echo "   The consolidated setup will finish installing the app."
    echo "   Run make pi when it completes."
else
    echo "   1. Enable SPI interface:"
    echo "      sudo raspi-config"
    echo "      → Interface Options → SPI → Enable"
    echo ""
    echo "   2. Reboot your Pi:"
    echo "      sudo reboot"
    echo ""
    echo "   3. Run the flight tracker again:"
    echo "      make pi"
fi
echo ""
echo "   The display should now work without warnings!"

#!/bin/bash
# Install Waveshare E-ink Display Libraries for Raspberry Pi
# Run this on your Raspberry Pi

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LIBS_DIR="$PROJECT_ROOT/src/raspi/ui/hw/libs"

echo "📦 Installing Waveshare E-Paper Display Libraries"
echo "=================================================="

# Check if running on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   The hardware drivers won't work on other systems"
    read -p "   Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install system dependencies
echo ""
echo "📥 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-rpi.gpio python3-spidev python3-pil git

# Create libs directory
mkdir -p "$LIBS_DIR"
cd "$LIBS_DIR"

# Clone Waveshare examples temporarily
echo ""
echo "📥 Downloading Waveshare libraries..."
if [ -d "waveshare-examples" ]; then
    rm -rf waveshare-examples
fi
git clone --depth 1 https://github.com/waveshare/e-Paper.git waveshare-examples

# Create waveshare library directory
mkdir -p waveshare
cd waveshare

# Copy required files
echo ""
echo "📋 Copying library files..."
cp ../waveshare-examples/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epd2in13_V4.py .
cp ../waveshare-examples/RaspberryPi_JetsonNano/python/lib/waveshare_epd/epdconfig.py .

# Create __init__.py
cat > __init__.py << 'EOF'
"""
Waveshare E-Paper Display Library
Adapted from: https://github.com/waveshare/e-Paper
"""
EOF

# Clean up
cd ..
rm -rf waveshare-examples

echo ""
echo "✅ Waveshare libraries installed!"
echo ""
echo "📋 Next steps:"
echo "   1. Enable SPI interface:"
echo "      sudo raspi-config"
echo "      → Interface Options → SPI → Enable"
echo ""
echo "   2. Reboot your Pi:"
echo "      sudo reboot"
echo ""
echo "   3. Run the flight tracker again:"
echo "      ./scripts/start-raspi-all.sh"
echo ""
echo "   The display should now work without warnings!"

#!/bin/bash
# Install GPIO system packages on Raspberry Pi
# Run this once: sudo ./scripts/install-gpio-packages.sh

set -e

echo "📦 Installing GPIO System Packages"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run as root: sudo $0"
    exit 1
fi

# Check if on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "❌ Not running on Raspberry Pi"
    exit 1
fi

echo "📥 Updating package lists..."
apt-get update

echo ""
echo "📦 Installing GPIO and SPI packages..."
apt-get install -y \
    python3-spidev \
    python3-gpiozero \
    python3-rpi.gpio \
    python3-lgpio \
    python3-rpi-lgpio \
    python3-pil

echo ""
echo "✅ System packages installed!"
echo ""
echo "📋 Verifying installation..."
python3 -c "import spidev; print('✅ spidev')" 2>/dev/null || echo "❌ spidev"
python3 -c "import gpiozero; print('✅ gpiozero')" 2>/dev/null || echo "❌ gpiozero"
python3 -c "import RPi.GPIO; print('✅ RPi.GPIO')" 2>/dev/null || echo "❌ RPi.GPIO"
python3 -c "import lgpio; print('✅ lgpio')" 2>/dev/null || echo "❌ lgpio"

echo ""
echo "✅ Done! Now run:"
echo "   ./scripts/test-display.sh"
echo "   ./scripts/start-raspi-all.sh"

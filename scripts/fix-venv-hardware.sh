#!/bin/bash
# Quick fix: Install hardware packages in the venv
# Run this if start-raspi-all.sh shows "No module named 'spidev'"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔧 Installing hardware packages in virtual environment..."

cd "$PROJECT_ROOT/src/backend"
if [ -d "venv" ]; then
    echo "📦 Found backend venv, installing packages..."
    source venv/bin/activate
    pip install spidev gpiozero RPi.GPIO || {
        echo "⚠️  pip install failed, packages may need system install"
        echo "   Run: sudo apt-get install python3-spidev python3-gpiozero python3-rpi.gpio"
    }
    deactivate
    echo "✅ Backend venv updated"
else
    echo "⚠️  No backend venv found"
fi

cd "$PROJECT_ROOT/src/raspi"
if [ -f "requirements-pi.txt" ]; then
    echo ""
    echo "📦 Installing from requirements-pi.txt..."
    pip3 install -r requirements-pi.txt --user --break-system-packages 2>/dev/null || \
    pip3 install -r requirements-pi.txt --user || \
    pip3 install -r requirements-pi.txt
    echo "✅ Hardware packages installed"
else
    echo "⚠️  requirements-pi.txt not found"
fi

echo ""
echo "✅ Done! Now run:"
echo "   ./scripts/test-display.sh    # Test display hardware"
echo "   ./scripts/start-raspi-all.sh # Start full system"

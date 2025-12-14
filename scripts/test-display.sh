#!/bin/bash
# Quick test script for Waveshare display
# Run this to test display hardware without starting the full system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🧪 Waveshare Display Test"
echo "========================="
echo ""

# Check if on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "❌ Not running on Raspberry Pi"
    exit 1
fi

cd "$PROJECT_ROOT/src/raspi"

# Check if venv exists, if not use system Python
if [ -d "venv" ]; then
    echo "📦 Using virtual environment..."
    source venv/bin/activate
    
    # Install hardware packages in venv if needed
    if [ -f "requirements-pi.txt" ]; then
        echo "📥 Ensuring hardware packages are installed in venv..."
        pip install -q -r requirements-pi.txt 2>/dev/null || {
            echo "⚠️  pip install failed, trying system packages..."
        }
    fi
else
    echo "📦 Using system Python (no venv found)..."
fi

# Verify imports work
echo ""
echo "🔍 Checking Python modules..."
python3 -c "import spidev" 2>/dev/null && echo "✅ spidev" || echo "❌ spidev - MISSING!"
python3 -c "import gpiozero" 2>/dev/null && echo "✅ gpiozero" || echo "❌ gpiozero - MISSING!"
python3 -c "import RPi.GPIO" 2>/dev/null && echo "✅ RPi.GPIO" || echo "❌ RPi.GPIO - MISSING!"

echo ""
echo "🚀 Running display test..."
echo ""

# Run the test script
python3 test_display.py

echo ""
echo "✅ Test complete!"

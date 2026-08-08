#!/bin/bash
# Quick test script for Waveshare display
# Run this to test display hardware without starting the full system

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Waveshare Display Test"
echo "========================="
echo ""

# Check if on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "FAIL: Not running on Raspberry Pi"
    exit 1
fi

cd "$PROJECT_ROOT/src/raspi"

# Use the Makefile-managed Pi environment when it exists. It inherits the
# Raspberry Pi OS hardware modules through --system-site-packages.
if [ -x "$PROJECT_ROOT/.venv-pi/bin/python" ]; then
    PYTHON_BIN="$PROJECT_ROOT/.venv-pi/bin/python"
    echo "Using .venv-pi..."
else
    PYTHON_BIN="python3"
    echo "Using system Python (.venv-pi has not been created yet)..."
fi

# Verify imports work
echo ""
echo "Checking Python modules..."
"$PYTHON_BIN" -c "import spidev" 2>/dev/null && echo "PASS: spidev" || echo "FAIL: spidev - MISSING!"
"$PYTHON_BIN" -c "import gpiozero" 2>/dev/null && echo "PASS: gpiozero" || echo "FAIL: gpiozero - MISSING!"
"$PYTHON_BIN" -c "import RPi.GPIO" 2>/dev/null && echo "PASS: RPi.GPIO compatibility module" || echo "FAIL: RPi.GPIO - MISSING!"

echo ""
echo "Running display test..."
echo ""

# Run the test script
"$PYTHON_BIN" test_display.py

echo ""
echo "PASS: Test complete!"

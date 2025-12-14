#!/bin/bash

# Start the Raspberry Pi Flight Tracker Client

echo "🚀 Starting Flight Tracker Raspberry Pi Client"
echo "=============================================="
echo ""

# Navigate to raspi directory
cd "$(dirname "$0")/../src/raspi"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi
echo "✅ Python 3 found"

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import PIL, requests, toml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some dependencies are missing"
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt
fi
echo "✅ Dependencies OK"

# Check if config file exists
if [ ! -f "config.toml" ]; then
    echo "❌ config.toml not found"
    echo "Please create config.toml from config.toml.example"
    exit 1
fi
echo "✅ Config file found"

echo ""
echo "🌐 Starting Flight Tracker Agent..."
echo "   Press Ctrl+C to stop"
echo ""

# Start the agent
python3 agent.py

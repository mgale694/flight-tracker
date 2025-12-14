#!/bin/bash

# Start the Flight Tracker Backend API

echo "🚀 Starting Flight Tracker Backend..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/../src/backend"

# Activate virtual environment
echo "🔧 Activating uvve virtual environment (flight-tracker)..."
uvve activate flight-tracker

# Install/update dependencies
echo "📥 Installing dependencies..."
uv pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Start the server
echo "🌐 Starting FastAPI server..."
echo "   Local:   http://localhost:8000"
echo "   Network: http://$(ipconfig getifaddr en0 2>/dev/null || hostname):8000"
echo "   Docs:    http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py

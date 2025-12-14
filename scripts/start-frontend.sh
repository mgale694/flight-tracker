#!/bin/bash

# Start the Flight Tracker Frontend

echo "🚀 Starting Flight Tracker Frontend..."
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/../src/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Start the dev server
echo "🌐 Starting Vite dev server..."
echo "   Local:   http://localhost:5173"
echo "   Network: http://$(ipconfig getifaddr en0 2>/dev/null || hostname):5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev

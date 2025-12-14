#!/bin/bash

# Kill all Flight Tracker processes and free up ports

echo "🛑 Stopping all Flight Tracker processes..."
echo "==========================================="
echo ""

# Kill Python processes (backend and raspi agent)
echo "🔧 Stopping Python processes..."
pkill -f "python.*main.py" 2>/dev/null && echo "   ✅ Backend stopped" || echo "   ℹ️  No backend process found"
pkill -f "python.*agent.py" 2>/dev/null && echo "   ✅ Raspi agent stopped" || echo "   ℹ️  No raspi agent found"

# Kill Node/npm processes (frontend dev server)
echo ""
echo "🔧 Stopping Node processes..."
pkill -f "npm.*dev" 2>/dev/null && echo "   ✅ npm dev server stopped" || echo "   ℹ️  No npm dev server found"
pkill -f "npx serve" 2>/dev/null && echo "   ✅ serve stopped" || echo "   ℹ️  No serve process found"
pkill -f "vite" 2>/dev/null && echo "   ✅ vite stopped" || echo "   ℹ️  No vite process found"

# Kill processes on specific ports
echo ""
echo "🔧 Freeing up ports..."
if lsof -ti:8000 >/dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "   ✅ Port 8000 freed (Backend)"
else
    echo "   ℹ️  Port 8000 already free"
fi

if lsof -ti:5173 >/dev/null 2>&1; then
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    echo "   ✅ Port 5173 freed (Frontend)"
else
    echo "   ℹ️  Port 5173 already free"
fi

echo ""
echo "✅ All Flight Tracker processes stopped"
echo ""

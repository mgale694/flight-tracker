# Source Code Directory

This directory contains all the source code for the Flight Tracker project, organized into three main components.

## 📁 Directory Structure

### `backend/`

FastAPI-based backend service that provides:

- RESTful API endpoints for flight data
- Configuration management
- Activity logging
- Real-time flight tracking using FlightRadar24 API

**Key Files:**

- `main.py` - FastAPI application entry point
- `tracker.py` - Flight tracking logic
- `config.toml` - Backend configuration
- `requirements.txt` - Python dependencies

**API Endpoints:**

- `GET /flights` - Current tracked flights
- `GET /config` - Configuration settings
- `POST /config` - Update configuration
- `GET /logs` - Activity logs
- `DELETE /logs` - Clear logs
- `GET /health` - Health check

### `frontend/`

Modern React-based web interface:

#### `frontend/react/`

Production web dashboard built with:

- **React 18** with TypeScript
- **Vite** for fast development and building
- **CSS custom properties** for theming
- **Responsive design** for desktop and mobile

**Features:**

- Real-time flight display simulation
- Interactive flight departure board
- Settings management interface
- Activity logging console
- Dark/light theme toggle
- Raspberry Pi display emulation

#### `frontend/stremlit/` (Legacy)

Initial proof-of-concept Streamlit interface (deprecated)

### `raspi/`

Raspberry Pi specific implementation for physical hardware:

- E-ink display drivers for multiple display types
- Hardware interface and GPIO control
- Voice feedback system
- Boot sequence and status displays
- Configuration for physical deployment

**Key Components:**

- `tracker.py` - Main tracking application
- `ui/` - Display interface and rendering
- `config.toml` - Hardware configuration
- Hardware drivers for various e-ink displays

## 🔄 Data Flow

```
FlightRadar24 API → Backend (FastAPI) → Frontend (React)
                        ↓
                 Raspberry Pi Display
```

1. **Backend** fetches flight data from FlightRadar24 API
2. **Frontend** polls backend for updates and displays in web interface
3. **Raspberry Pi** runs independently or connects to backend
4. All components can share configuration through API

## 🚀 Development Workflow

1. **Backend Development**: Work in `backend/` directory
2. **Frontend Development**: Work in `frontend/react/` directory
3. **Hardware Testing**: Deploy to `raspi/` directory on Raspberry Pi
4. **Integration Testing**: Run all components together

## 📝 Configuration

Each component has its own configuration:

- **Backend**: `backend/config.toml`
- **Raspberry Pi**: `raspi/config.toml`
- **Frontend**: Environment variables and runtime settings

## 🔧 Build Process

- **Backend**: Direct Python execution (`python main.py`)
- **Frontend**: Vite build system (`npm run build`)
- **Raspberry Pi**: Direct Python execution with hardware dependencies

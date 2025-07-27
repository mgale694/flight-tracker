# Flight Tracker Backend

FastAPI backend for the Flight Tracker application that replicates the flight radar API functionality from the Raspberry Pi version.

## Features

- Real-time flight tracking using FlightRadar24 API
- WebSocket support for live updates
- Configuration management
- RESTful API endpoints
- Boot sequence simulation

## Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Run the backend:

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - API information
- `GET /config` - Get current configuration
- `POST /config` - Update configuration
- `GET /boot` - Get boot screen data
- `GET /flights` - Get current flights in area
- `POST /session/start` - Start flight tracking session
- `POST /session/stop` - Stop flight tracking session
- `GET /session/status` - Get session status
- `WebSocket /ws` - Real-time updates

## Configuration

The backend uses a `config.toml` file for configuration. You can modify:

- `address`: Location to center flight tracking
- `search_radius_meters`: Search radius in meters
- `max_flights`: Maximum flights to track per session
- `max_elapsed_time`: Maximum session duration in seconds

## Development

To run with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

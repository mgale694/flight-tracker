# Backend - FastAPI Flight Tracker Service

FastAPI-based backend service that provides real-time flight tracking capabilities and serves as the API layer for the Flight Tracker web interface.

## 🚀 Features

- **Real-time Flight Tracking**: Uses FlightRadar24 API to track aircraft in configurable areas
- **RESTful API**: Comprehensive endpoints for flight data, configuration, and logging
- **Activity Logging**: In-memory logging system with API access
- **Configuration Management**: Dynamic configuration updates via API
- **Health Monitoring**: Health check endpoints for system monitoring
- **CORS Support**: Enabled for web dashboard integration

## 📁 Files Overview

```
backend/
├── main.py              # FastAPI application and route definitions
├── tracker.py           # Flight tracking logic and FlightRadar24 integration
├── config.toml          # Configuration file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- pip package manager

### Install Dependencies

```bash
cd src/backend
pip install -r requirements.txt
```

### Configuration

Edit `config.toml` to customize tracking parameters:

```toml
[main]
address = "Your Address Here"
search_radius_meters = 10000
max_flights = 25
max_elapsed_time = 2400

[api]
user_agent = "Flight Tracker v1.0"
timeout = 30
retry_attempts = 3
```

### Run the Server

```bash
python main.py

# With custom host/port
python main.py --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Flight Data

- `GET /flights` - Get current flights in tracking area
- `GET /health` - Health check and system status

### Configuration

- `GET /config` - Get current configuration
- `POST /config` - Update configuration settings

### Activity Logs

- `GET /logs` - Get activity logs
- `DELETE /logs` - Clear activity logs

### Documentation

- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## 🔧 Key Components

### FlightTracker Class (`tracker.py`)

- Manages FlightRadar24 API integration
- Handles flight data processing and filtering
- Provides detailed flight information including:
  - Aircraft registration and model
  - Airline information
  - Route details (origin/destination)
  - Real-time position and altitude

### Activity Logging System

- In-memory log storage (last 1000 entries)
- Structured logging with categories:
  - `SYSTEM` - System events
  - `API` - API calls and responses
  - `CONFIG` - Configuration changes
  - `RADAR` - Flight detection events
  - `FLIGHT` - Individual flight details

### Configuration Management

- Dynamic configuration updates
- Automatic tracker reinitialization on changes
- Validation and error handling

## 🔄 Integration

### With Frontend

The backend serves the React frontend via CORS-enabled API endpoints. The frontend polls the `/flights` endpoint every 5 seconds for real-time updates.

### With Raspberry Pi

The Raspberry Pi implementation can run independently or connect to this backend service for centralized configuration and logging.

## 🐛 Development & Debugging

### Enable Debug Mode

```bash
# Run with detailed logging
python main.py --host 127.0.0.1 --port 8000
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Get current flights
curl http://localhost:8000/flights

# Update configuration
curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"address": "New Address", "search_radius_meters": 5000}'
```

### Monitoring Logs

Access logs via the API:

```bash
curl http://localhost:8000/logs
```

## 📊 Performance Notes

- **Flight API Calls**: Limited by FlightRadar24 rate limits
- **Memory Usage**: Activity logs are limited to 1000 entries
- **Response Times**: Typically 200-500ms for flight data requests
- **Concurrent Users**: Supports multiple frontend connections

## 🚨 Error Handling

The backend includes comprehensive error handling for:

- FlightRadar24 API failures
- Configuration validation errors
- Network connectivity issues
- Invalid request parameters

All errors are logged to the activity system and returned as appropriate HTTP status codes.

To run with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

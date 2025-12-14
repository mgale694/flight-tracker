# Flight Tracker Backend

FastAPI backend service for tracking flights in a specific geographic area using FlightRadar24 data.

## Features

- **Real-time Flight Tracking**: Fetches live flight data from FlightRadar24 API
- **Geolocation-based**: Search for flights within a configurable radius of any address
- **RESTful API**: Clean HTTP endpoints for all operations
- **Activity Logging**: Comprehensive logging system for monitoring and debugging
- **Configuration Management**: Dynamic configuration updates via API
- **CORS Enabled**: Ready for cross-origin requests from web frontend
- **Clean Architecture**: Organized with routes, services, models, and utilities

## Requirements

- Python 3.8+
- Internet connection for FlightRadar24 API and geocoding

## Installation

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the application**:
   Edit `config.toml` to set your default location and preferences:
   ```toml
   [main]
   address = "Your City, Country"
   search_radius_meters = 3000
   max_flights = 20
   max_elapsed_time = 1800
   ```

## Usage

### Start the Server

**Development mode** (with auto-reload):

```bash
python main.py
```

**Production mode**:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:

- Local: `http://localhost:8000`
- Network: `http://<your-ip>:8000`

### API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health & Info

#### `GET /`

Root endpoint with API information.

**Response**:

```json
{
  "name": "Flight Tracker API",
  "version": "1.0.0",
  "status": "running"
}
```

#### `GET /api/health`

Health check endpoint.

**Response**:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-14T10:30:00.000Z"
}
```

### Flight Data

#### `GET /api/flights`

Get current flights in the configured area.

**Response**:

```json
[
  {
    "id": "abc123",
    "callsign": "UAL1234",
    "registration": "N12345",
    "aircraft": "B738",
    "airline": "UAL",
    "origin": "SFO",
    "destination": "LAX",
    "altitude": 35000,
    "speed": 450,
    "heading": 180,
    "latitude": 37.7749,
    "longitude": -122.4194,
    "distance": 1250.5,
    "timestamp": "2025-12-14T10:30:00.000Z"
  }
]
```

#### `GET /api/flight/{flight_id}`

Get detailed information about a specific flight.

**Parameters**:

- `flight_id` (path): Flight identifier

**Response**: Detailed flight information from FlightRadar24

### Configuration

#### `GET /api/config`

Get current configuration.

**Response**:

```json
{
  "main": {
    "address": "San Francisco, CA",
    "search_radius_meters": 3000,
    "max_flights": 20,
    "max_elapsed_time": 1800
  },
  "logging": {
    "max_activities": 500,
    "categories": ["SYSTEM", "RADAR", "FLIGHT", "CONFIG", "ERROR", "INFO"]
  }
}
```

#### `PUT /api/config`

Update configuration.

**Request Body**:

```json
{
  "address": "New York, NY",
  "search_radius_meters": 5000,
  "max_flights": 30,
  "max_elapsed_time": 1800
}
```

**Response**: Updated configuration

**Note**: All fields are optional. Only include fields you want to update.

### Activity Logs

#### `GET /api/activities`

Get activity logs.

**Query Parameters**:

- `limit` (optional): Maximum number of activities to return
- `category` (optional): Filter by category (SYSTEM, RADAR, FLIGHT, CONFIG, ERROR, INFO)

**Response**:

```json
[
  {
    "timestamp": "2025-12-14T10:30:00.000Z",
    "category": "FLIGHT",
    "message": "Found 5 flight(s) in area",
    "details": {
      "count": 5
    }
  }
]
```

#### `DELETE /api/activities`

Clear all activity logs.

**Response**:

```json
{
  "message": "Activity logs cleared"
}
```

## Configuration

### Main Configuration (`config.toml`)

```toml
[main]
# Address to track flights around
address = "San Francisco, CA"

# Search radius in meters (100-50000)
search_radius_meters = 3000

# Maximum number of flights to return (1-100)
max_flights = 20

# Maximum age of flight data in seconds
max_elapsed_time = 1800

[logging]
# Maximum number of activity logs to store
max_activities = 500

# Log categories
categories = ["SYSTEM", "RADAR", "FLIGHT", "CONFIG", "ERROR", "INFO"]
```

## Architecture

### Project Structure

```
backend/
├── main.py                    # Application entry point
├── config.toml               # Configuration file
├── requirements.txt          # Python dependencies
├── models/                   # Data models and schemas
│   ├── __init__.py
│   ├── schemas.py           # Pydantic models
│   └── enums.py             # Enumerations
├── routes/                   # API endpoints
│   ├── __init__.py
│   ├── system.py            # Health & root endpoints
│   ├── flights.py           # Flight endpoints
│   ├── config.py            # Configuration endpoints
│   └── activities.py        # Activity log endpoints
├── services/                 # Business logic
│   ├── __init__.py
│   ├── flight_service.py    # Flight tracking service
│   ├── config_service.py    # Configuration management
│   └── activity_service.py  # Activity logging
├── utils/                    # Utilities
│   ├── __init__.py
│   └── lifecycle.py         # App lifecycle management
└── shared/                   # Shared constants
    ├── __init__.py
    └── constants.py         # Application constants
```

### Core Components

1. **`main.py`**: FastAPI application entry point that wires everything together
2. **`models/`**: Pydantic schemas and enums for data validation
3. **`routes/`**: API endpoint definitions organized by domain
4. **`services/`**: Business logic layer (flight tracking, config, logging)
5. **`utils/`**: Helper utilities and lifecycle management
6. **`shared/`**: Shared constants and configuration
7. **`config.toml`**: Runtime configuration file

### Data Flow

1. Client requests flights via `/api/flights`
2. **Route** (`routes/flights.py`) receives the request
3. **Config Service** loads configuration from `config.toml`
4. **Flight Service** geocodes address to coordinates
5. **Flight Service** fetches flights from FlightRadar24 API
6. Flights filtered by distance from center point
7. Sorted by distance (closest first)
8. **Activity Service** logs the operation
9. Response returned to client

## Activity Log Categories

- **SYSTEM**: System startup, shutdown, and status changes
- **RADAR**: Flight radar queries and searches
- **FLIGHT**: Individual flight detections and updates
- **CONFIG**: Configuration changes
- **ERROR**: Errors and exceptions
- **INFO**: General information and health checks

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid input (e.g., bad address)
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a detail message:

```json
{
  "detail": "Error message here"
}
```

## Development

### Design Principles

- **Separation of Concerns**: Routes, services, and models are clearly separated
- **Dependency Injection**: Services are injected into routes for better testability
- **Single Responsibility**: Each module has a clear, focused purpose
- **Type Safety**: Full Pydantic models and type hints throughout
- **Clean Entry Point**: `main.py` simply wires components together

### Testing

**Test health endpoint**:

```bash
curl http://localhost:8000/api/health
```

**Test flights endpoint**:

```bash
curl http://localhost:8000/api/flights
```

**Test configuration update**:

```bash
curl -X PUT http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{"address": "Los Angeles, CA", "search_radius_meters": 5000}'
```

**Test activity logs**:

```bash
curl http://localhost:8000/api/activities?limit=10
```

### CORS Configuration

By default, CORS is enabled for all origins (`*`) for development. For production, update the CORS middleware in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### "Could not geocode address"

- Check that the address is valid and recognizable by geocoding services
- Try a more specific address (city, state, country)
- Check internet connection

### "Error fetching flights"

- FlightRadar24 API may be rate-limited
- Check internet connection
- Reduce query frequency

### No flights returned

- Increase `search_radius_meters` in config
- Check that the location has air traffic
- Verify FlightRadar24 API is accessible

### Port already in use

- Change port: `uvicorn main:app --port 8001`
- Or kill process using port 8000

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **FlightRadarAPI**: FlightRadar24 API client
- **geopy**: Geocoding library
- **toml**: TOML configuration parser
- **pydantic**: Data validation

## Performance

- **Geocoding**: Cached per address (no repeated lookups)
- **Activity Logs**: Rotated automatically (FIFO at max_activities limit)
- **API Calls**: Consider rate limits when polling frequently

## License

See root LICENSE file.

## Support

For issues or questions, check:

- API documentation at `/docs`
- Activity logs for debugging
- FlightRadar24 API status

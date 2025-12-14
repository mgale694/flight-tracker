# Backend Architecture Documentation

## Overview

The Flight Tracker backend follows a clean, layered architecture with clear separation of concerns. This document explains the structure and responsibilities of each component.

## Directory Structure

```
src/backend/
├── main.py                    # Application entry point
├── config.toml               # Runtime configuration
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
├── README.md                # Usage documentation
│
├── models/                   # Data models and validation
│   ├── __init__.py          # Package exports
│   ├── schemas.py           # Pydantic models for API
│   └── enums.py             # Enumerations (categories, status)
│
├── routes/                   # API endpoints (controllers)
│   ├── __init__.py          # Package exports
│   ├── system.py            # Health check & root endpoints
│   ├── flights.py           # Flight tracking endpoints
│   ├── config.py            # Configuration endpoints
│   └── activities.py        # Activity log endpoints
│
├── services/                 # Business logic layer
│   ├── __init__.py          # Package exports
│   ├── flight_service.py    # FlightRadar24 integration
│   ├── config_service.py    # Configuration management
│   └── activity_service.py  # Activity logging
│
├── utils/                    # Helper utilities
│   ├── __init__.py          # Package exports
│   └── lifecycle.py         # App startup/shutdown
│
└── shared/                   # Shared constants & config
    ├── __init__.py          # Package exports
    └── constants.py         # Application-wide constants
```

## Layer Responsibilities

### 1. Entry Point (`main.py`)

**Purpose**: Application initialization and wiring

**Responsibilities**:

- Create FastAPI application
- Configure CORS middleware
- Initialize all services
- Register routes with dependency injection
- Set up lifecycle events

**Key Function**: `create_app()` - Returns configured FastAPI instance

### 2. Models Layer (`models/`)

**Purpose**: Data validation and type definitions

**Files**:

- `schemas.py`: Pydantic models for request/response validation

  - `FlightData`: Flight information schema
  - `ConfigUpdate`: Configuration update schema
  - `ActivityLog`: Activity log entry schema
  - `HealthResponse`, `APIResponse`, `MessageResponse`: Response schemas

- `enums.py`: Enumerated types
  - `ActivityCategory`: Log categories (SYSTEM, RADAR, FLIGHT, etc.)
  - `APIStatus`: API status values

**Best Practices**:

- All API inputs/outputs must have Pydantic models
- Use Field validators for constraints
- Keep models focused and single-purpose

### 3. Routes Layer (`routes/`)

**Purpose**: HTTP endpoint definitions (thin controllers)

**Files**:

- `system.py`: Root (`/`) and health check (`/api/health`)
- `flights.py`: Flight endpoints (`/api/flights`, `/api/flight/{id}`)
- `config.py`: Configuration endpoints (`/api/config`)
- `activities.py`: Activity log endpoints (`/api/activities`)

**Pattern**: Each route file exports a `setup_*_routes()` function that:

1. Takes service dependencies as parameters
2. Defines route handlers with closures over services
3. Returns configured APIRouter

**Responsibilities**:

- Define HTTP routes and methods
- Validate request data (via Pydantic)
- Call appropriate services
- Handle HTTP-specific concerns (status codes, errors)
- Return responses

**NOT responsible for**:

- Business logic
- Data persistence
- External API calls
- Complex data transformations

### 4. Services Layer (`services/`)

**Purpose**: Business logic and external integrations

**Files**:

#### `flight_service.py` - `FlightTrackerService`

**Responsibilities**:

- Integrate with FlightRadar24 API
- Geocode addresses to coordinates
- Filter flights by distance
- Parse flight data
- Cache geocoding results

**Key Methods**:

- `geocode_address(address)`: Convert address to coordinates
- `get_flights_in_area(address, radius, max_flights)`: Get nearby flights
- `get_flight_details(flight_id)`: Get detailed flight info
- `clear_cache()`: Clear geocoding cache

#### `config_service.py` - `ConfigService`

**Responsibilities**:

- Load configuration from TOML file
- Save configuration to TOML file
- Update specific config values
- Provide default configuration
- Cache configuration in memory

**Key Methods**:

- `load_config()`: Load from file
- `save_config(config)`: Save to file
- `update_config(config_update)`: Update specific fields
- `get_main_config()`: Get main config section

#### `activity_service.py` - `ActivityLoggerService`

**Responsibilities**:

- Log activities with categories
- Store logs in memory (FIFO deque)
- Filter logs by category
- Limit and pagination
- Automatic rotation

**Key Methods**:

- `log(category, message, details)`: Log an activity
- `get_activities(limit, category)`: Get filtered logs
- `clear()`: Clear all logs

### 5. Utils Layer (`utils/`)

**Purpose**: Helper utilities and cross-cutting concerns

**Files**:

#### `lifecycle.py` - `AppLifecycle`

**Responsibilities**:

- Application startup tasks
- Application shutdown tasks
- Coordinate service initialization

**Key Methods**:

- `startup()`: Execute on app startup
- `shutdown()`: Execute on app shutdown

### 6. Shared Layer (`shared/`)

**Purpose**: Application-wide constants and configuration

**Files**:

#### `constants.py`

**Contains**:

- Application metadata (name, version, description)
- File paths (BASE_DIR, CONFIG_FILE)
- Server configuration (host, port)
- CORS configuration
- Logging configuration

**Usage**: Import constants instead of hardcoding values

## Data Flow Example

### Request: GET /api/flights

```
1. HTTP Request
   ↓
2. routes/flights.py :: get_flights()
   ↓
3. services/config_service.py :: get_main_config()
   ↓ (returns address, radius, max_flights)
4. services/activity_service.py :: log("RADAR", ...)
   ↓
5. services/flight_service.py :: get_flights_in_area()
   ↓
   5a. geocode_address() - cache lookup/geocode
   ↓
   5b. FlightRadar24 API call
   ↓
   5c. Filter by distance
   ↓
   5d. Parse and format
   ↓
6. services/activity_service.py :: log("FLIGHT", ...)
   ↓
7. routes/flights.py - return List[FlightData]
   ↓
8. FastAPI - serialize to JSON
   ↓
9. HTTP Response
```

## Dependency Injection Pattern

Routes use closure-based dependency injection:

```python
# In routes/flights.py
def setup_flight_routes(
    flight_service: FlightTrackerService,
    config_service: ConfigService,
    activity_service: ActivityLoggerService
):
    @router.get("/flights")
    async def get_flights():
        # Has access to all services via closure
        config = config_service.get_main_config()
        flights = flight_service.get_flights_in_area(...)
        return flights

    return router

# In main.py
flight_router = setup_flight_routes(
    flight_service,
    config_service,
    activity_service
)
app.include_router(flight_router)
```

**Benefits**:

- Services are easily testable (mock injection)
- Clear dependencies at route setup
- No global state
- Explicit rather than implicit

## Error Handling Strategy

### Service Layer

- Raise specific exceptions (ValueError, Exception)
- Include descriptive error messages
- Let routes handle HTTP concerns

### Route Layer

- Catch service exceptions
- Log errors via activity_service
- Convert to HTTPException with appropriate status code
- Return error details to client

Example:

```python
try:
    flights = flight_service.get_flights_in_area(...)
except ValueError as e:
    activity_service.log(ActivityCategory.ERROR, str(e))
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    activity_service.log(ActivityCategory.ERROR, str(e))
    raise HTTPException(status_code=500, detail=str(e))
```

## Configuration Management

### config.toml Structure

```toml
[main]
address = "San Francisco, CA"
search_radius_meters = 3000
max_flights = 20
max_elapsed_time = 1800

[logging]
max_activities = 500
categories = ["SYSTEM", "RADAR", "FLIGHT", "CONFIG", "ERROR", "INFO"]
```

### Loading Priority

1. Load from `config.toml` file
2. If load fails, use cached config
3. If no cache, use default config

### Update Flow

1. Client sends PUT /api/config
2. Route validates via Pydantic
3. Service updates config dict
4. Service saves to file
5. Service updates cache
6. Related services are notified (e.g., clear geocoding cache)

## Best Practices

### Adding New Endpoints

1. **Define Pydantic models** in `models/schemas.py`
2. **Create service method** in appropriate service
3. **Add route** in appropriate routes file
4. **Use dependency injection** via setup function
5. **Log activities** at key points
6. **Handle errors** appropriately

### Adding New Services

1. **Create service file** in `services/`
2. **Define class** with clear methods
3. **Export** from `services/__init__.py`
4. **Initialize** in `main.py`
5. **Inject** into relevant routes

### Testing Strategy

- **Unit test services** with mocked dependencies
- **Integration test routes** with test client
- **Mock external APIs** (FlightRadar24)
- **Test error cases** explicitly

## Common Patterns

### Service Initialization

```python
# In main.py
service = ServiceClass(dependencies)
```

### Route Setup

```python
# In routes/
def setup_routes(service_a, service_b):
    @router.get("/endpoint")
    async def handler():
        result = service_a.do_something()
        return result
    return router
```

### Activity Logging

```python
activity_service.log(
    ActivityCategory.FLIGHT,
    "Descriptive message",
    {"key": "value"}  # Optional details
)
```

### Configuration Access

```python
config = config_service.get_main_config()
value = config.get("key", default_value)
```

## Migration Notes

### From Original Structure

**Old**:

- Everything in `main.py`
- Direct imports of tracker and logger
- Global instances

**New**:

- Layered architecture
- Dependency injection
- No global state (except in main.py setup)
- Clear separation of concerns

### Backward Compatibility

The API endpoints remain identical. Only internal structure changed.

## Future Enhancements

Possible improvements to the architecture:

1. **Database Layer**: Add models/repositories for persistent storage
2. **Caching Layer**: Redis for flight data caching
3. **Testing**: Add `tests/` directory with pytest
4. **API Versioning**: Support `/api/v1/` and `/api/v2/`
5. **Authentication**: Add auth middleware and user management
6. **WebSockets**: Real-time flight updates
7. **Background Tasks**: Celery for periodic flight updates
8. **Metrics**: Prometheus integration for monitoring

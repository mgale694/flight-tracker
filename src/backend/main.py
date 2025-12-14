"""FastAPI backend entry point for Flight Tracker system."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import shared constants
from shared import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    CONFIG_FILE,
    CORS_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_ALLOW_HEADERS,
    MAX_ACTIVITIES
)

# Import services
from services import FlightTrackerService, ConfigService, ActivityLoggerService

# Import routes setup functions
from routes import (
    setup_flight_routes,
    setup_config_routes,
    setup_activity_routes,
    setup_system_routes
)

# Import utilities
from utils import AppLifecycle


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application instance
    """
    # Initialize FastAPI app
    app = FastAPI(
        title=APP_NAME,
        description=APP_DESCRIPTION,
        version=APP_VERSION
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_METHODS,
        allow_headers=CORS_ALLOW_HEADERS,
    )
    
    # Initialize services
    config_service = ConfigService(CONFIG_FILE)
    activity_service = ActivityLoggerService(max_activities=MAX_ACTIVITIES)
    flight_service = FlightTrackerService()
    
    # Initialize lifecycle manager
    lifecycle = AppLifecycle(config_service, activity_service, flight_service)
    
    # Register lifecycle events
    @app.on_event("startup")
    async def startup_event():
        """Execute startup tasks."""
        await lifecycle.startup()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Execute shutdown tasks."""
        await lifecycle.shutdown()
    
    # Setup and include routers
    system_router = setup_system_routes(activity_service)
    flight_router = setup_flight_routes(flight_service, config_service, activity_service)
    config_router = setup_config_routes(config_service, activity_service, flight_service)
    activity_router = setup_activity_routes(activity_service)
    
    app.include_router(system_router)
    app.include_router(flight_router)
    app.include_router(config_router)
    app.include_router(activity_router)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    from shared import DEFAULT_HOST, DEFAULT_PORT
    
    uvicorn.run(
        "main:app",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        reload=True,
        log_level="info"
    )

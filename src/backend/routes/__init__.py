"""Routes package for Flight Tracker API."""
from .flights import setup_flight_routes
from .config import setup_config_routes
from .activities import setup_activity_routes
from .system import setup_system_routes

__all__ = [
    "setup_flight_routes",
    "setup_config_routes",
    "setup_activity_routes",
    "setup_system_routes"
]

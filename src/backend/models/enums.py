"""Enums for the Flight Tracker API."""
from enum import Enum


class ActivityCategory(str, Enum):
    """Activity log categories."""
    SYSTEM = "SYSTEM"
    RADAR = "RADAR"
    FLIGHT = "FLIGHT"
    CONFIG = "CONFIG"
    ERROR = "ERROR"
    INFO = "INFO"


class APIStatus(str, Enum):
    """API status values."""
    RUNNING = "running"
    HEALTHY = "healthy"
    ERROR = "error"

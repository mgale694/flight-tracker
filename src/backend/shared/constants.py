"""Shared constants and configuration for Flight Tracker API."""
from pathlib import Path

# Application metadata
APP_NAME = "Flight Tracker API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Backend API for tracking flights in a specific geographic area"

# File paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_FILE = BASE_DIR / "config.toml"

# Server configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000

# CORS configuration
CORS_ORIGINS = ["*"]  # In production, specify actual origins
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Logging configuration
MAX_ACTIVITIES = 500

"""Pydantic models and schemas for the Flight Tracker API."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FlightData(BaseModel):
    """Flight data model."""
    id: str
    callsign: str
    registration: str
    aircraft: str
    airline: str
    origin: str
    destination: str
    altitude: int
    speed: int
    heading: int
    latitude: float
    longitude: float
    distance: float
    timestamp: str


class ConfigUpdate(BaseModel):
    """Model for configuration updates."""
    address: Optional[str] = None
    search_radius_meters: Optional[int] = Field(None, ge=100, le=50000)
    max_flights: Optional[int] = Field(None, ge=1, le=100)
    max_elapsed_time: Optional[int] = Field(None, ge=60, le=7200)


class ActivityLog(BaseModel):
    """Activity log entry model."""
    timestamp: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str


class APIResponse(BaseModel):
    """Generic API response model."""
    name: str
    version: str
    status: str


class MessageResponse(BaseModel):
    """Simple message response model."""
    message: str

"""Pydantic models and schemas for the Flight Tracker API."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class FlightData(BaseModel):
    """Flight data model."""
    id: str
    callsign: str
    registration: str
    aircraft: str
    airline: str
    origin: str
    destination: str
    origin_name: Optional[str] = None
    destination_name: Optional[str] = None
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
    display_hold_time: Optional[int] = Field(None, ge=5, le=300)
    display_fields: Optional[list[str]] = Field(None, description="List of fields to display on e-ink (FROM, TO, AIRLINE, MODEL, REG, ROUTE)")
    bearing_degrees: Optional[float] = Field(None, ge=0, lt=360)
    field_of_view_degrees: Optional[float] = Field(None, gt=0, le=360)
    min_distance_km: Optional[float] = Field(None, ge=0, le=50)
    max_distance_km: Optional[float] = Field(None, gt=0, le=50)
    min_altitude_ft: Optional[int] = Field(None, ge=-1000, le=60000)
    max_altitude_ft: Optional[int] = Field(None, ge=-1000, le=60000)


class PairDeviceRequest(BaseModel):
    """Prototype pairing request made after local development sign-in."""

    pairing_code: str = Field(min_length=4, max_length=32)


class PairingStatus(BaseModel):
    """Safe public pairing state; never includes the pairing code."""

    device_id: str
    paired: bool
    setup_url: str
    authentication_mode: str = "development"


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

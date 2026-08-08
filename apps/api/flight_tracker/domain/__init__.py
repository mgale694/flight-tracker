"""Framework-independent Flight Tracker domain."""

from .errors import (
    DomainValidationError,
    FlightTrackerError,
    ProviderError,
    ProviderRateLimited,
    ProviderResponseInvalid,
    ProviderTimeout,
    ProviderUnavailable,
    ViewingZoneNotConfigured,
)
from .models import (
    AircraftState,
    Device,
    DeviceStatus,
    DisplayAircraft,
    DisplaySnapshot,
    FlightInformation,
    SnapshotStatus,
    User,
    ViewingZone,
    VisibleAircraft,
)

__all__ = [
    "AircraftState",
    "Device",
    "DeviceStatus",
    "DisplayAircraft",
    "DisplaySnapshot",
    "DomainValidationError",
    "FlightInformation",
    "FlightTrackerError",
    "ProviderError",
    "ProviderRateLimited",
    "ProviderResponseInvalid",
    "ProviderTimeout",
    "ProviderUnavailable",
    "SnapshotStatus",
    "User",
    "ViewingZone",
    "ViewingZoneNotConfigured",
    "VisibleAircraft",
]

"""Typed, provider-neutral domain models.

These models deliberately avoid FastAPI, database, and provider SDK imports.
Transport schemas and SQLAlchemy records may map to them at application
boundaries without making the domain depend on those technologies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from .errors import DomainValidationError


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainValidationError(f"{field_name} must be timezone-aware")


def _validate_coordinates(latitude: float, longitude: float) -> None:
    if not -90.0 <= latitude <= 90.0:
        raise DomainValidationError("latitude must be between -90 and 90")
    if not -180.0 <= longitude <= 180.0:
        raise DomainValidationError("longitude must be between -180 and 180")


class DeviceStatus(StrEnum):
    """Lifecycle state recorded for a physical display."""

    UNPAIRED = "unpaired"
    ONLINE = "online"
    OFFLINE = "offline"
    REVOKED = "revoked"


class SnapshotStatus(StrEnum):
    """Every semantic state understood by display clients."""

    CONFIGURATION_REQUIRED = "configuration_required"
    SCANNING = "scanning"
    AIRCRAFT_VISIBLE = "aircraft_visible"
    MULTIPLE_AIRCRAFT = "multiple_aircraft"
    NO_AIRCRAFT = "no_aircraft"
    OFFLINE = "offline"
    PROVIDER_UNAVAILABLE = "provider_unavailable"


@dataclass(frozen=True, slots=True)
class User:
    """Minimal account owner domain entity."""

    id: str
    email: str
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise DomainValidationError("user id must not be empty")
        if "@" not in self.email:
            raise DomainValidationError("email must be a plausible address")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")


@dataclass(frozen=True, slots=True)
class Device:
    """A physical display owned independently from its credential."""

    id: str
    public_id: str
    owner_id: str | None
    name: str
    device_type: str
    hardware_revision: str | None = None
    firmware_version: str | None = None
    client_version: str | None = None
    status: DeviceStatus = DeviceStatus.UNPAIRED
    last_seen_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.public_id.strip():
            raise DomainValidationError("device ids must not be empty")
        if not self.name.strip() or not self.device_type.strip():
            raise DomainValidationError("device name and type must not be empty")
        if self.last_seen_at is not None:
            _require_aware(self.last_seen_at, "last_seen_at")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")


@dataclass(frozen=True, slots=True)
class ViewingZone:
    """The section of sky visible from a device's window."""

    device_id: str
    name: str
    latitude: float
    longitude: float
    bearing_degrees: float
    field_of_view_degrees: float
    min_distance_km: float = 0.0
    max_distance_km: float = 35.0
    min_altitude_ft: int | None = None
    max_altitude_ft: int | None = None
    enabled: bool = True
    id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.device_id.strip() or not self.name.strip():
            raise DomainValidationError("viewing zone device id and name must not be empty")
        _validate_coordinates(self.latitude, self.longitude)
        if not 0.0 <= self.bearing_degrees < 360.0:
            raise DomainValidationError("bearing_degrees must be at least 0 and less than 360")
        if not 0.0 < self.field_of_view_degrees <= 360.0:
            raise DomainValidationError(
                "field_of_view_degrees must be greater than 0 and at most 360"
            )
        if self.min_distance_km < 0.0:
            raise DomainValidationError("min_distance_km must not be negative")
        if self.max_distance_km <= 0.0:
            raise DomainValidationError("max_distance_km must be positive")
        if self.min_distance_km > self.max_distance_km:
            raise DomainValidationError("min_distance_km must not exceed max_distance_km")
        if (
            self.min_altitude_ft is not None
            and self.max_altitude_ft is not None
            and self.min_altitude_ft > self.max_altitude_ft
        ):
            raise DomainValidationError("min_altitude_ft must not exceed max_altitude_ft")
        _require_aware(self.created_at, "created_at")
        _require_aware(self.updated_at, "updated_at")


@dataclass(frozen=True, slots=True)
class AircraftState:
    """Normalised, short-lived live aircraft state."""

    provider: str
    provider_aircraft_id: str
    latitude: float
    longitude: float
    observed_at: datetime
    icao_hex: str | None = None
    callsign: str | None = None
    registration: str | None = None
    altitude_ft: int | None = None
    ground_speed_knots: float | None = None
    vertical_speed_fpm: int | None = None
    track_degrees: float | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip() or not self.provider_aircraft_id.strip():
            raise DomainValidationError("provider and provider_aircraft_id must not be empty")
        _validate_coordinates(self.latitude, self.longitude)
        _require_aware(self.observed_at, "observed_at")
        if self.ground_speed_knots is not None and self.ground_speed_knots < 0.0:
            raise DomainValidationError("ground_speed_knots must not be negative")
        if self.track_degrees is not None and not 0.0 <= self.track_degrees < 360.0:
            raise DomainValidationError("track_degrees must be at least 0 and less than 360")


@dataclass(frozen=True, slots=True)
class FlightInformation:
    """Optional, longer-lived provider enrichment."""

    provider: str
    enriched_at: datetime
    callsign: str | None = None
    flight_number: str | None = None
    airline_name: str | None = None
    airline_iata: str | None = None
    airline_icao: str | None = None
    registration: str | None = None
    aircraft_type_code: str | None = None
    aircraft_type_name: str | None = None
    origin_airport: str | None = None
    destination_airport: str | None = None
    scheduled_departure: datetime | None = None
    scheduled_arrival: datetime | None = None

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise DomainValidationError("provider must not be empty")
        _require_aware(self.enriched_at, "enriched_at")
        if self.scheduled_departure is not None:
            _require_aware(self.scheduled_departure, "scheduled_departure")
        if self.scheduled_arrival is not None:
            _require_aware(self.scheduled_arrival, "scheduled_arrival")


@dataclass(frozen=True, slots=True)
class VisibleAircraft:
    """Explainable result of evaluating live state against a viewing zone."""

    aircraft: AircraftState
    flight_information: FlightInformation | None
    distance_km: float
    bearing_degrees: float
    relative_bearing_degrees: float
    inside_view: bool
    relevance_score: float = 0.0


@dataclass(frozen=True, slots=True)
class DisplayAircraft:
    """Small semantic description of the primary aircraft for a display."""

    flight_number: str | None
    callsign: str | None
    registration: str | None
    aircraft_type: str | None
    origin: str | None
    destination: str | None
    altitude_ft: int | None
    distance_km: float
    bearing_degrees: float


@dataclass(frozen=True, slots=True)
class DisplaySnapshot:
    """Stable, screen-size-independent hardware contract."""

    generated_at: datetime
    status: SnapshotStatus
    refresh_after_seconds: int
    primary: DisplayAircraft | None = None
    secondary_count: int = 0

    def __post_init__(self) -> None:
        _require_aware(self.generated_at, "generated_at")
        if self.refresh_after_seconds <= 0:
            raise DomainValidationError("refresh_after_seconds must be positive")
        if self.secondary_count < 0:
            raise DomainValidationError("secondary_count must not be negative")
        aircraft_states = {
            SnapshotStatus.AIRCRAFT_VISIBLE,
            SnapshotStatus.MULTIPLE_AIRCRAFT,
        }
        if self.status in aircraft_states and self.primary is None:
            raise DomainValidationError("aircraft-visible snapshots require primary content")
        if self.status not in aircraft_states and self.primary is not None:
            raise DomainValidationError("non-aircraft snapshots must not include primary content")
        if self.status is SnapshotStatus.MULTIPLE_AIRCRAFT and self.secondary_count < 1:
            raise DomainValidationError("multiple-aircraft snapshots require a secondary aircraft")
        if self.status is SnapshotStatus.AIRCRAFT_VISIBLE and self.secondary_count != 0:
            raise DomainValidationError(
                "single-aircraft snapshots cannot include a secondary count"
            )

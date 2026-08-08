"""Provider contract and capability model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from flight_tracker.domain.errors import DomainValidationError
from flight_tracker.domain.models import AircraftState, FlightInformation


class ProviderCapability(StrEnum):
    LIVE_POSITION = "live_position"
    ALTITUDE = "altitude"
    GROUND_SPEED = "ground_speed"
    HEADING = "heading"
    REGISTRATION = "registration"
    AIRCRAFT_TYPE = "aircraft_type"
    AIRLINE = "airline"
    ROUTE = "route"
    AIRPORTS = "airports"
    SCHEDULE = "schedule"
    HISTORY = "history"


@dataclass(frozen=True, slots=True)
class GeographicArea:
    """Provider-neutral circular live-state query area."""

    center_latitude: float
    center_longitude: float
    radius_km: float

    def __post_init__(self) -> None:
        if not -90.0 <= self.center_latitude <= 90.0:
            raise DomainValidationError("center_latitude must be between -90 and 90")
        if not -180.0 <= self.center_longitude <= 180.0:
            raise DomainValidationError("center_longitude must be between -180 and 180")
        if self.radius_km <= 0.0:
            raise DomainValidationError("radius_km must be positive")


@runtime_checkable
class FlightDataProvider(Protocol):
    """Behaviour required by snapshot and live-aircraft services."""

    @property
    def name(self) -> str: ...

    @property
    def capabilities(self) -> frozenset[ProviderCapability]: ...

    async def get_aircraft(self, area: GeographicArea) -> list[AircraftState]: ...

    async def get_flight_information(self, aircraft: AircraftState) -> FlightInformation | None: ...

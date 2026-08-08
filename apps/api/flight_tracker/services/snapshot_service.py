"""Application service for producing the stable display contract."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from flight_tracker.domain.errors import ProviderError
from flight_tracker.domain.geometry import visible_aircraft
from flight_tracker.domain.models import (
    DisplayAircraft,
    DisplaySnapshot,
    FlightInformation,
    SnapshotStatus,
    ViewingZone,
    VisibleAircraft,
)
from flight_tracker.domain.ranking import rank_visible_aircraft
from flight_tracker.providers.base import FlightDataProvider, GeographicArea


class DeviceSnapshotService:
    """Own the provider → visibility → ranking → enrichment decision flow."""

    def __init__(
        self,
        provider: FlightDataProvider,
        *,
        refresh_after_seconds: int = 30,
        degraded_refresh_after_seconds: int = 60,
        configuration_refresh_after_seconds: int = 300,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if (
            min(
                refresh_after_seconds,
                degraded_refresh_after_seconds,
                configuration_refresh_after_seconds,
            )
            <= 0
        ):
            raise ValueError("snapshot refresh intervals must be positive")
        self.provider = provider
        self.refresh_after_seconds = refresh_after_seconds
        self.degraded_refresh_after_seconds = degraded_refresh_after_seconds
        self.configuration_refresh_after_seconds = configuration_refresh_after_seconds
        self.clock = clock or (lambda: datetime.now(UTC))

    async def generate(self, viewing_zone: ViewingZone | None) -> DisplaySnapshot:
        generated_at = self.clock()
        if viewing_zone is None or not viewing_zone.enabled:
            return DisplaySnapshot(
                generated_at=generated_at,
                status=SnapshotStatus.CONFIGURATION_REQUIRED,
                refresh_after_seconds=self.configuration_refresh_after_seconds,
            )

        area = GeographicArea(
            center_latitude=viewing_zone.latitude,
            center_longitude=viewing_zone.longitude,
            radius_km=viewing_zone.max_distance_km,
        )
        try:
            states = await self.provider.get_aircraft(area)
        except ProviderError:
            return DisplaySnapshot(
                generated_at=generated_at,
                status=SnapshotStatus.PROVIDER_UNAVAILABLE,
                refresh_after_seconds=self.degraded_refresh_after_seconds,
            )

        ranked = rank_visible_aircraft(visible_aircraft(states, viewing_zone), viewing_zone)
        if not ranked:
            return DisplaySnapshot(
                generated_at=generated_at,
                status=SnapshotStatus.NO_AIRCRAFT,
                refresh_after_seconds=self.refresh_after_seconds,
            )

        primary_match = ranked[0]
        enrichment = await self._get_optional_enrichment(primary_match)
        status = (
            SnapshotStatus.MULTIPLE_AIRCRAFT if len(ranked) > 1 else SnapshotStatus.AIRCRAFT_VISIBLE
        )
        return DisplaySnapshot(
            generated_at=generated_at,
            status=status,
            refresh_after_seconds=self.refresh_after_seconds,
            primary=self._display_aircraft(primary_match, enrichment),
            secondary_count=len(ranked) - 1,
        )

    async def _get_optional_enrichment(self, match: VisibleAircraft) -> FlightInformation | None:
        try:
            return await self.provider.get_flight_information(match.aircraft)
        except ProviderError:
            # Live state remains useful when optional enrichment is degraded.
            return None

    @staticmethod
    def _display_aircraft(
        match: VisibleAircraft, enrichment: FlightInformation | None
    ) -> DisplayAircraft:
        aircraft = match.aircraft
        return DisplayAircraft(
            flight_number=enrichment.flight_number if enrichment else None,
            callsign=(enrichment.callsign if enrichment else None) or aircraft.callsign,
            registration=(enrichment.registration if enrichment else None) or aircraft.registration,
            aircraft_type=(
                (enrichment.aircraft_type_name or enrichment.aircraft_type_code)
                if enrichment
                else None
            ),
            origin=enrichment.origin_airport if enrichment else None,
            destination=enrichment.destination_airport if enrichment else None,
            altitude_ft=aircraft.altitude_ft,
            distance_km=round(match.distance_km, 1),
            bearing_degrees=round(match.bearing_degrees, 1),
        )

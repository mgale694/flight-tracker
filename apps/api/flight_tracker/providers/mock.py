"""Seeded, moving flight data for local development and contract tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from random import Random

from flight_tracker.domain.errors import ProviderRateLimited, ProviderTimeout
from flight_tracker.domain.geometry import destination_point
from flight_tracker.domain.models import AircraftState, FlightInformation

from .base import GeographicArea, ProviderCapability


class MockScenario(StrEnum):
    NORMAL = "normal"
    EMPTY = "empty"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"


class MockFlightDataProvider:
    """Deterministic provider whose aircraft move once per live-state query.

    With a north-facing 80-degree view, MOCK001 enters the sector, crosses the
    centre, and later leaves it. MOCK002 approaches the sector more slowly,
    MOCK003 remains in the southern sky, and MOCK004 has deliberately partial
    live and enrichment data.
    """

    _capabilities = frozenset(
        {
            ProviderCapability.LIVE_POSITION,
            ProviderCapability.ALTITUDE,
            ProviderCapability.GROUND_SPEED,
            ProviderCapability.HEADING,
            ProviderCapability.REGISTRATION,
            ProviderCapability.AIRCRAFT_TYPE,
            ProviderCapability.AIRLINE,
            ProviderCapability.ROUTE,
            ProviderCapability.AIRPORTS,
        }
    )

    def __init__(
        self,
        *,
        seed: int = 20260808,
        scenario: MockScenario = MockScenario.NORMAL,
        start_time: datetime = datetime(2026, 8, 8, 12, 0, tzinfo=UTC),
    ) -> None:
        if start_time.tzinfo is None or start_time.utcoffset() is None:
            raise ValueError("start_time must be timezone-aware")
        self.seed = seed
        self.scenario = scenario
        self.start_time = start_time
        self.tick = 0

    @property
    def name(self) -> str:
        return "mock"

    @property
    def capabilities(self) -> frozenset[ProviderCapability]:
        return self._capabilities

    def reset(self) -> None:
        """Return the simulation to its first deterministic frame."""

        self.tick = 0

    async def get_aircraft(self, area: GeographicArea) -> list[AircraftState]:
        if self.scenario is MockScenario.TIMEOUT:
            raise ProviderTimeout("mock provider timed out")
        if self.scenario is MockScenario.RATE_LIMITED:
            raise ProviderRateLimited("mock provider rate limit reached", retry_after_seconds=60)
        if self.scenario is MockScenario.EMPTY:
            self.tick += 1
            return []

        current_tick = self.tick
        self.tick += 1
        rng = Random(self.seed)
        distance_adjustment = rng.uniform(-0.25, 0.25)
        observed_at = self.start_time + timedelta(seconds=current_tick * 30)

        definitions = (
            ("MOCK001", 300.0 + current_tick * 15.0, 8.0 + distance_adjustment),
            ("MOCK002", 60.0 - current_tick * 5.0, 14.0 - distance_adjustment),
            ("MOCK003", 180.0 + current_tick * 2.0, 22.0),
            ("MOCK004", 345.0 + current_tick * 4.0, 30.0),
        )

        states: list[AircraftState] = []
        for index, (identifier, bearing, distance) in enumerate(definitions, start=1):
            if distance > area.radius_km:
                continue
            latitude, longitude = destination_point(
                area.center_latitude,
                area.center_longitude,
                bearing % 360.0,
                distance,
            )
            is_partial = identifier == "MOCK004"
            states.append(
                AircraftState(
                    provider=self.name,
                    provider_aircraft_id=identifier,
                    icao_hex=f"A0000{index}",
                    callsign=None if is_partial else f"SKY{100 + index}",
                    registration=None if is_partial else f"G-MK{index:02d}",
                    latitude=latitude,
                    longitude=longitude,
                    altitude_ft=None if is_partial else 12_000 + index * 4_000,
                    ground_speed_knots=None if is_partial else 300.0 + index * 12.0,
                    vertical_speed_fpm=None if is_partial else (-400 + index * 150),
                    track_degrees=(bearing + 95.0) % 360.0,
                    observed_at=observed_at,
                )
            )
        return states

    async def get_flight_information(self, aircraft: AircraftState) -> FlightInformation | None:
        if self.scenario is MockScenario.TIMEOUT:
            raise ProviderTimeout("mock enrichment timed out")
        if self.scenario is MockScenario.RATE_LIMITED:
            raise ProviderRateLimited("mock provider rate limit reached", retry_after_seconds=60)
        if aircraft.provider_aircraft_id == "MOCK004":
            return FlightInformation(
                provider=self.name,
                enriched_at=aircraft.observed_at,
                aircraft_type_code="A20N",
            )

        number = int(aircraft.provider_aircraft_id.removeprefix("MOCK"))
        return FlightInformation(
            provider=self.name,
            enriched_at=aircraft.observed_at,
            callsign=aircraft.callsign,
            flight_number=f"FT{280 + number}",
            airline_name="Window Air",
            airline_iata="FT",
            airline_icao="SKY",
            registration=aircraft.registration,
            aircraft_type_code="A388" if number == 1 else "B789",
            aircraft_type_name="Airbus A380-800" if number == 1 else "Boeing 787-9",
            origin_airport="LHR",
            destination_airport="JFK" if number == 1 else "AMS",
        )

from datetime import UTC, datetime
from unittest import IsolatedAsyncioTestCase

from flight_tracker.domain.errors import ProviderTimeout
from flight_tracker.domain.geometry import destination_point
from flight_tracker.domain.models import AircraftState, SnapshotStatus, ViewingZone
from flight_tracker.providers import GeographicArea, MockFlightDataProvider, MockScenario
from flight_tracker.providers.base import ProviderCapability
from flight_tracker.services import DeviceSnapshotService

NOW = datetime(2026, 8, 8, 14, 30, tzinfo=UTC)


class LiveOnlyProvider:
    name = "live-only"
    capabilities = frozenset({ProviderCapability.LIVE_POSITION})

    async def get_aircraft(self, area: GeographicArea) -> list[AircraftState]:
        latitude, longitude = destination_point(
            area.center_latitude,
            area.center_longitude,
            0.0,
            5.0,
        )
        return [
            AircraftState(
                provider=self.name,
                provider_aircraft_id="LIVE001",
                callsign="RAW123",
                latitude=latitude,
                longitude=longitude,
                altitude_ft=18_000,
                observed_at=NOW,
            )
        ]

    async def get_flight_information(self, aircraft: AircraftState):
        raise ProviderTimeout("optional enrichment timed out")


class DeviceSnapshotServiceTests(IsolatedAsyncioTestCase):
    def make_zone(self, **overrides: object) -> ViewingZone:
        values: dict[str, object] = {
            "device_id": "device-1",
            "name": "North window",
            "latitude": 51.477,
            "longitude": -0.210,
            "bearing_degrees": 0.0,
            "field_of_view_degrees": 80.0,
            "max_distance_km": 35.0,
        }
        values.update(overrides)
        return ViewingZone(**values)  # type: ignore[arg-type]

    def service(self, provider) -> DeviceSnapshotService:
        return DeviceSnapshotService(provider, clock=lambda: NOW)

    async def test_missing_or_disabled_zone_requires_configuration(self) -> None:
        service = self.service(MockFlightDataProvider())

        missing = await service.generate(None)
        disabled = await service.generate(self.make_zone(enabled=False))

        self.assertEqual(missing.status, SnapshotStatus.CONFIGURATION_REQUIRED)
        self.assertEqual(disabled.status, SnapshotStatus.CONFIGURATION_REQUIRED)
        self.assertEqual(missing.refresh_after_seconds, 300)

    async def test_empty_sky_has_explicit_no_aircraft_state(self) -> None:
        service = self.service(MockFlightDataProvider(scenario=MockScenario.EMPTY))

        snapshot = await service.generate(self.make_zone())

        self.assertEqual(snapshot.status, SnapshotStatus.NO_AIRCRAFT)
        self.assertIsNone(snapshot.primary)

    async def test_provider_failure_has_degraded_state(self) -> None:
        service = self.service(MockFlightDataProvider(scenario=MockScenario.TIMEOUT))

        snapshot = await service.generate(self.make_zone())

        self.assertEqual(snapshot.status, SnapshotStatus.PROVIDER_UNAVAILABLE)
        self.assertEqual(snapshot.refresh_after_seconds, 60)

    async def test_complete_enrichment_populates_display_contract(self) -> None:
        service = self.service(MockFlightDataProvider())
        zone = self.make_zone(bearing_degrees=300.0, field_of_view_degrees=10.0)

        snapshot = await service.generate(zone)

        self.assertEqual(snapshot.status, SnapshotStatus.AIRCRAFT_VISIBLE)
        self.assertIsNotNone(snapshot.primary)
        assert snapshot.primary is not None
        self.assertEqual(snapshot.primary.flight_number, "FT281")
        self.assertEqual(snapshot.primary.aircraft_type, "Airbus A380-800")
        self.assertEqual(snapshot.primary.origin, "LHR")
        self.assertEqual(snapshot.primary.destination, "JFK")

    async def test_multiple_visible_aircraft_reports_secondary_count(self) -> None:
        provider = MockFlightDataProvider()
        service = self.service(provider)
        zone = self.make_zone()
        await service.generate(zone)
        await service.generate(zone)

        snapshot = await service.generate(zone)

        self.assertEqual(snapshot.status, SnapshotStatus.MULTIPLE_AIRCRAFT)
        self.assertGreaterEqual(snapshot.secondary_count, 1)

    async def test_enrichment_failure_preserves_useful_live_state(self) -> None:
        service = self.service(LiveOnlyProvider())

        snapshot = await service.generate(self.make_zone())

        self.assertEqual(snapshot.status, SnapshotStatus.AIRCRAFT_VISIBLE)
        self.assertIsNotNone(snapshot.primary)
        assert snapshot.primary is not None
        self.assertEqual(snapshot.primary.callsign, "RAW123")
        self.assertEqual(snapshot.primary.altitude_ft, 18_000)
        self.assertIsNone(snapshot.primary.flight_number)
        self.assertIsNone(snapshot.primary.origin)

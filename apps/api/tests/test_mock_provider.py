from unittest import IsolatedAsyncioTestCase

from flight_tracker.domain.errors import ProviderRateLimited, ProviderTimeout
from flight_tracker.domain.geometry import evaluate_aircraft
from flight_tracker.domain.models import ViewingZone
from flight_tracker.providers import GeographicArea, MockFlightDataProvider, MockScenario


class MockProviderTests(IsolatedAsyncioTestCase):
    area = GeographicArea(center_latitude=51.477, center_longitude=-0.210, radius_km=35.0)

    async def test_same_seed_produces_identical_moving_frames(self) -> None:
        first = MockFlightDataProvider(seed=42)
        second = MockFlightDataProvider(seed=42)

        self.assertEqual(await first.get_aircraft(self.area), await second.get_aircraft(self.area))
        self.assertEqual(await first.get_aircraft(self.area), await second.get_aircraft(self.area))

    async def test_aircraft_enters_and_leaves_north_facing_sector(self) -> None:
        provider = MockFlightDataProvider()
        zone = ViewingZone(
            device_id="device-1",
            name="North window",
            latitude=self.area.center_latitude,
            longitude=self.area.center_longitude,
            bearing_degrees=0.0,
            field_of_view_degrees=80.0,
            max_distance_km=self.area.radius_km,
        )
        mock001_visibility: list[bool] = []

        for _ in range(8):
            frame = await provider.get_aircraft(self.area)
            mock001 = next(item for item in frame if item.provider_aircraft_id == "MOCK001")
            mock001_visibility.append(evaluate_aircraft(mock001, zone).inside_view)

        self.assertFalse(mock001_visibility[0])
        self.assertTrue(mock001_visibility[2])
        self.assertFalse(mock001_visibility[7])

    async def test_partial_enrichment_does_not_fabricate_fields(self) -> None:
        provider = MockFlightDataProvider()
        frame = await provider.get_aircraft(self.area)
        partial = next(item for item in frame if item.provider_aircraft_id == "MOCK004")

        enrichment = await provider.get_flight_information(partial)

        self.assertIsNotNone(enrichment)
        assert enrichment is not None
        self.assertEqual(enrichment.aircraft_type_code, "A20N")
        self.assertIsNone(enrichment.flight_number)
        self.assertIsNone(enrichment.origin_airport)

    async def test_empty_scenario_advances_without_aircraft(self) -> None:
        provider = MockFlightDataProvider(scenario=MockScenario.EMPTY)

        self.assertEqual(await provider.get_aircraft(self.area), [])
        self.assertEqual(provider.tick, 1)

    async def test_timeout_and_rate_limit_are_explicit(self) -> None:
        timeout_provider = MockFlightDataProvider(scenario=MockScenario.TIMEOUT)
        limited_provider = MockFlightDataProvider(scenario=MockScenario.RATE_LIMITED)

        with self.assertRaises(ProviderTimeout):
            await timeout_provider.get_aircraft(self.area)
        with self.assertRaises(ProviderRateLimited) as raised:
            await limited_provider.get_aircraft(self.area)
        self.assertEqual(raised.exception.retry_after_seconds, 60)

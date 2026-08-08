from datetime import UTC, datetime
from unittest import TestCase

from flight_tracker.domain.geometry import (
    angular_difference_degrees,
    destination_point,
    evaluate_aircraft,
    great_circle_distance_km,
    initial_bearing_degrees,
)
from flight_tracker.domain.models import AircraftState, ViewingZone

NOW = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


class VisibleSkyGeometryTests(TestCase):
    latitude = 51.477
    longitude = -0.210

    def make_zone(self, **overrides: object) -> ViewingZone:
        values: dict[str, object] = {
            "device_id": "device-1",
            "name": "Test window",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "bearing_degrees": 0.0,
            "field_of_view_degrees": 80.0,
            "min_distance_km": 0.0,
            "max_distance_km": 35.0,
        }
        values.update(overrides)
        return ViewingZone(**values)  # type: ignore[arg-type]

    def aircraft_at(
        self, bearing: float, distance_km: float = 10.0, altitude_ft: int | None = 20_000
    ) -> AircraftState:
        latitude, longitude = destination_point(
            self.latitude,
            self.longitude,
            bearing,
            distance_km,
        )
        return AircraftState(
            provider="test",
            provider_aircraft_id=f"aircraft-{bearing}-{distance_km}",
            latitude=latitude,
            longitude=longitude,
            altitude_ft=altitude_ft,
            observed_at=NOW,
        )

    def test_distance_and_all_cardinal_intercardinal_bearings(self) -> None:
        for expected_bearing in range(0, 360, 45):
            with self.subTest(bearing=expected_bearing):
                aircraft = self.aircraft_at(float(expected_bearing), 12.5)
                distance = great_circle_distance_km(
                    self.latitude,
                    self.longitude,
                    aircraft.latitude,
                    aircraft.longitude,
                )
                bearing = initial_bearing_degrees(
                    self.latitude,
                    self.longitude,
                    aircraft.latitude,
                    aircraft.longitude,
                )
                self.assertAlmostEqual(distance, 12.5, places=6)
                self.assertAlmostEqual(bearing, expected_bearing, places=6)

    def test_exact_viewing_zone_centre_is_visible(self) -> None:
        zone = self.make_zone(bearing_degrees=125.0)

        match = evaluate_aircraft(self.aircraft_at(125.0), zone)

        self.assertTrue(match.inside_view)
        self.assertAlmostEqual(match.relative_bearing_degrees, 0.0, places=6)

    def test_field_of_view_boundary_is_inclusive(self) -> None:
        zone = self.make_zone(field_of_view_degrees=80.0)

        self.assertTrue(evaluate_aircraft(self.aircraft_at(40.0), zone).inside_view)

    def test_just_outside_field_of_view_is_excluded(self) -> None:
        zone = self.make_zone(field_of_view_degrees=80.0)

        self.assertFalse(evaluate_aircraft(self.aircraft_at(40.01), zone).inside_view)

    def test_sector_crossing_north_handles_zero_and_360(self) -> None:
        zone = self.make_zone(bearing_degrees=350.0, field_of_view_degrees=40.0)

        match = evaluate_aircraft(self.aircraft_at(10.0), zone)

        self.assertTrue(match.inside_view)
        self.assertAlmostEqual(match.relative_bearing_degrees, 20.0, places=6)
        self.assertEqual(angular_difference_degrees(350.0, 10.0), 20.0)

    def test_minimum_and_maximum_distance_boundaries_are_inclusive(self) -> None:
        zone = self.make_zone(min_distance_km=5.0, max_distance_km=20.0)

        self.assertTrue(evaluate_aircraft(self.aircraft_at(0.0, 5.0), zone).inside_view)
        self.assertTrue(evaluate_aircraft(self.aircraft_at(0.0, 20.0), zone).inside_view)
        self.assertFalse(evaluate_aircraft(self.aircraft_at(0.0, 4.9), zone).inside_view)
        self.assertFalse(evaluate_aircraft(self.aircraft_at(0.0, 20.1), zone).inside_view)

    def test_minimum_and_maximum_altitude_boundaries_are_inclusive(self) -> None:
        zone = self.make_zone(min_altitude_ft=1_000, max_altitude_ft=45_000)

        self.assertTrue(
            evaluate_aircraft(self.aircraft_at(0.0, altitude_ft=1_000), zone).inside_view
        )
        self.assertTrue(
            evaluate_aircraft(self.aircraft_at(0.0, altitude_ft=45_000), zone).inside_view
        )
        self.assertFalse(
            evaluate_aircraft(self.aircraft_at(0.0, altitude_ft=999), zone).inside_view
        )
        self.assertFalse(
            evaluate_aircraft(self.aircraft_at(0.0, altitude_ft=45_001), zone).inside_view
        )

    def test_missing_altitude_requires_an_unconstrained_zone(self) -> None:
        unconstrained = self.make_zone()
        constrained = self.make_zone(min_altitude_ft=1_000)
        aircraft = self.aircraft_at(0.0, altitude_ft=None)

        self.assertTrue(evaluate_aircraft(aircraft, unconstrained).inside_view)
        self.assertFalse(evaluate_aircraft(aircraft, constrained).inside_view)

    def test_extremely_wide_field_of_view_includes_opposite_direction(self) -> None:
        zone = self.make_zone(field_of_view_degrees=360.0)

        self.assertTrue(evaluate_aircraft(self.aircraft_at(180.0), zone).inside_view)

    def test_narrow_field_of_view_excludes_small_offset(self) -> None:
        zone = self.make_zone(field_of_view_degrees=2.0)

        self.assertTrue(evaluate_aircraft(self.aircraft_at(1.0), zone).inside_view)
        self.assertFalse(evaluate_aircraft(self.aircraft_at(1.01), zone).inside_view)

    def test_disabled_zone_never_matches(self) -> None:
        zone = self.make_zone(enabled=False)

        self.assertFalse(evaluate_aircraft(self.aircraft_at(0.0), zone).inside_view)

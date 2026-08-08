from datetime import UTC, datetime
from unittest import TestCase

from flight_tracker.domain.errors import DomainValidationError
from flight_tracker.domain.models import (
    AircraftState,
    DisplayAircraft,
    DisplaySnapshot,
    SnapshotStatus,
    ViewingZone,
)

NOW = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


class ViewingZoneValidationTests(TestCase):
    def make_zone(self, **overrides: object) -> ViewingZone:
        values: dict[str, object] = {
            "device_id": "device-1",
            "name": "Living Room Window",
            "latitude": 51.477,
            "longitude": -0.210,
            "bearing_degrees": 125.0,
            "field_of_view_degrees": 80.0,
            "min_distance_km": 0.0,
            "max_distance_km": 35.0,
        }
        values.update(overrides)
        return ViewingZone(**values)  # type: ignore[arg-type]

    def test_accepts_valid_zone(self) -> None:
        zone = self.make_zone(min_altitude_ft=1_000, max_altitude_ft=45_000)

        self.assertEqual(zone.bearing_degrees, 125.0)

    def test_rejects_invalid_coordinates(self) -> None:
        with self.assertRaisesRegex(DomainValidationError, "latitude"):
            self.make_zone(latitude=91.0)
        with self.assertRaisesRegex(DomainValidationError, "longitude"):
            self.make_zone(longitude=-181.0)

    def test_rejects_360_degree_bearing(self) -> None:
        with self.assertRaisesRegex(DomainValidationError, "bearing_degrees"):
            self.make_zone(bearing_degrees=360.0)

    def test_rejects_invalid_distance_order(self) -> None:
        with self.assertRaisesRegex(DomainValidationError, "min_distance_km"):
            self.make_zone(min_distance_km=20.0, max_distance_km=10.0)

    def test_rejects_invalid_altitude_order(self) -> None:
        with self.assertRaisesRegex(DomainValidationError, "min_altitude_ft"):
            self.make_zone(min_altitude_ft=30_000, max_altitude_ft=20_000)


class AircraftStateValidationTests(TestCase):
    def test_missing_optional_provider_fields_remain_missing(self) -> None:
        state = AircraftState(
            provider="mock",
            provider_aircraft_id="aircraft-1",
            latitude=51.5,
            longitude=-0.2,
            observed_at=NOW,
        )

        self.assertIsNone(state.callsign)
        self.assertIsNone(state.altitude_ft)

    def test_rejects_naive_observation_time(self) -> None:
        with self.assertRaisesRegex(DomainValidationError, "timezone-aware"):
            AircraftState(
                provider="mock",
                provider_aircraft_id="aircraft-1",
                latitude=51.5,
                longitude=-0.2,
                observed_at=datetime(2026, 8, 8, 12, 0),
            )


class DisplaySnapshotValidationTests(TestCase):
    def test_visible_state_requires_primary_aircraft(self) -> None:
        with self.assertRaisesRegex(DomainValidationError, "require primary"):
            DisplaySnapshot(
                generated_at=NOW,
                status=SnapshotStatus.AIRCRAFT_VISIBLE,
                refresh_after_seconds=30,
            )

    def test_non_aircraft_state_rejects_primary_aircraft(self) -> None:
        primary = DisplayAircraft(
            flight_number=None,
            callsign="SKY101",
            registration=None,
            aircraft_type=None,
            origin=None,
            destination=None,
            altitude_ft=20_000,
            distance_km=5.0,
            bearing_degrees=10.0,
        )

        with self.assertRaisesRegex(DomainValidationError, "must not include"):
            DisplaySnapshot(
                generated_at=NOW,
                status=SnapshotStatus.NO_AIRCRAFT,
                refresh_after_seconds=30,
                primary=primary,
            )

    def test_multiple_aircraft_state_requires_a_secondary_count(self) -> None:
        primary = DisplayAircraft(
            flight_number="FT281",
            callsign="SKY101",
            registration="G-MK01",
            aircraft_type="Airbus A380-800",
            origin="LHR",
            destination="JFK",
            altitude_ft=16_000,
            distance_km=8.0,
            bearing_degrees=300.0,
        )

        with self.assertRaisesRegex(DomainValidationError, "secondary aircraft"):
            DisplaySnapshot(
                generated_at=NOW,
                status=SnapshotStatus.MULTIPLE_AIRCRAFT,
                refresh_after_seconds=30,
                primary=primary,
                secondary_count=0,
            )

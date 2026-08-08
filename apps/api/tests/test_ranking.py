from datetime import UTC, datetime
from unittest import TestCase

from flight_tracker.domain.geometry import destination_point, evaluate_aircraft
from flight_tracker.domain.models import AircraftState, ViewingZone
from flight_tracker.domain.ranking import rank_visible_aircraft, relevance_score

NOW = datetime(2026, 8, 8, 12, 0, tzinfo=UTC)


class AircraftRankingTests(TestCase):
    def setUp(self) -> None:
        self.zone = ViewingZone(
            device_id="device-1",
            name="North window",
            latitude=51.477,
            longitude=-0.210,
            bearing_degrees=0.0,
            field_of_view_degrees=80.0,
            max_distance_km=40.0,
        )

    def make_match(
        self,
        identifier: str,
        *,
        bearing: float,
        distance: float,
        complete: bool = True,
    ):
        latitude, longitude = destination_point(
            self.zone.latitude,
            self.zone.longitude,
            bearing,
            distance,
        )
        aircraft = AircraftState(
            provider="test",
            provider_aircraft_id=identifier,
            latitude=latitude,
            longitude=longitude,
            observed_at=NOW,
            callsign="TEST1" if complete else None,
            registration="G-TEST" if complete else None,
            altitude_ft=20_000 if complete else None,
            ground_speed_knots=320.0 if complete else None,
            track_degrees=90.0 if complete else None,
        )
        return evaluate_aircraft(aircraft, self.zone)

    def test_angular_closeness_has_highest_priority(self) -> None:
        centred_farther = self.make_match("centred", bearing=0.0, distance=25.0)
        edge_closer = self.make_match("edge", bearing=35.0, distance=5.0)

        ranked = rank_visible_aircraft([edge_closer, centred_farther], self.zone)

        self.assertEqual(ranked[0].aircraft.provider_aircraft_id, "centred")

    def test_distance_breaks_equal_angle_scores(self) -> None:
        farther = self.make_match("farther", bearing=10.0, distance=25.0)
        closer = self.make_match("closer", bearing=350.0, distance=5.0)

        ranked = rank_visible_aircraft([farther, closer], self.zone)

        self.assertEqual(ranked[0].aircraft.provider_aircraft_id, "closer")

    def test_completeness_breaks_equal_geometry(self) -> None:
        partial = self.make_match("partial", bearing=0.0, distance=10.0, complete=False)
        complete = self.make_match("complete", bearing=0.0, distance=10.0, complete=True)

        ranked = rank_visible_aircraft([partial, complete], self.zone)

        self.assertEqual(ranked[0].aircraft.provider_aircraft_id, "complete")

    def test_outside_aircraft_has_zero_score_and_is_not_ranked(self) -> None:
        outside = self.make_match("outside", bearing=180.0, distance=10.0)

        self.assertEqual(relevance_score(outside, self.zone), 0.0)
        self.assertEqual(rank_visible_aircraft([outside], self.zone), [])

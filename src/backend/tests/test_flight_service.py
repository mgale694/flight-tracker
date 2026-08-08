from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest import TestCase

from services import FlightTrackerService


class FlightTrackerServiceAirportTests(TestCase):
    def test_location_preview_returns_full_address_and_caches_result(self) -> None:
        class FakeGeocoder:
            calls = 0

            def geocode(self, _address, exactly_one=True):
                self.calls += 1
                return SimpleNamespace(
                    latitude=51.5034,
                    longitude=-0.1276,
                    address="10 Downing Street, Westminster, London, SW1A 2AA, UK",
                )

        service = object.__new__(FlightTrackerService)
        service.geocoder = FakeGeocoder()
        service.last_address = None
        service.last_coordinates = None
        service.last_formatted_address = None

        first = service.resolve_location("SW1A 2AA")
        second = service.resolve_location("SW1A 2AA")

        self.assertEqual(first["formatted_address"], second["formatted_address"])
        self.assertEqual(first["latitude"], 51.5034)
        self.assertEqual(service.geocoder.calls, 1)
        self.assertTrue(service.has_cached_location("SW1A 2AA"))
        self.assertFalse(service.has_cached_location("10 Downing Street"))

    def test_airport_catalog_supplies_full_names_without_flight_details(self) -> None:
        service = object.__new__(FlightTrackerService)
        service._airport_names = {
            "LHR": "London Heathrow Airport",
            "AMS": "Amsterdam Airport Schiphol",
        }
        flight = SimpleNamespace(
            id="test-flight",
            callsign="TEST1",
            origin_airport_iata="LHR",
            destination_airport_iata="AMS",
        )

        result = service._parse_flight_object(flight, 1_250)

        self.assertEqual(result["origin_name"], "London Heathrow Airport")
        self.assertEqual(result["destination_name"], "Amsterdam Airport Schiphol")

    def test_failed_flight_details_are_not_retried_every_poll(self) -> None:
        class ForbiddenAPI:
            calls = 0

            def get_flight_details(self, _flight):
                self.calls += 1
                raise RuntimeError("403 Forbidden")

        service = object.__new__(FlightTrackerService)
        service.fr_api = ForbiddenAPI()
        service._flight_detail_cache = {}
        service._detail_backoff_until = 0
        flight = SimpleNamespace(id="blocked", callsign="TEST2")

        with redirect_stdout(StringIO()):
            service._enrich_flight(flight)
            service._enrich_flight(flight)

        self.assertEqual(service.fr_api.calls, 1)

        with redirect_stdout(StringIO()):
            service._enrich_flight(SimpleNamespace(id="another", callsign="TEST3"))

        self.assertEqual(service.fr_api.calls, 1)

    def test_bearing_filter_handles_north_wraparound(self) -> None:
        self.assertAlmostEqual(
            FlightTrackerService._bearing_between(51.5, -0.1, 52.5, -0.1),
            0,
        )
        self.assertAlmostEqual(
            FlightTrackerService._bearing_between(51.5, -0.1, 51.5, 0.9),
            89.6,
            places=0,
        )
        self.assertTrue(FlightTrackerService._bearing_is_visible(355, 0, 20))
        self.assertTrue(FlightTrackerService._bearing_is_visible(5, 0, 20))
        self.assertFalse(FlightTrackerService._bearing_is_visible(25, 0, 20))
        self.assertTrue(FlightTrackerService._bearing_is_visible(180, None, None))

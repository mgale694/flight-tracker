from FlightRadar24 import FlightRadar24API
from geopy.geocoders import Nominatim
import logging
import time


class FlightTracker:
    def __init__(self, config):
        self.config = config
        self.address = config.get(
            "address", "31 Maltings Place, Fulham, London, SW62BU"
        )
        self.search_radius = config.get("search_radius_meters", 3000)
        self.max_flights = config.get("max_flights", 20)
        self.max_elapsed_time = config.get("max_elapsed_time", 30 * 60)

        # Initialize APIs
        self.nominatim = Nominatim(user_agent="Flight Tracker")
        self.fr_api = FlightRadar24API()

        # State tracking
        self.flights_overhead = {}
        self.flights_detailed = {}
        self.location = None
        self.bounds = None
        self.start_time = None

        self._setup_location()

    def _setup_location(self):
        """Setup location and bounds for flight tracking"""
        self.location = self.nominatim.geocode(self.address)
        if not self.location:
            raise Exception(f"Could not geocode address: {self.address}")

        logging.info(f"Location found: {self.location.address}")
        logging.info(
            f"Coordinates: [{self.location.latitude}, {self.location.longitude}]"
        )

        self.bounds = self.fr_api.get_bounds_by_point(
            self.location.latitude, self.location.longitude, self.search_radius
        )

    def start_session(self):
        """Start a new flight tracking session"""
        self.start_time = time.time()
        self.flights_overhead = {}
        self.flights_detailed = {}
        logging.info("Flight tracking session started")

    def get_flights(self):
        """Get current flights in the area"""
        try:
            return self.fr_api.get_flights(bounds=self.bounds)
        except Exception as e:
            logging.error(f"Error fetching flights: {e}")
            return []

    def get_flight_details(self, flight):
        """Get detailed information for a specific flight"""
        try:
            flight_details = self.fr_api.get_flight_details(flight)
            flight.set_flight_details(flight_details)
            return flight
        except Exception as e:
            logging.error(f"Error getting flight details for {flight.callsign}: {e}")
            return flight

    def process_flight(self, flight):
        """Process a detected flight"""
        if flight.callsign not in self.flights_overhead:
            self.flights_overhead[flight.callsign] = {
                "FROM": flight.origin_airport_name,
                "TO": flight.destination_airport_name,
                "detected_at": time.time(),
            }
            self.flights_detailed[flight.id] = flight

            logging.info(
                f"FLIGHT: {flight.callsign} | "
                f"FROM: {flight.origin_airport_name} | "
                f"TO: {flight.destination_airport_name} | "
                f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            return True  # New flight detected
        return False  # Already tracked

    def get_session_stats(self):
        """Get current session statistics"""
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        return {
            "flights_count": len(self.flights_overhead),
            "elapsed_time": elapsed,
            "elapsed_str": time.strftime("%H:%M:%S", time.gmtime(elapsed)),
            "location_short": f"{self.location.address.split(',')[0]}, {self.location.address.split(',')[-1].strip()}",
        }

    def should_continue(self):
        """Check if tracking session should continue"""
        if not self.start_time:
            return True

        elapsed = time.time() - self.start_time
        return (
            len(self.flights_overhead) < self.max_flights
            and elapsed < self.max_elapsed_time
        )

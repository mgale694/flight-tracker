from flightradar24.api import FlightRadar24API
from geopy.geocoders import Nominatim
import logging
import time
import random


class Flight:
    """Flight data model matching the original structure"""

    def __init__(self, flight_data):
        # Handle both object attributes and dictionary keys
        def safe_get(obj, attr, default="Unknown"):
            if hasattr(obj, attr):
                return getattr(obj, attr, default)
            elif isinstance(obj, dict):
                return obj.get(attr, default)
            else:
                return default

        self.callsign = safe_get(flight_data, "callsign")
        self.id = safe_get(flight_data, "id", "")
        self.latitude = safe_get(flight_data, "latitude", 0.0)
        self.longitude = safe_get(flight_data, "longitude", 0.0)
        self.altitude = safe_get(flight_data, "altitude")
        self.ground_speed = safe_get(flight_data, "ground_speed")

        # Handle airport information - might be in different fields
        self.origin_airport_name = safe_get(
            flight_data, "origin_airport_name"
        ) or safe_get(flight_data, "origin", "Unknown")
        self.destination_airport_name = safe_get(
            flight_data, "destination_airport_name"
        ) or safe_get(flight_data, "destination", "Unknown")
        self.origin_airport_iata = safe_get(flight_data, "origin_airport_iata", "N/A")
        self.destination_airport_iata = safe_get(
            flight_data, "destination_airport_iata", "N/A"
        )

        # Airline and aircraft info
        self.airline_name = safe_get(flight_data, "airline_name") or safe_get(
            flight_data, "airline", "Unknown"
        )
        self.aircraft_model = safe_get(flight_data, "aircraft_model") or safe_get(
            flight_data, "aircraft", "Unknown"
        )
        self.registration = safe_get(flight_data, "registration")

        # Convert numeric values to strings for display consistency
        if isinstance(self.altitude, (int, float)):
            self.altitude = str(int(self.altitude)) if self.altitude else "Unknown"
        if isinstance(self.ground_speed, (int, float)):
            self.ground_speed = (
                str(int(self.ground_speed)) if self.ground_speed else "Unknown"
            )

    def to_dict(self):
        return {
            "callsign": self.callsign,
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "ground_speed": self.ground_speed,
            "origin_airport_name": self.origin_airport_name,
            "destination_airport_name": self.destination_airport_name,
            "origin_airport_iata": self.origin_airport_iata,
            "destination_airport_iata": self.destination_airport_iata,
            "airline_name": self.airline_name,
            "aircraft_model": self.aircraft_model,
            "registration": self.registration,
        }


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
            flights = self.fr_api.get_flights(bounds=self.bounds)
            return [Flight(flight) for flight in flights]
        except Exception as e:
            logging.error(f"Error fetching flights: {e}")
            return []

    def get_flight_details(self, flight):
        """Get detailed information for a specific flight"""
        try:
            # For the web version, we'll use the existing flight data
            # The original gets more details from the API but this should work for demo
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

    def update_config(self, new_config):
        """Update configuration and reinitialize if needed"""
        old_address = self.address
        self.config.update(new_config)
        self.address = new_config.get("address", self.address)
        self.search_radius = new_config.get("search_radius_meters", self.search_radius)
        self.max_flights = new_config.get("max_flights", self.max_flights)
        self.max_elapsed_time = new_config.get(
            "max_elapsed_time", self.max_elapsed_time
        )

        # If address changed, update location
        if old_address != self.address:
            self._setup_location()


class Voice:
    def __init__(self):
        pass

    def on_starting(self):
        return random.choice(
            [
                "Flight Tracker starting up...",
                "Scanning the skies...",
                "Ready to track flights!",
                "Looking up for aircraft...",
            ]
        )

    def on_flight_detected(self, callsign):
        return random.choice(
            [
                f"Found {callsign} overhead!",
                f"Tracking {callsign}",
                f"Aircraft {callsign} detected",
                f"New flight: {callsign}",
            ]
        )

    def on_boot_complete(self):
        return random.choice(
            [
                "Boot sequence complete!",
                "System ready!",
                "All systems go!",
                "Ready for flight tracking!",
            ]
        )

    def on_session_complete(self, count):
        return random.choice(
            [
                f"Session complete! Tracked {count} flights",
                f"Found {count} aircraft today",
                f"Flight tracking session ended: {count} flights",
                f"Monitored {count} flights overhead",
            ]
        )


def get_boot_phrases():
    """Get list of boot phrases with corresponding faces"""
    return [
        ("(-__-)", "Oi I was sleeping!"),
        ("(•__•)", "Wakey wakey!"),
        ("(≤__≤)", "Rise and shine!"),
        ("(*__*)", "Back from dreamland..."),
        ("(≠__≠)", "Did you bring coffee?"),
        ("(*__*)", "Yawn... what's up?"),
        ("(ø__ø)", "Booting up with a smile!"),
        ("(#__#)", "Let me stretch first..."),
        ("(≥__≥)", "Good morning, world!"),
        ("(O__O)", "Ready for takeoff!"),
    ]


def get_random_boot_face():
    """Get a random boot face and phrase"""
    return random.choice(get_boot_phrases())

"""Flight tracking service using FlightRadar24 API."""
from datetime import datetime, timezone
import math
import os
import time
from typing import List, Dict, Optional, Tuple
from FlightRadar24 import FlightRadar24API
from geopy.extra.rate_limiter import RateLimiter
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class FlightTrackerService:
    """Service for tracking flights in a specific geographic area."""
    
    def __init__(self):
        """Initialize the flight tracker service."""
        self.fr_api = FlightRadar24API()
        self.geocoder = Nominatim(
            user_agent=os.getenv(
                "FLIGHT_TRACKER_GEOCODER_USER_AGENT",
                "skypane-flight-tracker/1.0",
            ),
            domain=os.getenv(
                "FLIGHT_TRACKER_GEOCODER_DOMAIN",
                "nominatim.openstreetmap.org",
            ),
            scheme="https",
        )
        self._geocode = RateLimiter(
            self.geocoder.geocode,
            min_delay_seconds=1,
            max_retries=0,
            swallow_exceptions=False,
        )
        self.last_coordinates: Optional[Tuple[float, float]] = None
        self.last_address: Optional[str] = None
        self.last_formatted_address: Optional[str] = None
        self._airport_names: Optional[Dict[str, str]] = None
        self._flight_detail_cache: Dict[str, Tuple[float, Optional[Dict]]] = {}
        self._detail_backoff_until = 0.0
    
    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Convert an address to coordinates.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            ValueError: If address cannot be geocoded
        """
        location = self.resolve_location(address)
        return location["latitude"], location["longitude"]

    def resolve_location(self, address: str) -> Dict:
        """Resolve a postcode or address into a full address and map coordinates."""

        normalized_address = address.strip()
        if not normalized_address:
            raise ValueError("Enter a postcode or full address")

        if (
            normalized_address == self.last_address
            and self.last_coordinates
            and self.last_formatted_address
        ):
            return {
                "query": normalized_address,
                "formatted_address": self.last_formatted_address,
                "latitude": self.last_coordinates[0],
                "longitude": self.last_coordinates[1],
            }

        try:
            geocode = getattr(self, "_geocode", self.geocoder.geocode)
            location = geocode(normalized_address, exactly_one=True)
            if location is None:
                raise ValueError(f"Could not find: {normalized_address}")

            coordinates = (float(location.latitude), float(location.longitude))
            formatted_address = str(
                getattr(location, "address", None) or normalized_address
            )
            self.last_address = normalized_address
            self.last_coordinates = coordinates
            self.last_formatted_address = formatted_address
            return {
                "query": normalized_address,
                "formatted_address": formatted_address,
                "latitude": coordinates[0],
                "longitude": coordinates[1],
            }
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Geocoding error: {str(e)}")

    def has_cached_location(self, address: str) -> bool:
        """Return whether an address already has a complete cached resolution."""

        return (
            address.strip() == self.last_address
            and self.last_coordinates is not None
            and self.last_formatted_address is not None
        )
    
    def get_flights_in_area(
        self,
        address: str,
        radius_meters: int = 3000,
        max_flights: int = 20,
        bearing_degrees: Optional[float] = None,
        field_of_view_degrees: Optional[float] = None,
        min_distance_meters: float = 0,
    ) -> List[Dict]:
        """Get flights within a radius of an address.
        
        Args:
            address: Center address for search
            radius_meters: Search radius in meters
            max_flights: Maximum number of flights to return
            bearing_degrees: Centre bearing of the visible sector
            field_of_view_degrees: Width of the visible sector
            min_distance_meters: Ignore aircraft closer than this distance
            
        Returns:
            List of flight data dictionaries
        """
        try:
            # Get coordinates for the address
            center_lat, center_lon = self.geocode_address(address)
            center_coords = (center_lat, center_lon)
            
            # Use get_flights() instead of get_bounds() - more reliable
            # Calculate bounding box for the area
            # One degree latitude is approximately 111 km. Longitude contracts
            # towards the poles, so account for the configured latitude.
            lat_offset = radius_meters / 111000
            longitude_scale = max(abs(math.cos(math.radians(center_lat))), 0.01)
            lon_offset = radius_meters / (111000 * longitude_scale)
            
            # Define the bounding box
            bounds_str = f"{center_lat + lat_offset},{center_lat - lat_offset},{center_lon - lon_offset},{center_lon + lon_offset}"
            
            # Get flights using get_flights() method with bounds parameter
            try:
                flights_data = self.fr_api.get_flights(bounds=bounds_str)
            except Exception as e:
                print(f"FlightRadar24 API error: {e}")
                return []
            
            # Check if API returned valid data
            if not flights_data or not isinstance(flights_data, list):
                print(f"FlightRadar24 API returned invalid data: {type(flights_data).__name__}")
                return []
            
            if len(flights_data) == 0:
                print(f"FlightRadar24 API returned no flights for bounds at {center_lat}, {center_lon}")
                return []
            
            # Filter flights by actual distance
            flights_in_range = []
            
            for flight in flights_data:
                # Flight object from get_flights() has attributes, not array indices
                try:
                    # Get latitude and longitude
                    flight_lat = getattr(flight, 'latitude', None)
                    flight_lon = getattr(flight, 'longitude', None)
                    
                    if flight_lat is None or flight_lon is None:
                        continue
                    
                    flight_coords = (flight_lat, flight_lon)
                    
                    # Calculate distance
                    distance = geodesic(center_coords, flight_coords).meters
                    
                    aircraft_bearing = self._bearing_between(
                        center_lat,
                        center_lon,
                        float(flight_lat),
                        float(flight_lon),
                    )
                    inside_view = self._bearing_is_visible(
                        aircraft_bearing,
                        bearing_degrees,
                        field_of_view_degrees,
                    )

                    if min_distance_meters <= distance <= radius_meters and inside_view:
                        self._enrich_flight(flight)
                        
                        # Parse flight data from Flight object
                        flight_info = self._parse_flight_object(flight, distance)
                        flights_in_range.append(flight_info)
                        
                        if len(flights_in_range) >= max_flights:
                            break
                
                except Exception as e:
                    # Skip flights with parsing errors
                    print(f"Error parsing flight: {e}")
                    continue
            
            # Sort by distance (closest first)
            flights_in_range.sort(key=lambda x: x['distance'])
            
            return flights_in_range
            
        except Exception as e:
            raise Exception(f"Error fetching flights: {str(e)}")

    @staticmethod
    def _bearing_between(
        origin_latitude: float,
        origin_longitude: float,
        target_latitude: float,
        target_longitude: float,
    ) -> float:
        """Calculate the initial compass bearing from the observer to an aircraft."""

        origin_latitude_radians = math.radians(origin_latitude)
        target_latitude_radians = math.radians(target_latitude)
        longitude_delta = math.radians(target_longitude - origin_longitude)
        x = math.sin(longitude_delta) * math.cos(target_latitude_radians)
        y = (
            math.cos(origin_latitude_radians) * math.sin(target_latitude_radians)
            - math.sin(origin_latitude_radians)
            * math.cos(target_latitude_radians)
            * math.cos(longitude_delta)
        )
        return (math.degrees(math.atan2(x, y)) + 360) % 360

    @staticmethod
    def _bearing_is_visible(
        aircraft_bearing: float,
        centre_bearing: Optional[float],
        field_of_view: Optional[float],
    ) -> bool:
        """Return whether a bearing falls inside the configured viewing sector."""

        if centre_bearing is None or field_of_view is None or field_of_view >= 360:
            return True
        angular_difference = abs((aircraft_bearing - centre_bearing + 180) % 360 - 180)
        return angular_difference <= field_of_view / 2
    
    def _parse_flight_object(self, flight, distance: float) -> Dict:
        """Parse Flight object from FlightRadar24 API into structured format.
        
        Args:
            flight: Flight object from FlightRadar24API.get_flights()
            distance: Distance from tracking point in meters
            
        Returns:
            Parsed flight data dictionary with comprehensive information
        """
        origin_code = getattr(flight, 'origin_airport_iata', 'N/A') or 'N/A'
        dest_code = getattr(flight, 'destination_airport_iata', 'N/A') or 'N/A'
        origin_name = self._resolve_airport_name(
            origin_code, getattr(flight, 'origin_airport_name', None)
        )
        destination_name = self._resolve_airport_name(
            dest_code, getattr(flight, 'destination_airport_name', None)
        )
        
        return {
            # Basic identification
            "id": getattr(flight, 'id', 'N/A'),
            "icao_24bit": getattr(flight, 'icao_24bit', None),
            "callsign": getattr(flight, 'callsign', 'N/A') or getattr(flight, 'number', 'N/A'),
            "number": getattr(flight, 'number', None),
            "registration": getattr(flight, 'registration', 'N/A') or 'N/A',
            
            # Aircraft information
            "aircraft": getattr(flight, 'aircraft_model', None) or getattr(flight, 'aircraft_code', 'Unknown') or 'Unknown',
            "aircraft_code": getattr(flight, 'aircraft_code', None),
            "aircraft_model": getattr(flight, 'aircraft_model', None),
            "aircraft_age": getattr(flight, 'aircraft_age', None),
            "aircraft_country_id": getattr(flight, 'aircraft_country_id', None),
            
            # Airline information
            "airline": getattr(flight, 'airline_name', None) or getattr(flight, 'airline_short_name', None) or self._extract_airline(getattr(flight, 'callsign', '') or ''),
            "airline_name": getattr(flight, 'airline_name', None),
            "airline_short_name": getattr(flight, 'airline_short_name', None),
            "airline_iata": getattr(flight, 'airline_iata', None),
            "airline_icao": getattr(flight, 'airline_icao', None),
            
            # Origin airport
            "origin": origin_code,
            "origin_name": origin_name,
            "origin_airport_iata": origin_code,
            "origin_airport_icao": getattr(flight, 'origin_airport_icao', None),
            "origin_airport_country_code": getattr(flight, 'origin_airport_country_code', None),
            "origin_airport_country_name": getattr(flight, 'origin_airport_country_name', None),
            "origin_airport_latitude": getattr(flight, 'origin_airport_latitude', None),
            "origin_airport_longitude": getattr(flight, 'origin_airport_longitude', None),
            "origin_airport_altitude": getattr(flight, 'origin_airport_altitude', None),
            "origin_airport_gate": getattr(flight, 'origin_airport_gate', None),
            "origin_airport_terminal": getattr(flight, 'origin_airport_terminal', None),
            
            # Destination airport
            "destination": dest_code,
            "destination_name": destination_name,
            "destination_airport_iata": dest_code,
            "destination_airport_icao": getattr(flight, 'destination_airport_icao', None),
            "destination_airport_country_code": getattr(flight, 'destination_airport_country_code', None),
            "destination_airport_country_name": getattr(flight, 'destination_airport_country_name', None),
            "destination_airport_latitude": getattr(flight, 'destination_airport_latitude', None),
            "destination_airport_longitude": getattr(flight, 'destination_airport_longitude', None),
            "destination_airport_altitude": getattr(flight, 'destination_airport_altitude', None),
            "destination_airport_gate": getattr(flight, 'destination_airport_gate', None),
            "destination_airport_terminal": getattr(flight, 'destination_airport_terminal', None),
            "destination_airport_baggage": getattr(flight, 'destination_airport_baggage', None),
            
            # Flight status and position
            "altitude": int(getattr(flight, 'altitude', 0) or 0),
            "speed": int(getattr(flight, 'ground_speed', 0) or 0),
            "ground_speed": int(getattr(flight, 'ground_speed', 0) or 0),
            "heading": int(getattr(flight, 'heading', 0) or 0),
            "vertical_speed": getattr(flight, 'vertical_speed', None),
            "squawk": getattr(flight, 'squawk', None),
            "on_ground": getattr(flight, 'on_ground', None),
            "latitude": float(getattr(flight, 'latitude', 0.0)),
            "longitude": float(getattr(flight, 'longitude', 0.0)),
            
            # Status information
            "status_text": getattr(flight, 'status_text', None),
            "status_icon": getattr(flight, 'status_icon', None),
            
            # Time and tracking
            "time": getattr(flight, 'time', None),
            "distance": round(distance, 2),
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

    def _enrich_flight(self, flight) -> None:
        """Apply cached details and avoid repeatedly hitting a blocked endpoint."""

        flight_id = str(getattr(flight, "id", "") or "")
        if not flight_id:
            return

        now = time.monotonic()
        if now < getattr(self, "_detail_backoff_until", 0.0):
            return

        cached = self._flight_detail_cache.get(flight_id)
        if cached and now - cached[0] < 900:
            details = cached[1]
        else:
            try:
                details = self.fr_api.get_flight_details(flight)
            except Exception as detail_error:
                details = None
                if "403" in str(detail_error):
                    self._detail_backoff_until = now + 900
                print(
                    "WARNING: Could not fetch details for "
                    f"{getattr(flight, 'callsign', 'unknown')}: {detail_error}"
                )
            self._flight_detail_cache[flight_id] = (now, details)

        if details:
            flight.set_flight_details(details)

        if len(self._flight_detail_cache) > 1_000:
            self._flight_detail_cache = {
                key: value
                for key, value in self._flight_detail_cache.items()
                if now - value[0] < 900
            }

    def _resolve_airport_name(self, code: str, provider_name: Optional[str]) -> str:
        """Resolve a full airport name without relying on flight-detail access."""

        if provider_name and provider_name != code:
            return provider_name

        if self._airport_names is None:
            try:
                airports = self.fr_api.get_airports()
                self._airport_names = {
                    str(airport_code): str(airport.name)
                    for airport in airports
                    for airport_code in (
                        getattr(airport, "iata", None),
                        getattr(airport, "icao", None),
                    )
                    if airport_code and getattr(airport, "name", None)
                }
            except Exception as airport_error:
                print(f"WARNING: Could not load airport names: {airport_error}")
                self._airport_names = {}

        return self._airport_names.get(code, code)
    
    def _extract_airline(self, callsign: str) -> str:
        """Extract airline code from callsign.
        
        Args:
            callsign: Flight callsign
            
        Returns:
            Airline code or 'N/A'
        """
        if not callsign or len(callsign) < 3:
            return "N/A"
        
        # Extract first 2-3 letters as airline code
        airline_code = ""
        for char in callsign:
            if char.isalpha():
                airline_code += char
            else:
                break
        
        return airline_code if airline_code else "N/A"
    
    def get_flight_details(self, flight_id: str) -> Optional[Dict]:
        """Get detailed information about a specific flight.
        
        Args:
            flight_id: Flight identifier
            
        Returns:
            Detailed flight information or None if not found
        """
        try:
            details = self.fr_api.get_flight_details(flight_id)
            return details
        except Exception:
            return None
    
    def clear_cache(self):
        """Clear cached geocoding data."""
        self.last_address = None
        self.last_coordinates = None
        self.last_formatted_address = None

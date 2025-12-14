"""Flight tracking service using FlightRadar24 API."""
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from FlightRadar24 import FlightRadar24API
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


class FlightTrackerService:
    """Service for tracking flights in a specific geographic area."""
    
    def __init__(self):
        """Initialize the flight tracker service."""
        self.fr_api = FlightRadar24API()
        self.geocoder = Nominatim(user_agent="flight-tracker")
        self.last_coordinates: Optional[Tuple[float, float]] = None
        self.last_address: Optional[str] = None
    
    def geocode_address(self, address: str) -> Tuple[float, float]:
        """Convert an address to coordinates.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            ValueError: If address cannot be geocoded
        """
        # Cache coordinates for same address
        if address == self.last_address and self.last_coordinates:
            return self.last_coordinates
        
        try:
            location = self.geocoder.geocode(address)
            if location is None:
                raise ValueError(f"Could not geocode address: {address}")
            
            coordinates = (location.latitude, location.longitude)
            self.last_address = address
            self.last_coordinates = coordinates
            return coordinates
        except Exception as e:
            raise ValueError(f"Geocoding error: {str(e)}")
    
    def get_flights_in_area(
        self,
        address: str,
        radius_meters: int = 3000,
        max_flights: int = 20
    ) -> List[Dict]:
        """Get flights within a radius of an address.
        
        Args:
            address: Center address for search
            radius_meters: Search radius in meters
            max_flights: Maximum number of flights to return
            
        Returns:
            List of flight data dictionaries
        """
        try:
            # Get coordinates for the address
            center_lat, center_lon = self.geocode_address(address)
            center_coords = (center_lat, center_lon)
            
            # Use get_flights() instead of get_bounds() - more reliable
            # Calculate bounding box for the area
            # 1 degree latitude ≈ 111 km
            lat_offset = (radius_meters / 111000) * 2
            lon_offset = (radius_meters / (111000 * abs(center_lat / 90))) * 2 if center_lat != 0 else lat_offset
            
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
                    
                    if distance <= radius_meters:
                        # Fetch detailed flight information to get airport names, airline names, etc.
                        try:
                            flight_details = self.fr_api.get_flight_details(flight.id)
                            if flight_details:
                                flight.set_flight_details(flight_details)
                                print(f"✓ Got details for {flight.callsign}: {getattr(flight, 'airline_name', 'N/A')}, {getattr(flight, 'origin_airport_name', 'N/A')} → {getattr(flight, 'destination_airport_name', 'N/A')}")
                        except Exception as detail_error:
                            print(f"⚠ Could not fetch details for {getattr(flight, 'callsign', 'unknown')}: {detail_error}")
                        
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
            "origin_name": getattr(flight, 'origin_airport_name', None) or origin_code,
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
            "destination_name": getattr(flight, 'destination_airport_name', None) or dest_code,
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
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _parse_flight_data(
        self, 
        flight_id: str, 
        flight_data: List, 
        distance: float
    ) -> Dict:
        """Parse raw flight data into structured format (legacy method).
        
        Args:
            flight_id: Flight identifier
            flight_data: Raw flight data array from FlightRadar24
            distance: Distance from tracking point in meters
            
        Returns:
            Parsed flight data dictionary
        """
        # FlightRadar24 data format (indices):
        # 0: flight_id, 1: lat, 2: lon, 3: heading, 4: altitude (ft),
        # 5: speed (knots), 6: squawk, 7: radar, 8: aircraft type,
        # 9: registration, 10: timestamp, 11: origin, 12: destination,
        # 13: flight number, 14: on_ground, 15: vertical_speed, 16: callsign
        
        origin_code = flight_data[11] if len(flight_data) > 11 and flight_data[11] else "N/A"
        dest_code = flight_data[12] if len(flight_data) > 12 and flight_data[12] else "N/A"
        
        return {
            "id": flight_id,
            "callsign": flight_data[16] if len(flight_data) > 16 else flight_data[13] if len(flight_data) > 13 else "N/A",
            "registration": flight_data[9] if len(flight_data) > 9 and flight_data[9] else "N/A",
            "aircraft": flight_data[8] if len(flight_data) > 8 and flight_data[8] else "Unknown",
            "airline": self._extract_airline(flight_data[16] if len(flight_data) > 16 else ""),
            "origin": origin_code,
            "destination": dest_code,
            "origin_name": origin_code,
            "destination_name": dest_code,
            "altitude": int(flight_data[4]) if len(flight_data) > 4 and flight_data[4] else 0,
            "speed": int(flight_data[5]) if len(flight_data) > 5 and flight_data[5] else 0,
            "heading": int(flight_data[3]) if len(flight_data) > 3 and flight_data[3] else 0,
            "latitude": float(flight_data[1]) if len(flight_data) > 1 else 0.0,
            "longitude": float(flight_data[2]) if len(flight_data) > 2 else 0.0,
            "distance": round(distance, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
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

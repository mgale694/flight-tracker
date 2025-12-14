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
            
            # Get flights in the general area (bounding box)
            # Calculate approximate bounding box
            # 1 degree latitude ≈ 111 km
            lat_offset = (radius_meters / 111000) * 2
            lon_offset = (radius_meters / (111000 * abs(center_lat / 90))) * 2 if center_lat != 0 else lat_offset
            
            bounds = self.fr_api.get_bounds({
                'tl_y': center_lat + lat_offset,
                'tl_x': center_lon - lon_offset,
                'br_y': center_lat - lat_offset,
                'br_x': center_lon + lon_offset
            })
            
            # Filter flights by actual distance
            flights_in_range = []
            
            for flight_id, flight_data in bounds.items():
                if not isinstance(flight_data, list) or len(flight_data) < 13:
                    continue
                
                try:
                    # Extract flight position
                    flight_lat = flight_data[1]
                    flight_lon = flight_data[2]
                    
                    if flight_lat is None or flight_lon is None:
                        continue
                    
                    flight_coords = (flight_lat, flight_lon)
                    
                    # Calculate distance
                    distance = geodesic(center_coords, flight_coords).meters
                    
                    if distance <= radius_meters:
                        # Parse flight data
                        flight_info = self._parse_flight_data(flight_id, flight_data, distance)
                        flights_in_range.append(flight_info)
                        
                        if len(flights_in_range) >= max_flights:
                            break
                
                except Exception:
                    # Skip flights with parsing errors
                    continue
            
            # Sort by distance (closest first)
            flights_in_range.sort(key=lambda x: x['distance'])
            
            return flights_in_range
            
        except Exception as e:
            raise Exception(f"Error fetching flights: {str(e)}")
    
    def _parse_flight_data(
        self, 
        flight_id: str, 
        flight_data: List, 
        distance: float
    ) -> Dict:
        """Parse raw flight data into structured format.
        
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
        
        return {
            "id": flight_id,
            "callsign": flight_data[16] if len(flight_data) > 16 else flight_data[13] if len(flight_data) > 13 else "N/A",
            "registration": flight_data[9] if len(flight_data) > 9 and flight_data[9] else "N/A",
            "aircraft": flight_data[8] if len(flight_data) > 8 and flight_data[8] else "Unknown",
            "airline": self._extract_airline(flight_data[16] if len(flight_data) > 16 else ""),
            "origin": flight_data[11] if len(flight_data) > 11 and flight_data[11] else "N/A",
            "destination": flight_data[12] if len(flight_data) > 12 and flight_data[12] else "N/A",
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

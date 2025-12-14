"""Flight tracker that can use backend API or standalone FlightRadar24"""
import logging
from typing import List, Optional
import time


class FlightTracker:
    """Flight tracker with backend API mode and standalone mode"""
    
    def __init__(self, config):
        self.config = config
        self.use_backend = config.get("main", {}).get("use_backend_api", True)
        
        if self.use_backend:
            from api_client import BackendAPIClient
            api_url = config.get("main", {}).get("api_url", "http://localhost:8000")
            self.api_client = BackendAPIClient(api_url)
            logging.info(f"Flight tracker initialized in API mode: {api_url}")
        else:
            # Standalone mode - use FlightRadar24API directly
            try:
                from FlightRadar24 import FlightRadar24API
                from geopy.geocoders import Nominatim
                from geopy.distance import geodesic
                
                self.fr_api = FlightRadar24API()
                self.geocoder = Nominatim(user_agent="flight-tracker-raspi")
                logging.info("Flight tracker initialized in standalone mode")
            except ImportError as e:
                logging.error(f"Cannot initialize standalone mode: {e}")
                logging.error("Install FlightRadar24-API and geopy packages")
                raise
    
    def get_flights(self) -> List:
        """Get current flights"""
        if self.use_backend:
            return self._get_flights_from_backend()
        else:
            return self._get_flights_standalone()
    
    def _get_flights_from_backend(self) -> List:
        """Get flights from backend API"""
        try:
            flights_data = self.api_client.get_flights()
            
            # Convert dict to object-like structure for compatibility
            if flights_data:
                return [FlightData(**flight) for flight in flights_data]
            return []
        except Exception as e:
            logging.error(f"Error getting flights from backend: {e}")
            return []
    
    def _get_flights_standalone(self) -> List:
        """Get flights using FlightRadar24 directly (standalone mode)"""
        try:
            from geopy.distance import geodesic
            
            main_config = self.config.get("main", {})
            address = main_config.get("address", "London, UK")
            radius = main_config.get("search_radius_meters", 3000)
            
            # Geocode address
            location = self.geocoder.geocode(address)
            if not location:
                logging.error(f"Could not geocode address: {address}")
                return []
            
            center_coords = (location.latitude, location.longitude)
            
            # Calculate bounding box
            lat_offset = (radius / 111000) * 2
            lon_offset = (radius / (111000 * abs(location.latitude / 90))) * 2
            
            bounds_str = f"{location.latitude + lat_offset},{location.latitude - lat_offset},{location.longitude - lon_offset},{location.longitude + lon_offset}"
            
            # Get flights
            flights_data = self.fr_api.get_flights(bounds=bounds_str)
            
            if not flights_data or not isinstance(flights_data, list):
                return []
            
            # Filter by distance and convert to objects
            flights_in_range = []
            for flight in flights_data:
                try:
                    flight_lat = getattr(flight, 'latitude', None)
                    flight_lon = getattr(flight, 'longitude', None)
                    
                    if flight_lat and flight_lon:
                        distance = geodesic(center_coords, (flight_lat, flight_lon)).meters
                        if distance <= radius:
                            flights_in_range.append(flight)
                except Exception:
                    continue
            
            return flights_in_range
            
        except Exception as e:
            logging.error(f"Error in standalone mode: {e}")
            return []


class FlightData:
    """Simple flight data object for backend API response"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

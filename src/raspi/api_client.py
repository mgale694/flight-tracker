"""
Flight Tracker API Client
Provides a unified interface for raspi to communicate with the backend API
"""

import requests
import logging
from typing import Dict, Any
import time


class FlightTrackerAPIClient:
    """Client for communicating with the Flight Tracker backend API"""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {method} {url} - {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """Check if the backend API is healthy"""
        response = self._make_request("GET", "/health")
        return response.json()

    def get_config(self) -> Dict[str, Any]:
        """Get the full configuration from backend"""
        response = self._make_request("GET", "/config/full")
        return response.json()

    def get_raspi_config(self) -> Dict[str, Any]:
        """Get raspi-specific configuration"""
        response = self._make_request("GET", "/config/raspi")
        return response.json()

    def update_raspi_config(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Update raspi configuration"""
        response = self._make_request("POST", "/config/raspi", json=config)
        return response.json()

    def get_boot_data(self) -> Dict[str, Any]:
        """Get boot screen data"""
        response = self._make_request("GET", "/boot")
        return response.json()

    def get_live_flights(self) -> Dict[str, Any]:
        """Get live flight data"""
        response = self._make_request("GET", "/flights/live")
        return response.json()

    def get_flights(self) -> Dict[str, Any]:
        """Get current flights (basic endpoint)"""
        response = self._make_request("GET", "/flights")
        return response.json()

    def process_flight(self, flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a flight detection"""
        response = self._make_request("POST", "/flights/process", json=flight_data)
        return response.json()

    def start_session(self) -> Dict[str, str]:
        """Start a tracking session"""
        response = self._make_request("POST", "/session/start")
        return response.json()

    def stop_session(self) -> Dict[str, str]:
        """Stop the tracking session"""
        response = self._make_request("POST", "/session/stop")
        return response.json()

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        response = self._make_request("GET", "/session/status")
        return response.json()

    def is_backend_available(self) -> bool:
        """Check if the backend is available"""
        try:
            self.health_check()
            return True
        except Exception:
            return False


class FlightTrackerAPIAdapter:
    """
    Adapter that provides the same interface as the original FlightTracker
    but uses the backend API instead of direct FlightRadar24 calls
    """

    def __init__(self, config: Dict[str, Any], api_url: str = "http://localhost:8000"):
        self.config = config
        self.api_client = FlightTrackerAPIClient(api_url)
        self.start_time = None
        self.logger = logging.getLogger(__name__)

        # Check if backend is available, fallback to local if not
        self.use_backend = self.api_client.is_backend_available()
        if not self.use_backend:
            self.logger.warning("Backend API not available, falling back to local mode")
            # Import the original tracker as fallback
            from .tracker import FlightTracker as LocalFlightTracker

            self.local_tracker = LocalFlightTracker(config)
        else:
            self.logger.info("Using backend API for flight tracking")
            self.local_tracker = None

    def start_session(self):
        """Start a new flight tracking session"""
        self.start_time = time.time()
        if self.use_backend:
            try:
                return self.api_client.start_session()
            except Exception as e:
                self.logger.error(f"Failed to start session on backend: {e}")
                # Fallback to local
                if self.local_tracker:
                    return self.local_tracker.start_session()
        else:
            return self.local_tracker.start_session()

    def get_flights(self):
        """Get current flights in the area"""
        if self.use_backend:
            try:
                response = self.api_client.get_live_flights()
                # Convert to Flight objects for compatibility
                flights = []
                for flight_data in response.get("flights", []):
                    flights.append(Flight(flight_data))
                return flights
            except Exception as e:
                self.logger.error(f"Failed to get flights from backend: {e}")
                if self.local_tracker:
                    return self.local_tracker.get_flights()
                return []
        else:
            return self.local_tracker.get_flights()

    def get_flight_details(self, flight):
        """Get detailed information for a specific flight"""
        # If using backend, details are already included
        if self.use_backend:
            return flight
        else:
            return self.local_tracker.get_flight_details(flight)

    def process_flight(self, flight):
        """Process a detected flight"""
        if self.use_backend:
            try:
                response = self.api_client.process_flight(
                    flight.to_dict() if hasattr(flight, "to_dict") else flight
                )
                return response.get("is_new_flight", False)
            except Exception as e:
                self.logger.error(f"Failed to process flight on backend: {e}")
                if self.local_tracker:
                    return self.local_tracker.process_flight(flight)
                return False
        else:
            return self.local_tracker.process_flight(flight)

    def get_session_stats(self):
        """Get current session statistics"""
        if self.use_backend:
            try:
                response = self.api_client.get_session_status()
                return response.get("stats", {})
            except Exception as e:
                self.logger.error(f"Failed to get session stats from backend: {e}")
                if self.local_tracker:
                    return self.local_tracker.get_session_stats()
                return {}
        else:
            return self.local_tracker.get_session_stats()

    def should_continue(self):
        """Check if tracking session should continue"""
        if self.use_backend:
            try:
                response = self.api_client.get_session_status()
                return response.get("should_continue", True)
            except Exception as e:
                self.logger.error(f"Failed to check session status from backend: {e}")
                if self.local_tracker:
                    return self.local_tracker.should_continue()
                return False
        else:
            return self.local_tracker.should_continue()


class Flight:
    """Flight data model for compatibility"""

    def __init__(self, flight_data):
        if isinstance(flight_data, dict):
            for key, value in flight_data.items():
                setattr(self, key, value)
        else:
            # Copy attributes from object
            for attr in dir(flight_data):
                if not attr.startswith("_"):
                    setattr(self, attr, getattr(flight_data, attr))

    def to_dict(self):
        """Convert flight to dictionary"""
        return {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not attr.startswith("_") and not callable(getattr(self, attr))
        }

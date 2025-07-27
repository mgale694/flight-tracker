"""
Simplified Flight Tracker API Client for Raspi
Just polls the backend for flight data every few seconds
"""

import requests
import logging
from typing import Dict, Any
import time


class SimpleFlightTrackerAPI:
    """Simple client for the flight tracker backend"""

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

    def get_flights(self) -> Dict[str, Any]:
        """Get current flights - main polling endpoint"""
        response = self._make_request("GET", "/flights")
        return response.json()

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        response = self._make_request("GET", "/config")
        return response.json()

    def update_config(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Update configuration"""
        response = self._make_request("POST", "/config", json=config)
        return response.json()

    def health_check(self) -> Dict[str, Any]:
        """Check if the backend is healthy"""
        response = self._make_request("GET", "/health")
        return response.json()

    def is_available(self) -> bool:
        """Check if the backend is available"""
        try:
            self.health_check()
            return True
        except Exception:
            return False


class FlightPollingLoop:
    """Simple polling loop for flight updates"""

    def __init__(
        self, api_url: str = "http://localhost:8000", poll_interval: float = 2.0
    ):
        self.api = SimpleFlightTrackerAPI(api_url)
        self.poll_interval = poll_interval
        self.running = False
        self.logger = logging.getLogger(__name__)

    def start_polling(self, callback):
        """Start polling for flight updates"""
        self.running = True
        self.logger.info("Starting flight polling loop")

        while self.running:
            try:
                # Get current flights
                flight_data = self.api.get_flights()

                # Call the callback with the data
                callback(flight_data)

            except Exception as e:
                self.logger.error(f"Polling error: {e}")

            # Wait before next poll
            time.sleep(self.poll_interval)

    def stop_polling(self):
        """Stop polling"""
        self.running = False
        self.logger.info("Stopped flight polling loop")


# Compatibility wrapper for existing raspi code
class FlightTrackerAPIAdapter:
    """Simple adapter that just polls the backend"""

    def __init__(self, config: Dict[str, Any], api_url: str = "http://localhost:8000"):
        self.api = SimpleFlightTrackerAPI(api_url)
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Check if backend is available
        if not self.api.is_available():
            self.logger.warning("Backend API not available")
            raise Exception("Backend API not available")

    def get_flights(self):
        """Get current flights"""
        try:
            response = self.api.get_flights()
            flights = []
            for flight_data in response.get("flights", []):
                flights.append(Flight(flight_data))
            return flights
        except Exception as e:
            self.logger.error(f"Failed to get flights: {e}")
            return []


class Flight:
    """Simple flight data model"""

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


if __name__ == "__main__":
    # Quick test of the API client
    import logging

    logging.basicConfig(level=logging.INFO)

    api = SimpleFlightTrackerAPI()

    print("Testing Flight Tracker API...")

    # Test health check
    try:
        health = api.health_check()
        print(f"✅ Health check: {health}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test config
    try:
        config = api.get_config()
        print(f"✅ Config loaded: {config['main']['address']}")
    except Exception as e:
        print(f"❌ Config failed: {e}")

    # Test flights
    try:
        flights = api.get_flights()
        print(
            f"✅ Flights retrieved: {len(flights)} flights at {flights.get('location', 'unknown location')}"
        )
    except Exception as e:
        print(f"❌ Flights failed: {e}")

    print("Test complete!")

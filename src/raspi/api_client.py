"""Simple API client for backend communication"""
import requests
import logging
from typing import List, Dict, Optional


class BackendAPIClient:
    """Simple client for communicating with the Flight Tracker backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_flights(self) -> List[Dict]:
        """Get current flights from the backend"""
        try:
            response = self.session.get(f"{self.base_url}/api/flights", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching flights from backend: {e}")
            return []
    
    def get_config(self) -> Optional[Dict]:
        """Get configuration from the backend"""
        try:
            response = self.session.get(f"{self.base_url}/api/config", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching config from backend: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=3)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

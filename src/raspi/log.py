"""Simple logging system for session statistics"""
import os
import logging
from datetime import datetime


class SessionLog:
    """Track session statistics for flight tracking"""
    
    def __init__(self):
        self.session_start = datetime.now()
        self.flights_detected = 0
        self.unique_aircraft = set()
        self.last_flight_time = None
    
    def log_flight(self, flight):
        """Log a detected flight"""
        self.flights_detected += 1
        self.last_flight_time = datetime.now()
        
        # Track unique aircraft by registration
        registration = getattr(flight, 'registration', None)
        if registration and registration != 'N/A':
            self.unique_aircraft.add(registration)
        
        logging.info(f"FLIGHT: {getattr(flight, 'callsign', 'N/A')} - {registration}")
    
    def get_elapsed_time(self):
        """Get elapsed time since session start in seconds"""
        return (datetime.now() - self.session_start).total_seconds()
    
    def get_stats(self):
        """Get current session statistics"""
        from utils import format_duration
        
        return {
            'flights_count': self.flights_detected,
            'unique_count': len(self.unique_aircraft),
            'elapsed_str': format_duration(self.get_elapsed_time()),
            'elapsed_seconds': self.get_elapsed_time(),
        }

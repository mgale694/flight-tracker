import hashlib
import time
import re
import os
import logging
import shutil
from datetime import datetime


class FlightLog(object):
    FLIGHT_TOKEN = "FLIGHT:"
    BOOT_TOKEN = "BOOT:"
    SESSION_START_TOKEN = "Flight Tracker v1"

    def __init__(self, config):
        self.config = config
        self.path = config.get("log_path", "/tmp/flight_tracker.log")
        self.max_flights = config.get("max_flights", 20)

    def parse_stats(self):
        """Parse flight statistics from log file"""
        stats = {
            "flights_detected": 0,
            "unique_aircraft": set(),
            "session_start": None,
            "last_flight": None,
        }

        if not os.path.exists(self.path):
            return stats

        try:
            with open(self.path, "r") as f:
                for line in f:
                    if self.SESSION_START_TOKEN in line:
                        stats["session_start"] = self._parse_timestamp(line)
                    elif self.FLIGHT_TOKEN in line:
                        stats["flights_detected"] += 1
                        stats["last_flight"] = self._parse_timestamp(line)
                        # Extract callsign from flight log entry
                        match = re.search(r"FLIGHT: ([A-Z0-9]+)", line)
                        if match:
                            stats["unique_aircraft"].add(match.group(1))
        except Exception as e:
            logging.error(f"Error parsing flight log: {e}")

        return stats

    def _parse_timestamp(self, line):
        """Parse timestamp from log line"""
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if match:
            return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
        return None

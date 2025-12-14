"""Utility functions for the flight tracker client"""
import os
import time
import logging
from datetime import datetime


def setup_logging(config):
    """Setup logging configuration"""
    log_level = getattr(logging, config.get("logging", {}).get("level", "INFO"))
    log_file = config.get("logging", {}).get("log_file", "flight_tracker.log")

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def format_duration(seconds):
    """Format duration in seconds to H:MM or HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_timestamp(timestamp=None):
    """Format timestamp to readable string"""
    if timestamp is None:
        timestamp = time.time()
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def truncate_string(text, max_length, suffix="..."):
    """Truncate string if longer than max_length"""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def safe_getattr(obj, attr, default="N/A"):
    """Safely get attribute from object with default value"""
    try:
        value = getattr(obj, attr, default)
        return value if value is not None else default
    except:
        return default

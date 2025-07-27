import os
import time
import logging
from datetime import datetime


def setup_logging(config):
    """Setup logging configuration"""
    log_level = getattr(logging, config.get("logging", {}).get("level", "INFO"))
    log_path = config.get("logging", {}).get("path", "/tmp/flight_tracker.log")

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )


def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


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
        return getattr(obj, attr, default)
    except:
        return default


def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)


def file_exists(path):
    """Check if file exists"""
    return os.path.isfile(path)


def get_file_size(path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(path)
    except OSError:
        return 0

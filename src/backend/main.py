from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import toml
import os
import time
import logging
from datetime import datetime
from collections import deque
from tracker import FlightTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# In-memory log storage for activity tracking
activity_logs = deque(maxlen=1000)  # Keep last 1000 logs


class ActivityLog(BaseModel):
    id: str
    timestamp: datetime
    level: str
    message: str
    category: str


def add_activity_log(level: str, message: str, category: str = "SYSTEM"):
    """Add a log entry to the activity log"""
    log_entry = {
        "id": f"{int(time.time() * 1000)}-{len(activity_logs)}",
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message,
        "category": category,
    }
    activity_logs.append(log_entry)

    # Also log to console for debugging
    print(f"[{category}] {level.upper()}: {message}")


app = FastAPI(title="Flight Tracker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
flight_tracker: FlightTracker = None
current_config = {}


class ConfigUpdate(BaseModel):
    address: str
    search_radius_meters: int = 3000
    max_flights: int = 20
    max_elapsed_time: int = 1800


def load_config():
    """Load configuration from config.toml"""
    global current_config
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")

    try:
        with open(config_path, "r") as f:
            current_config = toml.load(f)
        logger.info("Configuration loaded from config.toml")
    except Exception as e:
        logger.warning(f"Could not load config.toml: {e}, using defaults")
        current_config = {
            "main": {
                "address": "31 Maltings Place, Fulham, London, SW62BU",
                "search_radius_meters": 3000,
                "max_flights": 20,
                "max_elapsed_time": 1800,
            }
        }

    return current_config


def initialize_tracker():
    """Initialize the flight tracker with current config"""
    global flight_tracker
    config = load_config()
    tracker_config = config.get("main", {})
    flight_tracker = FlightTracker(tracker_config)
    add_activity_log("success", "Flight tracker initialized successfully", "SYSTEM")
    add_activity_log(
        "info",
        f"Tracking location: {tracker_config.get('address', 'Unknown')}",
        "SYSTEM",
    )
    add_activity_log(
        "info",
        f"Search radius: {tracker_config.get('search_radius_meters', 3000)}m",
        "SYSTEM",
    )


# Initialize on startup
add_activity_log("info", "Flight Tracker Backend API starting up...", "SYSTEM")
initialize_tracker()
add_activity_log("success", "Flight Tracker Backend API ready", "SYSTEM")


@app.get("/")
async def root():
    return {"message": "Flight Tracker API", "version": "1.0.0"}


@app.get("/flights")
async def get_flights():
    """Get current flights in the area - main endpoint for polling"""
    if not flight_tracker:
        add_activity_log("error", "Flight tracker not initialized", "API")
        raise HTTPException(status_code=500, detail="Flight tracker not initialized")

    try:
        flights = flight_tracker.get_flights()
        flight_count = len(flights)

        if flight_count > 0:
            add_activity_log(
                "info", f"Retrieved {flight_count} active flights", "RADAR"
            )
            # Log interesting flights
            for flight in flights[:2]:  # Log first 2 flights
                callsign = flight.callsign or "Unknown"
                altitude = flight.altitude or "N/A"
                add_activity_log(
                    "debug", f"Flight {callsign} detected at {altitude}ft", "FLIGHT"
                )
        else:
            add_activity_log("debug", "No flights detected in tracking area", "RADAR")

        return {
            "flights": [flight.to_dict() for flight in flights],
            "timestamp": time.time(),
            "location": current_config.get("main", {}).get("address", "Unknown"),
        }
    except Exception as e:
        add_activity_log("error", f"Failed to retrieve flights: {str(e)}", "API")
        logger.error(f"Error getting flights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current configuration"""
    add_activity_log("debug", "Configuration requested via API", "CONFIG")
    return current_config


@app.post("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration"""
    global current_config, flight_tracker

    try:
        add_activity_log(
            "info",
            f"Configuration update requested for address: {config_update.address}",
            "CONFIG",
        )

        # Update config
        if "main" not in current_config:
            current_config["main"] = {}

        old_address = current_config["main"].get("address", "Unknown")
        current_config["main"]["address"] = config_update.address
        current_config["main"]["search_radius_meters"] = (
            config_update.search_radius_meters
        )
        current_config["main"]["max_flights"] = config_update.max_flights
        current_config["main"]["max_elapsed_time"] = config_update.max_elapsed_time

        # Save to file
        config_path = os.path.join(os.path.dirname(__file__), "config.toml")
        with open(config_path, "w") as f:
            toml.dump(current_config, f)

        # Reinitialize tracker with new config
        initialize_tracker()

        add_activity_log(
            "success",
            f"Configuration updated successfully. Location changed from '{old_address}' to '{config_update.address}'",
            "CONFIG",
        )
        add_activity_log(
            "info",
            f"Search radius: {config_update.search_radius_meters}m, Max flights: {config_update.max_flights}",
            "CONFIG",
        )

        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        add_activity_log("error", f"Failed to update configuration: {str(e)}", "CONFIG")
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    add_activity_log("debug", "Health check requested", "HEALTH")
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "tracker_initialized": flight_tracker is not None,
    }


@app.get("/logs")
async def get_activity_logs():
    """Get activity logs from backend"""
    return {"logs": list(activity_logs)}


@app.delete("/logs")
async def clear_activity_logs():
    """Clear all activity logs from backend"""
    global activity_logs
    log_count = len(activity_logs)
    activity_logs.clear()
    add_activity_log(
        "info",
        f"Activity logs cleared by user request ({log_count} logs removed)",
        "SYSTEM",
    )
    return {"status": "success", "message": f"Cleared {log_count} logs"}


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="Flight Tracker Backend API")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)

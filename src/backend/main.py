from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import toml
import os
import time
import logging
from tracker import FlightTracker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Flight Tracker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
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
    logger.info("Flight tracker initialized")


# Initialize on startup
initialize_tracker()


@app.get("/")
async def root():
    return {"message": "Flight Tracker API", "version": "1.0.0"}


@app.get("/flights")
async def get_flights():
    """Get current flights in the area - main endpoint for polling"""
    if not flight_tracker:
        raise HTTPException(status_code=500, detail="Flight tracker not initialized")

    try:
        flights = flight_tracker.get_flights()
        return {
            "flights": [flight.to_dict() for flight in flights],
            "timestamp": time.time(),
            "location": current_config.get("main", {}).get("address", "Unknown"),
        }
    except Exception as e:
        logger.error(f"Error getting flights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current configuration"""
    return current_config


@app.post("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration"""
    global current_config, flight_tracker

    try:
        # Update config
        if "main" not in current_config:
            current_config["main"] = {}

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

        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "tracker_initialized": flight_tracker is not None,
    }


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

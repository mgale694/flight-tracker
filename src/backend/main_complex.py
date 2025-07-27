from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import toml
import os
import time
import logging
from typing import List
from tracker import FlightTracker, Voice, get_random_boot_face

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
    ],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
flight_tracker: FlightTracker = None
voice = Voice()
tracking_active = False
current_config = {}


class ConfigUpdate(BaseModel):
    address: str
    search_radius_meters: int = 3000
    max_flights: int = 20
    max_elapsed_time: int = 1800


class FlightData(BaseModel):
    callsign: str
    id: str
    latitude: float
    longitude: float
    altitude: str
    ground_speed: str
    origin_airport_name: str
    destination_airport_name: str
    origin_airport_iata: str
    destination_airport_iata: str
    airline_name: str
    aircraft_model: str
    registration: str


class RaspiConfig(BaseModel):
    ui: dict = {}
    logging: dict = {}
    api: dict = {}
    development: dict = {}


def load_config():
    """Load configuration from config.toml or use defaults"""
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


@app.on_event("startup")
async def startup_event():
    """Initialize the flight tracker on startup"""
    initialize_tracker()


@app.get("/")
async def root():
    return {"message": "Flight Tracker API", "version": "1.0.0"}


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

        # Reinitialize tracker
        if flight_tracker:
            flight_tracker.update_config(current_config["main"])

        return {"status": "success", "message": "Configuration updated"}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/boot")
async def get_boot_data():
    """Get boot screen data"""
    face, phrase = get_random_boot_face()
    return {
        "face": face,
        "phrase": phrase,
        "timestamp": time.strftime("%H:%M:%S"),
        "message": voice.on_starting(),
    }


@app.get("/flights")
async def get_flights():
    """Get current flights in the area"""
    if not flight_tracker:
        raise HTTPException(status_code=500, detail="Flight tracker not initialized")

    try:
        flights = flight_tracker.get_flights()
        return {
            "flights": [flight.to_dict() for flight in flights],
            "stats": flight_tracker.get_session_stats()
            if flight_tracker.start_time
            else None,
        }
    except Exception as e:
        logger.error(f"Error getting flights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/start")
async def start_session():
    """Start a new flight tracking session"""
    global tracking_active
    if not flight_tracker:
        raise HTTPException(status_code=500, detail="Flight tracker not initialized")

    flight_tracker.start_session()
    tracking_active = True

    return {"status": "success", "message": "Flight tracking session started"}


@app.post("/session/stop")
async def stop_session():
    """Stop the current flight tracking session"""
    global tracking_active
    tracking_active = False

    stats = (
        flight_tracker.get_session_stats()
        if flight_tracker and flight_tracker.start_time
        else {"flights_count": 0}
    )

    return {"status": "success", "message": "Flight tracking session stopped", "stats": stats}


@app.get("/session/status")
async def get_session_status():
    """Get current session status"""
    if not flight_tracker or not flight_tracker.start_time:
        return {"active": False, "stats": None}

    return {
        "active": tracking_active,
        "stats": flight_tracker.get_session_stats(),
        "should_continue": flight_tracker.should_continue(),
    }


@app.websocket("/ws")
@app.get("/demo/flight")
async def get_demo_flight():
    """Get a demo flight for testing the display"""
    import random

    # Mock flight data for testing
    demo_flights = [
        {
            "callsign": "BA123",
            "id": "demo1",
            "latitude": 51.4748,
            "longitude": -0.1879,
            "altitude": "35000",
            "ground_speed": "485",
            "origin_airport_name": "London Heathrow Airport",
            "destination_airport_name": "John F Kennedy International Airport",
            "origin_airport_iata": "LHR",
            "destination_airport_iata": "JFK",
            "airline_name": "British Airways",
            "aircraft_model": "Boeing 777-300ER",
            "registration": "G-STBF",
        },
        {
            "callsign": "VS401",
            "id": "demo2",
            "latitude": 51.4755,
            "longitude": -0.1885,
            "altitude": "28000",
            "ground_speed": "420",
            "origin_airport_name": "Manchester Airport",
            "destination_airport_name": "Los Angeles International Airport",
            "origin_airport_iata": "MAN",
            "destination_airport_iata": "LAX",
            "airline_name": "Virgin Atlantic",
            "aircraft_model": "Airbus A350-1000",
            "registration": "G-VNEW",
        },
        {
            "callsign": "EZY456",
            "id": "demo3",
            "latitude": 51.4742,
            "longitude": -0.1872,
            "altitude": "22000",
            "ground_speed": "380",
            "origin_airport_name": "Paris Charles de Gaulle Airport",
            "destination_airport_name": "Edinburgh Airport",
            "origin_airport_iata": "CDG",
            "destination_airport_iata": "EDI",
            "airline_name": "easyJet",
            "aircraft_model": "Airbus A320-214",
            "registration": "G-EZWB",
        },
    ]

    selected_flight = random.choice(demo_flights)
    mock_stats = {
        "flights_count": random.randint(1, 5),
        "elapsed_time": random.randint(60, 300),
        "elapsed_str": f"00:{random.randint(1, 5):02d}:{random.randint(10, 59):02d}",
        "location_short": "Maltings Place, United Kingdom",
    }

    return {"flight": selected_flight, "stats": mock_stats}


@app.get("/config/full")
async def get_full_config():
    """Get complete configuration including UI settings for raspi"""
    return current_config


@app.get("/config/raspi")
async def get_raspi_config():
    """Get raspi-specific configuration"""
    config = current_config.copy()
    # Remove any sensitive backend-only settings if needed
    return config


@app.post("/config/raspi")
async def update_raspi_config(config_update: dict):
    """Update raspi-specific configuration"""
    global current_config, flight_tracker

    try:
        # Update the full config with raspi settings
        current_config.update(config_update)

        # Save to file
        config_path = os.path.join(os.path.dirname(__file__), "config.toml")
        with open(config_path, "w") as f:
            toml.dump(current_config, f)

        # Reinitialize tracker if main config changed
        if "main" in config_update and flight_tracker:
            flight_tracker.update_config(current_config["main"])

        return {"status": "success", "message": "Raspi configuration updated"}
    except Exception as e:
        logger.error(f"Error updating raspi config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/flights/live")
async def get_live_flights():
    """Get live flights with real-time data (for raspi use)"""
    if not flight_tracker:
        raise HTTPException(status_code=500, detail="Flight tracker not initialized")

    try:
        flights = flight_tracker.get_flights()
        flight_list = []

        for flight in flights:
            # Get detailed flight information
            detailed_flight = flight_tracker.get_flight_details(flight)
            flight_list.append(detailed_flight.to_dict())

        return {
            "flights": flight_list,
            "stats": flight_tracker.get_session_stats()
            if flight_tracker.start_time
            else None,
            "timestamp": time.time(),
            "location": {
                "address": flight_tracker.location.address
                if flight_tracker.location
                else None,
                "latitude": flight_tracker.location.latitude
                if flight_tracker.location
                else None,
                "longitude": flight_tracker.location.longitude
                if flight_tracker.location
                else None,
            },
        }
    except Exception as e:
        logger.error(f"Error getting live flights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flights/process")
async def process_flight(flight_data: dict):
    """Process a flight detection (used by raspi for tracking)"""
    if not flight_tracker:
        raise HTTPException(status_code=500, detail="Flight tracker not initialized")

    try:
        # Create a Flight object from the provided data
        from tracker import Flight

        flight = Flight(flight_data)

        # Process the flight
        is_new = flight_tracker.process_flight(flight)

        return {
            "processed": True,
            "is_new_flight": is_new,
            "stats": flight_tracker.get_session_stats()
            if flight_tracker.start_time
            else None,
        }
    except Exception as e:
        logger.error(f"Error processing flight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "tracker_initialized": flight_tracker is not None,
        "session_active": tracking_active,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

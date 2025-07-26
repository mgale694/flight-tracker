from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import toml
import os
import asyncio
import time
import json
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
websocket_connections: List[WebSocket] = []
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


async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected websockets"""
    if websocket_connections:
        disconnected = []
        for websocket in websocket_connections:
            try:
                await websocket.send_text(json.dumps(message))
            except Exception:
                disconnected.append(websocket)

        # Remove disconnected websockets
        for ws in disconnected:
            websocket_connections.remove(ws)


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

    await broadcast_to_websockets(
        {
            "type": "session_started",
            "message": voice.on_starting(),
            "timestamp": time.strftime("%H:%M:%S"),
        }
    )

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

    await broadcast_to_websockets(
        {
            "type": "session_stopped",
            "message": voice.on_session_complete(stats["flights_count"]),
            "stats": stats,
            "timestamp": time.strftime("%H:%M:%S"),
        }
    )

    return {"status": "success", "message": "Flight tracking session stopped"}


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
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)

    try:
        while True:
            # Keep connection alive and send periodic updates if tracking is active
            if tracking_active and flight_tracker and flight_tracker.start_time:
                # Get current flights and stats
                flights = flight_tracker.get_flights()
                stats = flight_tracker.get_session_stats()

                # Check for new flights
                new_flights = []
                for flight in flights:
                    if flight_tracker.process_flight(flight):
                        new_flights.append(flight)

                # Send updates if there are new flights
                if new_flights:
                    for flight in new_flights:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "new_flight",
                                    "flight": flight.to_dict(),
                                    "stats": flight_tracker.get_session_stats(),
                                    "message": voice.on_flight_detected(
                                        flight.callsign
                                    ),
                                    "timestamp": time.strftime("%H:%M:%S"),
                                }
                            )
                        )

                # Send periodic stats update
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "stats_update",
                            "stats": stats,
                            "timestamp": time.strftime("%H:%M:%S"),
                        }
                    )
                )

            await asyncio.sleep(2)  # Update every 2 seconds

    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

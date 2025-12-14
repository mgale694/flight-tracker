"""FastAPI backend for flight tracker system."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import toml
import os
from pathlib import Path

from tracker import FlightTracker
from logger import activity_logger


# Configuration
CONFIG_FILE = Path(__file__).parent / "config.toml"


class ConfigUpdate(BaseModel):
    """Model for configuration updates."""
    address: Optional[str] = None
    search_radius_meters: Optional[int] = Field(None, ge=100, le=50000)
    max_flights: Optional[int] = Field(None, ge=1, le=100)
    max_elapsed_time: Optional[int] = Field(None, ge=60, le=7200)


class FlightResponse(BaseModel):
    """Model for flight data response."""
    id: str
    callsign: str
    registration: str
    aircraft: str
    airline: str
    origin: str
    destination: str
    altitude: int
    speed: int
    heading: int
    latitude: float
    longitude: float
    distance: float
    timestamp: str


class ActivityResponse(BaseModel):
    """Model for activity log response."""
    timestamp: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None


# Initialize FastAPI app
app = FastAPI(
    title="Flight Tracker API",
    description="Backend API for tracking flights in a specific geographic area",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
flight_tracker = FlightTracker()
config_cache: Optional[Dict] = None


def load_config() -> Dict:
    """Load configuration from TOML file.
    
    Returns:
        Configuration dictionary
    """
    global config_cache
    try:
        config = toml.load(CONFIG_FILE)
        config_cache = config
        return config
    except Exception as e:
        activity_logger.log("ERROR", f"Failed to load config: {str(e)}")
        if config_cache:
            return config_cache
        # Return default config
        return {
            "main": {
                "address": "San Francisco, CA",
                "search_radius_meters": 3000,
                "max_flights": 20,
                "max_elapsed_time": 1800
            }
        }


def save_config(config: Dict) -> None:
    """Save configuration to TOML file.
    
    Args:
        config: Configuration dictionary to save
    """
    global config_cache
    try:
        with open(CONFIG_FILE, 'w') as f:
            toml.dump(config, f)
        config_cache = config
        activity_logger.log("CONFIG", "Configuration saved successfully")
    except Exception as e:
        activity_logger.log("ERROR", f"Failed to save config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    activity_logger.log("SYSTEM", "Flight Tracker API starting up")
    load_config()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    activity_logger.log("SYSTEM", "Flight Tracker API shutting down")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Flight Tracker API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": activity_logger.log("INFO", "Health check performed")["timestamp"]
    }


@app.get("/api/flights", response_model=List[FlightResponse])
async def get_flights():
    """Get current flights in the configured area.
    
    Returns:
        List of flights
    """
    try:
        config = load_config()
        main_config = config.get("main", {})
        
        address = main_config.get("address", "San Francisco, CA")
        radius = main_config.get("search_radius_meters", 3000)
        max_flights = main_config.get("max_flights", 20)
        
        activity_logger.log(
            "RADAR", 
            f"Fetching flights for {address} (radius: {radius}m)",
            {"address": address, "radius": radius}
        )
        
        flights = flight_tracker.get_flights_in_area(
            address=address,
            radius_meters=radius,
            max_flights=max_flights
        )
        
        activity_logger.log(
            "FLIGHT",
            f"Found {len(flights)} flight(s) in area",
            {"count": len(flights)}
        )
        
        return flights
        
    except ValueError as e:
        activity_logger.log("ERROR", f"Geocoding error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        activity_logger.log("ERROR", f"Error fetching flights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching flights: {str(e)}")


@app.get("/api/config")
async def get_config():
    """Get current configuration.
    
    Returns:
        Current configuration
    """
    config = load_config()
    activity_logger.log("CONFIG", "Configuration retrieved")
    return config


@app.put("/api/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration.
    
    Args:
        config_update: Configuration updates
        
    Returns:
        Updated configuration
    """
    try:
        config = load_config()
        main_config = config.get("main", {})
        
        # Update only provided fields
        updates = {}
        if config_update.address is not None:
            main_config["address"] = config_update.address
            updates["address"] = config_update.address
            # Clear cached coordinates when address changes
            flight_tracker.last_address = None
            flight_tracker.last_coordinates = None
        
        if config_update.search_radius_meters is not None:
            main_config["search_radius_meters"] = config_update.search_radius_meters
            updates["search_radius_meters"] = config_update.search_radius_meters
        
        if config_update.max_flights is not None:
            main_config["max_flights"] = config_update.max_flights
            updates["max_flights"] = config_update.max_flights
        
        if config_update.max_elapsed_time is not None:
            main_config["max_elapsed_time"] = config_update.max_elapsed_time
            updates["max_elapsed_time"] = config_update.max_elapsed_time
        
        config["main"] = main_config
        save_config(config)
        
        activity_logger.log(
            "CONFIG",
            "Configuration updated",
            updates
        )
        
        return config
        
    except Exception as e:
        activity_logger.log("ERROR", f"Failed to update config: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@app.get("/api/activities", response_model=List[ActivityResponse])
async def get_activities(
    limit: Optional[int] = None,
    category: Optional[str] = None
):
    """Get activity logs.
    
    Args:
        limit: Maximum number of activities to return
        category: Filter by category (SYSTEM, RADAR, FLIGHT, CONFIG, ERROR, INFO)
        
    Returns:
        List of activity logs
    """
    activities = activity_logger.get_activities(limit=limit, category=category)
    return activities


@app.delete("/api/activities")
async def clear_activities():
    """Clear all activity logs.
    
    Returns:
        Confirmation message
    """
    activity_logger.clear()
    return {"message": "Activity logs cleared"}


@app.get("/api/flight/{flight_id}")
async def get_flight_details(flight_id: str):
    """Get detailed information about a specific flight.
    
    Args:
        flight_id: Flight identifier
        
    Returns:
        Flight details
    """
    try:
        details = flight_tracker.get_flight_details(flight_id)
        if details is None:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        activity_logger.log(
            "FLIGHT",
            f"Retrieved details for flight {flight_id}"
        )
        
        return details
        
    except HTTPException:
        raise
    except Exception as e:
        activity_logger.log("ERROR", f"Error fetching flight details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching flight details: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    activity_logger.log("SYSTEM", "Starting Flight Tracker API server")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

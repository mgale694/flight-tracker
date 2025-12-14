"""Flight-related API routes."""
from fastapi import APIRouter, HTTPException
from typing import List
from models import FlightData
from services import FlightTrackerService, ConfigService, ActivityLoggerService
from models.enums import ActivityCategory

router = APIRouter(prefix="/api", tags=["flights"])


def setup_flight_routes(
    flight_service: FlightTrackerService,
    config_service: ConfigService,
    activity_service: ActivityLoggerService
):
    """Set up flight routes with injected services."""
    
    @router.get("/flights", response_model=List[FlightData])
    async def get_flights():
        """Get current flights in the configured area.
        
        Returns:
            List of flights
        """
        try:
            main_config = config_service.get_main_config()
            
            address = main_config.get("address", "San Francisco, CA")
            radius = main_config.get("search_radius_meters", 3000)
            max_flights = main_config.get("max_flights", 20)
            
            activity_service.log(
                ActivityCategory.RADAR, 
                f"Fetching flights for {address} (radius: {radius}m)",
                {"address": address, "radius": radius}
            )
            
            flights = flight_service.get_flights_in_area(
                address=address,
                radius_meters=radius,
                max_flights=max_flights
            )
            
            activity_service.log(
                ActivityCategory.FLIGHT,
                f"Found {len(flights)} flight(s) in area",
                {"count": len(flights)}
            )
            
            return flights
            
        except ValueError as e:
            activity_service.log(ActivityCategory.ERROR, f"Geocoding error: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            activity_service.log(ActivityCategory.ERROR, f"Error fetching flights: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching flights: {str(e)}")
    
    @router.get("/flight/{flight_id}")
    async def get_flight_details(flight_id: str):
        """Get detailed information about a specific flight.
        
        Args:
            flight_id: Flight identifier
            
        Returns:
            Flight details
        """
        try:
            details = flight_service.get_flight_details(flight_id)
            if details is None:
                raise HTTPException(status_code=404, detail="Flight not found")
            
            activity_service.log(
                ActivityCategory.FLIGHT,
                f"Retrieved details for flight {flight_id}"
            )
            
            return details
            
        except HTTPException:
            raise
        except Exception as e:
            activity_service.log(ActivityCategory.ERROR, f"Error fetching flight details: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error fetching flight details: {str(e)}")
    
    return router

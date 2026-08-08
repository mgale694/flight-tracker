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
            config = config_service.load_config()
            main_config = config.get("main", {})
            viewing_zone = config.get("viewing_zone", {})
            
            address = main_config.get("address", "San Francisco, CA")
            radius = round(
                float(
                    viewing_zone.get(
                        "max_distance_km",
                        main_config.get("search_radius_meters", 3000) / 1000,
                    )
                )
                * 1000
            )
            min_distance = float(viewing_zone.get("min_distance_km", 0)) * 1000
            bearing = float(viewing_zone.get("bearing_degrees", 0))
            field_of_view = float(viewing_zone.get("field_of_view_degrees", 360))
            max_flights = main_config.get("max_flights", 20)
            
            activity_service.log(
                ActivityCategory.RADAR, 
                f"Fetching flights for {address} ({bearing}°, {field_of_view}° view)",
                {
                    "address": address,
                    "bearing_degrees": bearing,
                    "field_of_view_degrees": field_of_view,
                    "min_distance_meters": min_distance,
                    "max_distance_meters": radius,
                }
            )
            
            flights = flight_service.get_flights_in_area(
                address=address,
                radius_meters=radius,
                max_flights=max_flights,
                bearing_degrees=bearing,
                field_of_view_degrees=field_of_view,
                min_distance_meters=min_distance,
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

"""Configuration-related API routes."""
from fastapi import APIRouter, HTTPException, Query
from models import ConfigUpdate
from services import ConfigService, ActivityLoggerService, FlightTrackerService
from models.enums import ActivityCategory

router = APIRouter(prefix="/api", tags=["config"])


def setup_config_routes(
    config_service: ConfigService,
    activity_service: ActivityLoggerService,
    flight_service: FlightTrackerService
):
    """Set up config routes with injected services."""
    
    @router.get("/config")
    async def get_config():
        """Get current configuration.
        
        Returns:
            Current configuration
        """
        config = config_service.load_config()
        activity_service.log(ActivityCategory.CONFIG, "Configuration retrieved")
        return config

    @router.get("/location-preview")
    def get_location_preview(
        address: str = Query(min_length=3, max_length=300),
    ):
        """Resolve a user-entered location for the settings map."""

        try:
            location = flight_service.resolve_location(address)
            activity_service.log(
                ActivityCategory.CONFIG,
                "Window location resolved",
                {"query": address, "formatted_address": location["formatted_address"]},
            )
            return location
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    
    @router.put("/config")
    async def update_config(config_update: ConfigUpdate):
        """Update configuration.
        
        Args:
            config_update: Configuration updates
            
        Returns:
            Updated configuration
        """
        try:
            config, updates = config_service.update_config(config_update)
            
            # Keep a location that was just resolved for the settings preview.
            if (
                "address" in updates
                and not flight_service.has_cached_location(str(updates["address"]))
            ):
                flight_service.clear_cache()
            
            activity_service.log(
                ActivityCategory.CONFIG,
                "Configuration updated",
                updates
            )
            
            return config
            
        except Exception as e:
            activity_service.log(ActivityCategory.ERROR, f"Failed to update config: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")
    
    return router

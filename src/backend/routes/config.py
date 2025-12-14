"""Configuration-related API routes."""
from fastapi import APIRouter, HTTPException
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
            
            # Clear cached coordinates if address changed
            if "address" in updates:
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

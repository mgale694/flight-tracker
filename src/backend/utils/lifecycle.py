"""Application lifecycle management utilities."""
from pathlib import Path
from services import FlightTrackerService, ConfigService, ActivityLoggerService
from models.enums import ActivityCategory


class AppLifecycle:
    """Manages application startup and shutdown."""
    
    def __init__(
        self,
        config_service: ConfigService,
        activity_service: ActivityLoggerService,
        flight_service: FlightTrackerService
    ):
        """Initialize app lifecycle manager.
        
        Args:
            config_service: Configuration service instance
            activity_service: Activity logging service instance
            flight_service: Flight tracker service instance
        """
        self.config_service = config_service
        self.activity_service = activity_service
        self.flight_service = flight_service
    
    async def startup(self):
        """Execute startup tasks."""
        self.activity_service.log(ActivityCategory.SYSTEM, "Flight Tracker API starting up")
        # Load initial configuration
        self.config_service.load_config()
    
    async def shutdown(self):
        """Execute shutdown tasks."""
        self.activity_service.log(ActivityCategory.SYSTEM, "Flight Tracker API shutting down")
        # Clear any cached data
        self.flight_service.clear_cache()

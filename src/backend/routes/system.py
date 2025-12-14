"""Health and system-related API routes."""
from fastapi import APIRouter
from models import HealthResponse, APIResponse
from services import ActivityLoggerService
from models.enums import ActivityCategory, APIStatus
import subprocess
import logging

router = APIRouter(tags=["system"])


def setup_system_routes(activity_service: ActivityLoggerService):
    """Set up system routes with injected services."""
    
    @router.get("/", response_model=APIResponse)
    async def root():
        """Root endpoint with API information.
        
        Returns:
            API information
        """
        return APIResponse(
            name="Flight Tracker API",
            version="1.0.0",
            status=APIStatus.RUNNING
        )
    
    @router.get("/api/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint.
        
        Returns:
            Health status
        """
        timestamp = activity_service.log(ActivityCategory.INFO, "Health check performed")["timestamp"]
        return HealthResponse(
            status=APIStatus.HEALTHY,
            timestamp=timestamp
        )
    
    @router.post("/api/system/clear-display")
    async def clear_display():
        """Clear the e-ink display.
        
        Returns:
            Success status
        """
        try:
            # Send signal to clear display via systemctl or direct command
            result = subprocess.run(
                ["pkill", "-USR1", "-f", "raspi.*agent"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            activity_service.log(ActivityCategory.INFO, "Display clear requested")
            
            return {
                "status": "success",
                "message": "Display clear signal sent"
            }
        except Exception as e:
            logging.error(f"Failed to clear display: {e}")
            activity_service.log(ActivityCategory.ERROR, f"Display clear failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @router.post("/api/system/shutdown")
    async def shutdown_system():
        """Shutdown the flight tracker system.
        
        Returns:
            Success status
        """
        try:
            activity_service.log(ActivityCategory.INFO, "System shutdown requested")
            
            # Stop the flight tracker services
            subprocess.Popen(
                ["bash", "-c", "sleep 1 && pkill -TERM -f 'flight-tracker'"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return {
                "status": "success",
                "message": "Shutdown initiated"
            }
        except Exception as e:
            logging.error(f"Failed to shutdown: {e}")
            activity_service.log(ActivityCategory.ERROR, f"Shutdown failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    return router

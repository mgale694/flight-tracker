"""Health and system-related API routes."""
from fastapi import APIRouter
from models import HealthResponse, APIResponse
from services import ActivityLoggerService
from models.enums import ActivityCategory, APIStatus

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
    
    return router

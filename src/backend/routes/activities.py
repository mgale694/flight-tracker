"""Activity log-related API routes."""
from fastapi import APIRouter
from typing import List, Optional
from models import ActivityLog, MessageResponse
from services import ActivityLoggerService

router = APIRouter(prefix="/api", tags=["activities"])


def setup_activity_routes(activity_service: ActivityLoggerService):
    """Set up activity routes with injected services."""
    
    @router.get("/activities", response_model=List[ActivityLog])
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
        activities = activity_service.get_activities(limit=limit, category=category)
        return activities
    
    @router.delete("/activities", response_model=MessageResponse)
    async def clear_activities():
        """Clear all activity logs.
        
        Returns:
            Confirmation message
        """
        activity_service.clear()
        return MessageResponse(message="Activity logs cleared")
    
    return router

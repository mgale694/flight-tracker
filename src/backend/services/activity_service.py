"""Activity logging service."""
from datetime import datetime
from typing import List, Dict, Optional, Any
from collections import deque
from models.enums import ActivityCategory


class ActivityLoggerService:
    """Service for managing activity logs with categories and rotation."""
    
    def __init__(self, max_activities: int = 500):
        """Initialize the activity logger service.
        
        Args:
            max_activities: Maximum number of activities to store (FIFO)
        """
        self.max_activities = max_activities
        self.activities: deque = deque(maxlen=max_activities)
    
    def log(
        self, 
        category: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log an activity.
        
        Args:
            category: Activity category (SYSTEM, RADAR, FLIGHT, CONFIG, ERROR, INFO)
            message: Log message
            details: Optional additional details
            
        Returns:
            The activity log entry
        """
        activity = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "category": category.upper(),
            "message": message,
        }
        
        if details:
            activity["details"] = details
        
        self.activities.append(activity)
        return activity
    
    def get_activities(
        self, 
        limit: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get activity logs.
        
        Args:
            limit: Maximum number of activities to return (most recent first)
            category: Filter by category
            
        Returns:
            List of activity log entries
        """
        activities = list(self.activities)
        
        # Filter by category if specified
        if category:
            activities = [a for a in activities if a["category"] == category.upper()]
        
        # Reverse to get most recent first
        activities.reverse()
        
        # Apply limit
        if limit:
            activities = activities[:limit]
        
        return activities
    
    def clear(self):
        """Clear all activity logs."""
        self.activities.clear()
        self.log(ActivityCategory.SYSTEM, "Activity logs cleared")

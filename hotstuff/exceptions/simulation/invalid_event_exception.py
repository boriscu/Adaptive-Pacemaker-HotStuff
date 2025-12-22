"""
InvalidEventException.

Raised when an invalid event is encountered in the simulation.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class InvalidEventException(HotStuffException):
    """
    Exception raised when an event is invalid or cannot be processed.
    
    This can occur when:
    - Event type is unknown
    - Event data is malformed
    - Event is scheduled for an invalid time
    """
    
    def __init__(self, message: str, event_type: str = None, event_id: str = None, scheduled_time: int = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the event error.
            event_type: Type of the invalid event.
            event_id: ID of the invalid event.
            scheduled_time: Scheduled time of the event.
        """
        context = {}
        if event_type:
            context["event_type"] = event_type
        if event_id:
            context["event_id"] = event_id
        if scheduled_time is not None:
            context["scheduled_time"] = scheduled_time
        super().__init__(message, context)

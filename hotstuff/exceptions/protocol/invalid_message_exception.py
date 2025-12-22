"""
InvalidMessageException.

Raised when a received message is invalid or unexpected.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class InvalidMessageException(HotStuffException):
    """
    Exception raised when a message fails validation.
    
    This can occur when:
    - Message type doesn't match current phase
    - Message is from an unexpected sender
    - Message contains invalid data
    """
    
    def __init__(self, message: str, message_type: str = None, sender_id: int = None, view_number: int = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the validation failure.
            message_type: Type of the invalid message.
            sender_id: ID of the message sender.
            view_number: View number of the message.
        """
        context = {}
        if message_type:
            context["message_type"] = message_type
        if sender_id is not None:
            context["sender_id"] = sender_id
        if view_number is not None:
            context["view_number"] = view_number
        super().__init__(message, context)

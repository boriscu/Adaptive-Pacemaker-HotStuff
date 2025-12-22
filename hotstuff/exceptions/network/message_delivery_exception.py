"""
MessageDeliveryException.

Raised when a message cannot be delivered.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class MessageDeliveryException(HotStuffException):
    """
    Exception raised when message delivery fails.
    
    This can occur when:
    - Target replica doesn't exist
    - Network is partitioned
    - Message queue is full
    """
    
    def __init__(self, message: str, sender_id: int = None, target_id: int = None, message_type: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the delivery failure.
            sender_id: ID of the sending replica.
            target_id: ID of the target replica.
            message_type: Type of message that failed to deliver.
        """
        context = {}
        if sender_id is not None:
            context["sender_id"] = sender_id
        if target_id is not None:
            context["target_id"] = target_id
        if message_type:
            context["message_type"] = message_type
        super().__init__(message, context)

"""
SafetyViolationException.

Raised when a safety rule of the protocol is violated.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class SafetyViolationException(HotStuffException):
    """
    Exception raised when a protocol safety rule is violated.
    
    This is a critical exception that indicates a bug in the implementation
    or an attempted attack. Safety violations should never occur in
    correct implementations with honest participants.
    """
    
    def __init__(self, message: str, replica_id: int = None, view_number: int = None, rule_violated: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the safety violation.
            replica_id: ID of the replica where violation occurred.
            view_number: View number when violation occurred.
            rule_violated: Name of the safety rule that was violated.
        """
        context = {}
        if replica_id is not None:
            context["replica_id"] = replica_id
        if view_number is not None:
            context["view_number"] = view_number
        if rule_violated:
            context["rule_violated"] = rule_violated
        super().__init__(message, context)

"""
PhaseViolationException.

Raised when an operation is attempted in an incorrect phase.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class PhaseViolationException(HotStuffException):
    """
    Exception raised when an action is attempted in the wrong phase.
    
    Each phase in Basic HotStuff expects specific messages and actions.
    This exception is raised when the protocol flow is violated.
    """
    
    def __init__(self, message: str, current_phase: str = None, expected_phase: str = None, replica_id: int = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the phase violation.
            current_phase: The current phase of the replica.
            expected_phase: The expected phase for the operation.
            replica_id: ID of the replica where violation occurred.
        """
        context = {}
        if current_phase:
            context["current_phase"] = current_phase
        if expected_phase:
            context["expected_phase"] = expected_phase
        if replica_id is not None:
            context["replica_id"] = replica_id
        super().__init__(message, context)

"""
InvalidQCException.

Raised when a Quorum Certificate is invalid or malformed.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class InvalidQCException(HotStuffException):
    """
    Exception raised when a QC fails validation.
    
    This can occur when:
    - QC has insufficient signatures
    - QC signatures don't match the claimed block
    - QC type doesn't match expected phase
    """
    
    def __init__(self, message: str, qc_type: str = None, expected_signatures: int = None, actual_signatures: int = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the validation failure.
            qc_type: Type of the invalid QC.
            expected_signatures: Expected number of signatures.
            actual_signatures: Actual number of signatures found.
        """
        context = {}
        if qc_type:
            context["qc_type"] = qc_type
        if expected_signatures is not None:
            context["expected_signatures"] = expected_signatures
        if actual_signatures is not None:
            context["actual_signatures"] = actual_signatures
        super().__init__(message, context)

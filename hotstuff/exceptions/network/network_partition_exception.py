"""
NetworkPartitionException.

Raised when a network partition is detected or simulated.
"""

from typing import List

from hotstuff.exceptions.base_exception import HotStuffException


class NetworkPartitionException(HotStuffException):
    """
    Exception raised when a network partition affects communication.
    
    This is primarily used in fault injection scenarios during testing.
    """
    
    def __init__(self, message: str, partitioned_replicas: List[int] = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the partition.
            partitioned_replicas: List of replica IDs that are partitioned.
        """
        context = {}
        if partitioned_replicas:
            context["partitioned_replicas"] = partitioned_replicas
        super().__init__(message, context)

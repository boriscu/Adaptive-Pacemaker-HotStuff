"""
FaultType enumeration.

Defines the types of faults that can be injected into replicas for testing.
"""

from enum import Enum
from enum import auto


class FaultType(Enum):
    """
    Enumeration of fault types for simulation.
    
    NONE: No fault, replica operates correctly.
    CRASH: Replica stops responding completely (crash fault).
    SILENT: Replica receives messages but doesn't send votes (passive Byzantine).
    DOUBLE_VOTE: Replica may vote for conflicting proposals (active Byzantine).
    RANDOM_DROP: Replica randomly drops some messages (unreliable Byzantine).
    """
    
    NONE = auto()
    CRASH = auto()
    SILENT = auto()
    DOUBLE_VOTE = auto()
    RANDOM_DROP = auto()

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
    CRASH: Replica stops responding (crash fault).
    BYZANTINE: Replica may behave arbitrarily (not implemented in basic simulation).
    """
    
    NONE = auto()
    CRASH = auto()
    BYZANTINE = auto()

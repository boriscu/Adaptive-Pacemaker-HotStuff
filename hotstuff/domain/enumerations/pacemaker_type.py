"""
PacemakerType enumeration.

Defines the available pacemaker strategies for the simulation.
"""

from enum import Enum
from enum import auto


class PacemakerType(Enum):
    """
    Enumeration of pacemaker strategies.
    
    BASELINE: Fixed timeout duration, simple view increment on timeout.
    ADAPTIVE: EMA-based timeout adjustment based on observed view durations.
    """
    
    BASELINE = auto()
    ADAPTIVE = auto()

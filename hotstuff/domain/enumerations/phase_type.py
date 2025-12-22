"""
PhaseType enumeration.

Defines the phases in Basic HotStuff consensus round.
Each view progresses through these phases sequentially.
"""

from enum import Enum
from enum import auto


class PhaseType(Enum):
    """
    Enumeration of phases in a Basic HotStuff consensus round.
    
    A view progresses through: PREPARE -> PRE_COMMIT -> COMMIT -> DECIDE.
    The NEW_VIEW phase represents the initial state when entering a new view.
    """
    
    NEW_VIEW = auto()
    PREPARE = auto()
    PRE_COMMIT = auto()
    COMMIT = auto()
    DECIDE = auto()

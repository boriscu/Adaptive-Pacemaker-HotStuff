"""
EventType enumeration.

Defines all event types for the discrete-event simulation.
"""

from enum import Enum
from enum import auto


class EventType(Enum):
    """
    Enumeration of simulation event types.
    
    Each event type corresponds to a meaningful protocol event that can be
    visualized and stepped through in the UI.
    """
    
    MESSAGE_SEND = auto()
    MESSAGE_RECEIVE = auto()
    VOTE_SEND = auto()
    QC_FORMATION = auto()
    PHASE_TRANSITION = auto()
    LOCK_UPDATE = auto()
    COMMIT = auto()
    VIEW_CHANGE = auto()
    TIMEOUT = auto()
    PROPOSAL = auto()
    EXECUTE = auto()

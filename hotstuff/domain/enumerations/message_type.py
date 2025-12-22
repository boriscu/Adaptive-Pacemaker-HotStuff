"""
MessageType enumeration.

Defines all message types used in the HotStuff protocol as per the paper.
Maps directly to the type field in Msg(type, node, qc).
"""

from enum import Enum
from enum import auto


class MessageType(Enum):
    """
    Enumeration of all message types in the HotStuff protocol.
    
    These types correspond to the different phases and control messages
    defined in Algorithm 2 (Basic HotStuff) of the paper.
    """
    
    NEW_VIEW = auto()
    PREPARE = auto()
    PREPARE_VOTE = auto()
    PRE_COMMIT = auto()
    PRE_COMMIT_VOTE = auto()
    COMMIT = auto()
    COMMIT_VOTE = auto()
    DECIDE = auto()

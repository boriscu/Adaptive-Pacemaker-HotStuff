"""
ReplicaRole enumeration.

Defines the roles a replica can have in a given view.
As per the paper, a replica can have multiple roles concurrently.
"""

from enum import Enum
from enum import auto


class ReplicaRole(Enum):
    """
    Enumeration of replica roles.
    
    LEADER: The designated leader for the current view, responsible for proposing blocks.
    REPLICA: A non-leader participant that votes on proposals.
    
    Note: As per Section 4.3 of the paper, a replica can have multiple roles,
    and role blocks can proceed concurrently.
    """
    
    LEADER = auto()
    REPLICA = auto()

"""
CommitEvent.

Event representing a block being committed.
"""

from pydantic import Field

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.event_type import EventType
from hotstuff.simulation.events.base_event import BaseEvent


class CommitEvent(BaseEvent):
    """Event representing a block commit."""
    
    event_type: EventType = Field(
        default=EventType.COMMIT,
        description="Always COMMIT"
    )
    replica_id: ReplicaId = Field(description="ID of the replica committing")
    block_hash: BlockHash = Field(description="Hash of the committed block")
    block_height: int = Field(description="Height of the committed block")

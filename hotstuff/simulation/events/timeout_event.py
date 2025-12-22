"""
TimeoutEvent.

Event representing a pacemaker timeout.
"""

from pydantic import Field

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.enumerations.event_type import EventType
from hotstuff.simulation.events.base_event import BaseEvent


class TimeoutEvent(BaseEvent):
    """Event representing a timeout in a view."""
    
    event_type: EventType = Field(
        default=EventType.TIMEOUT,
        description="Always TIMEOUT"
    )
    replica_id: ReplicaId = Field(description="ID of the replica that timed out")
    view_number: ViewNumber = Field(description="View that timed out")

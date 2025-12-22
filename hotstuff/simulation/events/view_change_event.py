"""
ViewChangeEvent.

Event representing a view change.
"""

from pydantic import Field

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.enumerations.event_type import EventType
from hotstuff.simulation.events.base_event import BaseEvent


class ViewChangeEvent(BaseEvent):
    """Event representing a view change."""
    
    event_type: EventType = Field(
        default=EventType.VIEW_CHANGE,
        description="Always VIEW_CHANGE"
    )
    replica_id: ReplicaId = Field(description="ID of the replica changing views")
    old_view: ViewNumber = Field(description="Previous view number")
    new_view: ViewNumber = Field(description="New view number")

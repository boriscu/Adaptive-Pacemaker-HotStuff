"""
MessageReceiveEvent.

Event representing a message being received.
"""

from pydantic import Field

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.event_type import EventType
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.simulation.events.base_event import BaseEvent


class MessageReceiveEvent(BaseEvent):
    """Event representing a message being received."""
    
    event_type: EventType = Field(
        default=EventType.MESSAGE_RECEIVE,
        description="Always MESSAGE_RECEIVE"
    )
    sender_id: ReplicaId = Field(description="ID of the sending replica")
    recipient_id: ReplicaId = Field(description="ID of the receiving replica")
    message_type: MessageType = Field(description="Type of message received")
    message_id: str = Field(description="ID of the message")

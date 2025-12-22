"""
MessageSendEvent.

Event representing a message being sent.
"""

from pydantic import Field

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.event_type import EventType
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.simulation.events.base_event import BaseEvent


class MessageSendEvent(BaseEvent):
    """Event representing a message being sent."""
    
    event_type: EventType = Field(
        default=EventType.MESSAGE_SEND,
        description="Always MESSAGE_SEND"
    )
    sender_id: ReplicaId = Field(description="ID of the sending replica")
    target_id: ReplicaId = Field(description="ID of the target replica")
    message_type: MessageType = Field(description="Type of message sent")
    message_id: str = Field(description="ID of the message")

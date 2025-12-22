"""
Base message model.

Abstract base class for all HotStuff protocol messages.
Corresponds to Msg(type, node, qc) in Algorithm 1.
"""

from abc import ABC
from typing import Optional
import uuid

from pydantic import BaseModel
from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.message_type import MessageType


class BaseMessage(BaseModel, ABC):
    """
    Base class for all HotStuff protocol messages.
    
    As per Algorithm 1 in the paper, Msg(type, node, qc) sets:
    - type: message type
    - viewNumber: curView
    - node: block reference
    - justify: QC
    
    This base class provides common fields for all messages.
    """
    
    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique identifier for this message"
    )
    message_type: MessageType = Field(
        description="Type of this message"
    )
    sender_id: ReplicaId = Field(
        description="ID of the replica that sent this message"
    )
    view_number: ViewNumber = Field(
        description="View number when this message was created"
    )
    timestamp: int = Field(
        default=0,
        description="Simulation timestamp when message was created"
    )
    target_id: Optional[ReplicaId] = Field(
        default=None,
        description="Target replica ID, None for broadcast messages"
    )
    
    model_config = {"frozen": True}

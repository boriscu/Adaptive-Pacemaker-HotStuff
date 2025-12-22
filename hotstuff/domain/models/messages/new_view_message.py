"""
NewViewMessage model.

Sent by replicas to the next leader when entering a new view.
Corresponds to Msg(new-view, ⊥, prepareQC) in Algorithm 2.
"""

from typing import Optional

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_message import BaseMessage


class NewViewMessage(BaseMessage):
    """
    Message sent to the next leader when entering a new view.
    
    As per Algorithm 2, in the Finally block:
    - send Msg(new-view, ⊥, prepareQC) to leader(curView + 1)
    
    The justify_qc is the sender's prepareQC (highest QC they know of).
    """
    
    message_type: MessageType = Field(
        default=MessageType.NEW_VIEW,
        description="Always NEW_VIEW for this message type"
    )
    justify_qc: Optional[QuorumCertificate] = Field(
        default=None,
        description="The sender's prepareQC (highest known QC)"
    )
    
    @classmethod
    def create(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        justify_qc: Optional[QuorumCertificate],
        target_id: ReplicaId,
        timestamp: int = 0
    ) -> "NewViewMessage":
        """Factory method to create a NewViewMessage."""
        return cls(
            sender_id=sender_id,
            view_number=view_number,
            justify_qc=justify_qc,
            target_id=target_id,
            timestamp=timestamp
        )

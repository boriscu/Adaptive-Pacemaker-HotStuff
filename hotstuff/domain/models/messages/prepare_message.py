"""
PrepareMessage model.

Sent by the leader to propose a new block in the PREPARE phase.
Corresponds to Msg(prepare, curProposal, highQC) in Algorithm 2.
"""

from typing import Optional

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_message import BaseMessage


class PrepareMessage(BaseMessage):
    """
    PREPARE phase message from leader to all replicas.
    
    As per Algorithm 2:
    - Leader broadcasts Msg(prepare, curProposal, highQC)
    - curProposal is the new block created from highQC.node
    - highQC is selected from received new-view messages
    """
    
    message_type: MessageType = Field(
        default=MessageType.PREPARE,
        description="Always PREPARE for this message type"
    )
    block: Block = Field(
        description="The proposed block (curProposal in paper)"
    )
    high_qc: Optional[QuorumCertificate] = Field(
        default=None,
        description="The highest QC known to the leader (highQC in paper)"
    )
    
    @classmethod
    def create(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        block: Block,
        high_qc: Optional[QuorumCertificate],
        timestamp: int = 0
    ) -> "PrepareMessage":
        """Factory method to create a PrepareMessage."""
        return cls(
            sender_id=sender_id,
            view_number=view_number,
            block=block,
            high_qc=high_qc,
            timestamp=timestamp
        )

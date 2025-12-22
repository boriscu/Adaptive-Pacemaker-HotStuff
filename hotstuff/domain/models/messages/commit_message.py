"""
CommitMessage model.

Sent by the leader after collecting enough PRE-COMMIT votes to form precommitQC.
Corresponds to Msg(commit, ⊥, precommitQC) in Algorithm 2.
"""

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_message import BaseMessage


class CommitMessage(BaseMessage):
    """
    COMMIT phase message from leader to all replicas.
    
    As per Algorithm 2:
    - Leader broadcasts Msg(commit, ⊥, precommitQC)
    - precommitQC is formed from (n-f) PRE-COMMIT votes
    - On receiving this, replicas update lockedQC ← precommitQC
    """
    
    message_type: MessageType = Field(
        default=MessageType.COMMIT,
        description="Always COMMIT for this message type"
    )
    precommit_qc: QuorumCertificate = Field(
        description="The QC formed from PRE-COMMIT votes"
    )
    
    @classmethod
    def create(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        precommit_qc: QuorumCertificate,
        timestamp: int = 0
    ) -> "CommitMessage":
        """Factory method to create a CommitMessage."""
        return cls(
            sender_id=sender_id,
            view_number=view_number,
            precommit_qc=precommit_qc,
            timestamp=timestamp
        )

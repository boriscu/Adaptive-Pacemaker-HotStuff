"""
PreCommitMessage model.

Sent by the leader after collecting enough PREPARE votes to form prepareQC.
Corresponds to Msg(pre-commit, ⊥, prepareQC) in Algorithm 2.
"""

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_message import BaseMessage


class PreCommitMessage(BaseMessage):
    """
    PRE-COMMIT phase message from leader to all replicas.
    
    As per Algorithm 2:
    - Leader broadcasts Msg(pre-commit, ⊥, prepareQC)
    - prepareQC is formed from (n-f) PREPARE votes
    """
    
    message_type: MessageType = Field(
        default=MessageType.PRE_COMMIT,
        description="Always PRE_COMMIT for this message type"
    )
    prepare_qc: QuorumCertificate = Field(
        description="The QC formed from PREPARE votes"
    )
    
    @classmethod
    def create(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        prepare_qc: QuorumCertificate,
        timestamp: int = 0
    ) -> "PreCommitMessage":
        """Factory method to create a PreCommitMessage."""
        return cls(
            sender_id=sender_id,
            view_number=view_number,
            prepare_qc=prepare_qc,
            timestamp=timestamp
        )

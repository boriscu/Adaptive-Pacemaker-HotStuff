"""
DecideMessage model.

Sent by the leader after collecting enough COMMIT votes to form commitQC.
Corresponds to Msg(decide, ⊥, commitQC) in Algorithm 2.
"""

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_message import BaseMessage


class DecideMessage(BaseMessage):
    """
    DECIDE phase message from leader to all replicas.
    
    As per Algorithm 2:
    - Leader broadcasts Msg(decide, ⊥, commitQC)
    - commitQC is formed from (n-f) COMMIT votes
    - On receiving this, replicas execute the committed block
    """
    
    message_type: MessageType = Field(
        default=MessageType.DECIDE,
        description="Always DECIDE for this message type"
    )
    commit_qc: QuorumCertificate = Field(
        description="The QC formed from COMMIT votes"
    )
    
    @classmethod
    def create(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        commit_qc: QuorumCertificate,
        timestamp: int = 0
    ) -> "DecideMessage":
        """Factory method to create a DecideMessage."""
        return cls(
            sender_id=sender_id,
            view_number=view_number,
            commit_qc=commit_qc,
            timestamp=timestamp
        )

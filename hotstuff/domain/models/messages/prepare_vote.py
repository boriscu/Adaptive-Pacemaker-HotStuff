"""
PrepareVote model.

Vote message sent in response to a PREPARE message.
"""

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.partial_signature import PartialSignature
from hotstuff.domain.models.messages.base_vote_message import BaseVoteMessage


class PrepareVote(BaseVoteMessage):
    """
    Vote in response to a PREPARE message.
    
    As per Algorithm 2, replicas send voteMsg(prepare, m.node, ⊥)
    to the leader after receiving a valid PREPARE message.
    """
    
    message_type: MessageType = Field(
        default=MessageType.PREPARE_VOTE,
        description="Always PREPARE_VOTE for this message type"
    )
    
    @classmethod
    def create(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        block_hash: BlockHash,
        target_id: ReplicaId,
        timestamp: int = 0
    ) -> "PrepareVote":
        """Factory method to create a PrepareVote."""
        partial_sig = PartialSignature(
            replica_id=sender_id,
            message_type=MessageType.PREPARE_VOTE,
            view_number=view_number,
            block_hash=block_hash
        )
        return cls(
            sender_id=sender_id,
            view_number=view_number,
            block_hash=block_hash,
            partial_signature=partial_sig,
            target_id=target_id,
            timestamp=timestamp
        )

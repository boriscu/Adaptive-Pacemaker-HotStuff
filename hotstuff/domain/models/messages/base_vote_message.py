"""
Base vote message model.

Abstract base class for all vote messages in HotStuff.
Corresponds to voteMsg(type, node, qc) in Algorithm 1.
"""

from abc import ABC

from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.partial_signature import PartialSignature
from hotstuff.domain.models.messages.base_message import BaseMessage


class BaseVoteMessage(BaseMessage, ABC):
    """
    Base class for all vote messages.
    
    As per Algorithm 1, voteMsg(type, node, qc):
    - Creates a Msg with the given parameters
    - Adds partialSig = tsign_r(<type, viewNumber, node>)
    
    Vote messages are sent from replicas to the leader.
    """
    
    block_hash: BlockHash = Field(
        description="Hash of the block being voted on"
    )
    partial_signature: PartialSignature = Field(
        description="Partial signature from the voting replica"
    )

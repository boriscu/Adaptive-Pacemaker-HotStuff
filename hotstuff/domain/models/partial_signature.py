"""
PartialSignature model.

Represents a partial threshold signature from a single replica.
Corresponds to partialSig in the paper's voteMsg function.
"""

import hashlib

from pydantic import BaseModel
from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType


class PartialSignature(BaseModel):
    """
    A partial signature from a replica.
    
    In the paper, this is created by tsign_r(<type, viewNumber, node>).
    For simulation purposes, we represent this as a simple hash of the
    signed content along with the signer's ID.
    
    This is a simplified model - real implementations would use
    threshold signature schemes like BLS.
    """
    
    replica_id: ReplicaId = Field(
        description="ID of the replica that created this signature"
    )
    message_type: MessageType = Field(
        description="Type of message being signed"
    )
    view_number: ViewNumber = Field(
        description="View number of the message being signed"
    )
    block_hash: BlockHash = Field(
        description="Hash of the block being signed"
    )
    
    model_config = {"frozen": True}
    
    @property
    def signature_digest(self) -> str:
        """
        Compute a digest representing this signature.
        
        In a real implementation, this would be a cryptographic signature.
        """
        content = f"{self.replica_id}|{self.message_type.name}|{self.view_number}|{self.block_hash}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

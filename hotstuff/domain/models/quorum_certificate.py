"""
QuorumCertificate model.

Represents a Quorum Certificate (QC) formed by combining threshold signatures.
Corresponds to QC(V) in Algorithm 1 of the paper.
"""

from typing import List

from pydantic import BaseModel
from pydantic import Field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.partial_signature import PartialSignature


class QuorumCertificate(BaseModel):
    """
    A Quorum Certificate proving that a quorum of replicas agreed on a message.
    
    As per Algorithm 1 in the paper:
    - QC aggregates partial signatures using tcombine
    - Fields: type, viewNumber, node (via block_hash), sig (combined signature)
    
    The QC serves as proof that at least 2f+1 replicas (for n=3f+1) have
    signed the same message.
    """
    
    qc_type: MessageType = Field(
        description="Type of the QC (PREPARE, PRE_COMMIT, COMMIT)"
    )
    view_number: ViewNumber = Field(
        description="View number when this QC was formed"
    )
    block_hash: BlockHash = Field(
        description="Hash of the block this QC certifies"
    )
    signatures: List[PartialSignature] = Field(
        default_factory=list,
        description="List of partial signatures that form this QC"
    )
    
    model_config = {"frozen": True}
    
    def is_valid(self, quorum_size: int) -> bool:
        """
        Check if this QC has enough signatures to be valid.
        
        Args:
            quorum_size: The required number of signatures (2f+1 for n=3f+1).
            
        Returns:
            True if the QC has at least quorum_size unique signatures.
        """
        unique_signers = set(sig.replica_id for sig in self.signatures)
        return len(unique_signers) >= quorum_size
    
    @property
    def signer_count(self) -> int:
        """Get the number of unique signers in this QC."""
        return len(set(sig.replica_id for sig in self.signatures))
    
    @property
    def signer_ids(self) -> List[int]:
        """Get the list of replica IDs that signed this QC."""
        return sorted(set(sig.replica_id for sig in self.signatures))

"""
QuorumCertificateFactory for creating QCs.

Implements the QC(V) function from Algorithm 1.
"""

from typing import List

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.partial_signature import PartialSignature
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_vote_message import BaseVoteMessage


class QuorumCertificateFactory:
    """
    Factory for creating QuorumCertificate instances.
    
    Implements QC(V) from Algorithm 1:
    - Aggregates partial signatures from votes using tcombine
    - Sets type, viewNumber, node (block_hash), and sig fields
    """
    
    @classmethod
    def create_qc(
        cls,
        votes: List[BaseVoteMessage],
        qc_type: MessageType
    ) -> QuorumCertificate:
        """
        Create a QC from a set of votes.
        
        This implements QC(V) from Algorithm 1, which:
        - sig ← tcombine({p.partialSig : p ∈ V})
        - Sets (type, viewNumber, node) from the votes
        
        Args:
            votes: List of vote messages to aggregate.
            qc_type: Type of QC (PREPARE_VOTE, PRE_COMMIT_VOTE, COMMIT_VOTE).
            
        Returns:
            QuorumCertificate aggregating the votes.
            
        Raises:
            ValueError: If votes list is empty or inconsistent.
        """
        if not votes:
            raise ValueError("Cannot create QC from empty votes list")
        
        first_vote = votes[0]
        block_hash = first_vote.block_hash
        view_number = first_vote.view_number
        
        for vote in votes:
            if vote.block_hash != block_hash:
                raise ValueError("All votes must be for the same block")
            if vote.view_number != view_number:
                raise ValueError("All votes must be from the same view")
        
        signatures = [vote.partial_signature for vote in votes]
        
        return QuorumCertificate(
            qc_type=qc_type,
            view_number=view_number,
            block_hash=block_hash,
            signatures=signatures
        )
    
    @classmethod
    def create_qc_from_signatures(
        cls,
        signatures: List[PartialSignature],
        qc_type: MessageType,
        view_number: ViewNumber,
        block_hash: BlockHash
    ) -> QuorumCertificate:
        """
        Create a QC directly from partial signatures.
        
        Alternative factory method when votes are not available.
        
        Args:
            signatures: List of partial signatures.
            qc_type: Type of QC.
            view_number: View number for the QC.
            block_hash: Hash of the certified block.
            
        Returns:
            QuorumCertificate with the given signatures.
        """
        return QuorumCertificate(
            qc_type=qc_type,
            view_number=view_number,
            block_hash=block_hash,
            signatures=signatures
        )
    
    @classmethod
    def create_empty_qc(
        cls,
        qc_type: MessageType,
        view_number: ViewNumber,
        block_hash: BlockHash
    ) -> QuorumCertificate:
        """
        Create an empty QC (primarily for testing or genesis).
        
        Args:
            qc_type: Type of QC.
            view_number: View number for the QC.
            block_hash: Hash of the certified block.
            
        Returns:
            QuorumCertificate with no signatures.
        """
        return QuorumCertificate(
            qc_type=qc_type,
            view_number=view_number,
            block_hash=block_hash,
            signatures=[]
        )

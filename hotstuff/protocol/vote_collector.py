"""
VoteCollector for QC formation.

Collects votes and forms QCs when quorum is reached.
"""

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_vote_message import BaseVoteMessage
from hotstuff.factories.qc_factory import QuorumCertificateFactory
from hotstuff.logging_config.logger import StructuredLogger


VoteKey = Tuple[ViewNumber, BlockHash, MessageType]


class VoteCollector:
    """
    Collects votes and forms QCs when quorum is reached.
    
    Votes are collected per (view, block_hash, vote_type) tuple.
    When the number of votes reaches the quorum threshold, a QC is formed.
    """
    
    def __init__(self, quorum_size: int):
        """
        Initialize the vote collector.
        
        Args:
            quorum_size: Number of votes required to form a QC (2f+1).
        """
        self._quorum_size = quorum_size
        self._votes: Dict[VoteKey, List[BaseVoteMessage]] = {}
        self._formed_qcs: Dict[VoteKey, QuorumCertificate] = {}
        self._logger = StructuredLogger.get_logger("vote_collector")
    
    def add_vote(self, vote: BaseVoteMessage) -> Optional[QuorumCertificate]:
        """
        Add a vote and return QC if quorum is reached.
        
        Deduplicates votes from the same sender.
        
        Args:
            vote: The vote message to add.
            
        Returns:
            QuorumCertificate if quorum is newly reached, None otherwise.
        """
        key = (vote.view_number, vote.block_hash, vote.message_type)
        
        if key in self._formed_qcs:
            self._logger.debug(f"QC already formed for {key}")
            return None
        
        if key not in self._votes:
            self._votes[key] = []
        
        existing_senders = {v.sender_id for v in self._votes[key]}
        if vote.sender_id in existing_senders:
            self._logger.debug(f"Duplicate vote from {vote.sender_id} for {key}")
            return None
        
        self._votes[key].append(vote)
        vote_count = len(self._votes[key])
        
        self._logger.debug(
            f"Vote from {vote.sender_id} for {vote.message_type.name}, "
            f"view {vote.view_number}, block {vote.block_hash[:8]}: "
            f"{vote_count}/{self._quorum_size}"
        )
        
        if vote_count >= self._quorum_size:
            qc = QuorumCertificateFactory.create_qc(
                votes=self._votes[key],
                qc_type=vote.message_type
            )
            self._formed_qcs[key] = qc
            self._logger.info(
                f"QC formed for {vote.message_type.name}, "
                f"view {vote.view_number}, block {vote.block_hash[:8]}"
            )
            return qc
        
        return None
    
    def get_qc(
        self,
        view_number: ViewNumber,
        block_hash: BlockHash,
        vote_type: MessageType
    ) -> Optional[QuorumCertificate]:
        """
        Get a previously formed QC.
        
        Args:
            view_number: View number of the QC.
            block_hash: Block hash of the QC.
            vote_type: Type of votes that formed the QC.
            
        Returns:
            The QC if it exists, None otherwise.
        """
        key = (view_number, block_hash, vote_type)
        return self._formed_qcs.get(key)
    
    def get_vote_count(
        self,
        view_number: ViewNumber,
        block_hash: BlockHash,
        vote_type: MessageType
    ) -> int:
        """
        Get the current vote count for a (view, block, type) tuple.
        
        Args:
            view_number: View number.
            block_hash: Block hash.
            vote_type: Type of votes.
            
        Returns:
            Number of votes collected.
        """
        key = (view_number, block_hash, vote_type)
        return len(self._votes.get(key, []))
    
    def has_quorum(
        self,
        view_number: ViewNumber,
        block_hash: BlockHash,
        vote_type: MessageType
    ) -> bool:
        """
        Check if quorum has been reached.
        
        Args:
            view_number: View number.
            block_hash: Block hash.
            vote_type: Type of votes.
            
        Returns:
            True if quorum reached, False otherwise.
        """
        key = (view_number, block_hash, vote_type)
        return key in self._formed_qcs
    
    def clear_view(self, view_number: ViewNumber) -> None:
        """
        Clear all votes for a specific view.
        
        Used during view change to clean up old state.
        
        Args:
            view_number: View to clear.
        """
        keys_to_remove = [k for k in self._votes if k[0] == view_number]
        for key in keys_to_remove:
            del self._votes[key]
        
        qc_keys_to_remove = [k for k in self._formed_qcs if k[0] == view_number]
        for key in qc_keys_to_remove:
            del self._formed_qcs[key]
    
    def clear_all(self) -> None:
        """Clear all votes and QCs."""
        self._votes.clear()
        self._formed_qcs.clear()
    
    @property
    def quorum_size(self) -> int:
        """Get the quorum size."""
        return self._quorum_size

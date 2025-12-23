"""
SafetyRules implementation.

Implements the safeNode predicate from Algorithm 1 of the paper.
"""

from typing import Optional
from typing import Dict

from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.logging_config.logger import StructuredLogger


class SafetyRules:
    """
    Safety rules for HotStuff consensus.
    
    Implements the safeNode(node, qc) predicate from Algorithm 1:
    - (node extends from lockedQC.node) OR (qc.viewNumber > lockedQC.viewNumber)
    
    This ensures that a replica only votes for a proposal if either:
    1. The proposed block extends the locked block, OR
    2. The proposal comes with a QC from a higher view than the locked QC
    """
    
    def __init__(self):
        """Initialize safety rules."""
        self._logger = StructuredLogger.get_logger("safety")
        self._block_registry: Dict[BlockHash, Block] = {}
    
    def register_block(self, block: Block) -> None:
        """
        Register a block for ancestry checking.
        
        Args:
            block: Block to register.
        """
        self._block_registry[block.block_hash] = block
    
    def is_safe_node(
        self,
        block: Block,
        justify_qc: Optional[QuorumCertificate],
        locked_qc: Optional[QuorumCertificate]
    ) -> bool:
        """
        Check if it's safe to vote for a block.
        
        Implements safeNode(node, qc) from Algorithm 1:
        - (node extends from lockedQC.node) OR (qc.viewNumber > lockedQC.viewNumber)
        
        Args:
            block: The proposed block to check.
            justify_qc: The QC justifying the proposal (highQC from leader).
            locked_qc: The replica's current locked QC.
            
        Returns:
            True if safe to vote, False otherwise.
        """
        if locked_qc is None:
            self._logger.debug(f"Safe: no locked QC, accepting block {block.block_hash}")
            return True
        
        if self._extends_from(block, locked_qc.block_hash):
            self._logger.debug(
                f"Safe: block {block.block_hash} extends locked block {locked_qc.block_hash}"
            )
            return True
        
        if justify_qc is not None and justify_qc.view_number > locked_qc.view_number:
            self._logger.debug(
                f"Safe: justify QC view {justify_qc.view_number} > "
                f"locked QC view {locked_qc.view_number}"
            )
            return True
        
        self._logger.debug(
            f"Unsafe: block {block.block_hash} does not extend locked block "
            f"and justify QC view not higher"
        )
        return False
    
    def _extends_from(self, block: Block, ancestor_hash: BlockHash) -> bool:
        """
        Check if a block extends from an ancestor.
        
        Traverses the chain to check ancestry.
        
        Args:
            block: The block to check.
            ancestor_hash: Hash of the potential ancestor.
            
        Returns:
            True if block extends ancestor, False otherwise.
        """
        current_hash = block.parent_hash
        visited = set()
        
        while current_hash is not None and current_hash not in visited:
            visited.add(current_hash)
            
            if current_hash == ancestor_hash:
                return True
            
            parent_block = self._block_registry.get(current_hash)
            if parent_block is None:
                break
            current_hash = parent_block.parent_hash
        
        return block.parent_hash == ancestor_hash
    
    def validate_qc(
        self,
        qc: QuorumCertificate,
        quorum_size: int
    ) -> bool:
        """
        Validate a Quorum Certificate.
        
        Args:
            qc: The QC to validate.
            quorum_size: Required number of signatures (2f+1).
            
        Returns:
            True if QC is valid, False otherwise.
        """
        if not qc.is_valid(quorum_size):
            self._logger.warning(
                f"Invalid QC: has {qc.signer_count} signatures, need {quorum_size}"
            )
            return False
        return True
    
    def clear_registry(self) -> None:
        """Clear the block registry."""
        self._block_registry.clear()

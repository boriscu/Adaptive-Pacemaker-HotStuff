from typing import List
from hotstuff.domain.models import Block
from hotstuff.pacemaker.interface import Pacemaker
from hotstuff.logger import logger
from hotstuff.metrics.collector import collector
from hotstuff.protocol.block_tree import BlockTree

class Executor:
    """
    Handles the execution and commitment of blocks.
    """
    def __init__(self, my_id: int, pacemaker: Pacemaker, block_tree: BlockTree):
        self.my_id = my_id
        self.pacemaker = pacemaker
        self.block_tree = block_tree
        
        self.committed_blocks: List[Block] = []
        self.executed_up_to_height = 0

    def commit(self, block: Block):
        """
        Executes the block and its ancestors if not already executed.
        Recursive execution logic.
        """
        if block.height <= self.executed_up_to_height:
            return
            
        # Need to commit ancestors first
        if block.parent_hash:
            parent = self.block_tree.get_block(block.parent_hash)
            if parent:
                self.commit(parent)
        
        # Execute self
        self.committed_blocks.append(block)
        self.executed_up_to_height = block.height
        logger.info(f"Replica {self.my_id} COMMITTED block {block.hash[:8]} (Height {block.height})")
        
        # Notify Pacemaker
        self.pacemaker.on_commit_success(latency=0.1) # Mock latency
        
        # Record Metrics
        # In a real sim we'd track when this block was proposed vs now
        collector.record_commit(timestamp=0, num_blocks=1, latency=0.1)

    def get_committed_blocks(self) -> List[Block]:
        return self.committed_blocks

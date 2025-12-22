from typing import Dict, Optional, List
from hotstuff.domain.models import Block, QC, Command, QCSignature
from hotstuff.domain.enums import MsgType
from hotstuff.config import config, ProtocolMode

class BlockTree:
    """
    Manages the block tree structure, including:
    - Storage of blocks and QCs
    - Ancestry checks
    - Genesis initialization
    - New block creation
    """
    def __init__(self):
        self.blocks: Dict[str, Block] = {}
        self.qcs: Dict[str, QC] = {}
        self.genesis_block: Optional[Block] = None
        self.genesis_qc: Optional[QC] = None

    def initialize_genesis(self) -> QC:
        """
        Creates and stores the genesis block and QC.
        Returns the genesis QC.
        """
        genesis_cmd = Command(payload="GENESIS")
        self.genesis_block = Block(
            parent_hash=None, 
            cmd=genesis_cmd, 
            view=0, 
            height=0
        )
        self.blocks[self.genesis_block.hash] = self.genesis_block
        
        # Mock Genesis QC
        self.genesis_qc = QC(
            type=MsgType.GENERIC if config.PROTOCOL == ProtocolMode.CHAINED else MsgType.DECIDE,
            view_number=0,
            node_hash=self.genesis_block.hash,
            sig=QCSignature(signers=set())
        )
        self.qcs[self.genesis_qc.node_hash] = self.genesis_qc
        
        return self.genesis_qc

    def add_block(self, block: Block):
        """Stores a block."""
        self.blocks[block.hash] = block

    def get_block(self, block_hash: str) -> Optional[Block]:
        """Retrieves a block by hash."""
        return self.blocks.get(block_hash)

    def add_qc(self, qc: QC):
        """Stores a QC."""
        self.qcs[qc.node_hash] = qc

    def get_qc(self, node_hash: str) -> Optional[QC]:
        """Retrieves a QC by the hash of the node it certifies."""
        return self.qcs.get(node_hash)

    def create_leaf(self, parent_hash: str, cmd: Command, justify_qc: QC, view_number: int) -> Block:
        """
        Creates a new block extending the parent.
        """
        parent = self.blocks.get(parent_hash)
        height = parent.height + 1 if parent else 1
        
        new_block = Block(
            parent_hash=parent_hash,
            cmd=cmd,
            view=view_number,
            height=height,
            justify=justify_qc
        )
        return new_block

    def extends(self, block: Block, target_hash: str) -> bool:
        """
        Checks if block is a descendant of the block with target_hash.
        """
        curr = block
        while curr.parent_hash is not None:
            if curr.parent_hash == target_hash:
                return True
            curr = self.blocks.get(curr.parent_hash)
            if curr is None:
                break
        return block.hash == target_hash # or itself

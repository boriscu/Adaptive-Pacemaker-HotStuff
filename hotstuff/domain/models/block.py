"""
Block model.

Represents a block (node) in the HotStuff blockchain.
Corresponds to the 'node' concept in the paper's pseudocode.
"""

import hashlib
from typing import Optional

from pydantic import BaseModel
from pydantic import Field
from pydantic import computed_field

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.types.command import Command


class Block(BaseModel):
    """
    A block in the HotStuff blockchain.
    
    Corresponds to the 'node' concept in the paper. Each block contains
    a command (transaction), references its parent, and is proposed at
    a specific view by a specific replica.
    
    The genesis block has parent_hash=None and height=0.
    """
    
    parent_hash: Optional[BlockHash] = Field(
        default=None,
        description="Hash of the parent block, None for genesis"
    )
    command: Command = Field(
        description="The client command/transaction contained in this block"
    )
    height: int = Field(
        ge=0,
        description="Height in the blockchain, genesis is 0"
    )
    proposer_id: ReplicaId = Field(
        description="ID of the replica that proposed this block"
    )
    view_number: ViewNumber = Field(
        description="View number when this block was proposed"
    )
    
    model_config = {"frozen": True}
    
    @computed_field
    @property
    def block_hash(self) -> BlockHash:
        """
        Compute the hash of this block.
        
        Uses SHA-256 hash of the block's content for deterministic identification.
        """
        content = f"{self.parent_hash}|{self.command}|{self.height}|{self.proposer_id}|{self.view_number}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        return BlockHash(hash_value)
    


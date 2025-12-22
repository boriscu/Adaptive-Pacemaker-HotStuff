from typing import Optional
import hashlib
from pydantic import BaseModel
from .command import Command
from .qc import QC

class Block(BaseModel):
    """
    Represents a Node/Leaf in the tree (b).
    """
    parent_hash: Optional[str] = None
    cmd: Optional[Command] = None
    justify: Optional[QC] = None # connect to parent via QC or direct hash
    
    height: int = 0
    view: int = 0 # The view in which this block was proposed
    
    @property
    def hash(self) -> str:
        # Deterministic content hash
        # Handle None cmd for genesis
        cmd_str = str(self.cmd.id) if self.cmd else "None"
        content = f"{self.parent_hash}:{cmd_str}:{self.view}"
        return hashlib.sha256(content.encode()).hexdigest()

from typing import Optional
from pydantic import BaseModel
from ..enums import MsgType
from .qc_signature import QCSignature

class QC(BaseModel):
    """
    Quorum Certificate.
    QC(V)
    """
    type: MsgType
    view_number: int    # viewNumber
    node_hash: str      # node (hash of the block)
    sig: Optional[QCSignature] = None # tcombine result

    @property
    def is_genesis(self) -> bool:
        return self.view_number == 0

# Rebuild if needed for Pydantic v2 deferred resolution (not needed here as deps are ordered)

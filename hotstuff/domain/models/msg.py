from typing import Optional
from pydantic import BaseModel
from ..enums import MsgType
from .block import Block
from .qc import QC

class Msg(BaseModel):
    """
    Standard Protocol Message.
    Msg(type, node, justify)
    """
    type: MsgType
    view_number: int  # viewNumber
    node: Optional[Block] = None # The payload/proposal (node)
    justify: Optional[QC] = None # The QC justifying this message (highQC or prepareQC etc)
    sender: int # Initiator of the message

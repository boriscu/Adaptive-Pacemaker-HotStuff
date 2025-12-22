from pydantic import BaseModel
from ..enums import MsgType
from .partial_signature import PartialSignature

class VoteMsg(BaseModel):
    """
    Vote Message.
    voteMsg(type, node, qc)
    """
    type: MsgType
    view_number: int
    node_hash: str # Hash of the block we are voting for
    partial_sig: PartialSignature
    sender: int

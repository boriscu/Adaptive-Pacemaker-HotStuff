from pydantic import BaseModel
from ..enums import MsgType

class PartialSignature(BaseModel):
    """
    Simulates a threshold signature share from a single replica.
    tsign_r(<type, viewNumber, node_hash>)
    """
    replica_id: int
    msg_type: MsgType
    view: int
    node_hash: str

    def verify(self, replica_id: int, msg_type: MsgType, view: int, node_hash: str) -> bool:
        # Trivial verification in simulation: check fields
        return (self.replica_id == replica_id and 
                self.msg_type == msg_type and 
                self.view == view and 
                self.node_hash == node_hash)

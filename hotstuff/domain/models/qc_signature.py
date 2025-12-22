from typing import Set
from pydantic import BaseModel

class QCSignature(BaseModel):
    """
    Simulates a combined threshold signature.
    tcombine(..., {partial_sigs})
    """
    signers: Set[int] # Set of replica IDs who signed
    
    def validate(self, n: int, f: int) -> bool:
        return len(self.signers) >= (n - f)

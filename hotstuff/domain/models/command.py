from pydantic import BaseModel, Field
import hashlib

class Command(BaseModel):
    """Represents a client command (op) to be executed."""
    id: str = Field(default_factory=lambda: hashlib.sha256(b"").hexdigest()[:8])
    payload: str

    def __hash__(self):
        return hash(self.id)

"""
BaseEvent for simulation events.

Abstract base class for all simulation events.
"""

import uuid
from abc import ABC

from pydantic import BaseModel
from pydantic import Field

from hotstuff.domain.enumerations.event_type import EventType


class BaseEvent(BaseModel, ABC):
    """
    Base class for all simulation events.
    
    Events are the fundamental unit of simulation progress.
    Each event represents a meaningful protocol action.
    """
    
    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4())[:8],
        description="Unique identifier for this event"
    )
    event_type: EventType = Field(
        description="Type of this event"
    )
    timestamp: int = Field(
        description="Simulation time when this event occurs"
    )
    description: str = Field(
        default="",
        description="Human-readable description of this event"
    )
    
    model_config = {"frozen": True}
    
    def to_dict(self) -> dict:
        """Convert event to dictionary for serialization."""
        return self.model_dump()

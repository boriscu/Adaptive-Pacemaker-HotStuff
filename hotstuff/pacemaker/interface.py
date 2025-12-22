from abc import ABC, abstractmethod
from typing import Optional
from ..domain.models import QC
from ..config import config

class Pacemaker(ABC):
    """
    Algorithm 5: Pacemaker Interface.
    Manages view counters, leader election, and timeouts.
    Does NOT handle safety/commit logic (that's Replica's job).
    """

    @abstractmethod
    def get_leader(self, view: int) -> int:
        """Returns the leader for a given view."""
        pass

    @abstractmethod
    def get_current_view(self) -> int:
        """Returns current view."""
        pass
    
    @abstractmethod
    def advance_view(self) -> int:
        """Increments view and returns the new view."""
        pass

    @abstractmethod
    def get_timeout_duration(self) -> float:
        """Returns the duration to wait before triggering a timeout in the current view."""
        pass

    @abstractmethod
    def on_commit_success(self, latency: float):
        """Feedback hook: Called when a block is committed successfully."""
        pass
    
    @abstractmethod
    def on_timeout(self):
        """Feedback hook: Called when a view timed out."""
        pass

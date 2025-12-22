from .interface import Pacemaker
from ..config import config

class BaselinePacemaker(Pacemaker):
    """
    Standard Pacemaker.
    - Round Robin Leader Election.
    - Fixed Timeout (Delta).
    """
    def __init__(self, n: int = config.N):
        self.n = n
        self.current_view = 1
    
    def get_leader(self, view: int) -> int:
        return (view % self.n)

    def get_current_view(self) -> int:
        return self.current_view

    def advance_view(self) -> int:
        self.current_view += 1
        return self.current_view

    def get_timeout_duration(self) -> float:
        return config.DELTA

    def on_commit_success(self, latency: float):
        pass

    def on_timeout(self):
        pass

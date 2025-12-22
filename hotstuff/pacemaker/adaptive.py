from .interface import Pacemaker
from ..config import config

class AdaptivePacemaker(Pacemaker):
    """
    Adaptive Pacemaker.
    - Round Robin Leader
    - Adaptive Timeout based on past performance (Exponential Moving Average).
    """
    def __init__(self, n: int = config.N):
        self.n = n
        self.current_view = 1
        self.current_timeout = config.DELTA
        self.min_timeout = config.DELTA / 4.0
        self.max_timeout = config.DELTA * 10.0
        # Exponential Weight for Moving Average
        self.alpha = 0.125 

    def get_leader(self, view: int) -> int:
        return (view % self.n)

    def get_current_view(self) -> int:
        return self.current_view

    def advance_view(self) -> int:
        self.current_view += 1
        return self.current_view

    def get_timeout_duration(self) -> float:
        return self.current_timeout

    def on_commit_success(self, latency: float):
        """
        If we commit fast, we can safely reduce the timeout.
        Target timeout = 2 * observed_latency (Safety margin).
        """
        target = max(self.min_timeout, latency * 2.0)
        # Update using EMA
        self.current_timeout = (1 - self.alpha) * self.current_timeout + self.alpha * target

    def on_timeout(self):
        """
        If we timed out, we need to back off.
        """
        self.current_timeout = min(self.max_timeout, self.current_timeout * 1.5)

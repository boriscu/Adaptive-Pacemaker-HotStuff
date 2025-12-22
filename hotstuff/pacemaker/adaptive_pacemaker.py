"""
AdaptivePacemaker implementation.

EMA-based timeout adjustment for improved liveness.
"""

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.pacemaker.interface import PacemakerInterface
from hotstuff.logging_config.logger import StructuredLogger


class AdaptivePacemaker(PacemakerInterface):
    """
    Adaptive pacemaker with EMA-based timeout adjustment.
    
    Adjusts timeout based on observed view completion times:
    - On success: timeout = alpha * observed + (1 - alpha) * timeout
    - On timeout: increase timeout (exponential backoff)
    
    This improves liveness by adapting to network conditions.
    """
    
    def __init__(
        self,
        base_timeout_ms: int,
        alpha: float = 0.5,
        min_timeout_ms: int = 500,
        max_timeout_ms: int = 5000
    ):
        """
        Initialize the adaptive pacemaker.
        
        Args:
            base_timeout_ms: Initial timeout duration.
            alpha: EMA smoothing factor (0 < alpha < 1).
            min_timeout_ms: Minimum timeout duration.
            max_timeout_ms: Maximum timeout duration.
        """
        self._base_timeout_ms = base_timeout_ms
        self._current_timeout_ms = base_timeout_ms
        self._alpha = alpha
        self._min_timeout_ms = min_timeout_ms
        self._max_timeout_ms = max_timeout_ms
        
        self._current_view: ViewNumber = ViewNumber(0)
        self._timeout_time: int = -1
        self._timer_active: bool = False
        self._view_start_time: int = 0
        self._consecutive_timeouts: int = 0
        
        self._logger = StructuredLogger.get_logger("pacemaker.adaptive")
    
    def start_timer(self, view_number: ViewNumber, current_time: int) -> int:
        """
        Start the timer for a view.
        
        Args:
            view_number: The view to time.
            current_time: Current simulation time.
            
        Returns:
            Timeout time (when timer expires).
        """
        self._current_view = view_number
        self._view_start_time = current_time
        self._timeout_time = current_time + self._current_timeout_ms
        self._timer_active = True
        
        self._logger.debug(
            f"Timer started for view {view_number}, "
            f"timeout={self._current_timeout_ms}ms, "
            f"expires at {self._timeout_time}"
        )
        
        return self._timeout_time
    
    def stop_timer(self) -> None:
        """Stop the current timer."""
        self._timer_active = False
        self._timeout_time = -1
        self._logger.debug(f"Timer stopped for view {self._current_view}")
    
    def on_timeout(self, current_time: int) -> ViewNumber:
        """
        Handle a timeout event with exponential backoff.
        
        Args:
            current_time: Current simulation time.
            
        Returns:
            The next view number.
        """
        self._consecutive_timeouts += 1
        
        backoff_multiplier = min(2 ** self._consecutive_timeouts, 4)
        new_timeout = min(
            self._current_timeout_ms * backoff_multiplier,
            self._max_timeout_ms
        )
        
        old_timeout = self._current_timeout_ms
        self._current_timeout_ms = int(new_timeout)
        
        next_view = ViewNumber(self._current_view + 1)
        
        self._logger.info(
            f"Timeout #{self._consecutive_timeouts} in view {self._current_view}, "
            f"timeout: {old_timeout}ms -> {self._current_timeout_ms}ms, "
            f"advancing to view {next_view}"
        )
        
        self._timer_active = False
        return next_view
    
    def on_view_success(self, view_number: ViewNumber, duration_ms: int) -> None:
        """
        Adjust timeout based on successful view completion.
        
        Uses EMA: timeout = alpha * observed + (1 - alpha) * timeout
        
        Args:
            view_number: The view that completed.
            duration_ms: Duration of the view in milliseconds.
        """
        self._consecutive_timeouts = 0
        
        old_timeout = self._current_timeout_ms
        
        ema_timeout = self._alpha * duration_ms + (1 - self._alpha) * self._current_timeout_ms
        
        safety_margin = 1.5
        target_timeout = ema_timeout * safety_margin
        
        self._current_timeout_ms = int(max(
            self._min_timeout_ms,
            min(target_timeout, self._max_timeout_ms)
        ))
        
        self._logger.debug(
            f"View {view_number} success in {duration_ms}ms, "
            f"timeout: {old_timeout}ms -> {self._current_timeout_ms}ms"
        )
    
    def get_current_timeout(self) -> int:
        """Get the current timeout duration."""
        return self._current_timeout_ms
    
    def get_timeout_time(self) -> int:
        """Get the absolute timeout time."""
        return self._timeout_time if self._timer_active else -1
    
    def reset(self) -> None:
        """Reset the pacemaker state."""
        self._current_view = ViewNumber(0)
        self._current_timeout_ms = self._base_timeout_ms
        self._timeout_time = -1
        self._timer_active = False
        self._view_start_time = 0
        self._consecutive_timeouts = 0
    
    @property
    def is_timer_active(self) -> bool:
        """Check if timer is active."""
        return self._timer_active
    
    @property
    def consecutive_timeouts(self) -> int:
        """Get the number of consecutive timeouts."""
        return self._consecutive_timeouts

"""
BasePacemaker implementation.

Fixed timeout pacemaker with simple view increment on timeout.
"""

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.pacemaker.interface import PacemakerInterface
from hotstuff.logging_config.logger import StructuredLogger


class BasePacemaker(PacemakerInterface):
    """
    Baseline pacemaker with fixed timeout.
    
    Uses a constant timeout duration for all views.
    On timeout, simply advances to the next view.
    """
    
    def __init__(self, base_timeout_ms: int):
        """
        Initialize the base pacemaker.
        
        Args:
            base_timeout_ms: Fixed timeout duration in milliseconds.
        """
        self._base_timeout_ms = base_timeout_ms
        self._current_view: ViewNumber = ViewNumber(0)
        self._timeout_time: int = -1
        self._timer_active: bool = False
        self._logger = StructuredLogger.get_logger("pacemaker.base")
    
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
        self._timeout_time = current_time + self._base_timeout_ms
        self._timer_active = True
        
        self._logger.debug(
            f"Timer started for view {view_number}, "
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
        Handle a timeout event.
        
        Args:
            current_time: Current simulation time.
            
        Returns:
            The next view number.
        """
        next_view = ViewNumber(self._current_view + 1)
        self._logger.info(
            f"Timeout in view {self._current_view}, "
            f"advancing to view {next_view}"
        )
        self._timer_active = False
        return next_view
    
    def on_view_success(self, view_number: ViewNumber, duration_ms: int) -> None:
        """
        Notify that a view completed successfully.
        
        The base pacemaker ignores this (fixed timeout).
        
        Args:
            view_number: The view that completed.
            duration_ms: Duration of the view in milliseconds.
        """
        self._logger.debug(
            f"View {view_number} completed successfully in {duration_ms}ms"
        )
    
    def get_current_timeout(self) -> int:
        """Get the current timeout duration."""
        return self._base_timeout_ms
    
    def get_timeout_time(self) -> int:
        """Get the absolute timeout time."""
        return self._timeout_time if self._timer_active else -1
    
    def reset(self) -> None:
        """Reset the pacemaker state."""
        self._current_view = ViewNumber(0)
        self._timeout_time = -1
        self._timer_active = False
    
    @property
    def is_timer_active(self) -> bool:
        """Check if timer is active."""
        return self._timer_active

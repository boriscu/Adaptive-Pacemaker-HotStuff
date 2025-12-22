"""
PacemakerInterface abstract class.

Defines the interface for pacemaker implementations.
"""

from abc import ABC
from abc import abstractmethod

from hotstuff.domain.types.view_number import ViewNumber


class PacemakerInterface(ABC):
    """
    Abstract interface for pacemaker implementations.
    
    The pacemaker is responsible for liveness in HotStuff:
    - Managing view timeouts
    - Triggering view changes when needed
    - Synchronizing view numbers across replicas
    
    Different pacemaker strategies can be plugged in via this interface.
    """
    
    @abstractmethod
    def start_timer(self, view_number: ViewNumber, current_time: int) -> int:
        """
        Start the timer for a view.
        
        Args:
            view_number: The view to time.
            current_time: Current simulation time.
            
        Returns:
            Timeout time (when timer expires).
        """
        pass
    
    @abstractmethod
    def stop_timer(self) -> None:
        """Stop the current timer."""
        pass
    
    @abstractmethod
    def on_timeout(self, current_time: int) -> ViewNumber:
        """
        Handle a timeout event.
        
        Args:
            current_time: Current simulation time.
            
        Returns:
            The next view number to transition to.
        """
        pass
    
    @abstractmethod
    def on_view_success(self, view_number: ViewNumber, duration_ms: int) -> None:
        """
        Notify that a view completed successfully.
        
        Used by adaptive pacemakers to adjust timeout.
        
        Args:
            view_number: The view that completed.
            duration_ms: Duration of the view in milliseconds.
        """
        pass
    
    @abstractmethod
    def get_current_timeout(self) -> int:
        """
        Get the current timeout duration.
        
        Returns:
            Timeout duration in milliseconds.
        """
        pass
    
    @abstractmethod
    def get_timeout_time(self) -> int:
        """
        Get the absolute time when the current timer expires.
        
        Returns:
            Timeout time, or -1 if no timer is active.
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the pacemaker state."""
        pass

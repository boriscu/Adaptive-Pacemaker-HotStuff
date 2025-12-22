"""
SimulationClock for tracking simulation time.
"""


class SimulationClock:
    """
    Simulation clock for discrete-event simulation.
    
    Tracks the current simulation time in milliseconds.
    """
    
    def __init__(self, start_time: int = 0):
        """
        Initialize the simulation clock.
        
        Args:
            start_time: Initial time value in milliseconds.
        """
        self._current_time = start_time
    
    @property
    def current_time(self) -> int:
        """Get the current simulation time."""
        return self._current_time
    
    def advance(self, delta: int) -> None:
        """
        Advance the clock by a delta.
        
        Args:
            delta: Time to advance in milliseconds.
        """
        if delta < 0:
            raise ValueError("Cannot advance clock by negative delta")
        self._current_time += delta
    
    def advance_to(self, time: int) -> None:
        """
        Advance the clock to a specific time.
        
        Args:
            time: Target time in milliseconds.
        """
        if time < self._current_time:
            raise ValueError(
                f"Cannot advance clock backwards from {self._current_time} to {time}"
            )
        self._current_time = time
    
    def reset(self, start_time: int = 0) -> None:
        """
        Reset the clock.
        
        Args:
            start_time: New initial time value.
        """
        self._current_time = start_time

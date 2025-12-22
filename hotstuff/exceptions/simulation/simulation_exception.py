"""
SimulationException.

Base exception for simulation-related errors.
"""

from hotstuff.exceptions.base_exception import HotStuffException


class SimulationException(HotStuffException):
    """
    Exception raised for general simulation errors.
    
    This can occur when:
    - Simulation state is invalid
    - Configuration is invalid
    - Simulation cannot proceed
    """
    
    def __init__(self, message: str, simulation_time: int = None, current_event: str = None):
        """
        Initialize the exception.
        
        Args:
            message: Description of the simulation error.
            simulation_time: Current simulation time when error occurred.
            current_event: Event being processed when error occurred.
        """
        context = {}
        if simulation_time is not None:
            context["simulation_time"] = simulation_time
        if current_event:
            context["current_event"] = current_event
        super().__init__(message, context)

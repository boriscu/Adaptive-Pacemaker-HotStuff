import heapq
from typing import List, Tuple, Any, Callable, Dict, Optional
from dataclasses import dataclass, field
from hotstuff.logger import logger

@dataclass(order=True)
class Event:
    timestamp: float
    callback: Callable = field(compare=False)
    args: Tuple = field(compare=False, default_factory=tuple)
    description: str = field(compare=False, default="")

class SimulationEngine:
    """
    Deterministic Discrete Event Simulator.
    Manages a priority queue of events and executes them in timestamp order.
    """
    def __init__(self):
        self.events: List[Event] = []
        self.current_time: float = 0.0
        self.is_running: bool = False
        self._target_speed_ratio: float = 0.0 # 0.0 means max speed, 1.0 means realtime (if timestamps were seconds)
        # Note: In pure simulation, "realtime" is just a visual delay. 
        # The logic depends only on virtual time (self.current_time).

    def schedule(self, delay: float, callback: Callable, *args, description: str = ""):
        """
        Schedules an event to occur at (current_time + delay).
        """
        execution_time = self.current_time + delay
        event = Event(execution_time, callback, args, description)
        heapq.heappush(self.events, event)

    def run(self, max_time: float = 1000.0, step_limit: Optional[int] = None):
        """
        Runs the simulation loop.
        """
        self.is_running = True
        steps = 0
        
        logger.debug(f"Starting simulation. Max time: {max_time}")
        
        while self.events and self.is_running:
            # Peek next event
            event = self.events[0]
            
            if event.timestamp > max_time:
                break
            
            if step_limit and steps >= step_limit:
                break

            # Pop event
            heapq.heappop(self.events)
            
            # Advance time
            self.current_time = event.timestamp
            
            # Execute
            try:
                event.callback(*event.args)
            except Exception as e:
                logger.error(f"Error executing event '{event.description}': {e}", exc_info=True)
            
            steps += 1
        
        logger.debug(f"Simulation ended at time {self.current_time:.4f}. Steps: {steps}")
        self.is_running = False

    def stop(self):
        self.is_running = False

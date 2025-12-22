"""
DiscreteEventScheduler for managing simulation events.

Priority queue-based scheduler for discrete-event simulation.
"""

import heapq
from typing import List
from typing import Optional
from typing import Tuple
from typing import Any


class DiscreteEventScheduler:
    """
    Priority queue-based event scheduler.
    
    Events are scheduled with timestamps and processed in chronological order.
    """
    
    def __init__(self):
        """Initialize the scheduler."""
        self._event_queue: List[Tuple[int, int, Any]] = []
        self._event_counter: int = 0
    
    def schedule(self, event: Any, timestamp: int) -> None:
        """
        Schedule an event for a given time.
        
        Args:
            event: The event to schedule.
            timestamp: When the event should occur.
        """
        self._event_counter += 1
        heapq.heappush(self._event_queue, (timestamp, self._event_counter, event))
    
    def next_event(self) -> Optional[Tuple[int, Any]]:
        """
        Get and remove the next event.
        
        Returns:
            Tuple of (timestamp, event), or None if queue is empty.
        """
        if self.is_empty():
            return None
        
        timestamp, _, event = heapq.heappop(self._event_queue)
        return (timestamp, event)
    
    def peek(self) -> Optional[Tuple[int, Any]]:
        """
        Peek at the next event without removing it.
        
        Returns:
            Tuple of (timestamp, event), or None if queue is empty.
        """
        if self.is_empty():
            return None
        
        timestamp, _, event = self._event_queue[0]
        return (timestamp, event)
    
    def peek_time(self) -> Optional[int]:
        """
        Get the timestamp of the next event.
        
        Returns:
            Next event time, or None if queue is empty.
        """
        if self.is_empty():
            return None
        return self._event_queue[0][0]
    
    def is_empty(self) -> bool:
        """Check if the scheduler is empty."""
        return len(self._event_queue) == 0
    
    def clear(self) -> None:
        """Clear all scheduled events."""
        self._event_queue.clear()
        self._event_counter = 0
    
    @property
    def pending_count(self) -> int:
        """Get the number of pending events."""
        return len(self._event_queue)

"""
MessageQueue for managing message delivery.

FIFO queue per replica with delivery time tracking.
"""

from typing import List
from typing import Dict
from typing import Tuple
from collections import defaultdict
import heapq

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.models.messages.base_message import BaseMessage


class MessageQueue:
    """
    Priority queue for message delivery.
    
    Messages are stored with their delivery times and delivered
    in order when the simulation time reaches the delivery time.
    """
    
    def __init__(self):
        """Initialize the message queue."""
        self._queues: Dict[int, List[Tuple[int, int, BaseMessage]]] = defaultdict(list)
        self._in_flight: List[Tuple[BaseMessage, int, int, int]] = []
        self._message_counter: int = 0
    
    def enqueue(
        self,
        message: BaseMessage,
        sender_id: ReplicaId,
        target_id: ReplicaId,
        delivery_time: int
    ) -> None:
        """
        Add a message to the queue for delivery.
        
        Args:
            message: The message to queue.
            sender_id: ID of the sending replica.
            target_id: ID of the target replica.
            delivery_time: Simulation time when message should be delivered.
        """
        self._message_counter += 1
        heapq.heappush(
            self._queues[target_id],
            (delivery_time, self._message_counter, message)
        )
        self._in_flight.append((message, sender_id, target_id, delivery_time))
    
    def get_delivered_messages(
        self,
        replica_id: ReplicaId,
        current_time: int
    ) -> List[BaseMessage]:
        """
        Get all messages delivered to a replica by current time.
        
        Messages are removed from the queue once retrieved.
        
        Args:
            replica_id: ID of the replica.
            current_time: Current simulation time.
            
        Returns:
            List of delivered messages in order.
        """
        delivered = []
        queue = self._queues[replica_id]
        
        while queue and queue[0][0] <= current_time:
            delivery_time, _, message = heapq.heappop(queue)
            delivered.append(message)
            self._remove_from_in_flight(message, replica_id, delivery_time)
        
        return delivered
    
    def peek_next_delivery_time(self, replica_id: ReplicaId) -> int:
        """
        Peek at the next delivery time for a replica.
        
        Args:
            replica_id: ID of the replica.
            
        Returns:
            Next delivery time, or -1 if queue is empty.
        """
        queue = self._queues[replica_id]
        if queue:
            return queue[0][0]
        return -1
    
    def get_in_flight_messages(self) -> List[Tuple[BaseMessage, int, int, int]]:
        """
        Get all messages currently in flight.
        
        Returns:
            List of (message, sender_id, target_id, delivery_time) tuples.
        """
        return list(self._in_flight)
    
    def _remove_from_in_flight(
        self,
        message: BaseMessage,
        target_id: ReplicaId,
        delivery_time: int
    ) -> None:
        """Remove a delivered message from the in-flight list."""
        self._in_flight = [
            (m, s, t, d) for (m, s, t, d) in self._in_flight
            if not (m.message_id == message.message_id and t == target_id and d == delivery_time)
        ]
    
    def clear(self) -> None:
        """Clear all queues."""
        self._queues.clear()
        self._in_flight.clear()
        self._message_counter = 0
    
    def get_queue_size(self, replica_id: ReplicaId) -> int:
        """Get the number of pending messages for a replica."""
        return len(self._queues[replica_id])
    
    def get_total_in_flight(self) -> int:
        """Get the total number of messages in flight."""
        return len(self._in_flight)

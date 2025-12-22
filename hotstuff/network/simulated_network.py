"""
SimulatedNetwork implementation.

Provides configurable network delays and message delivery for simulation.
"""

import random
from typing import List
from typing import Set
from typing import Optional

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.models.messages.base_message import BaseMessage
from hotstuff.network.interface import NetworkInterface
from hotstuff.network.message_queue import MessageQueue
from hotstuff.logging_config.logger import StructuredLogger


class SimulatedNetwork(NetworkInterface):
    """
    Simulated network with configurable delays.
    
    Provides deterministic message delivery with configurable
    delay ranges. Supports fault injection through replica blocking.
    """
    
    def __init__(
        self,
        delay_min_ms: int,
        delay_max_ms: int,
        random_seed: Optional[int] = None
    ):
        """
        Initialize the simulated network.
        
        Args:
            delay_min_ms: Minimum network delay in milliseconds.
            delay_max_ms: Maximum network delay in milliseconds.
            random_seed: Random seed for deterministic delays.
        """
        self._delay_min_ms = delay_min_ms
        self._delay_max_ms = delay_max_ms
        self._random = random.Random(random_seed)
        self._message_queue = MessageQueue()
        self._registered_replicas: Set[int] = set()
        self._blocked_replicas: Set[int] = set()
        self._logger = StructuredLogger.get_logger("network")
    
    def register_replica(self, replica_id: ReplicaId) -> None:
        """
        Register a replica with the network.
        
        Args:
            replica_id: ID of the replica to register.
        """
        self._registered_replicas.add(replica_id)
        self._logger.debug(f"Registered replica {replica_id}")
    
    def block_replica(self, replica_id: ReplicaId) -> None:
        """
        Block a replica from receiving messages (fault injection).
        
        Args:
            replica_id: ID of the replica to block.
        """
        self._blocked_replicas.add(replica_id)
        self._logger.info(f"Blocked replica {replica_id}")
    
    def unblock_replica(self, replica_id: ReplicaId) -> None:
        """
        Unblock a previously blocked replica.
        
        Args:
            replica_id: ID of the replica to unblock.
        """
        self._blocked_replicas.discard(replica_id)
        self._logger.info(f"Unblocked replica {replica_id}")
    
    def send(
        self,
        message: BaseMessage,
        target_id: ReplicaId,
        current_time: int
    ) -> int:
        """
        Send a message to a specific replica.
        
        Args:
            message: The message to send.
            target_id: ID of the target replica.
            current_time: Current simulation time.
            
        Returns:
            Delivery time for the message.
        """
        if target_id in self._blocked_replicas:
            self._logger.debug(f"Message to blocked replica {target_id} dropped")
            return -1
        
        delay = self._random.randint(self._delay_min_ms, self._delay_max_ms)
        delivery_time = current_time + delay
        
        self._message_queue.enqueue(
            message=message,
            sender_id=message.sender_id,
            target_id=target_id,
            delivery_time=delivery_time
        )
        
        self._logger.debug(
            f"Message {message.message_type.name} from {message.sender_id} "
            f"to {target_id} scheduled for delivery at {delivery_time}"
        )
        
        return delivery_time
    
    def broadcast(
        self,
        message: BaseMessage,
        sender_id: ReplicaId,
        current_time: int,
        include_sender: bool = False
    ) -> List[int]:
        """
        Broadcast a message to all replicas.
        
        Args:
            message: The message to broadcast.
            sender_id: ID of the sending replica.
            current_time: Current simulation time.
            include_sender: Whether to include sender in broadcast.
            
        Returns:
            List of delivery times for each recipient.
        """
        delivery_times = []
        
        for replica_id in self._registered_replicas:
            if replica_id == sender_id and not include_sender:
                continue
            
            delivery_time = self.send(message, ReplicaId(replica_id), current_time)
            if delivery_time >= 0:
                delivery_times.append(delivery_time)
        
        self._logger.debug(
            f"Broadcast {message.message_type.name} from {sender_id} "
            f"to {len(delivery_times)} replicas"
        )
        
        return delivery_times
    
    def get_pending_messages(
        self,
        replica_id: ReplicaId,
        current_time: int
    ) -> List[BaseMessage]:
        """
        Get all messages delivered to a replica by current time.
        
        Args:
            replica_id: ID of the replica to get messages for.
            current_time: Current simulation time.
            
        Returns:
            List of delivered messages.
        """
        if replica_id in self._blocked_replicas:
            return []
        
        return self._message_queue.get_delivered_messages(replica_id, current_time)
    
    def get_in_flight_messages(self) -> List[tuple]:
        """
        Get all messages currently in transit.
        
        Returns:
            List of (message, sender_id, target_id, delivery_time) tuples.
        """
        return self._message_queue.get_in_flight_messages()
    
    def get_next_delivery_time(self) -> int:
        """
        Get the earliest delivery time across all replicas.
        
        Returns:
            Earliest delivery time, or -1 if no pending messages.
        """
        min_time = -1
        for replica_id in self._registered_replicas:
            if replica_id in self._blocked_replicas:
                continue
            next_time = self._message_queue.peek_next_delivery_time(
                ReplicaId(replica_id)
            )
            if next_time >= 0:
                if min_time < 0 or next_time < min_time:
                    min_time = next_time
        return min_time
    
    def reset(self) -> None:
        """Reset the network state."""
        self._message_queue.clear()
        self._blocked_replicas.clear()
        self._logger.debug("Network reset")
    
    @property
    def registered_replica_count(self) -> int:
        """Get the number of registered replicas."""
        return len(self._registered_replicas)
    
    @property
    def total_in_flight(self) -> int:
        """Get the total number of messages in flight."""
        return self._message_queue.get_total_in_flight()

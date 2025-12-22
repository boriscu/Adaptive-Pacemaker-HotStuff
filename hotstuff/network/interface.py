"""
NetworkInterface abstract class.

Defines the interface for network communication between replicas.
"""

from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional

from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.models.messages.base_message import BaseMessage


class NetworkInterface(ABC):
    """
    Abstract interface for network communication.
    
    Implementations provide message sending and receiving capabilities
    between replicas. The simulated network adds configurable delays.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_in_flight_messages(self) -> List[tuple]:
        """
        Get all messages currently in transit.
        
        Returns:
            List of (message, sender_id, target_id, delivery_time) tuples.
        """
        pass
    
    @abstractmethod
    def register_replica(self, replica_id: ReplicaId) -> None:
        """
        Register a replica with the network.
        
        Args:
            replica_id: ID of the replica to register.
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Reset the network state."""
        pass

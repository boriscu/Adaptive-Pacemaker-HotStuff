"""
LeaderScheduler implementation.

Round-robin leader election as specified in the paper.
"""

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.logging_config.logger import StructuredLogger


class LeaderScheduler:
    """
    Leader election scheduler.
    
    Implements round-robin leader election:
    leader(view) = view mod n
    
    This is the simplest leader election scheme as mentioned in the paper.
    """
    
    def __init__(self, num_replicas: int):
        """
        Initialize the leader scheduler.
        
        Args:
            num_replicas: Total number of replicas in the network.
        """
        self._num_replicas = num_replicas
        self._logger = StructuredLogger.get_logger("leader_scheduler")
    
    def get_leader(self, view_number: ViewNumber) -> ReplicaId:
        """
        Get the leader for a given view.
        
        Implements: leader(view) = view mod n
        
        Args:
            view_number: The view number.
            
        Returns:
            ReplicaId of the leader for this view.
        """
        leader_id = view_number % self._num_replicas
        return ReplicaId(leader_id)
    
    def is_leader(self, replica_id: ReplicaId, view_number: ViewNumber) -> bool:
        """
        Check if a replica is the leader for a view.
        
        Args:
            replica_id: ID of the replica to check.
            view_number: The view number.
            
        Returns:
            True if the replica is the leader, False otherwise.
        """
        return self.get_leader(view_number) == replica_id
    
    def get_next_leader(self, current_view: ViewNumber) -> ReplicaId:
        """
        Get the leader for the next view.
        
        Args:
            current_view: Current view number.
            
        Returns:
            ReplicaId of the leader for view+1.
        """
        return self.get_leader(ViewNumber(current_view + 1))
    
    @property
    def num_replicas(self) -> int:
        """Get the number of replicas."""
        return self._num_replicas

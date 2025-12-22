"""
Unit tests for LeaderScheduler.
"""

import pytest

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.protocol.leader_scheduler import LeaderScheduler


class TestLeaderScheduler:
    """Tests for the LeaderScheduler class."""
    
    def test_round_robin_leader_selection(self):
        """Test that leaders are selected in round-robin fashion."""
        scheduler = LeaderScheduler(num_replicas=4)
        
        assert scheduler.get_leader(ViewNumber(0)) == ReplicaId(0)
        assert scheduler.get_leader(ViewNumber(1)) == ReplicaId(1)
        assert scheduler.get_leader(ViewNumber(2)) == ReplicaId(2)
        assert scheduler.get_leader(ViewNumber(3)) == ReplicaId(3)
        assert scheduler.get_leader(ViewNumber(4)) == ReplicaId(0)
        assert scheduler.get_leader(ViewNumber(5)) == ReplicaId(1)
    
    def test_is_leader(self):
        """Test the is_leader check."""
        scheduler = LeaderScheduler(num_replicas=4)
        
        assert scheduler.is_leader(ReplicaId(0), ViewNumber(0)) is True
        assert scheduler.is_leader(ReplicaId(1), ViewNumber(0)) is False
        assert scheduler.is_leader(ReplicaId(1), ViewNumber(1)) is True
        assert scheduler.is_leader(ReplicaId(0), ViewNumber(4)) is True
    
    def test_get_next_leader(self):
        """Test getting the next view's leader."""
        scheduler = LeaderScheduler(num_replicas=4)
        
        assert scheduler.get_next_leader(ViewNumber(0)) == ReplicaId(1)
        assert scheduler.get_next_leader(ViewNumber(3)) == ReplicaId(0)
    
    def test_different_replica_counts(self):
        """Test leader selection with different replica counts."""
        for num_replicas in [4, 7, 10]:
            scheduler = LeaderScheduler(num_replicas=num_replicas)
            
            for view in range(num_replicas * 2):
                leader = scheduler.get_leader(ViewNumber(view))
                assert 0 <= leader < num_replicas
                assert leader == view % num_replicas

"""
Integration tests for safety invariants.

Tests that the protocol never violates safety:
- No conflicting commits at the same height
- Locked QC is only updated to higher view QC
"""

import pytest

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.simulation.engine import SimulationEngine


class TestSafetyInvariants:
    """Tests for protocol safety invariants."""
    
    def test_no_conflicting_commits(self):
        """Test that no two replicas commit different blocks at the same height."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            base_timeout_ms=1000,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        engine.start()
        
        max_steps = 500
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        commits = [e for e in history if e.get("type") == "COMMIT"]
        
        commits_by_height = {}
        for commit in commits:
            height = commit.get("height")
            block_hash = commit.get("block_hash")
            
            if height not in commits_by_height:
                commits_by_height[height] = set()
            
            commits_by_height[height].add(block_hash)
        
        for height, blocks in commits_by_height.items():
            assert len(blocks) == 1, (
                f"Conflicting commits at height {height}: {blocks}"
            )
    
    def test_locked_qc_monotonically_increasing(self):
        """Test that locked QC view number only increases."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            base_timeout_ms=1000,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        engine.start()
        
        locked_views_by_replica = {i: 0 for i in range(4)}
        
        max_steps = 500
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        lock_updates = [e for e in history if e.get("type") == "LOCK_UPDATE"]
        
        for update in lock_updates:
            replica_id = update.get("replica_id")
            new_locked_view = update.get("locked_view")
            
            assert new_locked_view >= locked_views_by_replica[replica_id], (
                f"Replica {replica_id} locked view decreased from "
                f"{locked_views_by_replica[replica_id]} to {new_locked_view}"
            )
            
            locked_views_by_replica[replica_id] = new_locked_view
    
    def test_commits_happen_in_order(self):
        """Test that commits happen in order of height per replica."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            base_timeout_ms=1000,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        engine.start()
        
        max_steps = 500
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        commits = [e for e in history if e.get("type") == "COMMIT"]
        
        last_committed_height_by_replica = {i: 0 for i in range(4)}
        
        for commit in commits:
            replica_id = commit.get("replica_id")
            height = commit.get("height")
            
            expected_height = last_committed_height_by_replica[replica_id] + 1
            
            assert height == expected_height, (
                f"Replica {replica_id} committed height {height}, "
                f"expected {expected_height}"
            )
            
            last_committed_height_by_replica[replica_id] = height

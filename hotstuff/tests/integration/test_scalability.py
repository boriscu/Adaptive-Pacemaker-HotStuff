"""
Integration tests for scalability.

Tests that consensus works correctly with varying network sizes,
ensuring the synchronized view advancement fixes work correctly.
"""

import pytest

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.simulation.engine import SimulationEngine


class TestScalability:
    """Tests for consensus at various network sizes."""
    
    @pytest.mark.parametrize("num_replicas", [4, 7, 10, 13])
    def test_consensus_with_varying_replicas(self, num_replicas: int):
        """
        Test that consensus is reached with varying numbers of replicas.
        
        The synchronized view advancement should prevent view fragmentation
        and allow consensus to be reached even with larger networks.
        """
        max_faulty = (num_replicas - 1) // 3
        
        settings = Settings(
            num_replicas=num_replicas,
            num_faulty=0, 
            base_timeout_ms=5000,  
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        engine.start()
        
 
        max_steps = 500 * num_replicas
        
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        commits = [e for e in history if e.get("type") == "COMMIT"]
        
        assert len(commits) > 0, (
            f"No blocks committed with {num_replicas} replicas. "
            f"Total views: {engine.current_view}"
        )
    
    def test_view_progression_with_timeouts(self):
        """
        Test that view progression works even when timeouts occur.
        
        With the proper quorum_size (2f+1), the protocol should make progress.
        """
        settings = Settings(
            num_replicas=7,
            num_faulty=0,
            base_timeout_ms=100,   
            network_delay_min_ms=50,
            network_delay_max_ms=200,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        engine.start()
        
        max_steps = 5000
        
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        
        timeout_events = [e for e in history if e.get("type") == "TIMEOUT"]
        
        assert engine.current_view > 1, "Simulation should advance past view 1"
        
        commits = [e for e in history if e.get("type") == "COMMIT"]

    
    def test_large_network_commits_block(self):
        """
        Test that a larger network (13 replicas) can commit blocks.
        
        This is the key test for the scaling fix.
        """
        settings = Settings(
            num_replicas=13,
            num_faulty=0,
            base_timeout_ms=10000, 
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        engine.start()
        
        max_steps = 13 * 13 * 100  
        
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        commits = [e for e in history if e.get("type") == "COMMIT"]
        
        assert len(commits) > 0, (
            f"No blocks committed with 13 replicas. "
            f"Total views: {engine.current_view}"
        )

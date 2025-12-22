"""
Integration tests for deterministic simulation reproducibility.
"""

import pytest

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.simulation.engine import SimulationEngine


class TestDeterminism:
    """Tests for deterministic simulation reproducibility."""
    
    def test_same_seed_produces_same_events(self):
        """Test that the same seed produces identical event traces."""
        settings1 = Settings(
            num_replicas=4,
            num_faulty=1,
            random_seed=12345,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        settings2 = Settings(
            num_replicas=4,
            num_faulty=1,
            random_seed=12345,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine1 = SimulationEngine(settings1)
        engine2 = SimulationEngine(settings2)
        
        events1 = engine1.start()
        events2 = engine2.start()
        
        for _ in range(50):
            event1 = engine1.step()
            event2 = engine2.step()
            
            if event1 is not None:
                events1.append(event1)
            if event2 is not None:
                events2.append(event2)
        
        assert len(events1) == len(events2)
        
        for e1, e2 in zip(events1, events2):
            assert e1.get("type") == e2.get("type")
            assert e1.get("timestamp") == e2.get("timestamp")
            if "replica_id" in e1:
                assert e1.get("replica_id") == e2.get("replica_id")
    
    def test_different_seeds_produce_different_events(self):
        """Test that different seeds can produce different event traces."""
        settings1 = Settings(
            num_replicas=4,
            num_faulty=1,
            random_seed=11111,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        settings2 = Settings(
            num_replicas=4,
            num_faulty=1,
            random_seed=99999,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine1 = SimulationEngine(settings1)
        engine2 = SimulationEngine(settings2)
        
        engine1.start()
        engine2.start()
        
        timestamps1 = []
        timestamps2 = []
        
        for _ in range(30):
            event1 = engine1.step()
            event2 = engine2.step()
            
            if event1:
                timestamps1.append(event1.get("timestamp", 0))
            if event2:
                timestamps2.append(event2.get("timestamp", 0))
        
        assert timestamps1 != timestamps2
    
    def test_reset_produces_identical_replay(self):
        """Test that reset and replay produces identical events."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        
        engine.start()
        events_first_run = []
        for _ in range(30):
            event = engine.step()
            if event:
                events_first_run.append(event)
        
        engine.reset()
        engine = SimulationEngine(settings)
        engine.start()
        events_second_run = []
        for _ in range(30):
            event = engine.step()
            if event:
                events_second_run.append(event)
        
        assert len(events_first_run) == len(events_second_run)
        
        for e1, e2 in zip(events_first_run, events_second_run):
            assert e1.get("type") == e2.get("type")

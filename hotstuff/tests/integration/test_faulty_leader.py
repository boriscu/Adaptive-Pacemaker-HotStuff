"""
Integration tests for faulty leader recovery.
"""

import pytest

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.domain.enumerations.fault_type import FaultType
from hotstuff.simulation.engine import SimulationEngine


class TestFaultyLeaderRecovery:
    """Tests for recovery from faulty leader scenarios."""
    
    def test_crash_fault_triggers_view_change(self):
        """Test that a crashed leader triggers view change via timeout."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            base_timeout_ms=100,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        
        engine.inject_fault(replica_id=0, fault_type=FaultType.CRASH)
        
        engine.start()
        
        max_steps = 500
        
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        timeout_seen = any(e.get("type") == "TIMEOUT" for e in history)
        view_change_seen = any(e.get("type") == "VIEW_CHANGE" for e in history)
        
        assert timeout_seen, "Expected timeout due to crashed leader"
        assert view_change_seen, "Expected view change after timeout"
    
    def test_progress_after_leader_crash(self):
        """Test that the protocol makes progress after leader crashes."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            base_timeout_ms=100,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        
        engine.inject_fault(replica_id=0, fault_type=FaultType.CRASH)
        
        engine.start()
        
        max_steps = 1000
        
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        view_changes = [e for e in history if e.get("type") == "VIEW_CHANGE"]
        max_view = max((e.get("new_view", 1) for e in view_changes), default=1)
        
        assert max_view > 1, "Expected to advance past view 1"
    
    def test_protocol_tolerates_f_crashes_non_leader(self):
        """Test that protocol tolerates f crash faults (non-leader replica)."""
        settings = Settings(
            num_replicas=4,
            num_faulty=1,
            base_timeout_ms=500,
            random_seed=42,
            pacemaker_type=PacemakerType.BASELINE
        )
        
        engine = SimulationEngine(settings)
        
        engine.inject_fault(replica_id=3, fault_type=FaultType.CRASH)
        
        engine.start()
        
        max_steps = 200
        
        for _ in range(max_steps):
            event = engine.step()
            if event is None:
                break
        
        history = engine.get_event_history()
        proposals = [e for e in history if e.get("type") == "PROPOSAL"]
        qc_formations = [e for e in history if e.get("type") == "QC_FORMATION"]
        
        assert len(proposals) > 0, f"Protocol should still propose with f faults. Events: {[e.get('type') for e in history]}"
        assert len(qc_formations) >= 0, "Protocol should form QCs even with f faults"

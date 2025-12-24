"""
SimulationEngine for running the HotStuff simulation.

Main simulation loop with step-by-step control.
"""

from typing import List
from typing import Dict
from typing import Optional

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.domain.enumerations.fault_type import FaultType
from hotstuff.domain.models.replica_state import ReplicaState
from hotstuff.config.settings import Settings
from hotstuff.protocol.replica import Replica
from hotstuff.protocol.leader_scheduler import LeaderScheduler
from hotstuff.pacemaker.interface import PacemakerInterface
from hotstuff.pacemaker.base_pacemaker import BasePacemaker
from hotstuff.pacemaker.adaptive_pacemaker import AdaptivePacemaker
from hotstuff.network.simulated_network import SimulatedNetwork
from hotstuff.simulation.clock import SimulationClock
from hotstuff.simulation.scheduler import DiscreteEventScheduler
from hotstuff.logging_config.logger import StructuredLogger


class SimulationEngine:
    """
    Main simulation engine for HotStuff consensus.
    
    Manages replicas, network, pacemaker, and simulation clock.
    Provides step-by-step execution control for UI visualization.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the simulation engine.
        
        Args:
            settings: Configuration settings.
        """
        self._settings = settings
        self._clock = SimulationClock()
        self._scheduler = DiscreteEventScheduler()
        
        self._network = SimulatedNetwork(
            delay_min_ms=settings.network_delay_min_ms,
            delay_max_ms=settings.network_delay_max_ms,
            random_seed=settings.random_seed
        )
        
        self._leader_scheduler = LeaderScheduler(settings.num_replicas)
        
        self._pacemakers: Dict[int, PacemakerInterface] = {}
        self._replicas: Dict[int, Replica] = {}
        
        for i in range(settings.num_replicas):
            replica_id = ReplicaId(i)
            self._network.register_replica(replica_id)
            
            if settings.pacemaker_type == PacemakerType.ADAPTIVE:
                pacemaker = AdaptivePacemaker(
                    base_timeout_ms=settings.base_timeout_ms,
                    alpha=settings.adaptive_alpha,
                    min_timeout_ms=settings.adaptive_min_timeout_ms,
                    max_timeout_ms=settings.adaptive_max_timeout_ms
                )
            else:
                pacemaker = BasePacemaker(settings.base_timeout_ms)
            
            self._pacemakers[i] = pacemaker
            
            replica = Replica(
                replica_id=replica_id,
                num_replicas=settings.num_replicas,
                quorum_size=settings.quorum_size,
                network=self._network,
                leader_scheduler=self._leader_scheduler
            )
            self._replicas[i] = replica
        
        self._current_view: ViewNumber = ViewNumber(1)
        self._is_running: bool = False
        self._is_paused: bool = False
        self._event_history: List[dict] = []
        self._view_start_times: Dict[int, int] = {}
        self._view_timeout_votes: Dict[int, set] = {}
        self._quorum_size = settings.quorum_size
        
        self._logger = StructuredLogger.get_logger("engine")
        for i in range(settings.num_replicas - settings.num_faulty, settings.num_replicas):
            self._replicas[i].inject_fault(settings.fault_type)
            if settings.fault_type == FaultType.CRASH:
                self._network.block_replica(ReplicaId(i))
            self._logger.info(f"Replica {i} marked as faulty ({settings.fault_type.name})")
    
    def start(self) -> List[dict]:
        """
        Start the simulation.
        
        Initializes view 1 and returns initial events.
        
        Returns:
            List of initial events.
        """
        self._is_running = True
        self._is_paused = False
        
        self._logger.info("Simulation started")
        
        return self._start_view(ViewNumber(1))
    
    def _start_view(self, view_number: ViewNumber) -> List[dict]:
        """Start a new view for all replicas."""
        self._current_view = view_number
        self._view_start_times[view_number] = self._clock.current_time
        
        events = []
        
        for replica_id, replica in self._replicas.items():
            replica_events = replica.start_view(view_number, self._clock.current_time)
            events.extend(replica_events)
            
            pacemaker = self._pacemakers[replica_id]
            timeout_time = pacemaker.start_timer(view_number, self._clock.current_time)
            
            self._scheduler.schedule(
                {
                    "type": "TIMEOUT",
                    "replica_id": replica_id,
                    "view": view_number,
                    "timeout_time": timeout_time
                },
                timeout_time
            )
        
        self._logger.info(f"Started view {view_number}")
        
        for event in events:
            self._event_history.append(event)
        
        return events
    
    def step(self) -> Optional[dict]:
        """
        Execute a single simulation step.
        
        Returns:
            The event that was processed, or None if no events.
        """
        if not self._is_running:
            return None
        
        max_iterations = 100  
        for _ in range(max_iterations):
            next_delivery_time = self._network.get_next_delivery_time()
            next_scheduled_time = self._scheduler.peek_time()
            
            if next_delivery_time < 0 and next_scheduled_time is None:
                return None
            
            if next_delivery_time >= 0:
                if next_scheduled_time is None or next_delivery_time <= next_scheduled_time:
                    result = self._process_message_delivery(next_delivery_time)
                    if result is not None:
                        return result
                    continue
            
            if next_scheduled_time is not None:
                result = self._process_scheduled_event()
                if result is not None:
                    return result
                continue
            
            break
        
        return None
    
    def _process_message_delivery(self, delivery_time: int) -> Optional[dict]:
        """Process message deliveries at the given time."""
        self._clock.advance_to(delivery_time)
        
        event = None
        
        for replica_id in range(self._settings.num_replicas):
            messages = self._network.get_pending_messages(
                ReplicaId(replica_id),
                self._clock.current_time
            )
            
            for message in messages:
                replica = self._replicas[replica_id]
                message_events = replica.handle_message(message, self._clock.current_time)
                
                event = {
                    "type": "MESSAGE_RECEIVE",
                    "timestamp": self._clock.current_time,
                    "recipient_id": replica_id,
                    "sender_id": message.sender_id,
                    "message_type": message.message_type.name,
                    "message_id": message.message_id
                }
                self._event_history.append(event)
                
                for msg_event in message_events:
                    self._event_history.append(msg_event)
                    
                    if msg_event.get("type") == "COMMIT":
                        self._on_block_committed(replica_id, msg_event)
        
        return event
    
    def _process_scheduled_event(self) -> Optional[dict]:
        """Process the next scheduled event."""
        result = self._scheduler.next_event()
        if result is None:
            return None
        
        timestamp, scheduled_event = result
        self._clock.advance_to(timestamp)
        
        if scheduled_event.get("type") == "TIMEOUT":
            return self._handle_timeout(scheduled_event)
        
        return None
    
    def _handle_timeout(self, timeout_event: dict) -> Optional[dict]:
        """
        Handle a timeout event - advance this replica to the next view.
        
        Each replica advances independently on timeout. This ensures proper
        QC propagation - the new leader will collect new-view messages with
        QCs and select the highest one to propose with.
        """
        replica_id = timeout_event["replica_id"]
        view = timeout_event["view"]
        
        replica = self._replicas[replica_id]
        if replica.current_view != view:
            return None
        
        pacemaker = self._pacemakers[replica_id]
        next_view = pacemaker.on_timeout(self._clock.current_time)
        
        event = {
            "type": "TIMEOUT",
            "timestamp": self._clock.current_time,
            "replica_id": replica_id,
            "view": view,
            "next_view": next_view
        }
        self._event_history.append(event)
        
        self._logger.info(f"Replica {replica_id} timeout in view {view}")
        
        view_events = replica.start_view(next_view, self._clock.current_time)
        for v_event in view_events:
            self._event_history.append(v_event)
        
        new_timeout = pacemaker.start_timer(next_view, self._clock.current_time)
        self._scheduler.schedule(
            {
                "type": "TIMEOUT",
                "replica_id": replica_id,
                "view": next_view,
                "timeout_time": new_timeout
            },
            new_timeout
        )
        
        return event
    
    def _on_block_committed(self, replica_id: int, commit_event: dict) -> None:
        """
        Handle a block commit - advance this replica to next view.
        
        When a block is committed, the committing replica advances to the 
        next view. Other replicas will advance when they receive the Decide
        message or when they timeout.
        
        Note: Synchronized view advancement is used for the timeout path,
        not the commit path, to preserve proper commit ordering.
        """
        view = self._replicas[replica_id].current_view
        
        if view < self._current_view:
            return
        
        if view in self._view_start_times:
            duration = self._clock.current_time - self._view_start_times[view]
            pacemaker = self._pacemakers[replica_id]
            pacemaker.on_view_success(view, duration)
            pacemaker.stop_timer()
        
        next_view = ViewNumber(view + 1)
        
        if next_view > self._current_view:
            self._current_view = next_view
            self._view_start_times[next_view] = self._clock.current_time
        
        view_events = self._replicas[replica_id].start_view(next_view, self._clock.current_time)
        for v_event in view_events:
            self._event_history.append(v_event)
        
        pacemaker = self._pacemakers[replica_id]
        new_timeout = pacemaker.start_timer(next_view, self._clock.current_time)
        self._scheduler.schedule(
            {
                "type": "TIMEOUT",
                "replica_id": replica_id,
                "view": next_view,
                "timeout_time": new_timeout
            },
            new_timeout
        )
    
    def pause(self) -> None:
        """Pause the simulation."""
        self._is_paused = True
        self._logger.info("Simulation paused")
    
    def resume(self) -> None:
        """Resume the simulation."""
        self._is_paused = False
        self._logger.info("Simulation resumed")
    
    def reset(self) -> None:
        """Reset the simulation to initial state."""
        self._clock.reset()
        self._scheduler.clear()
        self._network.reset()
        self._event_history.clear()
        self._view_start_times.clear()
        self._view_timeout_votes.clear()
        
        for pacemaker in self._pacemakers.values():
            pacemaker.reset()
        
        for i in range(self._settings.num_replicas):
            replica_id = ReplicaId(i)
            self._network.register_replica(replica_id)
            
            replica = Replica(
                replica_id=replica_id,
                num_replicas=self._settings.num_replicas,
                quorum_size=self._settings.quorum_size,
                network=self._network,
                leader_scheduler=self._leader_scheduler
            )
            self._replicas[i] = replica
        
        for i in range(self._settings.num_replicas - self._settings.num_faulty, self._settings.num_replicas):
            self._replicas[i].inject_fault(self._settings.fault_type)
            if self._settings.fault_type == FaultType.CRASH:
                self._network.block_replica(ReplicaId(i))
        
        self._current_view = ViewNumber(1)
        self._is_running = False
        self._is_paused = False
        
        self._logger.info("Simulation reset")
    
    def inject_fault(self, replica_id: int, fault_type: FaultType) -> None:
        """Inject a fault into a replica."""
        if replica_id in self._replicas:
            self._replicas[replica_id].inject_fault(fault_type)
            if fault_type == FaultType.CRASH:
                self._network.block_replica(ReplicaId(replica_id))
    
    def clear_fault(self, replica_id: int) -> None:
        """Clear a fault from a replica."""
        if replica_id in self._replicas:
            self._replicas[replica_id].clear_fault()
            self._network.unblock_replica(ReplicaId(replica_id))
    
    def get_replica_states(self) -> List[ReplicaState]:
        """Get the state of all replicas."""
        return [replica.get_state() for replica in self._replicas.values()]
    
    def get_replica_state(self, replica_id: int) -> Optional[ReplicaState]:
        """Get the state of a specific replica."""
        if replica_id in self._replicas:
            return self._replicas[replica_id].get_state()
        return None
    
    def get_event_history(self) -> List[dict]:
        """Get the full event history."""
        return list(self._event_history)
    
    def get_recent_events(self, count: int = 50) -> List[dict]:
        """Get the most recent events."""
        return self._event_history[-count:]
    
    def get_in_flight_messages(self) -> List[dict]:
        """Get messages currently in flight."""
        in_flight = self._network.get_in_flight_messages()
        return [
            {
                "message_id": msg.message_id,
                "message_type": msg.message_type.name,
                "sender_id": sender_id,
                "target_id": target_id,
                "delivery_time": delivery_time
            }
            for msg, sender_id, target_id, delivery_time in in_flight
        ]
    
    @property
    def current_time(self) -> int:
        """Get the current simulation time."""
        return self._clock.current_time
    
    @property
    def current_view(self) -> ViewNumber:
        """Get the current view number."""
        return self._current_view
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self._is_running
    
    @property
    def is_paused(self) -> bool:
        """Check if simulation is paused."""
        return self._is_paused
    
    @property
    def settings(self) -> Settings:
        """Get the simulation settings."""
        return self._settings

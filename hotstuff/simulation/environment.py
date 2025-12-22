from typing import Dict, Callable
import random

from hotstuff.config import config, PacemakerMode
from hotstuff.logger import logger
from hotstuff.domain.enums import EventType
from hotstuff.network.simulated import SimulatedNetwork
from hotstuff.protocol.replica import Replica
from hotstuff.protocol.harness import ReplicaHarness
from hotstuff.pacemaker.baseline import BaselinePacemaker
from hotstuff.pacemaker.adaptive import AdaptivePacemaker
from hotstuff.simulation.engine import SimulationEngine

class Environment:
    """
    Sets up and manages the simulation world.
    - Creates Replicas, Network, Pacemakers.
    - bootstraps the run.
    """
    def __init__(self):
        self.engine = SimulationEngine()
        self.network = SimulatedNetwork(scheduler_callback=self._network_scheduler_shim)
        self.replicas: Dict[int, ReplicaHarness] = {}
        
        self.setup()
        
    def _network_scheduler_shim(self, delay: float, payload: object, destination: int):
        """
        Bridge between Network (which wants to send msg) and Engine (which schedules it).
        Payload is either Msg or VoteMsg.
        """
        # Determine EventType based on payload type? 
        # Actually Network abstractions usually separate send_msg and send_vote,
        # but SimulatedNetwork calls this same callback for both?
        # Let's check SimulatedNetwork implementation.
        # It calls callback(latency, msg, destination).
        
        # We need to wrap this into a callback that the Engine can execute.
        # The Engine callback should be independent of the destination instance if possible,
        # OR we lookup the destination here.
        
        target_replica = self.replicas.get(destination)
        if not target_replica:
            return

        # Determine type
        # We can inspect payload class name or attribute
        # But cleaner if we pass type or infer it.
        # HACK: check attribute 'node' (Msg) vs 'partial_sig' (VoteMsg)
        if hasattr(payload, 'partial_sig'):
            event_type = EventType.VOTE
        else:
            event_type = EventType.MSG
            
        self.engine.schedule(
            delay,
            target_replica.process_event,
            event_type,
            payload,
            description=f"Deliver {event_type} to R{destination}"
        )

    def _timer_scheduler_shim(self, delay: float, callback: Callable, *args):
        """
        Schedules a timeout callback on the engine.
        """
        self.engine.schedule(
            delay,
            callback,
            *args,
            description=f"Timeout for args {args}"
        )

    def setup(self):
        """
        Initialize the system based on config.
        """
        if config.SEED is not None:
            random.seed(config.SEED)
        
        logger.info(f"Setting up environment with N={config.N}, F={config.F}")
        
        for i in range(config.N):
            # 1. Create Pacemaker
            if config.PACEMAKER == PacemakerMode.ADAPTIVE:
                pm = AdaptivePacemaker(n=config.N)
            else:
                pm = BaselinePacemaker(n=config.N)
            
            # 2. Create Replica
            replica = Replica(
                id=i, 
                network=self.network, 
                pacemaker=pm,
                timer_scheduler=self._timer_scheduler_shim
            )
            
            # 3. Create Harness
            harness = ReplicaHarness(replica)
            self.replicas[i] = harness

    def start(self):
        """
        Bootstraps the simulation.
        Triggers the first View Change for all replicas to enter View 1.
        """
        logger.info("Bootstrapping simulation...")
        
        # Schedule initial "Start" / Next View events for all replicas
        # mimicking them finishing View 0 and moving to View 1
        for i in range(config.N):
            self.engine.schedule(
                random.uniform(0.0, 0.1), # slight jitter start
                self.replicas[i].process_event,
                EventType.NEXT_VIEW,
                None, # No payload for NEXT_VIEW
                description=f"Start Replica {i}"
            )

    def run(self, max_time: float = 100.0):
        self.start()
        self.engine.run(max_time=max_time)

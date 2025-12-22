import random
from typing import Callable

from hotstuff.network.interfaces import Network
from hotstuff.domain.models import Msg, VoteMsg
from hotstuff.config import config

class SimulatedNetwork(Network):
    """
    In-memory simulated network.
    It doesn't deliver messages immediately. It schedules them or queues them
    to be pulled by the simulation engine.
    """
    def __init__(self, scheduler_callback: Callable[[float, Any, int], None]):
        """
        Args:
            scheduler_callback: Function to schedule an event (delivery_time, payload, recipient_id).
                                signature: (delay, message, dest_id)
        """
        self.scheduler_callback = scheduler_callback
        self.total_replicas = config.N
        
    def _calculate_latency(self) -> float:
        """Returns deterministic or random latency based on config."""
        return random.uniform(config.NETWORK_LATENCY_MIN, config.NETWORK_LATENCY_MAX)

    def _should_drop(self) -> bool:
        return random.random() < config.DROP_PROBABILITY

    def send_msg(self, msg: Msg, destination: int):
        if self._should_drop():
            return
        latency = self._calculate_latency()
        self.scheduler_callback(latency, msg, destination)

    def broadcast_msg(self, msg: Msg):
        for i in range(self.total_replicas):
            if i != msg.sender: 
                self.send_msg(msg, i)

    def send_vote(self, vote: VoteMsg, destination: int):
        if self._should_drop():
            return
        latency = self._calculate_latency()
        self.scheduler_callback(latency, vote, destination)

    def broadcast_vote(self, vote: VoteMsg):
        for i in range(self.total_replicas):
            self.send_vote(vote, i)

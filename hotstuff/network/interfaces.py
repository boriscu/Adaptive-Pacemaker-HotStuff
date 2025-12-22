from abc import ABC, abstractmethod

from hotstuff.domain.models import Msg, VoteMsg

class Network(ABC):
    """
    Abstract Interface for the Network Layer.
    Replicas usage: self.network.send(msg, dest) or self.network.broadcast(msg).
    """

    @abstractmethod
    def send_msg(self, msg: Msg, destination: int):
        """Send a protocol message to a specific replica."""
        pass
    
    @abstractmethod
    def broadcast_msg(self, msg: Msg):
        """Broadcast a protocol message to all replicas."""
        pass

    @abstractmethod
    def send_vote(self, vote: VoteMsg, destination: int):
        """Send a vote to a specific replica (usually the leader)."""
        pass

    @abstractmethod
    def broadcast_vote(self, vote: VoteMsg):
        """Broadcast a vote (less common, but possible)."""
        pass

from abc import ABC, abstractmethod
from hotstuff.domain.models import Block, Msg, VoteMsg

class ReplicaInterface(ABC):
    """
    Abstract Interface for a HotStuff Replica.
    Defines the external API for the simulation engine to interaction with.
    """

    @abstractmethod
    def on_start(self):
        """Called start the replica."""
        pass

    @abstractmethod
    def on_receive_msg(self, msg: Msg):
        """Handler for incoming protocol messages."""
        pass

    @abstractmethod
    def on_receive_vote(self, vote: VoteMsg):
        """Handler for incoming votes."""
        pass
    
    @abstractmethod
    def on_next_view(self):
        """Handler for view timer interrupt."""
        pass

    @abstractmethod
    def get_commit_history(self) -> list[Block]:
        """Returns the list of committed blocks for verification."""
        pass

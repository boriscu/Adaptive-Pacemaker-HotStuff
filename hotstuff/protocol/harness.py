from hotstuff.protocol.replica import Replica
from hotstuff.domain.enums import EventType
from hotstuff.logger import logger

class ReplicaHarness:
    """
    Wrapper around the Replica to be used by the Simulation Engine.
    Handles exception isolation and metrics hooks.
    """
    def __init__(self, replica: Replica):
        self.replica = replica

    def process_event(self, event_type: EventType, payload):
        """
        Generic event dispatcher using EventType enum.
        """
        try:
            if event_type == EventType.MSG:
                self.replica.on_receive_msg(payload)
            elif event_type == EventType.VOTE:
                self.replica.on_receive_vote(payload)
            elif event_type == EventType.NEXT_VIEW:
                self.replica.on_next_view()
        except Exception as e:
            logger.error(f"Event processing error: {e}", exc_info=True)

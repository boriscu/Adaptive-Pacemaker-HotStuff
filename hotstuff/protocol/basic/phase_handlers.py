"""
Individual phase handlers for Basic HotStuff.

These classes provide a more granular separation for each phase,
useful for testing and documentation purposes.
"""

from typing import List
from typing import Optional
from typing import Dict

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.prepare_message import PrepareMessage
from hotstuff.domain.models.messages.precommit_message import PreCommitMessage
from hotstuff.domain.models.messages.commit_message import CommitMessage
from hotstuff.domain.models.messages.decide_message import DecideMessage
from hotstuff.protocol.safety_rules import SafetyRules
from hotstuff.protocol.leader_scheduler import LeaderScheduler
from hotstuff.factories.message_factory import MessageFactory
from hotstuff.network.simulated_network import SimulatedNetwork


class PreparePhaseHandler:
    """
    Handler for the PREPARE phase.

    Upon receiving a PREPARE message from the leader:
    1. Verify the block is safe using safeNode predicate
    2. If safe, send PREPARE_VOTE to the leader
    """

    def __init__(
        self,
        replica_id: ReplicaId,
        network: SimulatedNetwork,
        leader_scheduler: LeaderScheduler,
        safety_rules: SafetyRules,
        block_store: Dict[BlockHash, Block],
    ):
        self._replica_id = replica_id
        self._network = network
        self._leader_scheduler = leader_scheduler
        self._safety_rules = safety_rules
        self._block_store = block_store

    def handle(
        self,
        message: PrepareMessage,
        current_view: ViewNumber,
        locked_qc: Optional[QuorumCertificate],
        last_voted_view: Optional[ViewNumber],
        current_time: int,
    ) -> tuple[List[dict], Block, Optional[ViewNumber]]:
        """Process PREPARE message and vote if safe."""
        block = message.block

        self._block_store[block.block_hash] = block
        self._safety_rules.register_block(block)

        if not self._safety_rules.is_safe_node(block, message.high_qc, locked_qc):
            return [], block, last_voted_view

        if last_voted_view is not None and current_view <= last_voted_view:
            return [], block, last_voted_view

        leader_id = self._leader_scheduler.get_leader(current_view)

        vote = MessageFactory.create_prepare_vote(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=block.block_hash,
            target_id=leader_id,
            timestamp=current_time,
        )

        self._network.send(vote, leader_id, current_time)

        events = [
            {
                "type": "VOTE_SEND",
                "replica_id": self._replica_id,
                "vote_type": "PREPARE",
                "block_hash": block.block_hash,
                "timestamp": current_time,
            }
        ]

        return events, block, current_view


class PreCommitPhaseHandler:
    """
    Handler for the PRE-COMMIT phase.

    Upon receiving a PRE_COMMIT message:
    1. Update prepareQC
    2. Send PRE_COMMIT_VOTE to the leader
    """

    def __init__(
        self,
        replica_id: ReplicaId,
        network: SimulatedNetwork,
        leader_scheduler: LeaderScheduler,
    ):
        self._replica_id = replica_id
        self._network = network
        self._leader_scheduler = leader_scheduler

    def handle(
        self, message: PreCommitMessage, current_view: ViewNumber, current_time: int
    ) -> tuple[List[dict], QuorumCertificate]:
        """Process PRE_COMMIT message and vote."""
        leader_id = self._leader_scheduler.get_leader(current_view)

        vote = MessageFactory.create_precommit_vote(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=message.prepare_qc.block_hash,
            target_id=leader_id,
            timestamp=current_time,
        )

        self._network.send(vote, leader_id, current_time)

        events = [
            {
                "type": "VOTE_SEND",
                "replica_id": self._replica_id,
                "vote_type": "PRE_COMMIT",
                "block_hash": message.prepare_qc.block_hash,
                "timestamp": current_time,
            }
        ]

        return events, message.prepare_qc


class CommitPhaseHandler:
    """
    Handler for the COMMIT phase.

    Upon receiving a COMMIT message:
    1. Update lockedQC (this is the locking step!)
    2. Send COMMIT_VOTE to the leader
    """

    def __init__(
        self,
        replica_id: ReplicaId,
        network: SimulatedNetwork,
        leader_scheduler: LeaderScheduler,
    ):
        self._replica_id = replica_id
        self._network = network
        self._leader_scheduler = leader_scheduler

    def handle(
        self, message: CommitMessage, current_view: ViewNumber, current_time: int
    ) -> tuple[List[dict], QuorumCertificate]:
        """Process COMMIT message, lock, and vote."""
        leader_id = self._leader_scheduler.get_leader(current_view)

        vote = MessageFactory.create_commit_vote(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=message.precommit_qc.block_hash,
            target_id=leader_id,
            timestamp=current_time,
        )

        self._network.send(vote, leader_id, current_time)

        events = [
            {
                "type": "LOCK_UPDATE",
                "replica_id": self._replica_id,
                "locked_view": message.precommit_qc.view_number,
                "timestamp": current_time,
            },
            {
                "type": "VOTE_SEND",
                "replica_id": self._replica_id,
                "vote_type": "COMMIT",
                "block_hash": message.precommit_qc.block_hash,
                "timestamp": current_time,
            },
        ]

        return events, message.precommit_qc


class DecidePhaseHandler:
    """
    Handler for the DECIDE phase.

    Upon receiving a DECIDE message:
    1. Execute (commit) the block
    """

    def __init__(self, replica_id: ReplicaId, block_store: Dict[BlockHash, Block]):
        self._replica_id = replica_id
        self._block_store = block_store

    def handle(
        self, message: DecideMessage, committed_block_hashes: set, current_time: int
    ) -> tuple[List[dict], Optional[Block]]:
        """Process DECIDE message and commit the block."""
        block = self._block_store.get(message.commit_qc.block_hash)

        if block and block.block_hash not in committed_block_hashes:
            events = [
                {
                    "type": "COMMIT",
                    "replica_id": self._replica_id,
                    "block_hash": block.block_hash,
                    "height": block.height,
                    "timestamp": current_time,
                }
            ]

            return events, block

        return [], None

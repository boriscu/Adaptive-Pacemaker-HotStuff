"""
BasicHotStuffHandler - Main handler for Basic HotStuff protocol.

Implements Algorithm 2 from the HotStuff paper with 4 phases:
PREPARE -> PRE-COMMIT -> COMMIT -> DECIDE
"""

from typing import List
from typing import Optional
from typing import Dict

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.types.command import Command
from hotstuff.domain.enumerations.phase_type import PhaseType
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.new_view_message import NewViewMessage
from hotstuff.domain.models.messages.prepare_message import PrepareMessage
from hotstuff.domain.models.messages.precommit_message import PreCommitMessage
from hotstuff.domain.models.messages.commit_message import CommitMessage
from hotstuff.domain.models.messages.decide_message import DecideMessage
from hotstuff.domain.models.messages.prepare_vote import PrepareVote
from hotstuff.domain.models.messages.precommit_vote import PreCommitVote
from hotstuff.domain.models.messages.commit_vote import CommitVote
from hotstuff.protocol.safety_rules import SafetyRules
from hotstuff.protocol.vote_collector import VoteCollector
from hotstuff.protocol.leader_scheduler import LeaderScheduler
from hotstuff.factories.block_factory import BlockFactory
from hotstuff.factories.message_factory import MessageFactory
from hotstuff.network.simulated_network import SimulatedNetwork
from hotstuff.logging_config.logger import StructuredLogger


class BasicHotStuffHandler:
    """
    Handler for Basic HotStuff protocol.

    Implements Algorithm 2 from the HotStuff paper:
    - NEW-VIEW phase: Replicas send highQC to new leader
    - PREPARE phase: Leader proposes block, replicas vote if safe
    - PRE-COMMIT phase: Leader broadcasts prepareQC, replicas vote
    - COMMIT phase: Leader broadcasts precommitQC (lock), replicas vote
    - DECIDE phase: Leader broadcasts commitQC, replicas execute
    """

    def __init__(
        self,
        replica_id: ReplicaId,
        quorum_size: int,
        network: SimulatedNetwork,
        leader_scheduler: LeaderScheduler,
        safety_rules: SafetyRules,
        vote_collector: VoteCollector,
        block_store: Dict[BlockHash, Block],
        logger: StructuredLogger,
    ):
        """
        Initialize the Basic HotStuff handler.

        Args:
            replica_id: ID of the owning replica.
            quorum_size: Required votes for QC (2f+1).
            network: Network interface for communication.
            leader_scheduler: Leader election scheduler.
            safety_rules: Safety rules for voting.
            vote_collector: Vote collector for QC formation.
            block_store: Shared block storage.
            logger: Logger instance.
        """
        self._replica_id = replica_id
        self._quorum_size = quorum_size
        self._network = network
        self._leader_scheduler = leader_scheduler
        self._safety_rules = safety_rules
        self._vote_collector = vote_collector
        self._block_store = block_store
        self._logger = logger

        self._new_view_messages: List[NewViewMessage] = []
        self._command_counter: int = 0
        self._last_proposed_view: ViewNumber = ViewNumber(0)

    def handle_new_view(
        self,
        message: NewViewMessage,
        current_view: ViewNumber,
        is_leader: bool,
        current_time: int,
    ) -> tuple[List[dict], Optional[Block], Optional[PhaseType]]:
        """
        Handle a NEW_VIEW message (leader only).

        Args:
            message: The new-view message.
            current_view: Current view number.
            is_leader: Whether this replica is the leader.
            current_time: Current simulation time.

        Returns:
            Tuple of (events, pending_block, new_phase).
        """
        if not is_leader:
            return [], None, None

        self._new_view_messages.append(message)

        self._logger.debug(
            f"Received new-view from {message.sender_id}, "
            f"count: {len(self._new_view_messages)}/{self._quorum_size}"
        )

        if current_view <= self._last_proposed_view:
            return [], None, None

        if len(self._new_view_messages) >= self._quorum_size:
            self._last_proposed_view = current_view
            return self._propose_block(current_view, current_time)

        return [], None, None

    def _propose_block(
        self, current_view: ViewNumber, current_time: int
    ) -> tuple[List[dict], Block, PhaseType]:
        """Propose a new block as leader."""
        high_qc = self._select_high_qc()

        genesis = self._block_store.get(list(self._block_store.keys())[0])
        if high_qc is not None:
            parent_hash = high_qc.block_hash
            parent_block = self._block_store.get(parent_hash, genesis)
        else:
            parent_block = genesis

        self._command_counter += 1
        command = Command(f"cmd_{current_view}_{self._command_counter}")

        new_block = BlockFactory.create_block(
            parent=parent_block,
            command=command,
            proposer_id=self._replica_id,
            view_number=current_view,
        )

        self._block_store[new_block.block_hash] = new_block
        self._safety_rules.register_block(new_block)

        prepare_msg = MessageFactory.create_prepare_message(
            sender_id=self._replica_id,
            view_number=current_view,
            block=new_block,
            high_qc=high_qc,
            timestamp=current_time,
        )

        self._network.broadcast(prepare_msg, self._replica_id, current_time)

        self._logger.info(
            f"Leader proposed block {new_block.block_hash[:8]} "
            f"at height {new_block.height} in view {current_view}"
        )

        my_vote = PrepareVote.create(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=new_block.block_hash,
            target_id=self._replica_id,
            timestamp=current_time,
        )
        self._vote_collector.add_vote(my_vote)

        events = [
            {
                "type": "PROPOSAL",
                "replica_id": self._replica_id,
                "block_hash": new_block.block_hash,
                "view": current_view,
                "timestamp": current_time,
            }
        ]

        return events, new_block, PhaseType.PREPARE

    def _select_high_qc(self) -> Optional[QuorumCertificate]:
        """Select the highest QC from new-view messages."""
        high_qc = None
        highest_view = ViewNumber(-1)

        for msg in self._new_view_messages:
            if msg.justify_qc is not None:
                if msg.justify_qc.view_number > highest_view:
                    highest_view = msg.justify_qc.view_number
                    high_qc = msg.justify_qc

        return high_qc

    def handle_prepare(
        self,
        message: PrepareMessage,
        current_view: ViewNumber,
        locked_qc: Optional[QuorumCertificate],
        last_voted_view: Optional[ViewNumber],
        current_time: int,
    ) -> tuple[List[dict], Block, Optional[ViewNumber], PhaseType]:
        """
        Handle a PREPARE message from the leader.

        Args:
            message: The prepare message.
            current_view: Current view number.
            locked_qc: Current locked QC.
            last_voted_view: Last view this replica voted in.
            current_time: Current simulation time.

        Returns:
            Tuple of (events, pending_block, new_last_voted_view, new_phase).
        """
        block = message.block

        self._block_store[block.block_hash] = block
        self._safety_rules.register_block(block)

        if not self._safety_rules.is_safe_node(block, message.high_qc, locked_qc):
            self._logger.debug(f"Block {block.block_hash[:8]} is not safe, not voting")
            return [], block, last_voted_view, PhaseType.PREPARE

        if last_voted_view is not None and current_view <= last_voted_view:
            self._logger.debug(f"Already voted in view {last_voted_view}")
            return [], block, last_voted_view, PhaseType.PREPARE

        leader_id = self._leader_scheduler.get_leader(current_view)

        vote = MessageFactory.create_prepare_vote(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=block.block_hash,
            target_id=leader_id,
            timestamp=current_time,
        )

        self._network.send(vote, leader_id, current_time)

        self._logger.debug(f"Voted PREPARE for block {block.block_hash[:8]}")

        events = [
            {
                "type": "VOTE_SEND",
                "replica_id": self._replica_id,
                "vote_type": "PREPARE",
                "block_hash": block.block_hash,
                "timestamp": current_time,
            }
        ]

        return events, block, current_view, PhaseType.PREPARE

    def handle_prepare_vote(
        self,
        vote: PrepareVote,
        current_view: ViewNumber,
        is_leader: bool,
        current_time: int,
    ) -> tuple[List[dict], Optional[QuorumCertificate], Optional[PhaseType]]:
        """
        Handle a PREPARE_VOTE (leader only).

        Returns:
            Tuple of (events, new_prepare_qc, new_phase).
        """
        if not is_leader:
            return [], None, None

        qc = self._vote_collector.add_vote(vote)

        if qc is not None:
            precommit_msg = MessageFactory.create_precommit_message(
                sender_id=self._replica_id,
                view_number=current_view,
                prepare_qc=qc,
                timestamp=current_time,
            )

            self._network.broadcast(precommit_msg, self._replica_id, current_time)

            self._logger.info(f"Formed prepareQC, broadcasting PRE_COMMIT")

            my_vote = PreCommitVote.create(
                sender_id=self._replica_id,
                view_number=current_view,
                block_hash=qc.block_hash,
                target_id=self._replica_id,
                timestamp=current_time,
            )
            self._vote_collector.add_vote(my_vote)

            events = [
                {
                    "type": "QC_FORMATION",
                    "replica_id": self._replica_id,
                    "qc_type": "PREPARE",
                    "view": current_view,
                    "timestamp": current_time,
                }
            ]

            return events, qc, PhaseType.PRE_COMMIT

        return [], None, None

    def handle_precommit(
        self, message: PreCommitMessage, current_view: ViewNumber, current_time: int
    ) -> tuple[List[dict], QuorumCertificate, PhaseType]:
        """
        Handle a PRE_COMMIT message.

        Returns:
            Tuple of (events, prepare_qc, new_phase).
        """
        leader_id = self._leader_scheduler.get_leader(current_view)

        vote = MessageFactory.create_precommit_vote(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=message.prepare_qc.block_hash,
            target_id=leader_id,
            timestamp=current_time,
        )

        self._network.send(vote, leader_id, current_time)

        self._logger.debug(
            f"Voted PRE_COMMIT for block {message.prepare_qc.block_hash[:8]}"
        )

        events = [
            {
                "type": "VOTE_SEND",
                "replica_id": self._replica_id,
                "vote_type": "PRE_COMMIT",
                "block_hash": message.prepare_qc.block_hash,
                "timestamp": current_time,
            }
        ]

        return events, message.prepare_qc, PhaseType.PRE_COMMIT

    def handle_precommit_vote(
        self,
        vote: PreCommitVote,
        current_view: ViewNumber,
        is_leader: bool,
        current_time: int,
    ) -> tuple[List[dict], Optional[QuorumCertificate], Optional[PhaseType]]:
        """
        Handle a PRE_COMMIT_VOTE (leader only).

        Returns:
            Tuple of (events, new_locked_qc, new_phase).
        """
        if not is_leader:
            return [], None, None

        qc = self._vote_collector.add_vote(vote)

        if qc is not None:
            commit_msg = MessageFactory.create_commit_message(
                sender_id=self._replica_id,
                view_number=current_view,
                precommit_qc=qc,
                timestamp=current_time,
            )

            self._network.broadcast(commit_msg, self._replica_id, current_time)

            self._logger.info(
                f"Formed precommitQC, updated lockedQC, broadcasting COMMIT"
            )

            my_vote = CommitVote.create(
                sender_id=self._replica_id,
                view_number=current_view,
                block_hash=qc.block_hash,
                target_id=self._replica_id,
                timestamp=current_time,
            )
            self._vote_collector.add_vote(my_vote)

            events = [
                {
                    "type": "QC_FORMATION",
                    "replica_id": self._replica_id,
                    "qc_type": "PRE_COMMIT",
                    "view": current_view,
                    "timestamp": current_time,
                },
                {
                    "type": "LOCK_UPDATE",
                    "replica_id": self._replica_id,
                    "locked_view": qc.view_number,
                    "timestamp": current_time,
                },
            ]

            return events, qc, PhaseType.COMMIT

        return [], None, None

    def handle_commit(
        self, message: CommitMessage, current_view: ViewNumber, current_time: int
    ) -> tuple[List[dict], QuorumCertificate, PhaseType]:
        """
        Handle a COMMIT message.

        Returns:
            Tuple of (events, locked_qc, new_phase).
        """
        leader_id = self._leader_scheduler.get_leader(current_view)

        vote = MessageFactory.create_commit_vote(
            sender_id=self._replica_id,
            view_number=current_view,
            block_hash=message.precommit_qc.block_hash,
            target_id=leader_id,
            timestamp=current_time,
        )

        self._network.send(vote, leader_id, current_time)

        self._logger.debug(f"Updated lockedQC, voted COMMIT")

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

        return events, message.precommit_qc, PhaseType.COMMIT

    def handle_commit_vote(
        self,
        vote: CommitVote,
        current_view: ViewNumber,
        is_leader: bool,
        committed_block_hashes: set,
        current_time: int,
    ) -> tuple[List[dict], List[Block], Optional[PhaseType]]:
        """
        Handle a COMMIT_VOTE (leader only).

        Returns:
            Tuple of (events, committed_blocks, new_phase).
        """
        if not is_leader:
            return [], [], None

        qc = self._vote_collector.add_vote(vote)

        if qc is not None:
            decide_msg = MessageFactory.create_decide_message(
                sender_id=self._replica_id,
                view_number=current_view,
                commit_qc=qc,
                timestamp=current_time,
            )

            self._network.broadcast(decide_msg, self._replica_id, current_time)

            self._logger.info(f"Formed commitQC, broadcasting DECIDE")

            block = self._block_store.get(qc.block_hash)
            if block:
                events, committed_blocks = self._execute_branch(
                    block, committed_block_hashes, current_time
                )

                events.insert(
                    0,
                    {
                        "type": "QC_FORMATION",
                        "replica_id": self._replica_id,
                        "qc_type": "COMMIT",
                        "view": current_view,
                        "timestamp": current_time,
                    },
                )

                if committed_blocks:
                    return events, committed_blocks, PhaseType.DECIDE

        return [], [], None

    def handle_decide(
        self, message: DecideMessage, committed_block_hashes: set, current_time: int
    ) -> tuple[List[dict], List[Block], Optional[PhaseType]]:
        """
        Handle a DECIDE message.

        Returns:
            Tuple of (events, committed_blocks, new_phase).
        """
        block = self._block_store.get(message.commit_qc.block_hash)

        if block:
            events, committed_blocks = self._execute_branch(
                block, committed_block_hashes, current_time
            )

            if committed_blocks:
                return events, committed_blocks, PhaseType.DECIDE

        return [], [], None

    def _execute_branch(
        self, block: Block, committed_block_hashes: set, current_time: int
    ) -> tuple[List[dict], List[Block]]:
        """
        Execute a block and its uncommitted ancestors.

        Args:
            block: The tip block to execute.
            committed_block_hashes: Set of already committed block hashes.
            current_time: Current simulation time.

        Returns:
            Tuple of (events, list_of_executed_blocks).
        """
        to_commit = []
        current_block = block

        while (
            current_block is not None
            and current_block.block_hash not in committed_block_hashes
        ):

            if current_block.height == 0:
                break

            to_commit.append(current_block)
            current_block = self._block_store.get(current_block.parent_hash)

        to_commit.reverse()

        events = []
        for b in to_commit:
            self._logger.info(f"Executed block {b.block_hash[:8]} at height {b.height}")
            events.append(
                {
                    "type": "COMMIT",
                    "replica_id": self._replica_id,
                    "block_hash": b.block_hash,
                    "height": b.height,
                    "timestamp": current_time,
                }
            )

        return events, to_commit

    def clear_new_view_messages(self) -> None:
        """Clear collected new-view messages for a new view."""
        self._new_view_messages.clear()

    def add_new_view_message(self, message: NewViewMessage) -> None:
        """Add own new-view message when leader."""
        self._new_view_messages.append(message)

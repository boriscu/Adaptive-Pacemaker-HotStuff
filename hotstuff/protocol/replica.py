"""
Replica class.

Main protocol actor representing a single node in the HotStuff network.
Delegates protocol logic to the appropriate handler (Basic or Chained).
"""

from typing import List
from typing import Optional
from typing import Dict
import random

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.phase_type import PhaseType
from hotstuff.domain.enumerations.fault_type import FaultType
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.replica_state import ReplicaState
from hotstuff.domain.models.messages.base_message import BaseMessage
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
from hotstuff.protocol.basic.handler import BasicHotStuffHandler
from hotstuff.factories.block_factory import BlockFactory
from hotstuff.factories.message_factory import MessageFactory
from hotstuff.network.simulated_network import SimulatedNetwork
from hotstuff.logging_config.logger import StructuredLogger


class Replica:
    """
    A replica in the HotStuff consensus network.
    
    Manages replica state and delegates protocol logic to the appropriate
    handler (BasicHotStuffHandler for Basic HotStuff, or ChainedHotStuffHandler
    for Chained HotStuff in the future).
    """
    
    def __init__(
        self,
        replica_id: ReplicaId,
        num_replicas: int,
        quorum_size: int,
        network: SimulatedNetwork,
        leader_scheduler: LeaderScheduler
    ):
        """
        Initialize a replica.
        
        Args:
            replica_id: Unique identifier for this replica.
            num_replicas: Total number of replicas.
            quorum_size: Required votes for QC (2f+1).
            network: Network interface for communication.
            leader_scheduler: Leader election scheduler.
        """
        self._replica_id = replica_id
        self._num_replicas = num_replicas
        self._quorum_size = quorum_size
        self._network = network
        self._leader_scheduler = leader_scheduler
        
        self._current_view: ViewNumber = ViewNumber(1)
        self._current_phase: PhaseType = PhaseType.NEW_VIEW
        self._locked_qc: Optional[QuorumCertificate] = None
        self._prepare_qc: Optional[QuorumCertificate] = None
        self._pending_block: Optional[Block] = None
        self._committed_blocks: List[Block] = []
        self._committed_block_hashes: set = set()
        self._last_voted_view: Optional[ViewNumber] = None
        
        self._is_faulty: bool = False
        self._fault_type: FaultType = FaultType.NONE
        
        self._genesis_block = BlockFactory.create_genesis_block(ReplicaId(0))
        self._block_store: Dict[BlockHash, Block] = {
            self._genesis_block.block_hash: self._genesis_block
        }
        
        self._safety_rules = SafetyRules()
        self._safety_rules.register_block(self._genesis_block)
        
        self._vote_collector = VoteCollector(quorum_size)
        
        self._logger = StructuredLogger.get_logger(f"replica.{replica_id}")
        
        self._protocol_handler = BasicHotStuffHandler(
            replica_id=replica_id,
            quorum_size=quorum_size,
            network=network,
            leader_scheduler=leader_scheduler,
            safety_rules=self._safety_rules,
            vote_collector=self._vote_collector,
            block_store=self._block_store,
            logger=self._logger
        )
    
    @property
    def replica_id(self) -> ReplicaId:
        """Get the replica ID."""
        return self._replica_id
    
    @property
    def current_view(self) -> ViewNumber:
        """Get the current view number."""
        return self._current_view
    
    @property
    def current_phase(self) -> PhaseType:
        """Get the current phase."""
        return self._current_phase
    
    @property
    def locked_qc(self) -> Optional[QuorumCertificate]:
        """Get the locked QC."""
        return self._locked_qc
    
    @property
    def prepare_qc(self) -> Optional[QuorumCertificate]:
        """Get the prepare QC (highQC)."""
        return self._prepare_qc
    
    def is_leader(self) -> bool:
        """Check if this replica is the leader for current view."""
        return self._leader_scheduler.is_leader(self._replica_id, self._current_view)
    
    def get_state(self) -> ReplicaState:
        """Get a snapshot of the replica's state."""
        return ReplicaState(
            replica_id=self._replica_id,
            current_view=self._current_view,
            current_phase=self._current_phase,
            is_leader=self.is_leader(),
            is_faulty=self._is_faulty,
            fault_type=self._fault_type,
            locked_qc=self._locked_qc,
            prepare_qc=self._prepare_qc,
            pending_block=self._pending_block,
            committed_block_hashes=[b.block_hash for b in self._committed_blocks],
            last_voted_view=self._last_voted_view
        )
    
    def inject_fault(self, fault_type: FaultType) -> None:
        """Inject a fault into this replica."""
        self._is_faulty = True
        self._fault_type = fault_type
        self._logger.warning(f"Fault injected: {fault_type.name}")
    
    def clear_fault(self) -> None:
        """Clear any injected fault."""
        self._is_faulty = False
        self._fault_type = FaultType.NONE
    
    def start_view(self, view_number: ViewNumber, current_time: int) -> List[dict]:
        """
        Start a new view.
        
        Sends new-view message to the leader of the new view.
        Supports Faulty behavior.
        - Silent: update internal state but don't send new-view message
        - Random Drop: 50% chance to skip sending new-view message
        - Crash: crash the replica (drop all messages)
        
        Args:
            view_number: The new view number to start.
            current_time: Current simulation time.
            
        Returns:
            List of events generated.
        """
        if self._is_faulty and self._fault_type == FaultType.CRASH:
            return []
        
        if self._is_faulty and self._fault_type == FaultType.SILENT:
            self._current_view = view_number
            self._current_phase = PhaseType.NEW_VIEW
            self._protocol_handler.clear_new_view_messages()
            self._logger.warning(f"SILENT fault: not sending new-view for view {view_number}")
            return [{
                "type": "BYZANTINE_ACTION",
                "replica_id": self._replica_id,
                "action": "SILENT_NO_NEW_VIEW",
                "view": view_number,
                "timestamp": current_time
            }]
        
        if self._is_faulty and self._fault_type == FaultType.RANDOM_DROP:
            if random.random() < 0.5:
                self._current_view = view_number
                self._current_phase = PhaseType.NEW_VIEW
                self._protocol_handler.clear_new_view_messages()
                self._logger.warning(f"RANDOM_DROP: dropped new-view for view {view_number}")
                return [{
                    "type": "BYZANTINE_ACTION",
                    "replica_id": self._replica_id,
                    "action": "DROPPED_NEW_VIEW",
                    "view": view_number,
                    "timestamp": current_time
                }]
        
        self._current_view = view_number
        self._current_phase = PhaseType.NEW_VIEW
        self._protocol_handler.clear_new_view_messages()
        
        next_leader = self._leader_scheduler.get_leader(view_number)
        
        new_view_msg = MessageFactory.create_new_view_message(
            sender_id=self._replica_id,
            view_number=view_number,
            justify_qc=self._prepare_qc,
            target_id=next_leader,
            timestamp=current_time
        )
        
        self._network.send(new_view_msg, next_leader, current_time)
        
        self._logger.info(f"Started view {view_number}, sent new-view to leader {next_leader}")
        
        events = [{
            "type": "VIEW_CHANGE",
            "replica_id": self._replica_id,
            "new_view": view_number,
            "timestamp": current_time
        }]
        
        if self._replica_id == next_leader:
            self._protocol_handler.add_new_view_message(new_view_msg)
        
        return events
    
    def handle_message(self, message: BaseMessage, current_time: int) -> List[dict]:
        """
        Handle an incoming message.
        
        Routes to appropriate handler based on message type.
        
        Args:
            message: The message to handle.
            current_time: Current simulation time.
            
        Returns:
            List of events generated.
        """
        if self._is_faulty and self._fault_type == FaultType.CRASH:
            return []
        
        # SILENT fault: update internal state from messages but don't vote
        if self._is_faulty and self._fault_type == FaultType.SILENT:
            if message.view_number < self._current_view:
                return []
            # Just log and return - no voting
            self._logger.warning(f"SILENT fault: received {message.message_type.name} but not responding")
            return [{
                "type": "BYZANTINE_ACTION",
                "replica_id": self._replica_id,
                "action": f"SILENT_NO_VOTE_{message.message_type.name}",
                "view": message.view_number,
                "timestamp": current_time
            }]
        
        # RANDOM_DROP fault: 50% chance to ignore message
        if self._is_faulty and self._fault_type == FaultType.RANDOM_DROP:
            if random.random() < 0.5:
                self._logger.warning(f"RANDOM_DROP: dropped {message.message_type.name}")
                return [{
                    "type": "BYZANTINE_ACTION",
                    "replica_id": self._replica_id,
                    "action": f"DROPPED_{message.message_type.name}",
                    "view": message.view_number,
                    "timestamp": current_time
                }]
        
        if message.view_number < self._current_view:
            self._logger.debug(f"Ignoring old message from view {message.view_number}")
            return []
        
        handlers = {
            MessageType.NEW_VIEW: self._handle_new_view,
            MessageType.PREPARE: self._handle_prepare,
            MessageType.PREPARE_VOTE: self._handle_prepare_vote,
            MessageType.PRE_COMMIT: self._handle_precommit,
            MessageType.PRE_COMMIT_VOTE: self._handle_precommit_vote,
            MessageType.COMMIT: self._handle_commit,
            MessageType.COMMIT_VOTE: self._handle_commit_vote,
            MessageType.DECIDE: self._handle_decide,
        }
        
        handler = handlers.get(message.message_type)
        if handler:
            return handler(message, current_time)
        
        self._logger.warning(f"Unknown message type: {message.message_type}")
        return []
    
    def _handle_new_view(self, message: NewViewMessage, current_time: int) -> List[dict]:
        """Handle a new-view message (leader only)."""
        events, pending_block, new_phase = self._protocol_handler.handle_new_view(
            message=message,
            current_view=self._current_view,
            is_leader=self.is_leader(),
            current_time=current_time
        )
        
        if pending_block is not None:
            self._pending_block = pending_block
            self._last_voted_view = self._current_view
        if new_phase is not None:
            self._current_phase = new_phase
        
        return events
    
    def _handle_prepare(self, message: PrepareMessage, current_time: int) -> List[dict]:
        """Handle a prepare message from the leader."""
        events, pending_block, new_last_voted, new_phase = self._protocol_handler.handle_prepare(
            message=message,
            current_view=self._current_view,
            locked_qc=self._locked_qc,
            last_voted_view=self._last_voted_view,
            current_time=current_time
        )
        
        self._pending_block = pending_block
        if new_last_voted is not None:
            self._last_voted_view = new_last_voted
        self._current_phase = new_phase
        
        return events
    
    def _handle_prepare_vote(self, vote: PrepareVote, current_time: int) -> List[dict]:
        """Handle a prepare vote (leader only)."""
        events, new_prepare_qc, new_phase = self._protocol_handler.handle_prepare_vote(
            vote=vote,
            current_view=self._current_view,
            is_leader=self.is_leader(),
            current_time=current_time
        )
        
        if new_prepare_qc is not None:
            self._prepare_qc = new_prepare_qc
        if new_phase is not None:
            self._current_phase = new_phase
        
        return events
    
    def _handle_precommit(self, message: PreCommitMessage, current_time: int) -> List[dict]:
        """Handle a pre-commit message."""
        events, prepare_qc, new_phase = self._protocol_handler.handle_precommit(
            message=message,
            current_view=self._current_view,
            current_time=current_time
        )
        
        self._prepare_qc = prepare_qc
        self._current_phase = new_phase
        
        return events
    
    def _handle_precommit_vote(self, vote: PreCommitVote, current_time: int) -> List[dict]:
        """Handle a pre-commit vote (leader only)."""
        events, new_locked_qc, new_phase = self._protocol_handler.handle_precommit_vote(
            vote=vote,
            current_view=self._current_view,
            is_leader=self.is_leader(),
            current_time=current_time
        )
        
        if new_locked_qc is not None:
            self._locked_qc = new_locked_qc
        if new_phase is not None:
            self._current_phase = new_phase
        
        return events
    
    def _handle_commit(self, message: CommitMessage, current_time: int) -> List[dict]:
        """Handle a commit message."""
        events, locked_qc, new_phase = self._protocol_handler.handle_commit(
            message=message,
            current_view=self._current_view,
            current_time=current_time
        )
        
        self._locked_qc = locked_qc
        self._current_phase = new_phase
        
        return events
    
    def _handle_commit_vote(self, vote: CommitVote, current_time: int) -> List[dict]:
        """Handle a commit vote (leader only)."""
        events, committed_block, new_phase = self._protocol_handler.handle_commit_vote(
            vote=vote,
            current_view=self._current_view,
            is_leader=self.is_leader(),
            committed_block_hashes=self._committed_block_hashes,
            current_time=current_time
        )
        
        if committed_block is not None:
            self._committed_blocks.append(committed_block)
            self._committed_block_hashes.add(committed_block.block_hash)
        if new_phase is not None:
            self._current_phase = new_phase
        
        return events
    
    def _handle_decide(self, message: DecideMessage, current_time: int) -> List[dict]:
        """Handle a decide message."""
        events, committed_block, new_phase = self._protocol_handler.handle_decide(
            message=message,
            committed_block_hashes=self._committed_block_hashes,
            current_time=current_time
        )
        
        if committed_block is not None:
            self._committed_blocks.append(committed_block)
            self._committed_block_hashes.add(committed_block.block_hash)
        if new_phase is not None:
            self._current_phase = new_phase
        
        return events
    
    def get_committed_count(self) -> int:
        """Get the number of committed blocks."""
        return len(self._committed_blocks)
    
    def get_block(self, block_hash: BlockHash) -> Optional[Block]:
        """Get a block by hash."""
        return self._block_store.get(block_hash)

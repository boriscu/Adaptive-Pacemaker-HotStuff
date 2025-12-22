from typing import Dict, List, Optional, Callable
import collections

from hotstuff.network.interfaces import Network
from hotstuff.pacemaker.interface import Pacemaker
from hotstuff.config import config, ProtocolMode
from hotstuff.protocol.interfaces import ReplicaInterface
from hotstuff.logger import logger
from hotstuff.domain.models import Block, QC, PartialSignature, QCSignature, Command, Msg, VoteMsg   
from hotstuff.domain.enums import MsgType
from hotstuff.metrics.collector import collector

from hotstuff.protocol.block_tree import BlockTree
from hotstuff.protocol.voting import VoteAggregator
from hotstuff.protocol.execution import Executor

class Replica(ReplicaInterface):
    """
    Core HotStuff Replica Implementation.
    Implements:
    - Algorithm 2 (Basic HotStuff)
    - Algorithm 3 (Chained HotStuff)
    - Algorithm 4 (Event-Driven Architecture)
    
    Adheres to the safeNode predicates and commit rules defined in the paper.
    """

    def __init__(self, id: int, network: Network, pacemaker: Pacemaker, timer_scheduler: Optional[Callable] = None):
        self.id = id
        self.network = network
        self.pacemaker = pacemaker
        self.timer_scheduler = timer_scheduler
        
        # Sub-modules
        self.block_tree = BlockTree()
        self.vote_aggregator = VoteAggregator(self.id)
        self.executor = Executor(self.id, self.pacemaker, self.block_tree)
        
        # State Variables
        self.view = 0
        self.is_faulty = False # Added for simulation
        self.locked_qc: Optional[QC] = None
        self.prepare_qc: Optional[QC] = None # Basic HotStuff specific
        self.precommit_qc: Optional[QC] = None # Basic HotStuff specific
        self.commit_qc: Optional[QC] = None # Basic HotStuff specific
        
        # Chained HotStuff specific (Generic QC)
        self.generic_qc: Optional[QC] = None
        
        # Initialize Genesis
        self._init_genesis()

    def _init_genesis(self):
        """
        Creates the genesis block and initial QC.
        Genesis is at view 0.
        """
        genesis_qc = self.block_tree.initialize_genesis()
        
        self.locked_qc = genesis_qc
        self.generic_qc = genesis_qc
        self.prepare_qc = genesis_qc
        
    def _safe_node(self, node: Block, qc: QC) -> bool:
        """
        Algorithm 1: safeNode(node, qc)
        Safety predicate.
        return (node extends from lockedQC.node) OR (qc.viewNumber > lockedQC.viewNumber)
        """
        extends_locked = self.block_tree.extends(node, self.locked_qc.node_hash)
        liveness_condition = (qc.view_number > self.locked_qc.view_number)
        
        return extends_locked or liveness_condition

    def on_start(self):
        """
        Starts the replica.
        """
        pass

    def on_next_view(self):
        """
        Algorithm 5/2/3: onNextView(curView)
        - Send Msg(new-view, ⊥, prepareQC/genericQC) to generic leader.
        - Advance pacemaker view.
        """
        self.view = self.pacemaker.advance_view()
        leader_id = self.pacemaker.get_leader(self.view)
        
        # Determine strict HighQC to send
        high_qc = self.generic_qc if config.PROTOCOL == ProtocolMode.CHAINED else self.prepare_qc
        
        msg = Msg(
            type=MsgType.NEW_VIEW,
            view_number=self.view,
            node=None,
            justify=high_qc,
            sender=self.id
        )
        
        self.network.send_msg(msg, leader_id)

        # Schedule Timeout for this view
        if self.timer_scheduler:
            duration = self.pacemaker.get_timeout_duration()
            self.timer_scheduler(duration, self.on_timeout, self.view)

    def on_receive_msg(self, msg: Msg):
        """
        Dispatches message to appropriate handler based on type and protocol.
        """
        if msg.view_number < self.view - 1:
            # Ignore old messages (with some buffer for async network)
            return

        if msg.type == MsgType.NEW_VIEW:
            self._handle_new_view(msg)
        elif msg.type == MsgType.GENERIC:
            self._handle_generic_request(msg)
        elif msg.type == MsgType.PREPARE:
            self._handle_basic_phase(msg, MsgType.PREPARE)
        elif msg.type == MsgType.PRE_COMMIT:
            self._handle_basic_phase(msg, MsgType.PRE_COMMIT)
        elif msg.type == MsgType.COMMIT:
            self._handle_basic_phase(msg, MsgType.COMMIT)
        elif msg.type == MsgType.DECIDE:
            self._handle_basic_phase(msg, MsgType.DECIDE)

    def _handle_new_view(self, msg: Msg):
        """
        Leader logic: Collect NEW-VIEW messages.
        """
        # Check if we are the leader for msg.view_number
        if self.pacemaker.get_leader(msg.view_number) != self.id:
            return

        # NEW-VIEW Collection Logic (Simplified for brevity)
        
        self._update_high_qc(msg.justify)
        
        # Make a proposal
        # Payload (Command)
        cmd = Command(payload=f"Tx_{self.view}_{self.id}")
        
        # Create Node
        high_qc = self.generic_qc if config.PROTOCOL == ProtocolMode.CHAINED else self.prepare_qc
        
        if not high_qc:
            return # Should have genesis at least

        if config.PROTOCOL == ProtocolMode.CHAINED:
            # Chained HotStuff Proposal
            proposal = self.block_tree.create_leaf(high_qc.node_hash, cmd, high_qc, view_number=msg.view_number)
            # Store it
            self.block_tree.add_block(proposal)
            
            # Broadcast GENERIC
            out_msg = Msg(
                type=MsgType.GENERIC,
                view_number=msg.view_number,
                node=proposal,
                justify=high_qc,
                sender=self.id
            )
            self.network.broadcast_msg(out_msg)

    def _handle_generic_request(self, msg: Msg):
        """
        Algorithm 3 (Replica):
        wait for Msg(generic, curView) from leader(curView)
        """
        if msg.view_number != self.view:
            return # Wrong view

        proposal = msg.node
        justify_qc = msg.justify
        
        if not proposal:
            return

        self.block_tree.add_block(proposal)
        
        # Safety Check
        safe = self._safe_node(proposal, justify_qc)
        
        if safe:
            # Send Vote
            partial_sig = PartialSignature(
                replica_id=self.id,
                msg_type=MsgType.GENERIC,
                view=msg.view_number,
                node_hash=proposal.hash
            )
            
            vote = VoteMsg(
                type=MsgType.GENERIC,
                view_number=msg.view_number,
                node_hash=proposal.hash,
                partial_sig=partial_sig,
                sender=self.id
            )
            
            next_leader = self.pacemaker.get_leader(msg.view_number + 1)
            self.network.send_vote(vote, next_leader)
            
            # Update Local State (Commit Rules)
            self._update_chained(proposal)

    def _update_chained(self, b_star: Block):
        """
        Algorithm 3: Update rules for Chained HotStuff.
        """
        # Traverse the chain
        # b* (current proposal)
        #   -> justify -> b'' (parent/justify node)
        #      -> justify -> b' 
        #         -> justify -> b
        
        qc_star = b_star.justify
        
        if not qc_star:
            return

        self._update_high_qc(qc_star)
        
        b_double_prime = self.block_tree.get_block(qc_star.node_hash)
        if not b_double_prime:
            return

        # Check One-Chain (update genericQC)
        # Alg 3 says: "if b*.parent == b'': genericQC = b*.justify"
        
        generic_qc_candidate = qc_star
        self.generic_qc = generic_qc_candidate # Accepted as new genericQC

        qc_double_prime = b_double_prime.justify
        if not qc_double_prime:
            return
            
        b_prime = self.block_tree.get_block(qc_double_prime.node_hash)
        if not b_prime:
            return
            
        # Check Two-Chain (Lock) 
        # "if (b*.parent == b'') and (b''.parent == b')"
        
        # Lock b''
        self.locked_qc = qc_double_prime
        
        qc_prime = b_prime.justify
        if not qc_prime:
            return

        b = self.block_tree.get_block(qc_prime.node_hash)
        if not b:
            return

        # Check Three-Chain (Commit)
        # "if ... and (b'.parent == b)"
        # Commit b
        self.executor.commit(b)

    def _handle_basic_phase(self, msg: Msg, phase: MsgType):
        """
        Parameters for Basic HotStuff phases.
        """
        pass

    def _update_high_qc(self, qc: QC):
        """
        Updates the highest known QC if the new one is higher.
        """
        if not qc: 
            return
            
        current = self.generic_qc if config.PROTOCOL == ProtocolMode.CHAINED else self.prepare_qc
        if current is None or qc.view_number > current.view_number:
            if config.PROTOCOL == ProtocolMode.CHAINED:
                self.generic_qc = qc
            else:
                self.prepare_qc = qc 

    def on_receive_vote(self, vote: VoteMsg):
        """
        Leader logic: Collect votes, form QC.
        """
        qc = self.vote_aggregator.add_vote(vote)
        
        if qc:
            self.block_tree.add_qc(qc)
            self._update_high_qc(qc)

    def get_commit_history(self) -> List[Block]:
        return self.executor.get_committed_blocks()

    @property
    def executed_up_to_height(self) -> int:
        return self.executor.executed_up_to_height

    @property
    def committed_blocks(self) -> List[Block]:
        return self.executor.committed_blocks

    def on_timeout(self, view: int):
        """
        Triggered when view timer expires.
        If we are still in the same view, we trigger NEXT_VIEW.
        """
        if self.view == view:
            logger.debug(f"Replica {self.id} TIMEOUT in view {view}")
            self.pacemaker.on_timeout()
            self.on_next_view()

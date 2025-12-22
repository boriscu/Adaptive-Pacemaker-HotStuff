"""
MessageFactory for creating protocol messages.

Implements Msg(type, node, qc) and voteMsg(type, node, qc) from Algorithm 1.
"""

from typing import Optional
from typing import Union

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.block import Block
from hotstuff.domain.models.quorum_certificate import QuorumCertificate
from hotstuff.domain.models.messages.base_message import BaseMessage
from hotstuff.domain.models.messages.new_view_message import NewViewMessage
from hotstuff.domain.models.messages.prepare_message import PrepareMessage
from hotstuff.domain.models.messages.precommit_message import PreCommitMessage
from hotstuff.domain.models.messages.commit_message import CommitMessage
from hotstuff.domain.models.messages.decide_message import DecideMessage
from hotstuff.domain.models.messages.prepare_vote import PrepareVote
from hotstuff.domain.models.messages.precommit_vote import PreCommitVote
from hotstuff.domain.models.messages.commit_vote import CommitVote


class MessageFactory:
    """
    Factory for creating protocol messages.
    
    Implements:
    - Msg(type, node, qc): Creates a message with given type, block, and QC
    - voteMsg(type, node, qc): Creates a vote message with partial signature
    """
    
    @classmethod
    def create_new_view_message(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        justify_qc: Optional[QuorumCertificate],
        target_id: ReplicaId,
        timestamp: int = 0
    ) -> NewViewMessage:
        """Create a NEW_VIEW message."""
        return NewViewMessage.create(
            sender_id=sender_id,
            view_number=view_number,
            justify_qc=justify_qc,
            target_id=target_id,
            timestamp=timestamp
        )
    
    @classmethod
    def create_prepare_message(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        block: Block,
        high_qc: Optional[QuorumCertificate],
        timestamp: int = 0
    ) -> PrepareMessage:
        """Create a PREPARE message (leader proposal)."""
        return PrepareMessage.create(
            sender_id=sender_id,
            view_number=view_number,
            block=block,
            high_qc=high_qc,
            timestamp=timestamp
        )
    
    @classmethod
    def create_precommit_message(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        prepare_qc: QuorumCertificate,
        timestamp: int = 0
    ) -> PreCommitMessage:
        """Create a PRE_COMMIT message."""
        return PreCommitMessage.create(
            sender_id=sender_id,
            view_number=view_number,
            prepare_qc=prepare_qc,
            timestamp=timestamp
        )
    
    @classmethod
    def create_commit_message(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        precommit_qc: QuorumCertificate,
        timestamp: int = 0
    ) -> CommitMessage:
        """Create a COMMIT message."""
        return CommitMessage.create(
            sender_id=sender_id,
            view_number=view_number,
            precommit_qc=precommit_qc,
            timestamp=timestamp
        )
    
    @classmethod
    def create_decide_message(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        commit_qc: QuorumCertificate,
        timestamp: int = 0
    ) -> DecideMessage:
        """Create a DECIDE message."""
        return DecideMessage.create(
            sender_id=sender_id,
            view_number=view_number,
            commit_qc=commit_qc,
            timestamp=timestamp
        )
    
    @classmethod
    def create_prepare_vote(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        block_hash: BlockHash,
        target_id: ReplicaId,
        timestamp: int = 0
    ) -> PrepareVote:
        """Create a PREPARE vote message."""
        return PrepareVote.create(
            sender_id=sender_id,
            view_number=view_number,
            block_hash=block_hash,
            target_id=target_id,
            timestamp=timestamp
        )
    
    @classmethod
    def create_precommit_vote(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        block_hash: BlockHash,
        target_id: ReplicaId,
        timestamp: int = 0
    ) -> PreCommitVote:
        """Create a PRE_COMMIT vote message."""
        return PreCommitVote.create(
            sender_id=sender_id,
            view_number=view_number,
            block_hash=block_hash,
            target_id=target_id,
            timestamp=timestamp
        )
    
    @classmethod
    def create_commit_vote(
        cls,
        sender_id: ReplicaId,
        view_number: ViewNumber,
        block_hash: BlockHash,
        target_id: ReplicaId,
        timestamp: int = 0
    ) -> CommitVote:
        """Create a COMMIT vote message."""
        return CommitVote.create(
            sender_id=sender_id,
            view_number=view_number,
            block_hash=block_hash,
            target_id=target_id,
            timestamp=timestamp
        )

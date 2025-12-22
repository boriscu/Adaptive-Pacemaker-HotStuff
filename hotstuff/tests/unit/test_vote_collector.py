"""
Unit tests for VoteCollector.
"""

import pytest

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.domain.models.messages.prepare_vote import PrepareVote
from hotstuff.protocol.vote_collector import VoteCollector


class TestVoteCollector:
    """Tests for the VoteCollector class."""
    
    def test_collect_votes_until_quorum(self):
        """Test that QC is formed when quorum is reached."""
        collector = VoteCollector(quorum_size=3)
        block_hash = BlockHash("test_block_hash")
        view = ViewNumber(1)
        
        vote1 = PrepareVote.create(
            sender_id=ReplicaId(0),
            view_number=view,
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        result1 = collector.add_vote(vote1)
        assert result1 is None
        
        vote2 = PrepareVote.create(
            sender_id=ReplicaId(1),
            view_number=view,
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        result2 = collector.add_vote(vote2)
        assert result2 is None
        
        vote3 = PrepareVote.create(
            sender_id=ReplicaId(2),
            view_number=view,
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        result3 = collector.add_vote(vote3)
        
        assert result3 is not None
        assert result3.block_hash == block_hash
        assert result3.view_number == view
        assert result3.signer_count == 3
    
    def test_deduplicate_votes(self):
        """Test that duplicate votes from same sender are ignored."""
        collector = VoteCollector(quorum_size=3)
        block_hash = BlockHash("test_block_hash")
        view = ViewNumber(1)
        
        vote1 = PrepareVote.create(
            sender_id=ReplicaId(0),
            view_number=view,
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        collector.add_vote(vote1)
        
        vote1_dup = PrepareVote.create(
            sender_id=ReplicaId(0),
            view_number=view,
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        collector.add_vote(vote1_dup)
        
        assert collector.get_vote_count(view, block_hash, MessageType.PREPARE_VOTE) == 1
    
    def test_qc_only_formed_once(self):
        """Test that additional votes after QC don't create new QC."""
        collector = VoteCollector(quorum_size=3)
        block_hash = BlockHash("test_block_hash")
        view = ViewNumber(1)
        
        for i in range(3):
            vote = PrepareVote.create(
                sender_id=ReplicaId(i),
                view_number=view,
                block_hash=block_hash,
                target_id=ReplicaId(0)
            )
            collector.add_vote(vote)
        
        vote4 = PrepareVote.create(
            sender_id=ReplicaId(3),
            view_number=view,
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        result = collector.add_vote(vote4)
        
        assert result is None
    
    def test_separate_views(self):
        """Test that votes for different views are tracked separately."""
        collector = VoteCollector(quorum_size=3)
        block_hash = BlockHash("test_block_hash")
        
        for i in range(2):
            vote = PrepareVote.create(
                sender_id=ReplicaId(i),
                view_number=ViewNumber(1),
                block_hash=block_hash,
                target_id=ReplicaId(0)
            )
            collector.add_vote(vote)
        
        for i in range(2):
            vote = PrepareVote.create(
                sender_id=ReplicaId(i),
                view_number=ViewNumber(2),
                block_hash=block_hash,
                target_id=ReplicaId(0)
            )
            collector.add_vote(vote)
        
        assert collector.get_vote_count(ViewNumber(1), block_hash, MessageType.PREPARE_VOTE) == 2
        assert collector.get_vote_count(ViewNumber(2), block_hash, MessageType.PREPARE_VOTE) == 2
    
    def test_clear_view(self):
        """Test clearing votes for a specific view."""
        collector = VoteCollector(quorum_size=3)
        block_hash = BlockHash("test_block_hash")
        
        vote = PrepareVote.create(
            sender_id=ReplicaId(0),
            view_number=ViewNumber(1),
            block_hash=block_hash,
            target_id=ReplicaId(0)
        )
        collector.add_vote(vote)
        
        assert collector.get_vote_count(ViewNumber(1), block_hash, MessageType.PREPARE_VOTE) == 1
        
        collector.clear_view(ViewNumber(1))
        
        assert collector.get_vote_count(ViewNumber(1), block_hash, MessageType.PREPARE_VOTE) == 0

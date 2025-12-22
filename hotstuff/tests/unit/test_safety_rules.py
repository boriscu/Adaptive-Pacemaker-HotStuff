"""
Unit tests for SafetyRules.
"""

import pytest

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.command import Command
from hotstuff.domain.enumerations.message_type import MessageType
from hotstuff.protocol.safety_rules import SafetyRules
from hotstuff.factories.block_factory import BlockFactory
from hotstuff.factories.qc_factory import QuorumCertificateFactory


class TestSafetyRules:
    """Tests for the SafetyRules class."""
    
    def test_safe_node_no_locked_qc(self, genesis_block, sample_block):
        """Test that any block is safe when there's no locked QC."""
        safety = SafetyRules()
        safety.register_block(genesis_block)
        safety.register_block(sample_block)
        
        result = safety.is_safe_node(
            block=sample_block,
            justify_qc=None,
            locked_qc=None
        )
        
        assert result is True
    
    def test_safe_node_extends_locked(self, genesis_block):
        """Test that a block extending the locked block is safe."""
        safety = SafetyRules()
        safety.register_block(genesis_block)
        
        locked_block = BlockFactory.create_block(
            parent=genesis_block,
            command=Command("locked_cmd"),
            proposer_id=ReplicaId(0),
            view_number=ViewNumber(1)
        )
        safety.register_block(locked_block)
        
        locked_qc = QuorumCertificateFactory.create_empty_qc(
            qc_type=MessageType.PRE_COMMIT_VOTE,
            view_number=ViewNumber(1),
            block_hash=locked_block.block_hash
        )
        
        new_block = BlockFactory.create_block(
            parent=locked_block,
            command=Command("new_cmd"),
            proposer_id=ReplicaId(0),
            view_number=ViewNumber(2)
        )
        safety.register_block(new_block)
        
        result = safety.is_safe_node(
            block=new_block,
            justify_qc=None,
            locked_qc=locked_qc
        )
        
        assert result is True
    
    def test_safe_node_higher_view_qc(self, genesis_block):
        """Test that a block with higher view justify QC is safe."""
        safety = SafetyRules()
        safety.register_block(genesis_block)
        
        locked_block = BlockFactory.create_block(
            parent=genesis_block,
            command=Command("locked_cmd"),
            proposer_id=ReplicaId(0),
            view_number=ViewNumber(1)
        )
        safety.register_block(locked_block)
        
        locked_qc = QuorumCertificateFactory.create_empty_qc(
            qc_type=MessageType.PRE_COMMIT_VOTE,
            view_number=ViewNumber(1),
            block_hash=locked_block.block_hash
        )
        
        other_block = BlockFactory.create_block(
            parent=genesis_block,
            command=Command("other_cmd"),
            proposer_id=ReplicaId(1),
            view_number=ViewNumber(3)
        )
        safety.register_block(other_block)
        
        new_block = BlockFactory.create_block(
            parent=other_block,
            command=Command("new_cmd"),
            proposer_id=ReplicaId(0),
            view_number=ViewNumber(4)
        )
        safety.register_block(new_block)
        
        higher_view_qc = QuorumCertificateFactory.create_empty_qc(
            qc_type=MessageType.PREPARE_VOTE,
            view_number=ViewNumber(3),
            block_hash=other_block.block_hash
        )
        
        result = safety.is_safe_node(
            block=new_block,
            justify_qc=higher_view_qc,
            locked_qc=locked_qc
        )
        
        assert result is True
    
    def test_unsafe_node_doesnt_extend_and_lower_view(self, genesis_block):
        """Test that a block that doesn't extend and has lower view QC is unsafe."""
        safety = SafetyRules()
        safety.register_block(genesis_block)
        
        locked_block = BlockFactory.create_block(
            parent=genesis_block,
            command=Command("locked_cmd"),
            proposer_id=ReplicaId(0),
            view_number=ViewNumber(2)
        )
        safety.register_block(locked_block)
        
        locked_qc = QuorumCertificateFactory.create_empty_qc(
            qc_type=MessageType.PRE_COMMIT_VOTE,
            view_number=ViewNumber(2),
            block_hash=locked_block.block_hash
        )
        
        conflicting_block = BlockFactory.create_block(
            parent=genesis_block,
            command=Command("conflict_cmd"),
            proposer_id=ReplicaId(1),
            view_number=ViewNumber(3)
        )
        safety.register_block(conflicting_block)
        
        lower_view_qc = QuorumCertificateFactory.create_empty_qc(
            qc_type=MessageType.PREPARE_VOTE,
            view_number=ViewNumber(1),
            block_hash=genesis_block.block_hash
        )
        
        result = safety.is_safe_node(
            block=conflicting_block,
            justify_qc=lower_view_qc,
            locked_qc=locked_qc
        )
        
        assert result is False
    
    def test_validate_qc_valid(self):
        """Test QC validation with sufficient signatures."""
        safety = SafetyRules()
        
        from hotstuff.domain.models.partial_signature import PartialSignature
        
        signatures = [
            PartialSignature(
                replica_id=ReplicaId(i),
                message_type=MessageType.PREPARE_VOTE,
                view_number=ViewNumber(1),
                block_hash="test_hash"
            )
            for i in range(3)
        ]
        
        qc = QuorumCertificateFactory.create_qc_from_signatures(
            signatures=signatures,
            qc_type=MessageType.PREPARE_VOTE,
            view_number=ViewNumber(1),
            block_hash="test_hash"
        )
        
        assert safety.validate_qc(qc, quorum_size=3) is True
        assert safety.validate_qc(qc, quorum_size=4) is False

"""
BlockFactory for creating blocks.

Implements the createLeaf(parent, cmd) function from Algorithm 1.
"""

from typing import Optional

from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.types.command import Command
from hotstuff.domain.models.block import Block
from hotstuff.config.constants.defaults import GENESIS_VIEW_NUMBER


class BlockFactory:
    """
    Factory for creating Block instances.

    Implements the createLeaf(parent, cmd) function from Algorithm 1:
    - Sets parent to the given parent block
    - Sets cmd to the client command
    - Height is derived from parent height + 1
    """

    _block_counter: int = 0

    @classmethod
    def create_genesis_block(cls, proposer_id: ReplicaId = ReplicaId(0)) -> Block:
        """
        Create the genesis block (root of the blockchain).

        The genesis block has no parent and serves as the starting point
        for the blockchain.

        Args:
            proposer_id: ID of the proposer (default: replica 0).

        Returns:
            The genesis Block.
        """
        return Block(
            parent_hash=None,
            command=Command("genesis"),
            height=0,
            proposer_id=proposer_id,
            view_number=ViewNumber(GENESIS_VIEW_NUMBER),
        )

    @classmethod
    def create_block(
        cls,
        parent: Block,
        command: Command,
        proposer_id: ReplicaId,
        view_number: ViewNumber,
    ) -> Block:
        """
        Create a new block extending the parent block.

        This implements createLeaf(parent, cmd) from Algorithm 1.

        Args:
            parent: The parent block to extend.
            command: The client command to include.
            proposer_id: ID of the proposing replica.
            view_number: Current view number.

        Returns:
            New Block extending the parent.
        """
        cls._block_counter += 1
        return Block(
            parent_hash=parent.block_hash,
            command=command,
            height=parent.height + 1,
            proposer_id=proposer_id,
            view_number=view_number,
        )

    @classmethod
    def create_block_from_hash(
        cls,
        parent_hash: Optional[BlockHash],
        parent_height: int,
        command: Command,
        proposer_id: ReplicaId,
        view_number: ViewNumber,
    ) -> Block:
        """
        Create a new block from a parent hash instead of a Block object.

        Useful when the parent Block object is not available but the hash is known.

        Args:
            parent_hash: Hash of the parent block.
            parent_height: Height of the parent block.
            command: The client command to include.
            proposer_id: ID of the proposing replica.
            view_number: Current view number.

        Returns:
            New Block extending the parent.
        """
        cls._block_counter += 1
        return Block(
            parent_hash=parent_hash,
            command=command,
            height=parent_height + 1,
            proposer_id=proposer_id,
            view_number=view_number,
        )

    @classmethod
    def reset_counter(cls) -> None:
        """Reset the block counter (primarily for testing)."""
        cls._block_counter = 0

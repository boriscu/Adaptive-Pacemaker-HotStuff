"""
BlockHash type definition.

Represents a cryptographic hash of a block in the blockchain.
Used for block identification and parent-child relationships.
"""

from typing import NewType


BlockHash = NewType("BlockHash", str)

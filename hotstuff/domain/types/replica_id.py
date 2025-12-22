"""
ReplicaId type definition.

Represents a unique identifier for a replica in the HotStuff network.
Replica IDs are used for leader election and message routing.
"""

from typing import NewType


ReplicaId = NewType("ReplicaId", int)

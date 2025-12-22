"""
ViewNumber type definition.

Represents a monotonically increasing view number in the HotStuff protocol.
Each view corresponds to a single consensus round with a designated leader.
"""

from typing import NewType


ViewNumber = NewType("ViewNumber", int)

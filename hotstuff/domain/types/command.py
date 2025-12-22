"""
Command type definition.

Represents a client command or transaction to be included in a block.
In the simulation, this is a string placeholder for actual transaction data.
"""

from typing import NewType


Command = NewType("Command", str)

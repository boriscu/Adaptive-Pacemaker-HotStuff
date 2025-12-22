from enum import Enum

class MsgType(str, Enum):
    PREPARE = "PREPARE"
    PRE_COMMIT = "PRE_COMMIT"
    COMMIT = "COMMIT"
    DECIDE = "DECIDE"
    NEW_VIEW = "NEW_VIEW"
    GENERIC = "GENERIC" # For Chained HotStuff

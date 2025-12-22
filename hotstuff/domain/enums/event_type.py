from enum import Enum

class EventType(str, Enum):
    MSG = "MSG"
    VOTE = "VOTE"
    NEXT_VIEW = "NEXT_VIEW"

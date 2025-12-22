"""
System limits for HotStuff simulation.

Hard limits to prevent resource exhaustion.
"""

MAX_REPLICAS: int = 100
MIN_REPLICAS: int = 4
MAX_TIMEOUT_MS: int = 60000
MIN_TIMEOUT_MS: int = 100
MAX_NETWORK_DELAY_MS: int = 10000
MAX_VIEWS: int = 10000
MAX_EVENTS_PER_STEP: int = 1000
MAX_MESSAGE_QUEUE_SIZE: int = 10000
MAX_EVENT_HISTORY_SIZE: int = 100000

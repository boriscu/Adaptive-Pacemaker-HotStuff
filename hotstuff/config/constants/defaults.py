"""
Default values for HotStuff simulation configuration.

All default values are defined here as named constants.
"""

DEFAULT_NUM_REPLICAS: int = 4
DEFAULT_NUM_FAULTY: int = 1
DEFAULT_BASE_TIMEOUT_MS: int = 1000
DEFAULT_NETWORK_DELAY_MIN_MS: int = 10
DEFAULT_NETWORK_DELAY_MAX_MS: int = 100
DEFAULT_SIMULATION_SPEED: float = 1.0
DEFAULT_MAX_VIEWS: int = 100
DEFAULT_LOG_LEVEL: str = "INFO"

DEFAULT_ADAPTIVE_ALPHA: float = 0.5
DEFAULT_ADAPTIVE_MIN_TIMEOUT_MS: int = 500
DEFAULT_ADAPTIVE_MAX_TIMEOUT_MS: int = 5000

DEFAULT_UI_HOST: str = "127.0.0.1"
DEFAULT_UI_PORT: int = 5000
DEFAULT_UI_DEBUG: bool = True

GENESIS_BLOCK_HASH: str = "genesis_0000"
GENESIS_VIEW_NUMBER: int = 0

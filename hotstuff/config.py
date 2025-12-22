from enum import Enum
from typing import Optional
from pydantic_settings import BaseSettings

class ProtocolMode(str, Enum):
    BASIC = "BASIC"
    CHAINED = "CHAINED"

class PacemakerMode(str, Enum):
    BASELINE = "BASELINE"
    ADAPTIVE = "ADAPTIVE"

class Config(BaseSettings):
    """
    Global simulation configuration.
    Values can be overridden by environment variables (e.g. HOTSTUFF_N=10).
    """
    
    # System parameters
    N: int = 4  # Total number of replicas
    F: int = 1  # Max number of faulty replicas (N >= 3F + 1)
    
    # Timing (in seconds)
    DELTA: float = 1.0  # Base network delay or timeout step
    SEED: Optional[int] = 42 # Deterministic seed
    
    # Modes
    PROTOCOL: ProtocolMode = ProtocolMode.CHAINED
    PACEMAKER: PacemakerMode = PacemakerMode.BASELINE
    
    # Network
    NETWORK_LATENCY_MIN: float = 0.01
    NETWORK_LATENCY_MAX: float = 0.1
    DROP_PROBABILITY: float = 0.0

    class Config:
        env_prefix = "HOTSTUFF_"

# Global config instance
config = Config()

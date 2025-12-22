"""
Settings class for HotStuff simulation configuration.

Pydantic Settings with environment variable support.
"""

from typing import Optional

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings

from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.config.constants.defaults import DEFAULT_NUM_REPLICAS
from hotstuff.config.constants.defaults import DEFAULT_NUM_FAULTY
from hotstuff.config.constants.defaults import DEFAULT_BASE_TIMEOUT_MS
from hotstuff.config.constants.defaults import DEFAULT_NETWORK_DELAY_MIN_MS
from hotstuff.config.constants.defaults import DEFAULT_NETWORK_DELAY_MAX_MS
from hotstuff.config.constants.defaults import DEFAULT_SIMULATION_SPEED
from hotstuff.config.constants.defaults import DEFAULT_MAX_VIEWS
from hotstuff.config.constants.defaults import DEFAULT_LOG_LEVEL
from hotstuff.config.constants.defaults import DEFAULT_ADAPTIVE_ALPHA
from hotstuff.config.constants.defaults import DEFAULT_ADAPTIVE_MIN_TIMEOUT_MS
from hotstuff.config.constants.defaults import DEFAULT_ADAPTIVE_MAX_TIMEOUT_MS
from hotstuff.config.constants.defaults import DEFAULT_UI_HOST
from hotstuff.config.constants.defaults import DEFAULT_UI_PORT
from hotstuff.config.constants.defaults import DEFAULT_UI_DEBUG
from hotstuff.config.constants.limits import MAX_REPLICAS
from hotstuff.config.constants.limits import MIN_REPLICAS


class Settings(BaseSettings):
    """
    Configuration settings for HotStuff simulation.
    
    Supports loading from environment variables with HOTSTUFF_ prefix.
    All settings have sensible defaults for quick experimentation.
    """
    
    num_replicas: int = Field(
        default=DEFAULT_NUM_REPLICAS,
        ge=MIN_REPLICAS,
        le=MAX_REPLICAS,
        description="Total number of replicas (n). Must satisfy n = 3f + 1."
    )
    num_faulty: int = Field(
        default=DEFAULT_NUM_FAULTY,
        ge=0,
        description="Number of faulty replicas (f). Must satisfy n >= 3f + 1."
    )
    base_timeout_ms: int = Field(
        default=DEFAULT_BASE_TIMEOUT_MS,
        gt=0,
        description="Base timeout duration in milliseconds."
    )
    network_delay_min_ms: int = Field(
        default=DEFAULT_NETWORK_DELAY_MIN_MS,
        ge=0,
        description="Minimum network delay in milliseconds."
    )
    network_delay_max_ms: int = Field(
        default=DEFAULT_NETWORK_DELAY_MAX_MS,
        gt=0,
        description="Maximum network delay in milliseconds."
    )
    random_seed: Optional[int] = Field(
        default=None,
        description="Random seed for deterministic simulation. None for random."
    )
    pacemaker_type: PacemakerType = Field(
        default=PacemakerType.BASELINE,
        description="Type of pacemaker to use."
    )
    simulation_speed: float = Field(
        default=DEFAULT_SIMULATION_SPEED,
        gt=0.0,
        le=100.0,
        description="Simulation speed multiplier. 1.0 = real-time."
    )
    max_views: int = Field(
        default=DEFAULT_MAX_VIEWS,
        gt=0,
        description="Maximum number of views before stopping simulation."
    )
    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."
    )
    adaptive_alpha: float = Field(
        default=DEFAULT_ADAPTIVE_ALPHA,
        gt=0.0,
        lt=1.0,
        description="Smoothing factor for adaptive pacemaker EMA."
    )
    adaptive_min_timeout_ms: int = Field(
        default=DEFAULT_ADAPTIVE_MIN_TIMEOUT_MS,
        gt=0,
        description="Minimum timeout for adaptive pacemaker."
    )
    adaptive_max_timeout_ms: int = Field(
        default=DEFAULT_ADAPTIVE_MAX_TIMEOUT_MS,
        gt=0,
        description="Maximum timeout for adaptive pacemaker."
    )
    ui_host: str = Field(
        default=DEFAULT_UI_HOST,
        description="Host address for the UI server."
    )
    ui_port: int = Field(
        default=DEFAULT_UI_PORT,
        gt=0,
        lt=65536,
        description="Port for the UI server."
    )
    ui_debug: bool = Field(
        default=DEFAULT_UI_DEBUG,
        description="Enable Flask debug mode."
    )
    
    model_config = {
        "env_prefix": "HOTSTUFF_",
        "env_file": ".env",
        "extra": "ignore"
    }
    
    @field_validator("num_replicas")
    @classmethod
    def validate_num_replicas(cls, value: int) -> int:
        """Validate that num_replicas satisfies BFT requirements."""
        if (value - 1) % 3 != 0:
            raise ValueError(f"num_replicas must be 3f+1 for some integer f, got {value}")
        return value
    
    @property
    def quorum_size(self) -> int:
        """Calculate the quorum size (n - f = 2f + 1 for n = 3f + 1)."""
        return self.num_replicas - self.num_faulty
    
    @property
    def max_faulty(self) -> int:
        """Calculate the maximum tolerable faulty replicas."""
        return (self.num_replicas - 1) // 3
    
    def validate_fault_tolerance(self) -> bool:
        """Check if the configuration maintains BFT safety."""
        return self.num_faulty <= self.max_faulty

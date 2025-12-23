"""
Configuration schema for benchmark runs.

Pydantic models for loading and validating benchmark configurations.
"""

from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class SingleRunConfig(BaseModel):
    """Configuration for a single simulation run."""
    
    num_replicas: int = Field(default=4, ge=1, description="Number of replicas")
    num_faulty: int = Field(default=1, ge=0, description="Number of faulty replicas")
    pacemaker_type: str = Field(default="baseline", description="Pacemaker type")
    fault_type: str = Field(default="CRASH", description="Fault type for faulty replicas")
    base_timeout_ms: int = Field(default=1000, gt=0, description="Base timeout in ms")
    max_views: int = Field(default=50, gt=0, description="Maximum views to simulate")
    random_seed: Optional[int] = Field(default=None, description="Random seed")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for results."""
        return {
            "num_replicas": self.num_replicas,
            "num_faulty": self.num_faulty,
            "pacemaker_type": self.pacemaker_type,
            "fault_type": self.fault_type,
            "base_timeout_ms": self.base_timeout_ms,
            "max_views": self.max_views,
        }


class ConfigurationSet(BaseModel):
    """A set of parameter variations to generate configurations from."""
    
    num_replicas: List[int] = Field(default=[4], description="Replica counts to test")
    num_faulty: List[int] = Field(default=[1], description="Faulty counts to test")
    pacemaker_type: List[str] = Field(default=["baseline"], description="Pacemaker types")
    fault_type: List[str] = Field(default=["CRASH"], description="Fault types")
    base_timeout_ms: List[int] = Field(default=[1000], description="Timeout values")


class BenchmarkConfig(BaseModel):
    """Top-level benchmark configuration."""
    
    name: str = Field(default="Benchmark", description="Name of this benchmark")
    max_views: int = Field(default=50, gt=0, description="Views per simulation")
    runs_per_config: int = Field(default=5, ge=1, description="Runs per configuration")
    random_seed_base: Optional[int] = Field(
        default=42, 
        description="Base seed (each run uses seed_base + run_index)"
    )
    configurations: List[ConfigurationSet] = Field(
        default_factory=lambda: [ConfigurationSet()],
        description="Configuration sets to generate from"
    )
    
    def generate_run_configs(self) -> List[SingleRunConfig]:
        """Generate all SingleRunConfig combinations from configuration sets."""
        configs = []
        
        for config_set in self.configurations:
            for n in config_set.num_replicas:
                for f in config_set.num_faulty:
                    for pm in config_set.pacemaker_type:
                        for ft in config_set.fault_type:
                            for timeout in config_set.base_timeout_ms:
                                configs.append(SingleRunConfig(
                                    num_replicas=n,
                                    num_faulty=f,
                                    pacemaker_type=pm,
                                    fault_type=ft,
                                    base_timeout_ms=timeout,
                                    max_views=self.max_views,
                                ))
        
        return configs
    
    def total_runs(self) -> int:
        """Calculate total number of simulation runs."""
        return len(self.generate_run_configs()) * self.runs_per_config

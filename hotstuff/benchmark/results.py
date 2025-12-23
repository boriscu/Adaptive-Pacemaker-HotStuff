"""
Result models for benchmark runs.

Dataclasses for storing and aggregating simulation results.
"""

from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Dict
from statistics import mean
from statistics import stdev


@dataclass
class RunResult:
    """Result of a single simulation run."""
    
    config: Dict
    run_index: int
    success: bool
    blocks_committed: int
    total_views: int
    total_timeouts: int
    latency_avg_ms: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    throughput: float
    duration_ms: int
    
    def to_dict(self) -> dict:
        """Convert to flat dictionary for CSV export."""
        result = dict(self.config)
        result.update({
            "run_index": self.run_index,
            "success": self.success,
            "blocks_committed": self.blocks_committed,
            "total_views": self.total_views,
            "total_timeouts": self.total_timeouts,
            "latency_avg_ms": self.latency_avg_ms,
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p95_ms": self.latency_p95_ms,
            "latency_p99_ms": self.latency_p99_ms,
            "throughput": self.throughput,
            "duration_ms": self.duration_ms,
        })
        return result


@dataclass
class AggregatedResult:
    """Aggregated results across multiple runs of the same configuration."""
    
    config: Dict
    runs: int
    success_rate: float
    blocks_committed_mean: float
    blocks_committed_std: float
    timeouts_mean: float
    latency_avg_mean: float
    latency_avg_std: float
    latency_p95_mean: float
    throughput_mean: float
    throughput_std: float
    duration_mean_ms: float
    
    @classmethod
    def from_runs(cls, config: Dict, results: List[RunResult]) -> "AggregatedResult":
        """Create aggregated result from list of run results."""
        if not results:
            return cls(
                config=config, runs=0, success_rate=0.0,
                blocks_committed_mean=0.0, blocks_committed_std=0.0,
                timeouts_mean=0.0, latency_avg_mean=0.0, latency_avg_std=0.0,
                latency_p95_mean=0.0, throughput_mean=0.0, throughput_std=0.0,
                duration_mean_ms=0.0
            )
        
        successes = [r for r in results if r.success]
        success_rate = len(successes) / len(results) if results else 0.0
        
        blocks = [r.blocks_committed for r in results]
        timeouts = [r.total_timeouts for r in results]
        latencies = [r.latency_avg_ms for r in results if r.latency_avg_ms > 0]
        p95s = [r.latency_p95_ms for r in results if r.latency_p95_ms > 0]
        throughputs = [r.throughput for r in results]
        durations = [r.duration_ms for r in results]
        
        return cls(
            config=config,
            runs=len(results),
            success_rate=success_rate,
            blocks_committed_mean=mean(blocks) if blocks else 0.0,
            blocks_committed_std=stdev(blocks) if len(blocks) > 1 else 0.0,
            timeouts_mean=mean(timeouts) if timeouts else 0.0,
            latency_avg_mean=mean(latencies) if latencies else 0.0,
            latency_avg_std=stdev(latencies) if len(latencies) > 1 else 0.0,
            latency_p95_mean=mean(p95s) if p95s else 0.0,
            throughput_mean=mean(throughputs) if throughputs else 0.0,
            throughput_std=stdev(throughputs) if len(throughputs) > 1 else 0.0,
            duration_mean_ms=mean(durations) if durations else 0.0,
        )
    
    def to_dict(self) -> dict:
        """Convert to flat dictionary for CSV export."""
        result = dict(self.config)
        result.update({
            "runs": self.runs,
            "success_rate": self.success_rate,
            "blocks_committed_mean": self.blocks_committed_mean,
            "blocks_committed_std": self.blocks_committed_std,
            "timeouts_mean": self.timeouts_mean,
            "latency_avg_mean": self.latency_avg_mean,
            "latency_avg_std": self.latency_avg_std,
            "latency_p95_mean": self.latency_p95_mean,
            "throughput_mean": self.throughput_mean,
            "throughput_std": self.throughput_std,
            "duration_mean_ms": self.duration_mean_ms,
        })
        return result

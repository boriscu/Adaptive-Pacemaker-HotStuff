import time
import collections
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class MetricPoint:
    timestamp: float
    value: float

class MetricsCollector:
    """
    Centralized metrics collection singleton (or instance).
    """
    def __init__(self):
        # Time-series data
        self.commit_latencies: List[MetricPoint] = []
        self.view_changes: List[MetricPoint] = []
        self.throughput_data: List[MetricPoint] = [] # committed txs per second
        
        # Aggregates
        self.total_committed = 0
        self.start_time = 0.0
        
        # Per-Replica granular stats (optional)
        self.replica_stats: Dict[int, Dict] = collections.defaultdict(dict)

    def record_commit(self, timestamp: float, num_blocks: int = 1, latency: float = 0.0):
        self.total_committed += num_blocks
        self.commit_latencies.append(MetricPoint(timestamp, latency))
        
    def record_view_change(self, timestamp: float, view: int):
        self.view_changes.append(MetricPoint(timestamp, float(view)))
    
    def get_summary(self) -> Dict:
        """Calculate summary statistics."""
        avg_latency = 0.0
        if self.commit_latencies:
            avg_latency = sum(m.value for m in self.commit_latencies) / len(self.commit_latencies)
            
        return {
            "total_committed": self.total_committed,
            "view_changes": len(self.view_changes),
            "avg_latency": avg_latency
        }
    
    def reset(self):
        self.commit_latencies.clear()
        self.view_changes.clear()
        self.throughput_data.clear()
        self.total_committed = 0

# Global collector instance
collector = MetricsCollector()

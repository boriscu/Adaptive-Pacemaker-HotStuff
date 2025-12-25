"""
MetricsCollector for aggregating simulation metrics.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class MetricsSummary:
    """Summary of collected metrics."""

    total_blocks_committed: int = 0
    total_views: int = 0
    total_view_changes: int = 0
    total_timeouts: int = 0
    average_commit_latency_ms: float = 0.0
    throughput_blocks_per_second: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    simulation_duration_ms: int = 0


class MetricsCollector:
    """
    Collects and aggregates metrics from simulation events.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._commit_events: List[dict] = []
        self._view_change_events: List[dict] = []
        self._timeout_events: List[dict] = []
        self._block_proposal_times: Dict[str, int] = {}
        self._commit_latencies: List[int] = []
        self._start_time: int = 0
        self._end_time: int = 0

    def record_event(self, event: dict) -> None:
        """
        Record an event for metrics collection.

        Args:
            event: The event dictionary to record.
        """
        event_type = event.get("type")

        if event_type == "PROPOSAL":
            block_hash = event.get("block_hash")
            timestamp = event.get("timestamp", 0)
            self._block_proposal_times[block_hash] = timestamp

        elif event_type == "COMMIT":
            self._commit_events.append(event)
            block_hash = event.get("block_hash")
            commit_time = event.get("timestamp", 0)

            if block_hash in self._block_proposal_times:
                latency = commit_time - self._block_proposal_times[block_hash]
                self._commit_latencies.append(latency)

        elif event_type == "VIEW_CHANGE":
            self._view_change_events.append(event)

        elif event_type == "TIMEOUT":
            self._timeout_events.append(event)

        timestamp = event.get("timestamp", 0)
        if timestamp > self._end_time:
            self._end_time = timestamp

    def get_summary(self) -> MetricsSummary:
        """
        Get a summary of all collected metrics.

        Returns:
            MetricsSummary with aggregated metrics.
        """
        unique_commits = set()
        for event in self._commit_events:
            unique_commits.add(event.get("block_hash"))

        duration_ms = max(self._end_time - self._start_time, 1)
        duration_seconds = duration_ms / 1000.0

        total_commits = len(unique_commits)
        throughput = total_commits / duration_seconds if duration_seconds > 0 else 0

        avg_latency = 0.0
        p50 = 0.0
        p95 = 0.0
        p99 = 0.0

        if self._commit_latencies:
            sorted_latencies = sorted(self._commit_latencies)
            avg_latency = sum(sorted_latencies) / len(sorted_latencies)
            p50 = self._percentile(sorted_latencies, 50)
            p95 = self._percentile(sorted_latencies, 95)
            p99 = self._percentile(sorted_latencies, 99)

        return MetricsSummary(
            total_blocks_committed=total_commits,
            total_views=len(self._view_change_events),
            total_view_changes=len(self._view_change_events),
            total_timeouts=len(self._timeout_events),
            average_commit_latency_ms=avg_latency,
            throughput_blocks_per_second=throughput,
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            simulation_duration_ms=duration_ms,
        )

    def _percentile(self, sorted_data: List[int], percentile: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * percentile / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_data) else f
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

    def reset(self) -> None:
        """Reset all collected metrics."""
        self._commit_events.clear()
        self._view_change_events.clear()
        self._timeout_events.clear()
        self._block_proposal_times.clear()
        self._commit_latencies.clear()
        self._start_time = 0
        self._end_time = 0

    def set_start_time(self, time: int) -> None:
        """Set the simulation start time."""
        self._start_time = time

    def to_dict(self) -> dict:
        """Export metrics as dictionary."""
        summary = self.get_summary()
        return {
            "total_blocks_committed": summary.total_blocks_committed,
            "total_views": summary.total_views,
            "total_view_changes": summary.total_view_changes,
            "total_timeouts": summary.total_timeouts,
            "average_commit_latency_ms": summary.average_commit_latency_ms,
            "throughput_blocks_per_second": summary.throughput_blocks_per_second,
            "p50_latency_ms": summary.p50_latency_ms,
            "p95_latency_ms": summary.p95_latency_ms,
            "p99_latency_ms": summary.p99_latency_ms,
            "simulation_duration_ms": summary.simulation_duration_ms,
        }

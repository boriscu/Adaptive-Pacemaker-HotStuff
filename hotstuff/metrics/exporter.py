"""
MetricsExporter for exporting metrics to various formats.
"""

import json
from typing import Any
from pathlib import Path

from hotstuff.metrics.collector import MetricsCollector
from hotstuff.metrics.collector import MetricsSummary


class MetricsExporter:
    """
    Exports metrics to various formats (JSON, CSV).
    """
    
    def __init__(self, collector: MetricsCollector):
        """
        Initialize the exporter.
        
        Args:
            collector: The metrics collector to export from.
        """
        self._collector = collector
    
    def export_json(self, filepath: str) -> None:
        """
        Export metrics to JSON file.
        
        Args:
            filepath: Path to write the JSON file.
        """
        data = self._collector.to_dict()
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_json_string(self) -> str:
        """
        Export metrics as JSON string.
        
        Returns:
            JSON string of metrics.
        """
        return json.dumps(self._collector.to_dict(), indent=2)
    
    def get_summary(self) -> MetricsSummary:
        """Get the metrics summary."""
        return self._collector.get_summary()

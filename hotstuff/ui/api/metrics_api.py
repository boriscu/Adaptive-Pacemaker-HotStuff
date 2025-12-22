"""
Metrics API endpoints.
"""

from flask import Blueprint
from flask import jsonify

from hotstuff.metrics.collector import MetricsCollector


def create_metrics_blueprint(metrics: MetricsCollector) -> Blueprint:
    """
    Create the metrics API blueprint.
    
    Args:
        metrics: The metrics collector.
        
    Returns:
        Flask Blueprint with metrics endpoints.
    """
    bp = Blueprint("metrics", __name__)
    
    @bp.route("/summary", methods=["GET"])
    def get_summary():
        """Get metrics summary."""
        return jsonify(metrics.to_dict())
    
    @bp.route("/export", methods=["GET"])
    def export_metrics():
        """Export metrics as JSON."""
        return jsonify(metrics.to_dict())
    
    return bp

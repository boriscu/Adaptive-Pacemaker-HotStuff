"""
Simulation control API endpoints.
"""

from flask import Blueprint
from flask import jsonify
from flask import request

from hotstuff.simulation.engine import SimulationEngine
from hotstuff.metrics.collector import MetricsCollector
from hotstuff.domain.enumerations.fault_type import FaultType


def create_simulation_blueprint(engine: SimulationEngine, metrics: MetricsCollector) -> Blueprint:
    """
    Create the simulation API blueprint.
    
    Args:
        engine: The simulation engine.
        metrics: The metrics collector.
        
    Returns:
        Flask Blueprint with simulation endpoints.
    """
    bp = Blueprint("simulation", __name__)
    
    @bp.route("/start", methods=["POST"])
    def start():
        """Start the simulation."""
        metrics.reset()
        metrics.set_start_time(0)
        events = engine.start()
        for event in events:
            metrics.record_event(event)
        return jsonify({
            "status": "started",
            "events": events
        })
    
    @bp.route("/pause", methods=["POST"])
    def pause():
        """Pause the simulation."""
        engine.pause()
        return jsonify({"status": "paused"})
    
    @bp.route("/resume", methods=["POST"])
    def resume():
        """Resume the simulation."""
        engine.resume()
        return jsonify({"status": "resumed"})
    
    @bp.route("/step", methods=["POST"])
    def step():
        """Execute a single simulation step."""
        event = engine.step()
        if event:
            metrics.record_event(event)
        return jsonify({
            "event": event,
            "current_time": engine.current_time,
            "current_view": engine.current_view
        })
    
    @bp.route("/run", methods=["POST"])
    def run_steps():
        """Run multiple simulation steps."""
        data = request.get_json() or {}
        count = data.get("count", 10)
        
        events = []
        for _ in range(count):
            event = engine.step()
            if event:
                events.append(event)
                metrics.record_event(event)
            else:
                break
        
        return jsonify({
            "events": events,
            "current_time": engine.current_time,
            "current_view": engine.current_view
        })
    
    @bp.route("/reset", methods=["POST"])
    def reset():
        """Reset the simulation."""
        engine.reset()
        metrics.reset()
        return jsonify({"status": "reset"})
    
    @bp.route("/status", methods=["GET"])
    def status():
        """Get simulation status."""
        return jsonify({
            "is_running": engine.is_running,
            "is_paused": engine.is_paused,
            "current_time": engine.current_time,
            "current_view": engine.current_view
        })
    
    @bp.route("/fault", methods=["POST"])
    def inject_fault():
        """Inject a fault into a replica."""
        data = request.get_json() or {}
        replica_id = data.get("replica_id")
        fault_type_str = data.get("fault_type", "CRASH")
        
        if replica_id is None:
            return jsonify({"error": "replica_id required"}), 400
        
        try:
            fault_type = FaultType[fault_type_str]
        except KeyError:
            return jsonify({"error": f"Invalid fault type: {fault_type_str}"}), 400
        
        engine.inject_fault(replica_id, fault_type)
        return jsonify({
            "status": "fault_injected",
            "replica_id": replica_id,
            "fault_type": fault_type_str
        })
    
    @bp.route("/fault/clear", methods=["POST"])
    def clear_fault():
        """Clear a fault from a replica."""
        data = request.get_json() or {}
        replica_id = data.get("replica_id")
        
        if replica_id is None:
            return jsonify({"error": "replica_id required"}), 400
        
        engine.clear_fault(replica_id)
        return jsonify({
            "status": "fault_cleared",
            "replica_id": replica_id
        })
    
    @bp.route("/config", methods=["GET"])
    def get_config():
        """Get simulation configuration."""
        settings = engine.settings
        return jsonify({
            "num_replicas": settings.num_replicas,
            "num_faulty": settings.num_faulty,
            "quorum_size": settings.quorum_size,
            "base_timeout_ms": settings.base_timeout_ms,
            "pacemaker_type": settings.pacemaker_type.name,
            "network_delay_min_ms": settings.network_delay_min_ms,
            "network_delay_max_ms": settings.network_delay_max_ms
        })
    
    return bp

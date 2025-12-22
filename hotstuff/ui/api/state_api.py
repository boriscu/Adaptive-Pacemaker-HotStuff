"""
State query API endpoints.
"""

from flask import Blueprint
from flask import jsonify
from flask import request

from hotstuff.simulation.engine import SimulationEngine


def create_state_blueprint(engine: SimulationEngine) -> Blueprint:
    """
    Create the state API blueprint.
    
    Args:
        engine: The simulation engine.
        
    Returns:
        Flask Blueprint with state endpoints.
    """
    bp = Blueprint("state", __name__)
    
    @bp.route("/replicas", methods=["GET"])
    def get_replicas():
        """Get the state of all replicas."""
        states = engine.get_replica_states()
        return jsonify({
            "replicas": [_serialize_state(s) for s in states]
        })
    
    @bp.route("/replica/<int:replica_id>", methods=["GET"])
    def get_replica(replica_id: int):
        """Get the state of a specific replica."""
        state = engine.get_replica_state(replica_id)
        if state is None:
            return jsonify({"error": "Replica not found"}), 404
        return jsonify(_serialize_state(state))
    
    @bp.route("/network", methods=["GET"])
    def get_network():
        """Get in-flight messages."""
        messages = engine.get_in_flight_messages()
        return jsonify({
            "in_flight": messages,
            "count": len(messages)
        })
    
    @bp.route("/events", methods=["GET"])
    def get_events():
        """Get recent events."""
        count = request.args.get("count", 50, type=int)
        events = engine.get_recent_events(count)
        return jsonify({
            "events": events,
            "total": len(engine.get_event_history())
        })
    
    @bp.route("/events/all", methods=["GET"])
    def get_all_events():
        """Get all events."""
        events = engine.get_event_history()
        return jsonify({
            "events": events,
            "total": len(events)
        })
    
    return bp


def _serialize_state(state) -> dict:
    """Serialize a ReplicaState to dict."""
    return {
        "replica_id": state.replica_id,
        "current_view": state.current_view,
        "current_phase": state.current_phase.name,
        "is_leader": state.is_leader,
        "is_faulty": state.is_faulty,
        "fault_type": state.fault_type.name,
        "locked_qc": _serialize_qc(state.locked_qc),
        "prepare_qc": _serialize_qc(state.prepare_qc),
        "pending_block": _serialize_block(state.pending_block),
        "committed_count": len(state.committed_block_hashes),
        "last_voted_view": state.last_voted_view
    }


def _serialize_qc(qc) -> dict:
    """Serialize a QuorumCertificate to dict."""
    if qc is None:
        return None
    return {
        "type": qc.qc_type.name,
        "view": qc.view_number,
        "block_hash": qc.block_hash[:8] if qc.block_hash else None,
        "signer_count": qc.signer_count
    }


def _serialize_block(block) -> dict:
    """Serialize a Block to dict."""
    if block is None:
        return None
    return {
        "hash": block.block_hash[:8],
        "height": block.height,
        "view": block.view_number,
        "proposer": block.proposer_id
    }

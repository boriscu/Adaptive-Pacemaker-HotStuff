"""
Flask server for HotStuff simulation UI.
"""

from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.domain.enumerations.fault_type import FaultType
from hotstuff.simulation.engine import SimulationEngine
from hotstuff.metrics.collector import MetricsCollector
from hotstuff.ui.api.state_api import create_state_blueprint
from hotstuff.ui.api.metrics_api import create_metrics_blueprint


class EngineContainer:
    """
    Mutable container for the simulation engine.
    
    Allows the engine to be recreated with new settings.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = SimulationEngine(settings)
        self.metrics = MetricsCollector()
    
    def recreate(self, settings: Settings) -> None:
        """Recreate the engine with new settings."""
        self.settings = settings
        self.engine = SimulationEngine(settings)
        self.metrics.reset()


class Server:
    """
    Flask server for the HotStuff simulation UI.
    """
    
    def __init__(self, settings: Settings):
        """
        Initialize the server.
        
        Args:
            settings: Simulation settings.
        """
        self._container = EngineContainer(settings)
        self._app = Flask(
            __name__,
            template_folder="templates",
            static_folder="static"
        )
        
        self._register_routes()
        self._register_api_routes()
    
    def _register_routes(self) -> None:
        """Register main routes."""
        
        @self._app.route("/")
        def index():
            return render_template("index.html")
        
        @self._app.route("/health")
        def health():
            return jsonify({"status": "ok"})
    
    def _register_api_routes(self) -> None:
        """Register API routes."""
        container = self._container
        
        @self._app.route("/api/simulation/config", methods=["GET"])
        def get_config():
            settings = container.settings
            return jsonify({
                "num_replicas": settings.num_replicas,
                "num_faulty": settings.num_faulty,
                "quorum_size": settings.quorum_size,
                "max_faulty": settings.max_faulty,
                "base_timeout_ms": settings.base_timeout_ms,
                "pacemaker_type": settings.pacemaker_type.name,
                "network_delay_min_ms": settings.network_delay_min_ms,
                "network_delay_max_ms": settings.network_delay_max_ms
            })
        
        @self._app.route("/api/simulation/config", methods=["POST"])
        def update_config():
            """Update simulation configuration and recreate engine."""
            data = request.get_json() or {}
            
            num_replicas = data.get("num_replicas", container.settings.num_replicas)
            num_faulty = data.get("num_faulty", container.settings.num_faulty)
            pacemaker_str = data.get("pacemaker_type", container.settings.pacemaker_type.name)
            fault_type_str = data.get("fault_type", container.settings.fault_type.name)
            base_timeout = data.get("base_timeout_ms", container.settings.base_timeout_ms)
            
            try:
                pacemaker_type = PacemakerType[pacemaker_str.upper()]
            except KeyError:
                pacemaker_type = PacemakerType.BASELINE
            
            try:
                fault_type = FaultType[fault_type_str.upper()]
            except KeyError:
                fault_type = FaultType.CRASH
            
            if num_faulty >= num_replicas:
                return jsonify({
                    "error": f"num_faulty ({num_faulty}) must be less than num_replicas ({num_replicas})"
                }), 400
            
            if num_replicas < 1:
                return jsonify({"error": "num_replicas must be at least 1"}), 400
            
            new_settings = Settings(
                num_replicas=num_replicas,
                num_faulty=num_faulty,
                pacemaker_type=pacemaker_type,
                fault_type=fault_type,
                base_timeout_ms=base_timeout,
                random_seed=container.settings.random_seed
            )
            
            container.recreate(new_settings)
            
            return jsonify({
                "status": "configured",
                "num_replicas": new_settings.num_replicas,
                "num_faulty": new_settings.num_faulty,
                "quorum_size": new_settings.quorum_size,
                "max_faulty": new_settings.max_faulty,
                "pacemaker_type": new_settings.pacemaker_type.name,
                "fault_type": new_settings.fault_type.name,
                "base_timeout_ms": new_settings.base_timeout_ms
            })
        
        @self._app.route("/api/simulation/start", methods=["POST"])
        def start():
            container.metrics.reset()
            container.metrics.set_start_time(0)
            events = container.engine.start()
            for event in events:
                container.metrics.record_event(event)
            return jsonify({
                "status": "started",
                "events": events
            })
        
        @self._app.route("/api/simulation/pause", methods=["POST"])
        def pause():
            container.engine.pause()
            return jsonify({"status": "paused"})
        
        @self._app.route("/api/simulation/resume", methods=["POST"])
        def resume():
            container.engine.resume()
            return jsonify({"status": "resumed"})
        
        @self._app.route("/api/simulation/step", methods=["POST"])
        def step():
            event = container.engine.step()
            if event:
                container.metrics.record_event(event)
            return jsonify({
                "event": event,
                "current_time": container.engine.current_time,
                "current_view": container.engine.current_view
            })
        
        @self._app.route("/api/simulation/run", methods=["POST"])
        def run_steps():
            data = request.get_json() or {}
            count = data.get("count", 10)
            
            events = []
            for _ in range(count):
                event = container.engine.step()
                if event:
                    events.append(event)
                    container.metrics.record_event(event)
                else:
                    break
            
            return jsonify({
                "events": events,
                "current_time": container.engine.current_time,
                "current_view": container.engine.current_view
            })
        
        @self._app.route("/api/simulation/reset", methods=["POST"])
        def reset():
            container.engine.reset()
            container.metrics.reset()
            return jsonify({"status": "reset"})
        
        @self._app.route("/api/simulation/status", methods=["GET"])
        def status():
            return jsonify({
                "is_running": container.engine.is_running,
                "is_paused": container.engine.is_paused,
                "current_time": container.engine.current_time,
                "current_view": container.engine.current_view
            })
        
        @self._app.route("/api/state/replicas", methods=["GET"])
        def get_replicas():
            states = container.engine.get_replica_states()
            return jsonify({
                "replicas": [_serialize_state(s) for s in states]
            })
        
        @self._app.route("/api/state/network", methods=["GET"])
        def get_network():
            messages = container.engine.get_in_flight_messages()
            return jsonify({
                "in_flight": messages,
                "count": len(messages)
            })
        
        @self._app.route("/api/state/events", methods=["GET"])
        def get_events():
            count = request.args.get("count", 50, type=int)
            events = container.engine.get_recent_events(count)
            return jsonify({
                "events": events,
                "total": len(container.engine.get_event_history())
            })
        
        @self._app.route("/api/metrics/summary", methods=["GET"])
        def get_metrics():
            return jsonify(container.metrics.to_dict())
    
    def run(self, host: str = None, port: int = None, debug: bool = None) -> None:
        """
        Run the Flask server.
        
        Args:
            host: Host address (default from settings).
            port: Port number (default from settings).
            debug: Debug mode (default from settings).
        """
        self._app.run(
            host=host or self._container.settings.ui_host,
            port=port or self._container.settings.ui_port,
            debug=debug if debug is not None else self._container.settings.ui_debug
        )
    
    @property
    def app(self) -> Flask:
        """Get the Flask app instance."""
        return self._app
    
    @property
    def engine(self) -> SimulationEngine:
        """Get the simulation engine."""
        return self._container.engine


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

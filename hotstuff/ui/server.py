"""
Flask server for HotStuff simulation UI.
"""

from flask import Flask
from flask import render_template
from flask import jsonify

from hotstuff.config.settings import Settings
from hotstuff.simulation.engine import SimulationEngine
from hotstuff.metrics.collector import MetricsCollector
from hotstuff.ui.api.simulation_api import create_simulation_blueprint
from hotstuff.ui.api.state_api import create_state_blueprint
from hotstuff.ui.api.metrics_api import create_metrics_blueprint


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
        self._settings = settings
        self._app = Flask(
            __name__,
            template_folder="templates",
            static_folder="static"
        )
        
        self._engine = SimulationEngine(settings)
        self._metrics = MetricsCollector()
        
        self._register_routes()
        self._register_blueprints()
    
    def _register_routes(self) -> None:
        """Register main routes."""
        
        @self._app.route("/")
        def index():
            return render_template("index.html")
        
        @self._app.route("/health")
        def health():
            return jsonify({"status": "ok"})
    
    def _register_blueprints(self) -> None:
        """Register API blueprints."""
        simulation_bp = create_simulation_blueprint(self._engine, self._metrics)
        state_bp = create_state_blueprint(self._engine)
        metrics_bp = create_metrics_blueprint(self._metrics)
        
        self._app.register_blueprint(simulation_bp, url_prefix="/api/simulation")
        self._app.register_blueprint(state_bp, url_prefix="/api/state")
        self._app.register_blueprint(metrics_bp, url_prefix="/api/metrics")
    
    def run(self, host: str = None, port: int = None, debug: bool = None) -> None:
        """
        Run the Flask server.
        
        Args:
            host: Host address (default from settings).
            port: Port number (default from settings).
            debug: Debug mode (default from settings).
        """
        self._app.run(
            host=host or self._settings.ui_host,
            port=port or self._settings.ui_port,
            debug=debug if debug is not None else self._settings.ui_debug
        )
    
    @property
    def app(self) -> Flask:
        """Get the Flask app instance."""
        return self._app
    
    @property
    def engine(self) -> SimulationEngine:
        """Get the simulation engine."""
        return self._engine

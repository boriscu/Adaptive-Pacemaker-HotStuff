from flask import Flask, render_template, jsonify, request
import threading
import time
from hotstuff.simulation.environment import Environment
from hotstuff.metrics.collector import collector
from hotstuff.config import config, ProtocolMode
import logging

app = Flask(__name__)

class SimulationManager:
    def __init__(self):
        self.env = Environment()
        self.running = False
        self.started = False
        self.thread = None
        self.max_time = 1000.0
        self.step_delay = 2.5 

    def start_simulation(self):
        if self.running: 
            return
            
        if not self.started:
            self.env.start()
            self.started = True
            
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.start()

    def _run_loop(self):
        while self.running and self.env.engine.current_time < self.max_time:
            self.env.engine.run(max_time=self.env.engine.current_time + 1.0) # Run 1 sec virtual time
            time.sleep(self.step_delay) # Slow down for UI to catch up

    def stop_simulation(self):
        self.running = False
        self.env.engine.stop()
        if self.thread:
            self.thread.join()

    def reset_simulation(self):
        self.stop_simulation()
        collector.reset()
        self.env = Environment()
        self.started = False

sim_manager = SimulationManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Returns current simulation state."""
    # Collect state from replicas
    replicas_state = {}
    for rid, harness in sim_manager.env.replicas.items():
        r = harness.replica
        leader_id = r.pacemaker.get_leader(r.view)
        replicas_state[rid] = {
            "view": r.view,
            "height": r.executed_up_to_height,
            "commits": len(r.committed_blocks),
            "last_commit": r.committed_blocks[-1].hash[:8] if r.committed_blocks else "None",
            "is_leader": (leader_id == r.id),
            "is_faulty": r.is_faulty
        }

    return jsonify({
        "time": sim_manager.env.engine.current_time,
        "running": sim_manager.running,
        "metrics": collector.get_summary(),
        "replicas": replicas_state
    })

@app.route('/api/control', methods=['POST'])
def control():
    """Start/Stop/Reset"""
    action = request.json.get('action')
    if action == 'start':
        sim_manager.start_simulation()
    elif action == 'stop':
        sim_manager.stop_simulation()
    elif action == 'reset':
        sim_manager.reset_simulation()
    return jsonify({"success": True})

@app.route('/api/speed', methods=['POST'])
def set_speed():
    """Set simulation step delay."""
    data = request.json
    if 'delay' in data:
        sim_manager.step_delay = float(data['delay'])
    return jsonify({"success": True, "delay": sim_manager.step_delay})

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update global config."""
    # Needs restart to take effect
    data = request.json
    if 'N' in data: config.N = int(data['N'])
    if 'F' in data: config.F = int(data['F'])
    if 'PROTOCOL' in data: config.PROTOCOL = ProtocolMode(data['PROTOCOL'])
    return jsonify({"success": True, "message": "Changes apply on Reset"})

if __name__ == '__main__':
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(debug=True, port=5000)

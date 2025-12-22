# HotStuff Consensus Simulation

A faithful Python implementation of HotStuff (Basic and Chained) with Adaptive Pacemaker simulation.

## Features
- **Protocols**: Basic HotStuff, Chained HotStuff.
- **Pacemakers**: Baseline (Round-Robin + Fixed Timeout), Adaptive (Exponential Moving Average).
- **Simulation**: Deterministic discrete-event simulation engine.
- **Visualization**: Web-based dashboard (Flask + Realtime updates).
- **Metrics**: Throughput, Latency, View Changes.

## Structure
- `hotstuff/domain`: Core data structures (Block, QC, Msg) mirroring the paper.
- `hotstuff/protocol`: Safety logic (Replica) and Event Handling.
- `hotstuff/pacemaker`: Liveness logic.
- `hotstuff/network`: Simulated network with configurable latency.
- `hotstuff/simulation`: Event scheduler.
- `hotstuff/ui`: Flask server and Dashboard.

## Installation
```bash
pip install -r requirements.txt
```

## Running the Dashboard
```bash
python -m hotstuff.ui.server
```
Then open [http://localhost:5000](http://localhost:5000).

## Running Headless Test
```bash
python run_test.py
```

## Configuration
Configuration can be set via Environment Variables or the UI:
- `HOTSTUFF_N`: Total Replicas
- `HOTSTUFF_F`: Fault tolerance
- `HOTSTUFF_DELTA`: Base timeout

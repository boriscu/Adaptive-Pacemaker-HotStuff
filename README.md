# HotStuff Consensus Protocol Simulation

A complete, runnable Python simulation of the HotStuff BFT consensus protocol with visualization UI, adaptive pacemaker, and metrics collection.

## Features

- **Basic HotStuff Protocol**: Faithful implementation of the 3-phase commit protocol (Algorithm 2 from the paper)
- **Adaptive Pacemaker**: EMA-based timeout adjustment for improved liveness under varying network conditions
- **Visualization UI**: Flask-based web interface with real-time network graph and step-by-step replay
- **Metrics Collection**: Commit latency, throughput, view-change frequency, and percentile latencies
- **Fault Injection**: Support for crash fault simulation to test BFT properties
- **Deterministic Simulation**: Seed-based reproducibility for debugging and testing

## Quick Start

### Prerequisites

- Python 3.9+
- Conda (recommended) or pip

### Installation

```bash
# Create and activate conda environment
conda create -n hotstuff python=3.10
conda activate hotstuff

# Install dependencies
pip install -r requirements.txt
```

### Running the UI Server

```bash
# Start the web UI server
python -m hotstuff.main

# Access at http://127.0.0.1:5000
```

### Running Headless Simulation

```bash
# Run a headless simulation with default settings
python -m hotstuff.main --headless

# With custom settings
python -m hotstuff.main --headless --num-replicas 7 --pacemaker adaptive --max-views 50
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--headless` | Run without UI | False |
| `--port PORT` | UI server port | 5000 |
| `--num-replicas N` | Number of replicas (3f+1) | 4 |
| `--num-faulty F` | Number of faulty replicas | 1 |
| `--pacemaker TYPE` | `baseline` or `adaptive` | baseline |
| `--timeout MS` | Base timeout in milliseconds | 1000 |
| `--seed N` | Random seed for determinism | None |
| `--max-views N` | Max views for headless mode | 100 |
| `--log-level LEVEL` | DEBUG, INFO, WARNING, ERROR | INFO |

## Project Structure

```
hotstuff/
├── domain/                    # Domain models and types
│   ├── types/                 # Type aliases (ViewNumber, ReplicaId, etc.)
│   ├── enumerations/          # Enums (MessageType, PhaseType, etc.)
│   └── models/                # Pydantic models (Block, QC, Messages)
├── config/                    # Configuration (Pydantic Settings)
├── exceptions/                # Custom exception hierarchy
├── factories/                 # Factory classes (Block, QC, Message)
├── network/                   # Simulated network layer
├── protocol/                  # Core protocol logic
│   ├── replica.py            # Replica implementation (Algorithm 2)
│   ├── safety_rules.py       # safeNode predicate (Algorithm 1)
│   ├── vote_collector.py     # QC formation
│   └── leader_scheduler.py   # Round-robin leader election
├── pacemaker/                 # Liveness layer
│   ├── base_pacemaker.py     # Fixed timeout pacemaker
│   └── adaptive_pacemaker.py # EMA-based adaptive timeout
├── simulation/                # Discrete event simulation engine
├── metrics/                   # Metrics collection and export
├── ui/                        # Flask web UI
│   ├── server.py             # Flask server
│   ├── templates/            # HTML templates
│   └── static/               # CSS and JavaScript
└── tests/                     # Test suite
    ├── unit/                  # Unit tests
    └── integration/           # Integration tests
```

## Protocol Overview

HotStuff is a BFT consensus protocol that achieves O(n) message complexity per view through threshold signatures and a pipelined leader-based approach.

### Phases

1. **NEW-VIEW**: Replicas send their highest QC to the new leader
2. **PREPARE**: Leader proposes a block, replicas vote if safe
3. **PRE-COMMIT**: Leader broadcasts prepareQC, replicas vote
4. **COMMIT**: Leader broadcasts precommitQC, replicas lock and vote
5. **DECIDE**: Leader broadcasts commitQC, replicas execute

### Safety Rule

A replica votes for block `b` if:
- `b` extends from the locked block, OR
- The justify QC has a higher view than the locked QC

## Running Tests

```bash
# Run all tests
python -m pytest hotstuff/tests/ -v

# Run unit tests only
python -m pytest hotstuff/tests/unit/ -v

# Run integration tests
python -m pytest hotstuff/tests/integration/ -v
```

## Configuration

Configuration can be provided via:

1. Command line arguments
2. Environment variables (prefix: `HOTSTUFF_`)
3. `.env` file

Example `.env`:
```
HOTSTUFF_NUM_REPLICAS=7
HOTSTUFF_PACEMAKER_TYPE=adaptive
HOTSTUFF_BASE_TIMEOUT_MS=500
```

## References

- [HotStuff: BFT Consensus with Linearity and Responsiveness](https://arxiv.org/abs/1803.05069)
- [HotStuff GitHub (LibraBFT)](https://github.com/libra/libra)

## License

MIT License

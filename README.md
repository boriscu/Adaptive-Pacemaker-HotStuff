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

## Running Benchmarks

The project includes a comprehensive benchmarking system for evaluating protocol performance under various conditions.

### Using YAML Configuration

The easiest way to run benchmarks is using the `benchmark_config.yaml` file:

```bash
# Run benchmarks using the config file (auto-detected if present in root)
python -m hotstuff.benchmark

# Explicitly specify config file
python -m hotstuff.benchmark --config benchmark_config.yaml

# Run with aggregated results and plots
python -m hotstuff.benchmark --aggregate --plot

# Export to specific output file
python -m hotstuff.benchmark -o results/my_benchmark.csv
```

### Using CLI Arguments

You can also run benchmarks with command-line arguments:

```bash
# Basic benchmark with custom parameters
python -m hotstuff.benchmark --num-replicas 4,7,10 --pacemaker baseline,adaptive --runs 5

# Full example with all options
python -m hotstuff.benchmark \
    --num-replicas 10,20 \
    --num-faulty 1,3 \
    --pacemaker baseline,adaptive \
    --fault-type CRASH,SILENT,RANDOM_DROP \
    --max-views 100 \
    --runs 5 \
    --output results/benchmark.csv \
    --aggregate \
    --plot
```

### Benchmark CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config, -c` | Path to YAML configuration file | auto-detect |
| `--num-replicas` | Comma-separated replica counts | 4 |
| `--num-faulty` | Comma-separated faulty node counts | 1 |
| `--pacemaker` | Pacemaker types: `baseline`, `adaptive` | baseline |
| `--fault-type` | Fault types: `CRASH`, `SILENT`, `RANDOM_DROP` | CRASH |
| `--max-views` | Maximum views per simulation | 30 |
| `--runs, -r` | Runs per configuration | 5 |
| `--seed` | Base random seed | 42 |
| `--output, -o` | Output file path (CSV or JSON) | results/benchmark_results.csv |
| `--aggregate, -a` | Output aggregated results | False |
| `--plot, -p` | Generate plots (requires matplotlib) | False |
| `--quiet, -q` | Suppress progress output | False |
| `--log-level` | Logging level | WARNING |

### Benchmark Scenarios

The `benchmark_config.yaml` file includes pre-defined scenarios:

1. **Scalability Test**: Measures throughput as committee size grows
2. **Fault Tolerance Comparison**: Compares impact of different fault models
3. **Pacemaker Efficiency**: Evaluates Adaptive vs Baseline pacemaker
4. **Safety/Liveness Test**: Demonstrates failure when Byzantine limit exceeded

Edit the YAML file and uncomment the desired scenario to run it.

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

"""
HotStuff Consensus Simulation - Main Entry Point.

Run the simulation with the UI server or in headless mode.

Usage:
    python -m hotstuff.main                    # Start UI server
    python -m hotstuff.main --headless         # Run headless simulation
    python -m hotstuff.main --help             # Show help
"""

import argparse
import sys

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.simulation.engine import SimulationEngine
from hotstuff.metrics.collector import MetricsCollector
from hotstuff.logging_config.logger import StructuredLogger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="HotStuff Consensus Protocol Simulation"
    )
    
    parser.add_argument(
        "--ui", 
        action="store_true",
        default=True,
        help="Start the UI server (default)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run headless simulation without UI"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="UI server port (default: 5000)"
    )
    parser.add_argument(
        "--num-replicas",
        type=int,
        default=4,
        help="Number of replicas (default: 4, must be 3f+1)"
    )
    parser.add_argument(
        "--num-faulty",
        type=int,
        default=1,
        help="Number of faulty replicas (default: 1)"
    )
    parser.add_argument(
        "--pacemaker",
        choices=["baseline", "adaptive"],
        default="baseline",
        help="Pacemaker type (default: baseline)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1000,
        help="Base timeout in milliseconds (default: 1000)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for deterministic simulation"
    )
    parser.add_argument(
        "--max-views",
        type=int,
        default=100,
        help="Maximum views for headless mode (default: 100)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    return parser.parse_args()


def run_ui_server(settings: Settings, port: int):
    """Run the Flask UI server."""
    from hotstuff.ui.server import Server
    
    print(f"\n🔥 HotStuff Consensus Simulation")
    print(f"   Replicas: {settings.num_replicas} (f={settings.num_faulty})")
    print(f"   Pacemaker: {settings.pacemaker_type.name}")
    print(f"   Timeout: {settings.base_timeout_ms}ms")
    print(f"\n   Starting UI server at http://127.0.0.1:{port}")
    print(f"   Press Ctrl+C to stop\n")
    
    server = Server(settings)
    server.run(port=port, debug=False)


def run_headless(settings: Settings, max_views: int):
    """Run headless simulation."""
    logger = StructuredLogger.get_logger("main")
    
    print(f"\n🔥 HotStuff Headless Simulation")
    print(f"   Replicas: {settings.num_replicas} (f={settings.num_faulty})")
    print(f"   Pacemaker: {settings.pacemaker_type.name}")
    print(f"   Max Views: {max_views}\n")
    
    engine = SimulationEngine(settings)
    metrics = MetricsCollector()
    
    events = engine.start()
    for event in events:
        metrics.record_event(event)
    
    step_count = 0
    max_steps = max_views * 100
    
    while step_count < max_steps:
        event = engine.step()
        if event is None:
            break
        
        metrics.record_event(event)
        step_count += 1
        
        if event.get("type") == "COMMIT":
            logger.info(f"Block committed at height {event.get('height')}")
    
    summary = metrics.get_summary()
    
    print(f"\n📊 Simulation Results:")
    print(f"   Duration: {summary.simulation_duration_ms}ms")
    print(f"   Blocks Committed: {summary.total_blocks_committed}")
    print(f"   View Changes: {summary.total_view_changes}")
    print(f"   Timeouts: {summary.total_timeouts}")
    print(f"   Avg Latency: {summary.average_commit_latency_ms:.2f}ms")
    print(f"   Throughput: {summary.throughput_blocks_per_second:.2f} blocks/s")
    print(f"   P50 Latency: {summary.p50_latency_ms:.2f}ms")
    print(f"   P95 Latency: {summary.p95_latency_ms:.2f}ms\n")


def main():
    """Main entry point."""
    args = parse_args()
    
    StructuredLogger.configure(args.log_level)
    
    pacemaker_type = (
        PacemakerType.ADAPTIVE if args.pacemaker == "adaptive" 
        else PacemakerType.BASELINE
    )
    
    settings = Settings(
        num_replicas=args.num_replicas,
        num_faulty=args.num_faulty,
        base_timeout_ms=args.timeout,
        pacemaker_type=pacemaker_type,
        random_seed=args.seed,
        max_views=args.max_views,
        log_level=args.log_level,
        ui_port=args.port
    )
    
    if not settings.validate_fault_tolerance():
        print(f"Error: num_faulty ({args.num_faulty}) exceeds max tolerable "
              f"({settings.max_faulty}) for {args.num_replicas} replicas")
        sys.exit(1)
    
    if args.headless:
        run_headless(settings, args.max_views)
    else:
        run_ui_server(settings, args.port)


if __name__ == "__main__":
    main()

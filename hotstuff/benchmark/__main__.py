"""
Benchmark CLI and export utilities.

Command-line interface for running batch simulations.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import List
from typing import Optional

from hotstuff.benchmark.config_schema import BenchmarkConfig
from hotstuff.benchmark.runner import BenchmarkRunner
from hotstuff.benchmark.results import RunResult
from hotstuff.benchmark.results import AggregatedResult
from hotstuff.logging_config.logger import StructuredLogger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="HotStuff Benchmark Runner - Batch simulation tool"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--num-replicas",
        type=str,
        default="4",
        help="Comma-separated replica counts (e.g., '4,7,10')"
    )
    parser.add_argument(
        "--num-faulty",
        type=str,
        default="1",
        help="Comma-separated faulty counts (e.g., '0,1,2')"
    )
    parser.add_argument(
        "--pacemaker",
        type=str,
        default="baseline",
        help="Comma-separated pacemaker types (e.g., 'baseline,adaptive')"
    )
    parser.add_argument(
        "--fault-type",
        type=str,
        default="CRASH",
        help="Comma-separated fault types (e.g., 'CRASH,SILENT')"
    )
    parser.add_argument(
        "--max-views",
        type=int,
        default=30,
        help="Maximum views per simulation (default: 30)"
    )
    parser.add_argument(
        "--runs", "-r",
        type=int,
        default=5,
        help="Number of runs per configuration (default: 5)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed (default: 42)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="results/benchmark_results.csv",
        help="Output file path (default: results/benchmark_results.csv)"
    )
    parser.add_argument(
        "--aggregate", "-a",
        action="store_true",
        help="Output aggregated results instead of per-run"
    )
    parser.add_argument(
        "--plot", "-p",
        action="store_true",
        help="Generate plots (requires matplotlib)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="WARNING",
        help="Logging level (default: WARNING)"
    )
    
    return parser.parse_args()


def load_config_from_yaml(filepath: str) -> BenchmarkConfig:
    """Load benchmark configuration from YAML file."""
    try:
        import yaml
    except ImportError:
        print("Error: PyYAML is required for YAML config files.")
        print("Install with: pip install pyyaml")
        sys.exit(1)
    
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    return BenchmarkConfig(**data)


def build_config_from_args(args) -> BenchmarkConfig:
    """Build benchmark configuration from CLI arguments."""
    from hotstuff.benchmark.config_schema import ConfigurationSet
    
    replicas = [int(x.strip()) for x in args.num_replicas.split(",")]
    faulty = [int(x.strip()) for x in args.num_faulty.split(",")]
    pacemakers = [x.strip() for x in args.pacemaker.split(",")]
    fault_types = [x.strip().upper() for x in args.fault_type.split(",")]
    
    config_set = ConfigurationSet(
        num_replicas=replicas,
        num_faulty=faulty,
        pacemaker_type=pacemakers,
        fault_type=fault_types,
    )
    
    return BenchmarkConfig(
        name="CLI Benchmark",
        max_views=args.max_views,
        runs_per_config=args.runs,
        random_seed_base=args.seed,
        configurations=[config_set],
    )


def export_csv(results: List[dict], filepath: str) -> None:
    """Export results to CSV file."""
    if not results:
        print("No results to export")
        return
    
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = list(results[0].keys())
    
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"   Results exported to: {path}")


def export_json(results: List[dict], filepath: str) -> None:
    """Export results to JSON file."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"   Results exported to: {path}")


def generate_plots(aggregated: List[AggregatedResult], output_dir: str) -> None:
    """Generate plots from aggregated results."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("   Warning: matplotlib not installed, skipping plots")
        return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    baseline_results = [r for r in aggregated if r.config.get("pacemaker_type") == "baseline"]
    adaptive_results = [r for r in aggregated if r.config.get("pacemaker_type") == "adaptive"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if baseline_results:
        replicas = [r.config["num_replicas"] for r in baseline_results]
        throughput = [r.throughput_mean for r in baseline_results]
        ax.plot(replicas, throughput, 'b-o', label='Baseline')
    
    if adaptive_results:
        replicas = [r.config["num_replicas"] for r in adaptive_results]
        throughput = [r.throughput_mean for r in adaptive_results]
        ax.plot(replicas, throughput, 'r-s', label='Adaptive')
    
    ax.set_xlabel('Number of Replicas')
    ax.set_ylabel('Throughput (blocks/s)')
    ax.set_title('Throughput vs Replica Count')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.savefig(output_path / 'throughput.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot 2: Latency by replica count
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if baseline_results:
        replicas = [r.config["num_replicas"] for r in baseline_results]
        latency = [r.latency_p95_mean for r in baseline_results]
        ax.plot(replicas, latency, 'b-o', label='Baseline')
    
    if adaptive_results:
        replicas = [r.config["num_replicas"] for r in adaptive_results]
        latency = [r.latency_p95_mean for r in adaptive_results]
        ax.plot(replicas, latency, 'r-s', label='Adaptive')
    
    ax.set_xlabel('Number of Replicas')
    ax.set_ylabel('P95 Latency (ms)')
    ax.set_title('P95 Latency vs Replica Count')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.savefig(output_path / 'latency.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Plot 3: Success rate
    fig, ax = plt.subplots(figsize=(10, 6))
    
    configs = [f"n={r.config['num_replicas']},f={r.config['num_faulty']}" for r in aggregated]
    success_rates = [r.success_rate * 100 for r in aggregated]
    colors = ['green' if s == 100 else 'orange' if s > 50 else 'red' for s in success_rates]
    
    ax.bar(range(len(configs)), success_rates, color=colors)
    ax.set_xticks(range(len(configs)))
    ax.set_xticklabels(configs, rotation=45, ha='right')
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rate by Configuration')
    ax.set_ylim(0, 105)
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    
    plt.savefig(output_path / 'success_rate.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"   Plots saved to: {output_path}")


def main():
    """Main entry point for benchmark CLI."""
    args = parse_args()
    
    StructuredLogger.configure(args.log_level)
    
    # Load or build configuration
    if args.config:
        try:
            benchmark_config = load_config_from_yaml(args.config)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    else:
        benchmark_config = build_config_from_args(args)
    
    # Run benchmark
    runner = BenchmarkRunner(verbose=not args.quiet)
    results = runner.run_batch(benchmark_config)
    
    # Aggregate if requested
    if args.aggregate:
        aggregated = runner.aggregate_results(results)
        export_data = [r.to_dict() for r in aggregated]
    else:
        export_data = [r.to_dict() for r in results]
    
    # Export results
    output_path = args.output
    if output_path.endswith('.json'):
        export_json(export_data, output_path)
    else:
        export_csv(export_data, output_path)
    
    # Generate plots if requested
    if args.plot:
        aggregated = runner.aggregate_results(results)
        plot_dir = Path(output_path).parent / "plots"
        generate_plots(aggregated, str(plot_dir))
    
    # Print summary
    if not args.quiet:
        aggregated = runner.aggregate_results(results)
        print(f"\n📊 Summary:")
        print(f"   Configurations: {len(aggregated)}")
        print(f"   Total runs: {len(results)}")
        
        successful = sum(1 for r in results if r.success)
        print(f"   Successful: {successful}/{len(results)} ({100*successful/len(results):.1f}%)")
        
        if results:
            avg_throughput = sum(r.throughput for r in results) / len(results)
            avg_latency = sum(r.latency_avg_ms for r in results if r.latency_avg_ms > 0)
            latency_count = sum(1 for r in results if r.latency_avg_ms > 0)
            if latency_count > 0:
                avg_latency /= latency_count
            print(f"   Avg throughput: {avg_throughput:.2f} blocks/s")
            print(f"   Avg latency: {avg_latency:.2f} ms\n")


if __name__ == "__main__":
    main()

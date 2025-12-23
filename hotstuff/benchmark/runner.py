"""
Benchmark runner for executing batch simulations.

Runs simulations with different configurations and collects metrics.
"""

from typing import List
from typing import Optional
from typing import Callable

from hotstuff.config.settings import Settings
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.domain.enumerations.fault_type import FaultType
from hotstuff.simulation.engine import SimulationEngine
from hotstuff.metrics.collector import MetricsCollector
from hotstuff.benchmark.config_schema import SingleRunConfig
from hotstuff.benchmark.config_schema import BenchmarkConfig
from hotstuff.benchmark.results import RunResult
from hotstuff.benchmark.results import AggregatedResult
from hotstuff.logging_config.logger import StructuredLogger


class BenchmarkRunner:
    """
    Runs benchmark simulations across multiple configurations.
    
    Executes simulations headlessly and collects metrics for analysis.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the benchmark runner.
        
        Args:
            verbose: Whether to print progress information.
        """
        self._verbose = verbose
        self._logger = StructuredLogger.get_logger("benchmark")
    
    def run_single(
        self, 
        config: SingleRunConfig, 
        run_index: int = 0,
        seed: Optional[int] = None
    ) -> RunResult:
        """
        Run a single simulation with the given configuration.
        
        Args:
            config: Configuration for this run.
            run_index: Index of this run (for seeding).
            seed: Optional random seed.
            
        Returns:
            RunResult with metrics from this run.
        """
        # Convert config to Settings
        try:
            pacemaker_type = PacemakerType[config.pacemaker_type.upper()]
        except KeyError:
            pacemaker_type = PacemakerType.BASELINE
        
        try:
            fault_type = FaultType[config.fault_type.upper()]
        except KeyError:
            fault_type = FaultType.CRASH
        
        settings = Settings(
            num_replicas=config.num_replicas,
            num_faulty=config.num_faulty,
            pacemaker_type=pacemaker_type,
            fault_type=fault_type,
            base_timeout_ms=config.base_timeout_ms,
            random_seed=seed,
        )
        
        engine = SimulationEngine(settings)
        metrics = MetricsCollector()
        
        try:
            events = engine.start()
            metrics.set_start_time(0)
            
            scale_factor = 50 * (1 + config.num_faulty)
            max_steps = config.max_views * config.num_replicas * scale_factor
            step_count = 0
            
            while step_count < max_steps:
                event = engine.step()
                if event is None:
                    break
                step_count += 1
            
            # Collect all events from engine history
            for event in engine.get_event_history():
                metrics.record_event(event)
            
            summary = metrics.get_summary()
            success = summary.total_blocks_committed > 0
                
        except Exception as e:
            self._logger.error(f"Simulation error: {e}")
            success = False
            summary = metrics.get_summary()
        
        return RunResult(
            config=config.to_dict(),
            run_index=run_index,
            success=success,
            blocks_committed=summary.total_blocks_committed,
            total_views=summary.total_views,
            total_timeouts=summary.total_timeouts,
            latency_avg_ms=summary.average_commit_latency_ms,
            latency_p50_ms=summary.p50_latency_ms,
            latency_p95_ms=summary.p95_latency_ms,
            latency_p99_ms=summary.p99_latency_ms,
            throughput=summary.throughput_blocks_per_second,
            duration_ms=summary.simulation_duration_ms,
        )
    
    def run_batch(
        self,
        benchmark_config: BenchmarkConfig,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[RunResult]:
        """
        Run all configurations in a benchmark.
        
        Args:
            benchmark_config: The benchmark configuration.
            progress_callback: Optional callback(current, total) for progress.
            
        Returns:
            List of all run results.
        """
        configs = benchmark_config.generate_run_configs()
        total_runs = len(configs) * benchmark_config.runs_per_config
        
        if self._verbose:
            print(f"\n📊 Running benchmark: {benchmark_config.name}")
            print(f"   Configurations: {len(configs)}")
            print(f"   Runs per config: {benchmark_config.runs_per_config}")
            print(f"   Total runs: {total_runs}\n")
        
        results = []
        current_run = 0
        
        for config in configs:
            for run_idx in range(benchmark_config.runs_per_config):
                # Calculate seed for this run
                seed = None
                if benchmark_config.random_seed_base is not None:
                    seed = benchmark_config.random_seed_base + current_run
                
                result = self.run_single(config, run_idx, seed)
                results.append(result)
                
                current_run += 1
                
                if progress_callback:
                    progress_callback(current_run, total_runs)
                elif self._verbose:
                    status = "✓" if result.success else "✗"
                    print(f"   [{current_run}/{total_runs}] {status} n={config.num_replicas} "
                          f"f={config.num_faulty} pm={config.pacemaker_type} "
                          f"ft={config.fault_type} → {result.blocks_committed} blocks")
        
        if self._verbose:
            print(f"\n   Completed {total_runs} runs")
        
        return results
    
    def aggregate_results(
        self, 
        results: List[RunResult]
    ) -> List[AggregatedResult]:
        """
        Aggregate results by configuration.
        
        Args:
            results: List of individual run results.
            
        Returns:
            List of aggregated results (one per unique configuration).
        """
        config_groups = {}
        for result in results:
            config_key = tuple(sorted(result.config.items()))
            if config_key not in config_groups:
                config_groups[config_key] = []
            config_groups[config_key].append(result)
        
        aggregated = []
        for config_key, group_results in config_groups.items():
            config = dict(config_key)
            agg = AggregatedResult.from_runs(config, group_results)
            aggregated.append(agg)
        
        return aggregated

from hotstuff.simulation.environment import Environment
from hotstuff.config import config, ProtocolMode
from hotstuff.metrics.collector import collector
import logging

def test_simulation():
    """
    Runs a short simulation and verifies that blocks are committed.
    """
    print("=== Running Integration Test ===")
    
    # Configure
    config.N = 4
    config.F = 1
    config.PROTOCOL = ProtocolMode.CHAINED
    config.SEED = 42
    
    # Setup
    env = Environment()
    
    # Run
    # 5 views should be enough to commit at least one block in optimal path
    # 5 seconds max virtual time
    env.run(max_time=20.0) 
    
    # Verify
    metrics = collector.get_summary()
    print(f"Metrics: {metrics}")
    
    assert metrics['total_committed'] > 0, "No blocks committed!"
    print("SUCCESS: Blocks committed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_simulation()

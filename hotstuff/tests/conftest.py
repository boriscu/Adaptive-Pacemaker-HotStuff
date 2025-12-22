"""
Pytest fixtures for HotStuff tests.
"""

import pytest

from hotstuff.config.settings import Settings
from hotstuff.domain.types.view_number import ViewNumber
from hotstuff.domain.types.replica_id import ReplicaId
from hotstuff.domain.types.block_hash import BlockHash
from hotstuff.domain.types.command import Command
from hotstuff.domain.enumerations.pacemaker_type import PacemakerType
from hotstuff.protocol.leader_scheduler import LeaderScheduler
from hotstuff.network.simulated_network import SimulatedNetwork
from hotstuff.simulation.engine import SimulationEngine
from hotstuff.factories.block_factory import BlockFactory


@pytest.fixture
def default_settings():
    """Create default simulation settings."""
    return Settings(
        num_replicas=4,
        num_faulty=1,
        base_timeout_ms=1000,
        pacemaker_type=PacemakerType.BASELINE,
        random_seed=42
    )


@pytest.fixture
def adaptive_settings():
    """Create settings with adaptive pacemaker."""
    return Settings(
        num_replicas=4,
        num_faulty=1,
        base_timeout_ms=1000,
        pacemaker_type=PacemakerType.ADAPTIVE,
        random_seed=42
    )


@pytest.fixture
def network(default_settings):
    """Create a simulated network."""
    return SimulatedNetwork(
        delay_min_ms=default_settings.network_delay_min_ms,
        delay_max_ms=default_settings.network_delay_max_ms,
        random_seed=default_settings.random_seed
    )


@pytest.fixture
def leader_scheduler(default_settings):
    """Create a leader scheduler."""
    return LeaderScheduler(default_settings.num_replicas)


@pytest.fixture
def engine(default_settings):
    """Create a simulation engine."""
    return SimulationEngine(default_settings)


@pytest.fixture
def genesis_block():
    """Create a genesis block."""
    return BlockFactory.create_genesis_block()


@pytest.fixture
def sample_block(genesis_block):
    """Create a sample block."""
    return BlockFactory.create_block(
        parent=genesis_block,
        command=Command("test_command"),
        proposer_id=ReplicaId(0),
        view_number=ViewNumber(1)
    )

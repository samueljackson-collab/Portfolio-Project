"""
Test suite for P13-ha-webapp
High Availability Web Application with failover capabilities
"""

import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md", "Dockerfile", "app.py", "ARCHITECTURE.md"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_kubernetes_manifests_exist():
    """Test that Kubernetes manifests exist."""
    k8s_dir = PROJECT_ROOT / "k8s"
    assert k8s_dir.exists(), "Missing k8s directory"


def test_docker_config_exists():
    """Test that Docker configuration exists."""
    docker_dir = PROJECT_ROOT / "docker"
    assert docker_dir.exists(), "Missing docker directory"


def test_runbooks_exist():
    """Test that runbooks exist."""
    runbooks_dir = PROJECT_ROOT / "RUNBOOKS"
    assert runbooks_dir.exists(), "Missing RUNBOOKS directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "PLAYBOOK.md").exists(), "Missing PLAYBOOK.md"
    assert (PROJECT_ROOT / "TESTING.md").exists(), "Missing TESTING.md"


class TestNodeClass:
    """Tests for Node class."""

    def test_node_creation(self):
        """Test Node instantiation."""
        from app import Node
        node = Node("test-node", healthy=True)
        assert node.name == "test-node"
        assert node.healthy is True

    def test_node_heartbeat_healthy(self):
        """Test healthy node heartbeat."""
        from app import Node
        node = Node("primary", healthy=True)
        assert "healthy" in node.heartbeat()

    def test_node_heartbeat_unhealthy(self):
        """Test unhealthy node heartbeat."""
        from app import Node
        node = Node("primary", healthy=False)
        assert "unhealthy" in node.heartbeat()


class TestFailover:
    """Tests for failover simulation."""

    def test_failover_healthy_primary(self):
        """Test failover when primary is healthy."""
        from app import Node, simulate_failover
        primary = Node("primary", healthy=True)
        replica = Node("replica", healthy=True)
        log = simulate_failover(primary, replica)
        assert any("remains on primary" in line for line in log)

    def test_failover_unhealthy_primary(self):
        """Test failover when primary fails."""
        from app import Node, simulate_failover
        primary = Node("primary", healthy=False)
        replica = Node("replica", healthy=False)
        log = simulate_failover(primary, replica)
        assert any("Promoting replica" in line for line in log)
        assert replica.healthy is True

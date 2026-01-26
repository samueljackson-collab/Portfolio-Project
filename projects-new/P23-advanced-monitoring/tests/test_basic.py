"""
Test suite for P23-advanced-monitoring
Advanced monitoring with metrics, alerting, and dashboards
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md", "ARCHITECTURE.md"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_docker_producer_exists():
    """Test that Docker producer exists."""
    producer_dir = PROJECT_ROOT / "docker" / "producer"
    assert producer_dir.exists(), "Missing docker/producer directory"


def test_consumer_exists():
    """Test that consumer worker exists."""
    consumer_dir = PROJECT_ROOT / "consumer"
    assert consumer_dir.exists(), "Missing consumer directory"


def test_jobs_directory_exists():
    """Test that jobs directory exists."""
    jobs_dir = PROJECT_ROOT / "jobs"
    assert jobs_dir.exists(), "Missing jobs directory"


def test_kubernetes_manifests_exist():
    """Test that Kubernetes manifests exist."""
    k8s_dir = PROJECT_ROOT / "k8s"
    assert k8s_dir.exists(), "Missing k8s directory"


def test_runbooks_exist():
    """Test that runbooks exist."""
    runbooks_dir = PROJECT_ROOT / "RUNBOOKS"
    assert runbooks_dir.exists(), "Missing RUNBOOKS directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "PLAYBOOK.md").exists(), "Missing PLAYBOOK.md"
    assert (PROJECT_ROOT / "TESTING.md").exists(), "Missing TESTING.md"


def test_metrics_directory_exists():
    """Test that metrics directory exists."""
    metrics_dir = PROJECT_ROOT / "METRICS"
    assert metrics_dir.exists(), "Missing METRICS directory"

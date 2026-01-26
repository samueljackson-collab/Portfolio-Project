"""
Test suite for P15-cost-optimization
Cloud cost optimization and FinOps implementation
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


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


def test_source_code_exists():
    """Test that source code directory exists."""
    src_dir = PROJECT_ROOT / "src"
    assert src_dir.exists(), "Missing src directory"


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
    assert (PROJECT_ROOT / "THREAT_MODEL.md").exists(), "Missing THREAT_MODEL.md"


def test_metrics_directory_exists():
    """Test that metrics directory exists."""
    metrics_dir = PROJECT_ROOT / "METRICS"
    assert metrics_dir.exists(), "Missing METRICS directory"


def test_sop_directory_exists():
    """Test that SOP directory exists."""
    sop_dir = PROJECT_ROOT / "SOP"
    assert sop_dir.exists(), "Missing SOP directory"

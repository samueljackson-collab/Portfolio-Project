"""
Test suite for p10-multi-region
Multi-region deployment architecture
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_terraform_exists():
    """Test that Terraform configurations exist."""
    terraform_dir = PROJECT_ROOT / "terraform"
    assert terraform_dir.exists(), "Missing terraform directory"


def test_kubernetes_exists():
    """Test that Kubernetes configurations exist."""
    k8s_dir = PROJECT_ROOT / "k8s"
    assert k8s_dir.exists(), "Missing k8s directory"


def test_runbooks_exist():
    """Test that runbooks exist."""
    runbooks_dir = PROJECT_ROOT / "RUNBOOKS"
    assert runbooks_dir.exists(), "Missing RUNBOOKS directory"


def test_consumer_exists():
    """Test that consumer exists."""
    consumer_dir = PROJECT_ROOT / "consumer"
    assert consumer_dir.exists(), "Missing consumer directory"


def test_docker_config_exists():
    """Test that Docker configuration exists."""
    docker_dir = PROJECT_ROOT / "docker"
    assert docker_dir.exists(), "Missing docker directory"

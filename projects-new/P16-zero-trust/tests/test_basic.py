"""
Test suite for P16-zero-trust
Zero Trust Architecture implementation
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


def test_infrastructure_code_exists():
    """Test that infrastructure code exists."""
    infra_dir = PROJECT_ROOT / "infra"
    assert infra_dir.exists(), "Missing infra directory"


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


def test_security_documentation():
    """Test that security documentation exists."""
    assert (PROJECT_ROOT / "RISK_REGISTER.md").exists(), "Missing RISK_REGISTER.md"
    adrs_dir = PROJECT_ROOT / "ADRS"
    assert adrs_dir.exists(), "Missing ADRS directory"

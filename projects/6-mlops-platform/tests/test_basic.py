"""
Test suite for 6-mlops-platform
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md", "requirements.txt"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_ml_configs_exist():
    """Test that ML configuration directory exists."""
    configs_dir = PROJECT_ROOT / "configs"
    assert configs_dir.exists(), "Missing configs directory"


def test_kubernetes_manifests_exist():
    """Test that Kubernetes manifests exist for ML workflows."""
    k8s_dir = PROJECT_ROOT / "k8s"
    assert k8s_dir.exists(), "Missing k8s directory"


def test_scripts_exist():
    """Test that MLOps scripts exist."""
    scripts_dir = PROJECT_ROOT / "scripts"
    assert scripts_dir.exists(), "Missing scripts directory"


def test_monitoring_config_exists():
    """Test that monitoring configurations exist."""
    assert (PROJECT_ROOT / "prometheus").exists(), "Missing prometheus directory"
    assert (PROJECT_ROOT / "grafana").exists(), "Missing grafana directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"

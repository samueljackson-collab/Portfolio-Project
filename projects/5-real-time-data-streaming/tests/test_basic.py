"""
Test suite for 5-real-time-data-streaming
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = [
        "README.md",
        "Dockerfile",
        "requirements.txt",
        "docker-compose.yml",
    ]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_flink_sql_exists():
    """Test that Flink SQL directory exists."""
    flink_dir = PROJECT_ROOT / "flink-sql"
    assert flink_dir.exists(), "Missing flink-sql directory"


def test_schemas_exist():
    """Test that schema definitions exist."""
    schemas_dir = PROJECT_ROOT / "schemas"
    assert schemas_dir.exists(), "Missing schemas directory"


def test_kubernetes_manifests_exist():
    """Test that Kubernetes manifests directory exists."""
    k8s_dir = PROJECT_ROOT / "k8s"
    assert k8s_dir.exists(), "Missing k8s directory"


def test_monitoring_config_exists():
    """Test that monitoring configurations exist."""
    assert (PROJECT_ROOT / "prometheus").exists(), "Missing prometheus directory"
    assert (PROJECT_ROOT / "grafana").exists(), "Missing grafana directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"

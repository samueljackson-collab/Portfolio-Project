"""
Test suite for 23-advanced-monitoring
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
        "docker-compose.yml",
        "requirements.txt",
    ]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_prometheus_config_exists():
    """Test that Prometheus configuration exists."""
    prometheus_dir = PROJECT_ROOT / "prometheus"
    assert prometheus_dir.exists(), "Missing prometheus directory"


def test_grafana_dashboards_exist():
    """Test that Grafana dashboards exist."""
    dashboards_dir = PROJECT_ROOT / "dashboards"
    assert dashboards_dir.exists(), "Missing dashboards directory"


def test_alertmanager_config_exists():
    """Test that AlertManager configuration exists."""
    alertmanager_dir = PROJECT_ROOT / "alertmanager"
    assert alertmanager_dir.exists(), "Missing alertmanager directory"


def test_loki_config_exists():
    """Test that Loki logging configuration exists."""
    loki_dir = PROJECT_ROOT / "loki"
    assert loki_dir.exists(), "Missing loki directory"


def test_thanos_config_exists():
    """Test that Thanos configuration exists."""
    thanos_dir = PROJECT_ROOT / "thanos"
    assert thanos_dir.exists(), "Missing thanos directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"

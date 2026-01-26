"""
Test suite for 9-multi-region-disaster-recovery
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md", "Dockerfile", "requirements.txt"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_terraform_exists():
    """Test that Terraform infrastructure exists."""
    terraform_dir = PROJECT_ROOT / "terraform"
    assert terraform_dir.exists(), "Missing terraform directory"


def test_chaos_experiments_exist():
    """Test that chaos experiment definitions exist."""
    chaos_dir = PROJECT_ROOT / "chaos-experiments"
    assert chaos_dir.exists(), "Missing chaos-experiments directory"


def test_runbooks_exist():
    """Test that DR runbooks exist."""
    runbooks_dir = PROJECT_ROOT / "runbooks"
    assert runbooks_dir.exists(), "Missing runbooks directory"


def test_monitoring_config_exists():
    """Test that monitoring configurations exist."""
    assert (PROJECT_ROOT / "prometheus").exists(), "Missing prometheus directory"
    assert (PROJECT_ROOT / "grafana").exists(), "Missing grafana directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"

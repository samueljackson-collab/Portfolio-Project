"""
Test suite for 13-advanced-cybersecurity
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


def test_source_code_exists():
    """Test that SOAR source code directory exists."""
    src_dir = PROJECT_ROOT / "src"
    assert src_dir.exists(), "Missing src directory"


def test_security_data_exists():
    """Test that security data directory exists."""
    data_dir = PROJECT_ROOT / "data"
    assert data_dir.exists(), "Missing data directory"


def test_monitoring_config_exists():
    """Test that monitoring configurations exist."""
    assert (PROJECT_ROOT / "prometheus").exists(), "Missing prometheus directory"
    assert (PROJECT_ROOT / "grafana").exists(), "Missing grafana directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"

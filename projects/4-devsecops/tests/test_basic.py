"""
Test suite for 4-devsecops
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


def test_security_pipelines_exist():
    """Test that security scanning pipeline configurations exist."""
    pipelines_dir = PROJECT_ROOT / "pipelines"
    assert pipelines_dir.exists(), "Missing pipelines directory"


def test_security_reports_dir_exists():
    """Test that security reports directory exists."""
    reports_dir = PROJECT_ROOT / "reports"
    assert reports_dir.exists(), "Missing reports directory"


def test_monitoring_config_exists():
    """Test that monitoring configurations exist."""
    assert (PROJECT_ROOT / "prometheus").exists(), "Missing prometheus directory"
    assert (PROJECT_ROOT / "grafana").exists(), "Missing grafana directory"


def test_documentation_exists():
    """Test that documentation is complete."""
    assert (PROJECT_ROOT / "RUNBOOK.md").exists(), "Missing RUNBOOK.md"
    assert (PROJECT_ROOT / "docs").exists(), "Missing docs directory"

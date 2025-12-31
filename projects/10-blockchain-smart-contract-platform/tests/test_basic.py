"""
Test suite for 10-blockchain-smart-contract-platform
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def test_basic():
    """Basic test to ensure test framework is working."""
    assert True


def test_project_structure():
    """Test that project structure contains required files."""
    required_files = ["README.md", "Dockerfile", "package.json", "hardhat.config.ts"]
    for filename in required_files:
        assert (PROJECT_ROOT / filename).exists(), f"Missing required file: {filename}"


def test_smart_contracts_exist():
    """Test that smart contracts directory exists."""
    contracts_dir = PROJECT_ROOT / "contracts"
    assert contracts_dir.exists(), "Missing contracts directory"


def test_hardhat_tests_exist():
    """Test that Hardhat test directory exists."""
    test_dir = PROJECT_ROOT / "test"
    assert test_dir.exists(), "Missing test directory for Hardhat"


def test_scripts_exist():
    """Test that deployment scripts exist."""
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

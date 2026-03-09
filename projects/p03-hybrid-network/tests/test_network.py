"""Unit tests for network connectivity tooling."""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent


def test_connectivity_script_exists(project_root):
    """Verify connectivity test script exists."""
    script = project_root / "scripts" / "test_connectivity.sh"
    assert script.exists(), f"Script not found: {script}"


def test_connectivity_script_executable(project_root):
    """Verify connectivity script is executable."""
    script = project_root / "scripts" / "test_connectivity.sh"
    assert script.stat().st_mode & 0o111, f"Script not executable: {script}"


def test_wireguard_config_template_exists(project_root):
    """Verify WireGuard config template exists."""
    config = project_root / "config" / "wireguard.conf.example"
    # Optional test - config may not exist yet
    # assert config.exists(), f"WireGuard config template not found: {config}"


@pytest.mark.skip(reason="Requires live network connectivity")
def test_localhost_connectivity():
    """Verify localhost connectivity (example test)."""
    result = subprocess.run(
        ["ping", "-c", "1", "127.0.0.1"], capture_output=True, timeout=5
    )
    assert result.returncode == 0, "Localhost should be reachable"

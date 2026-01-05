"""Smoke tests for Advanced Monitoring project."""

from src.health_check import run_health_check


def test_health_check_passes():
    """Ensure core assets are present for readiness."""
    result = run_health_check()
    assert result["status"] == "ok", result

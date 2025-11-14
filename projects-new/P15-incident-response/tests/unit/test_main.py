"""
Unit tests for main module.
"""

from src.main import health_check


def test_health_check():
    """Test health check returns expected structure."""
    result = health_check()

    assert "status" in result
    assert "version" in result
    assert result["status"] == "healthy"

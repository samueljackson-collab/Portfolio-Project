"""Health check tests for 4-devsecops."""
from src.health_check import check_health


def test_health_check_unit():
    """Unit test the health check payload structure."""
    result = check_health()
    assert result["status"] == "ok"
    assert result["project"] == "4-devsecops"


def test_health_check_smoke():
    """Smoke test the health check timestamp payload."""
    result = check_health()
    assert "timestamp" in result

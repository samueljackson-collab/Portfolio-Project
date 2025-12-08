"""Lightweight tests to validate the scaffolded service module."""
import service


def test_health_check_contains_status_and_metadata():
    result = service.health_check()
    assert result["status"] == "ok"
    assert result["name"] == "cloud-architecture"
    assert "owner" in result and "description" in result

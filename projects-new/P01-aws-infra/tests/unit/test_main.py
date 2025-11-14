"""Unit-level tests for FastAPI application utilities."""

from src.config import get_settings, reset_settings_cache
from src.main import HealthResponse, health


def test_health_handler_uses_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    reset_settings_cache()
    settings = get_settings()

    result: HealthResponse = health(settings=settings)

    assert result.status == "healthy"
    assert result.environment == "staging"

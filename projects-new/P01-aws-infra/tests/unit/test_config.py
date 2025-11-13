"""Unit tests for configuration helpers."""

from src.config import get_settings, reset_settings_cache


def test_settings_loaded_from_env(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test App")
    monkeypatch.setenv("ENVIRONMENT", "stage")
    monkeypatch.setenv("API_KEYS", "one,two")
    reset_settings_cache()

    settings = get_settings()

    assert settings.app_name == "Test App"
    assert settings.environment == "stage"
    assert settings.api_keys == ["one", "two"]

    # Cleanup for other tests
    reset_settings_cache()

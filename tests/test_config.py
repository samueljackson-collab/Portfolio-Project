"""Tests for configuration utilities."""

from twistedmonk.config import AppConfig, load_config


def test_default_config_values(monkeypatch):
    """Configuration should provide sensible defaults when env vars are missing."""

    for env_var in (
        "TWISTEDMONK_ENV",
        "TWISTEDMONK_LOG_LEVEL",
        "TWISTEDMONK_TZ",
        "TWISTEDMONK_SECRETS_BACKEND",
        "TWISTEDMONK_FEATURE_FLAGS",
    ):
        monkeypatch.delenv(env_var, raising=False)

    load_config.cache_clear()
    config = load_config()

    assert isinstance(config, AppConfig)
    assert config.environment == "development"
    assert config.log_level == "INFO"
    assert config.default_timezone == "UTC"
    assert config.secrets_backend == "env"
    assert config.flags == tuple()


def test_feature_flag_parsing(monkeypatch):
    """Feature flags should be normalized to a tuple of trimmed values."""

    monkeypatch.setenv("TWISTEDMONK_FEATURE_FLAGS", "alpha,beta , gamma")

    load_config.cache_clear()
    config = load_config()

    assert config.flags == ("alpha", "beta", "gamma")

    load_config.cache_clear()
    monkeypatch.delenv("TWISTEDMONK_FEATURE_FLAGS", raising=False)

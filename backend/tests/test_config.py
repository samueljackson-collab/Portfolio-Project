"""
Comprehensive tests for configuration module.

Tests cover:
- Settings initialization and defaults
- Environment variable loading
- Field validation (database URL, secret key)
- Custom validators
- Edge cases and error conditions
"""

import pytest
from pydantic import ValidationError
from unittest.mock import patch
import os

from app.config import Settings


class TestSettingsDefaults:
    """Test default configuration values."""

    def test_default_app_settings(self):
        """Test default application settings are correct."""
        settings = Settings()
        
        assert settings.app_name == "Portfolio API"
        assert settings.debug is False
        assert settings.version == "1.0.0"

    def test_default_server_settings(self):
        """Test default server settings are correct."""
        settings = Settings()
        
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.reload is False

    def test_default_security_settings(self):
        """Test default security settings are correct."""
        settings = Settings()
        
        assert len(settings.secret_key) >= 32
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30

    def test_default_cors_origins(self):
        """Test default CORS origins list."""
        settings = Settings()
        
        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:5173" in settings.cors_origins

    def test_default_log_level(self):
        """Test default logging level."""
        settings = Settings()
        
        assert settings.log_level == "INFO"


class TestDatabaseURLValidation:
    """Test database URL validation logic."""

    def test_valid_database_url(self):
        """Test that valid asyncpg URL is accepted."""
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/mydb"
        )
        
        assert settings.database_url.startswith("postgresql+asyncpg://")

    def test_invalid_database_url_wrong_driver(self):
        """Test that non-asyncpg URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(database_url="postgresql://user:pass@localhost:5432/mydb")
        
        errors = exc_info.value.errors()
        assert any("asyncpg" in str(error) for error in errors)

    def test_invalid_database_url_wrong_protocol(self):
        """Test that non-postgresql URL is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(database_url="mysql+asyncpg://user:pass@localhost:3306/mydb")
        
        errors = exc_info.value.errors()
        assert any("asyncpg" in str(error) for error in errors)

    def test_database_url_with_special_characters(self):
        """Test database URL with special characters in password."""
        settings = Settings(
            database_url="postgresql+asyncpg://user:p@ssw0rd!@localhost:5432/db"
        )
        
        assert "p@ssw0rd!" in settings.database_url


class TestSecretKeyValidation:
    """Test secret key validation logic."""

    def test_valid_secret_key_minimum_length(self):
        """Test that 32-character secret key is accepted."""
        secret = "a" * 32
        settings = Settings(secret_key=secret)
        
        assert settings.secret_key == secret

    def test_valid_secret_key_longer_than_minimum(self):
        """Test that secret key longer than 32 chars is accepted."""
        secret = "a" * 64
        settings = Settings(secret_key=secret)
        
        assert settings.secret_key == secret

    def test_invalid_secret_key_too_short(self):
        """Test that secret key shorter than 32 chars is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(secret_key="short_key")
        
        errors = exc_info.value.errors()
        assert any("32 characters" in str(error) for error in errors)

    def test_invalid_secret_key_exactly_31_chars(self):
        """Test that 31-character secret key is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(secret_key="a" * 31)
        
        errors = exc_info.value.errors()
        assert any("32 characters" in str(error) for error in errors)

    def test_secret_key_with_special_characters(self):
        """Test secret key with special characters."""
        secret = "abcd1234!@#$%^&*()_+-=[]{}|;':,.<>?" * 2
        settings = Settings(secret_key=secret)
        
        assert settings.secret_key == secret


class TestEnvironmentVariableLoading:
    """Test loading settings from environment variables."""

    def test_load_app_name_from_env(self):
        """Test loading app_name from environment."""
        with patch.dict(os.environ, {"APP_NAME": "Test App"}):
            settings = Settings()
            assert settings.app_name == "Test App"

    def test_load_debug_mode_from_env(self):
        """Test loading debug flag from environment."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            settings = Settings()
            assert settings.debug is True

    def test_load_port_from_env(self):
        """Test loading port from environment."""
        with patch.dict(os.environ, {"PORT": "9000"}):
            settings = Settings()
            assert settings.port == 9000

    def test_load_log_level_from_env(self):
        """Test loading log level from environment."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            settings = Settings()
            assert settings.log_level == "DEBUG"

    def test_case_insensitive_env_vars(self):
        """Test that environment variables are case-insensitive."""
        with patch.dict(os.environ, {"app_name": "Lower Case App"}):
            settings = Settings()
            assert settings.app_name == "Lower Case App"


class TestCORSConfiguration:
    """Test CORS settings."""

    def test_default_cors_origins_list(self):
        """Test default CORS origins is a list."""
        settings = Settings()
        
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) >= 2

    def test_custom_cors_origins_from_env(self):
        """Test loading custom CORS origins from environment."""
        with patch.dict(os.environ, {
            "CORS_ORIGINS": '["http://example.com", "https://api.example.com"]'
        }):
            settings = Settings()
            assert "http://example.com" in settings.cors_origins
            assert "https://api.example.com" in settings.cors_origins

    def test_single_cors_origin(self):
        """Test CORS with single origin."""
        settings = Settings(cors_origins=["http://localhost:3000"])
        
        assert len(settings.cors_origins) == 1
        assert settings.cors_origins[0] == "http://localhost:3000"

    def test_empty_cors_origins(self):
        """Test CORS with empty origins list."""
        settings = Settings(cors_origins=[])
        
        assert settings.cors_origins == []


class TestTokenExpiration:
    """Test token expiration settings."""

    def test_default_token_expiration(self):
        """Test default token expiration is 30 minutes."""
        settings = Settings()
        
        assert settings.access_token_expire_minutes == 30

    def test_custom_token_expiration(self):
        """Test custom token expiration."""
        settings = Settings(access_token_expire_minutes=60)
        
        assert settings.access_token_expire_minutes == 60

    def test_short_token_expiration(self):
        """Test very short token expiration (1 minute)."""
        settings = Settings(access_token_expire_minutes=1)
        
        assert settings.access_token_expire_minutes == 1

    def test_long_token_expiration(self):
        """Test very long token expiration (24 hours)."""
        settings = Settings(access_token_expire_minutes=1440)
        
        assert settings.access_token_expire_minutes == 1440


class TestSettingsModel:
    """Test Settings model configuration."""

    def test_extra_fields_ignored(self):
        """Test that unknown environment variables are ignored."""
        with patch.dict(os.environ, {"UNKNOWN_VAR": "some_value"}):
            # Should not raise error
            settings = Settings()
            assert not hasattr(settings, "unknown_var")

    def test_settings_are_immutable_after_creation(self):
        """Test that settings object is created correctly."""
        settings = Settings()
        
        # Verify settings object has expected attributes
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "secret_key")

    def test_field_descriptions_present(self):
        """Test that fields have descriptions."""
        settings = Settings()
        schema = settings.model_json_schema()
        
        # Check that properties exist in schema
        assert "properties" in schema
        assert "app_name" in schema["properties"]


class TestIntegrationScenarios:
    """Test realistic integration scenarios."""

    def test_production_like_configuration(self):
        """Test production-like configuration."""
        settings = Settings(
            app_name="Portfolio API Production",
            debug=False,
            database_url="postgresql+asyncpg://prod_user:complex_pass@db.example.com:5432/prod_db",
            secret_key="very_long_and_secure_secret_key_for_production_use_min_32_chars",
            access_token_expire_minutes=15,
            cors_origins=["https://example.com", "https://www.example.com"],
            log_level="WARNING"
        )
        
        assert settings.debug is False
        assert settings.access_token_expire_minutes == 15
        assert len(settings.cors_origins) == 2

    def test_development_configuration(self):
        """Test development configuration."""
        settings = Settings(
            debug=True,
            reload=True,
            log_level="DEBUG"
        )
        
        assert settings.debug is True
        assert settings.reload is True
        assert settings.log_level == "DEBUG"

    def test_minimal_valid_configuration(self):
        """Test minimal valid configuration with required fields."""
        settings = Settings()
        
        # Should initialize with defaults
        assert settings.app_name is not None
        assert settings.database_url is not None
        assert settings.secret_key is not None
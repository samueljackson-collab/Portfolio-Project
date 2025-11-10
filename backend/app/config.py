"""
Application configuration management.

This module uses Pydantic Settings to load and validate environment variables.
Configuration is loaded from .env file and system environment.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have defaults except sensitive values (SECRET_KEY, DATABASE_URL)
    which must be provided via environment variables.
    """

    # Application Settings
    app_name: str = Field(default="Portfolio API", description="Application name")
    debug: bool = Field(default=False, description="Debug mode flag")
    version: str = Field(default="1.0.0", description="API version")

    # Server Settings
    host: str = Field(default="0.0.0.0", description="Server bind address")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    # Database Settings
    database_url: str = Field(
        default="postgresql+asyncpg://portfolio_user:securepassword@localhost:5432/portfolio_db",
        description="PostgreSQL connection URL",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/dbname"]
    )

    # Security Settings
    secret_key: str = Field(
        default="development-secret-key-change-in-production-min-32-chars",
        min_length=32,
        description="Secret key for JWT tokens (min 32 characters)"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT token expiration in minutes"
    )

    # CORS Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )

    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Validate that a database URL uses the asyncpg PostgreSQL driver.
        
        Parameters:
            v (str): Database URL to validate.
        
        Returns:
            str: The same database URL if it starts with "postgresql+asyncpg://".
        
        Raises:
            ValueError: If the URL does not start with "postgresql+asyncpg://".
        """
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use asyncpg driver: "
                "postgresql+asyncpg://user:pass@host:port/dbname"
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        Validate that the provided secret key meets the minimum length requirement.
        
        Parameters:
            v (str): Secret key value to validate.
        
        Returns:
            str: The validated secret key.
        
        Raises:
            ValueError: If `v` is shorter than 32 characters.
        """
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore unknown environment variables
    )


# Global settings instance
settings = Settings()
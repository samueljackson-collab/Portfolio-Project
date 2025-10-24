"""Application configuration management."""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = Field(default="Portfolio API", description="Application name")
    debug: bool = Field(default=False, description="Debug mode flag")
    testing: bool = Field(default=False, description="Testing mode flag")
    version: str = Field(default="1.0.0", description="API version")

    host: str = Field(default="0.0.0.0", description="Server bind address")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    database_url: str = Field(
        ..., description="PostgreSQL connection URL",
        examples=["postgresql+asyncpg://user:pass@localhost:5432/dbname"],
    )

    secret_key: str = Field(
        ..., min_length=32, description="Secret key for JWT tokens (min 32 characters)"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="JWT token expiration in minutes"
    )

    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    log_level: str = Field(default="INFO", description="Logging level")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        allowed_prefixes = ("postgresql+asyncpg://", "sqlite+aiosqlite://")
        if not value.startswith(allowed_prefixes):
            raise ValueError(
                "DATABASE_URL must use asyncpg (PostgreSQL) or aiosqlite drivers"
            )
        return value

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

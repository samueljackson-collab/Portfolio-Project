from functools import lru_cache
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    shopify_store_domain: str = Field(..., env="SHOPIFY_STORE_DOMAIN")
    shopify_access_token: str = Field(..., env="SHOPIFY_ACCESS_TOKEN")
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: str = Field("", env="REDIS_PASSWORD")
    allowed_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    api_rate_limit: int = Field(100, env="API_RATE_LIMIT")
    environment: str = Field("production", env="ENVIRONMENT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()

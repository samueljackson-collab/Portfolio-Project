from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PORTFOLIO_", env_file=".env", extra="ignore")

    env: str = "development"
    telemetry_endpoint: str = "https://telemetry.example.com"


@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache
from typing import List

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Portfolio API"
    debug: bool = True
    database_url: AnyUrl = Field(
        "postgresql+asyncpg://postgres:postgres@db:5432/portfolio", env="DATABASE_URL"
    )
    secret_key: str = Field("super-secret-key", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache

def get_settings() -> Settings:
    return Settings()


settings = get_settings()

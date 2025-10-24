from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field("portfolio-backend", env="APP_NAME")
    environment: str = Field("local", env="ENVIRONMENT")
    database_url: str = Field(..., env="DATABASE_URL")
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
Configuration management using Pydantic settings.
Loads environment variables with validation and type checking.

SECURITY WARNING: The default values below are for development only.
In production, always override these using environment variables:
- DATABASE_URL: Connection string for your production database
- SECRET_KEY: Strong randomly-generated secret (use: openssl rand -hex 32)
- Other sensitive configuration values

Never commit production secrets to version control!
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # WARNING: Development defaults only - override in production!
    DATABASE_URL: str = "postgresql://portfolio:portfolio_dev_pass@postgres:5432/portfolio"
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

"""
Configuration module for Twisted Monk Suite.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Twisted Monk Suite"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Redis Cache
    REDIS_ENABLED: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    CACHE_TTL: int = 3600  # 1 hour default
    
    # Database (for future use)
    DATABASE_URL: str = "sqlite:///./twisted_monk.db"
    
    # API Keys
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_API_SECRET: str = ""
    SHOPIFY_SHOP_URL: str = ""
    
    # Notifications
    SLACK_WEBHOOK_URL: str = ""
    EMAIL_SMTP_HOST: str = "smtp.gmail.com"
    EMAIL_SMTP_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = "alerts@twistedmonk.com"
    EMAIL_TO: List[str] = []
    
    # Inventory thresholds
    LOW_STOCK_THRESHOLD: int = 50
    CRITICAL_STOCK_THRESHOLD: int = 10
    
    # Lead time defaults
    DEFAULT_LEAD_TIME_DAYS: int = 7
    MAX_LEAD_TIME_DAYS: int = 60
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL from components."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @validator('ALLOWED_ORIGINS', 'ALLOWED_HOSTS', 'EMAIL_TO', pre=True)
    def parse_list_from_string(cls, v):
        """Parse comma-separated string into list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    @validator('DEBUG', 'REDIS_ENABLED', pre=True)
    def parse_bool(cls, v):
        """Parse boolean from string."""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()

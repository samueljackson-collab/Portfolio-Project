"""Application configuration helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Dict, List

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime configuration loaded from the environment."""

    app_name: str = Field(default="AWS Infrastructure Automation")
    environment: str = Field(default="development")
    aws_region: str = Field(default="us-east-1")
    api_keys: Set[str] = Field(default_factory=lambda: {"local-dev-key"})
    metrics_namespace: str = Field(default="aws_infra")
    feature_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "enable_telemetry": False,
            "enforce_rate_limiting": False,
        }
    )

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings using environment variables with sane defaults."""

        api_keys_env = os.getenv("API_KEYS")
        api_keys = [key.strip() for key in api_keys_env.split(",") if key.strip()] if api_keys_env else ["local-dev-key"]

        feature_flags = {
            "enable_telemetry": os.getenv("FEATURE_ENABLE_TELEMETRY", "false").lower() == "true",
            "enforce_rate_limiting": os.getenv("FEATURE_ENFORCE_RATE_LIMITING", "false").lower() == "true",
        }

        return cls(
            app_name=os.getenv("APP_NAME", "AWS Infrastructure Automation"),
            environment=os.getenv("ENVIRONMENT", "development"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            api_keys=api_keys,
            metrics_namespace=os.getenv("METRICS_NAMESPACE", "aws_infra"),
            feature_flags=feature_flags,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings.from_env()


def reset_settings_cache() -> None:
    """Clear cached settings for tests."""

    get_settings.cache_clear()

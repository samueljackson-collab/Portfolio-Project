"""Configuration loading for TwistedMonk services."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration loaded from environment variables."""

    environment: str = "development"
    log_level: str = "INFO"
    default_timezone: str = "UTC"
    secrets_backend: str = "env"
    feature_flags: Optional[str] = None

    @property
    def flags(self) -> tuple[str, ...]:
        """Expose feature flags as a normalized tuple."""
        if not self.feature_flags:
            return tuple()
        return tuple(flag.strip() for flag in self.feature_flags.split(",") if flag.strip())


@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    """Load the configuration from environment variables, caching the result."""

    return AppConfig(
        environment=os.getenv("TWISTEDMONK_ENV", "development"),
        log_level=os.getenv("TWISTEDMONK_LOG_LEVEL", "INFO"),
        default_timezone=os.getenv("TWISTEDMONK_TZ", "UTC"),
        secrets_backend=os.getenv("TWISTEDMONK_SECRETS_BACKEND", "env"),
        feature_flags=os.getenv("TWISTEDMONK_FEATURE_FLAGS"),
    )


__all__ = ["AppConfig", "load_config"]

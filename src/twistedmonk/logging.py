"""Logging helpers shared across TwistedMonk services."""

from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Any, Dict, Optional

from .config import load_config


DEFAULT_LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


def configure_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """Configure application logging using the shared defaults."""

    merged = dict(DEFAULT_LOGGING_CONFIG)
    if config:
        merged.update(config)

    runtime_config = load_config()
    merged.setdefault("root", {})
    merged["root"].setdefault("level", runtime_config.log_level)
    dictConfig(merged)

    logging.getLogger(__name__).debug("Logging configured with level %s", runtime_config.log_level)


__all__ = ["configure_logging", "DEFAULT_LOGGING_CONFIG"]

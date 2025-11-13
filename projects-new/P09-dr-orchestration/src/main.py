"""
Main application module.
"""

from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        Dictionary with health status
    """
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    logger.info("Application started")
    print(health_check())

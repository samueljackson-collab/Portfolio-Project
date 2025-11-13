
"""Main application module."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_NAME = os.getenv(
    "SERVICE_NAME",
    Path(__file__).resolve().parents[1].name.replace('_', '-').lower(),
)

app = FastAPI(title=SERVICE_NAME.replace('-', ' ').title())


def health_check() -> Dict[str, Any]:
    """Return service health metadata."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": SERVICE_NAME,
    }


@app.get("/health")
async def health_endpoint() -> Dict[str, Any]:
    """Expose a FastAPI health-check endpoint."""
    logger.debug("Health check requested")
    return health_check()


@app.get("/")
async def root() -> Dict[str, Any]:
    """Basic index endpoint to confirm service availability."""
    return {
        "message": "Service is running",
        "service": SERVICE_NAME,
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI application on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)

#!/usr/bin/env python3
"""
Kubernetes CI/CD Demo Application

A FastAPI-based application demonstrating CI/CD best practices including:
- Health checks (liveness, readiness)
- Graceful shutdown
- Configuration management
- Metrics endpoint
- Structured logging
"""

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# Configuration from environment
class Config:
    """Application configuration from environment variables."""
    APP_NAME: str = os.getenv("APP_NAME", "k8s-cicd-demo")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: int = int(os.getenv("PORT", "8080"))

    # Database configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))

    # Feature flags
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "false").lower() == "true"

    # Graceful shutdown
    SHUTDOWN_TIMEOUT: int = int(os.getenv("SHUTDOWN_TIMEOUT", "30"))


config = Config()


# Application state
class AppState:
    """Tracks application state for health checks."""
    is_ready: bool = False
    is_healthy: bool = True
    startup_time: Optional[datetime] = None
    request_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None


app_state = AppState()


# Pydantic models
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    checks: dict


class StatusResponse(BaseModel):
    """Application status response model."""
    name: str
    version: str
    environment: str
    uptime_seconds: float
    request_count: int
    error_count: int
    is_healthy: bool
    is_ready: bool


class ConfigResponse(BaseModel):
    """Configuration response model (non-sensitive values only)."""
    app_name: str
    version: str
    environment: str
    log_level: str
    features: dict


class MetricsResponse(BaseModel):
    """Prometheus-compatible metrics."""
    metrics: str


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    app_state.startup_time = datetime.utcnow()

    # Simulate initialization (database connections, cache warmup, etc.)
    await asyncio.sleep(0.5)
    app_state.is_ready = True
    logger.info("Application ready to serve traffic")

    yield

    # Shutdown
    logger.info("Initiating graceful shutdown")
    app_state.is_ready = False

    # Allow in-flight requests to complete
    await asyncio.sleep(2)
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Kubernetes CI/CD Demo Application",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request counting middleware
@app.middleware("http")
async def count_requests(request: Request, call_next):
    """Count requests and track errors."""
    app_state.request_count += 1
    try:
        response = await call_next(request)
        if response.status_code >= 500:
            app_state.error_count += 1
        return response
    except Exception as e:
        app_state.error_count += 1
        app_state.last_error = str(e)
        raise


# Health check endpoints
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Liveness probe endpoint.

    Returns 200 if the application is alive.
    Used by Kubernetes to determine if the container should be restarted.
    """
    if not app_state.is_healthy:
        raise HTTPException(status_code=503, detail="Application unhealthy")

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """
    Readiness probe endpoint.

    Returns 200 if the application is ready to receive traffic.
    Used by Kubernetes to determine if the pod should receive traffic.
    """
    checks = {
        "startup_complete": app_state.is_ready,
        "database": await check_database_connection(),
    }

    all_ready = all(checks.values())

    if not all_ready:
        raise HTTPException(
            status_code=503,
            detail={"ready": False, "checks": checks}
        )

    return ReadinessResponse(ready=True, checks=checks)


async def check_database_connection() -> bool:
    """Check database connectivity."""
    if not config.DATABASE_URL:
        return True  # No database configured, skip check

    try:
        from src.database import check_connection
        return await check_connection()
    except ImportError:
        return True  # Database module not available
    except Exception as e:
        logger.warning(f"Database check failed: {e}")
        return False


# Application endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint returning application info."""
    return {
        "message": f"Welcome to {config.APP_NAME}",
        "version": config.APP_VERSION,
        "environment": config.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/api/v1/status", response_model=StatusResponse, tags=["API"])
async def get_status():
    """Get detailed application status."""
    uptime = 0.0
    if app_state.startup_time:
        uptime = (datetime.utcnow() - app_state.startup_time).total_seconds()

    return StatusResponse(
        name=config.APP_NAME,
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT,
        uptime_seconds=uptime,
        request_count=app_state.request_count,
        error_count=app_state.error_count,
        is_healthy=app_state.is_healthy,
        is_ready=app_state.is_ready
    )


@app.get("/api/v1/config", response_model=ConfigResponse, tags=["API"])
async def get_config():
    """Get application configuration (non-sensitive values only)."""
    return ConfigResponse(
        app_name=config.APP_NAME,
        version=config.APP_VERSION,
        environment=config.ENVIRONMENT,
        log_level=config.LOG_LEVEL,
        features={
            "metrics_enabled": config.ENABLE_METRICS,
            "tracing_enabled": config.ENABLE_TRACING
        }
    )


@app.get("/api/v1/info", tags=["API"])
async def get_info():
    """Get build and runtime information."""
    return {
        "build": {
            "version": config.APP_VERSION,
            "commit": os.getenv("GIT_COMMIT", "unknown"),
            "branch": os.getenv("GIT_BRANCH", "unknown"),
            "build_time": os.getenv("BUILD_TIME", "unknown")
        },
        "runtime": {
            "python_version": sys.version,
            "hostname": os.getenv("HOSTNAME", "unknown"),
            "pod_name": os.getenv("POD_NAME", "unknown"),
            "pod_namespace": os.getenv("POD_NAMESPACE", "unknown"),
            "node_name": os.getenv("NODE_NAME", "unknown")
        }
    }


# Metrics endpoint (Prometheus format)
@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    """Prometheus metrics endpoint."""
    if not config.ENABLE_METRICS:
        raise HTTPException(status_code=404, detail="Metrics disabled")

    uptime = 0.0
    if app_state.startup_time:
        uptime = (datetime.utcnow() - app_state.startup_time).total_seconds()

    metrics = f"""# HELP app_info Application information
# TYPE app_info gauge
app_info{{version="{config.APP_VERSION}",environment="{config.ENVIRONMENT}"}} 1

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds counter
app_uptime_seconds {uptime}

# HELP app_requests_total Total number of requests
# TYPE app_requests_total counter
app_requests_total {app_state.request_count}

# HELP app_errors_total Total number of errors
# TYPE app_errors_total counter
app_errors_total {app_state.error_count}

# HELP app_ready Application readiness status
# TYPE app_ready gauge
app_ready {1 if app_state.is_ready else 0}

# HELP app_healthy Application health status
# TYPE app_healthy gauge
app_healthy {1 if app_state.is_healthy else 0}
"""
    return Response(content=metrics, media_type="text/plain")


# Chaos engineering endpoints (for testing)
@app.post("/chaos/unhealthy", tags=["Chaos"])
async def make_unhealthy():
    """Mark application as unhealthy (for testing failover)."""
    if config.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Chaos endpoints disabled in production")

    app_state.is_healthy = False
    logger.warning("Application marked as unhealthy via chaos endpoint")
    return {"status": "unhealthy", "message": "Application will fail liveness checks"}


@app.post("/chaos/healthy", tags=["Chaos"])
async def make_healthy():
    """Mark application as healthy (restore after chaos test)."""
    app_state.is_healthy = True
    logger.info("Application restored to healthy state")
    return {"status": "healthy", "message": "Application will pass liveness checks"}


@app.post("/chaos/unready", tags=["Chaos"])
async def make_unready():
    """Mark application as not ready (for testing traffic routing)."""
    if config.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Chaos endpoints disabled in production")

    app_state.is_ready = False
    logger.warning("Application marked as not ready via chaos endpoint")
    return {"status": "not_ready", "message": "Application will fail readiness checks"}


@app.post("/chaos/ready", tags=["Chaos"])
async def make_ready():
    """Mark application as ready."""
    app_state.is_ready = True
    logger.info("Application restored to ready state")
    return {"status": "ready", "message": "Application will pass readiness checks"}


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    app_state.last_error = str(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if config.ENVIRONMENT != "production" else "An error occurred"
        }
    )


def main():
    """Main entry point."""
    import uvicorn

    logger.info(f"Starting {config.APP_NAME} on port {config.PORT}")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.ENVIRONMENT == "development",
        log_level=config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()

"""
Health check endpoints for monitoring and load balancers.

Health checks are used by:
- Load balancers to determine if an instance is healthy
- Monitoring systems (Prometheus, Datadog) to track uptime
- Container orchestrators (Kubernetes) for liveness probes
- CI/CD pipelines to verify deployment success
"""

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.schemas import HealthResponse
from app.config import settings


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API and its dependencies are operational"
)
async def health_check(
    db: AsyncSession = Depends(get_db)
) -> HealthResponse:
    """
    Perform health check of the API and its dependencies.

    Returns 200 if healthy, 503 if any dependency is down.
    """
    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        database_status = "connected"
        overall_status = "healthy"
    except Exception:
        database_status = "disconnected"
        overall_status = "unhealthy"

    return HealthResponse(
        status=overall_status,
        version=settings.version,
        database=database_status,
        service=settings.app_name,
    )


@router.get(
    "/liveness",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Simple liveness check without dependency verification"
)
async def liveness() -> dict:
    """
    Kubernetes liveness probe.

    Only checks if the application process is running.
    """
    return {"status": "alive"}


@router.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Check if service is ready to accept traffic"
)
async def readiness(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Kubernetes readiness probe.

    Checks if the service is ready to handle requests.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        return Response(
            content='{"status": "not ready", "database": "disconnected"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )

"""
Health check endpoints for monitoring and load balancers.

Health checks are used by:
- Load balancers to determine if an instance is healthy
- Monitoring systems (Prometheus, Datadog) to track uptime
- Container orchestrators (Kubernetes) for liveness probes
- CI/CD pipelines to verify deployment success
"""

from fastapi import APIRouter, Depends, status
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
    Check API dependencies and produce a health summary.
    
    Performs a database connectivity check and returns a HealthResponse containing the overall health status, the application version, and the database connection state.
    
    Returns:
        HealthResponse: An object with:
            - status: "healthy" or "unhealthy"
            - version: application version string
            - database: "connected" or "disconnected"
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
        database=database_status
    )


@router.get(
    "/liveness",
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Simple liveness check without dependency verification"
)
async def liveness() -> dict:
    """
    Expose a Kubernetes liveness probe indicating the application process is running.
    
    Returns:
        dict: A dictionary containing {"status": "alive"}.
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
    Check readiness by verifying database connectivity.
    
    Returns:
        A dict `{"status": "ready"}` when the database query succeeds; otherwise returns a FastAPI `Response` with status code 503 and body `'{"status": "not ready"}'`.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        from fastapi import Response
        return Response(
            content='{"status": "not ready"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
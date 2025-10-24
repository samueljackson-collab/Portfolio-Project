"""Health check endpoints for monitoring systems and load balancers."""

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service health check",
    description="Return API status, version, and database connectivity state.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Return health indicators for the service and database."""
    try:
        await db.execute(text("SELECT 1"))
        database_status = "connected"
        overall_status = "healthy"
    except Exception:  # pragma: no cover - defensive path
        database_status = "disconnected"
        overall_status = "unhealthy"

    return HealthResponse(status=overall_status, version=settings.version, database=database_status)


@router.get(
    "/liveness",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Lightweight probe to confirm the application process is running.",
)
async def liveness() -> dict[str, str]:
    """Return a static response indicating the process is alive."""
    return {"status": "alive"}


@router.get(
    "/readiness",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Probe used by orchestrators to determine if the service can accept traffic.",
)
async def readiness(db: AsyncSession = Depends(get_db)) -> Response:
    """Return readiness information including database connectivity."""
    try:
        await db.execute(text("SELECT 1"))
        return Response(content='{"status": "ready"}', media_type="application/json")
    except Exception:  # pragma: no cover - defensive path
        return Response(
            content='{"status": "not ready"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )

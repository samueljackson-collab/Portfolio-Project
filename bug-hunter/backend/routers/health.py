import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from config import APP_VERSION
from database import AsyncSessionLocal

logger = logging.getLogger("bughunter.health")
router = APIRouter()


@router.get("/health")
async def health():
    """Liveness + readiness probe: verifies the database is reachable."""
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.error("Health check: database unreachable — %s", exc)
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "version": APP_VERSION, "db": "error"},
        )

    return {"status": "ok", "version": APP_VERSION, "db": db_status}

"""
Health check endpoint for monitoring and load balancer health checks.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db


router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    Returns 200 OK if service and database are healthy.
    """
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "backend",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "backend",
            "database": "disconnected",
            "error": str(e)
        }

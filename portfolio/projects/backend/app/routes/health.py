from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "environment": settings.env}

from fastapi import APIRouter

from .routes import auth, content, health

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(content.router)

__all__ = ["api_router"]

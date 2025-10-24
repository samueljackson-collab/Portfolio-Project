"""API router registration."""
from __future__ import annotations

from fastapi import APIRouter

from . import auth, content, health

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(health.router, tags=["health"])

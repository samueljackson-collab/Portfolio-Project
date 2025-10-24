from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, content, health

app = FastAPI(title="Portfolio Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(content.router, prefix="/content", tags=["content"])
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root() -> dict[str, str]:
    """Simple landing endpoint used by smoke tests."""

    return {"message": "Portfolio backend is running"}

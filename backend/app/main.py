"""Application entry-point for the FastAPI backend."""
from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .api import auth, items, users
from .db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio API", version="1.0.0", description="Backend API for the portfolio project.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myportfolio.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(items.router, prefix="/items", tags=["Items"])


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Simple health endpoint for uptime monitoring."""
    return {"status": "ok"}

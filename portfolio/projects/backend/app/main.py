from fastapi import FastAPI

from app.core.config import get_settings
from app.routes.health import router as health_router
from app.routes.projects import router as projects_router

settings = get_settings()

app = FastAPI(
    title="Portfolio API",
    version="0.1.0",
    description="Backend service powering the portfolio platform.",
)

app.include_router(health_router)
app.include_router(projects_router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "message": "Portfolio API",
        "documentation": "/docs",
        "telemetry": settings.telemetry_endpoint,
    }

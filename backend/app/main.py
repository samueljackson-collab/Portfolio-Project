"""FastAPI application instance and configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db
from app.routers import auth, content, health


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    app = FastAPI(title=settings.app_name, version=settings.version, debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(content.router)

    if not settings.testing:
        @app.on_event("startup")
        async def on_startup() -> None:
            await init_db()

        @app.on_event("shutdown")
        async def on_shutdown() -> None:
            await close_db()

    return app


app = create_application()

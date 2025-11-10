"""
FastAPI application entry point with CORS, middleware, and router registration.
Provides REST API for authentication and content management.
"""
import os
import time
import logging
from typing import Callable
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.requests import Request as StarletteRequest

from app.routers import auth, content, health
from app.database import engine, Base

# Register local logger
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Portfolio Backend API",
    description="REST API for portfolio content management",
    version="1.4.0",
    lifespan=lifespan,
)

# CORS middleware: use environment variable for allowed origins (comma-separated)
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register timing middleware and exception handlers from separate modules
# See app.middleware.timing and app.exception_handlers for implementations
try:
    from app.middleware.timing import timing_middleware
    from app.exception_handlers import (
        http_exception_handler,
        validation_exception_handler,
        generic_exception_handler,
    )

    app.middleware("http")(timing_middleware)
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException

    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
except Exception:
    # If imports fail at startup, log and continue; handlers/middleware will be skipped.
    logger.exception("Optional middleware/exception handlers could not be registered")

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(content.router, prefix="/api/content", tags=["content"])
import logging
import time
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from config import CORS_ORIGINS, APP_VERSION, DEBUG, DATA_DIR
from database import init_db
from limiter import limiter
from routers import health as health_router
from routers import scan as scan_router
from routers import reports as reports_router


# ── Logging ────────────────────────────────────────────────────────────────
def _setup_logging() -> None:
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_file = DATA_DIR / "bughunter.log"
    handlers.append(RotatingFileHandler(str(log_file), maxBytes=10 * 1024 * 1024, backupCount=5))
    logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO, format=fmt, handlers=handlers)


_setup_logging()
logger = logging.getLogger("bughunter")


# ── App factory ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bug Hunter API v%s starting up", APP_VERSION)
    await init_db()
    yield
    logger.info("Bug Hunter API shutting down")


app = FastAPI(
    title="Bug Hunter API",
    version=APP_VERSION,
    description="Cross-platform static code analysis and vulnerability reporting engine",
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# Attach rate limiter state and error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)


# ── Security headers ─────────────────────────────────────────────────────────
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


# ── Request logging ───────────────────────────────────────────────────────────
@app.middleware("http")
async def request_logging(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    logger.info("%s %s → %d (%.1f ms)", request.method, request.url.path, response.status_code, elapsed)
    response.headers["X-Process-Time"] = f"{elapsed:.1f}ms"
    return response


# ── Global exception handlers ─────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health_router.router)
app.include_router(scan_router.router)
app.include_router(reports_router.router)

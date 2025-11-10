"""
Main FastAPI application factory.

This module creates and configures the FastAPI application instance.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
import time

from app.config import settings
from app.database import init_db, close_db
from app.routers import health, auth, content


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("Starting up application...")
    logger.info(f"Environment: {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")

    if settings.debug:
        logger.warning("Running in debug mode - initializing database")
        await init_db()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    description="A full-stack portfolio API with authentication and content management",
    version=settings.version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log incoming HTTP requests and their responses, and attach processing time to the response.
    
    Parameters:
        call_next (Callable): ASGI call-next handler that receives the request and returns a Response.
    
    Returns:
        Response: The response returned by the downstream handler with an `X-Process-Time` header set to the request processing time in seconds.
    """
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path}")

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.3f}s"
    )

    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """
    Format Pydantic validation errors into an HTTP 422 JSON response.
    
    Parameters:
        exc (RequestValidationError): The validation error raised by request parsing; its `errors()` result is included in the response.
    
    Returns:
        JSONResponse: Response with status code 422 and content `{"detail": <list of validation error dicts>}`.
    """
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
):
    """
    Log the database error and return a generic HTTP 500 JSON response.
    
    Logs the provided SQLAlchemyError with stack information and responds with a JSON body containing a generic internal error message suitable for clients.
    
    Returns:
        A JSONResponse with HTTP status 500 and a `detail` message indicating an internal error.
    """
    logger.error(f"Database error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred. Please try again later."
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    """
    Handle unexpected exceptions raised during request processing.
    
    Parameters:
    	request (Request): The incoming HTTP request that triggered the exception.
    	exc (Exception): The unhandled exception instance.
    
    Returns:
    	JSONResponse: Response with HTTP 500 and a JSON body containing a generic `"detail"` error message.
    """
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please contact support."
        }
    )


# Register routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(content.router)


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Get API information and available endpoints"
)
async def root() -> dict:
    """
    Provide basic API metadata and quick links for the root endpoint.
    
    Returns:
        dict: A mapping with keys:
            - "message": welcome message string.
            - "version": API version string from settings.
            - "docs": URL to interactive docs or a message when disabled.
            - "health": health check endpoint path.
            - "endpoints": a dict mapping service names ("auth", "content", "health") to their paths and brief descriptions.
    """
    return {
        "message": "Welcome to the Portfolio API",
        "version": settings.version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health",
        "endpoints": {
            "auth": "/auth (register, login)",
            "content": "/content (CRUD operations)",
            "health": "/health (status check)"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )
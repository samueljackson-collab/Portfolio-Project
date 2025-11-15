"""
Twisted Monk Suite v1 - Backend API
Production-ready FastAPI application with comprehensive error handling, security, and monitoring.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis.asyncio as redis

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Redis client (global, initialized in lifespan)
redis_client: Optional[redis.Redis] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events."""
    global redis_client
    
    # Startup
    logger.info("Starting Twisted Monk Suite API...")
    try:
        if settings.REDIS_ENABLED:
            redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await redis_client.ping()
            logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Twisted Monk Suite API...")
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


# Initialize FastAPI app
app = FastAPI(
    title="Twisted Monk Suite API",
    description="Production-ready API for inventory management, lead time calculation, and Shopify integration",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware for security
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their processing time."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add custom header with process time
        response.headers["X-Process-Time"] = str(process_time)
        
        logger.info(
            f"Response: {request.method} {request.url.path} "
            f"Status: {response.status_code} Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} Error: {str(e)}")
        raise


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    logger.warning(f"Validation error for {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP error {exc.status_code} for {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception for {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Pydantic models
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    redis_connected: bool
    timestamp: float


class LeadTimeRequest(BaseModel):
    """Lead time calculation request."""
    supplier_id: str = Field(..., description="Supplier identifier")
    product_id: str = Field(..., description="Product SKU or ID")
    quantity: int = Field(..., gt=0, description="Order quantity")
    
    @validator('supplier_id', 'product_id')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class LeadTimeResponse(BaseModel):
    """Lead time calculation response."""
    supplier_id: str
    product_id: str
    estimated_days: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    cached: bool = False


class InventoryStatus(BaseModel):
    """Inventory status model."""
    product_id: str
    available: int
    reserved: int
    incoming: int
    status: str  # "in_stock", "low_stock", "out_of_stock"


class BundleRecommendation(BaseModel):
    """Bundle recommendation model."""
    main_product_id: str
    recommended_products: List[str]
    discount_percentage: Optional[float] = None
    reason: str


# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Twisted Monk Suite API v1",
        "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
    }


@app.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def health_check(request: Request):
    """
    Health check endpoint with Redis connectivity status.
    Rate limited to 60 requests per minute.
    """
    redis_connected = False
    if redis_client:
        try:
            await redis_client.ping()
            redis_connected = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        redis_connected=redis_connected,
        timestamp=time.time()
    )


@app.post("/api/v1/lead-time", response_model=LeadTimeResponse)
@limiter.limit("30/minute")
async def calculate_lead_time(
    request: Request,
    lead_time_req: LeadTimeRequest
) -> LeadTimeResponse:
    """
    Calculate estimated lead time for a product from a specific supplier.
    Rate limited to 30 requests per minute.
    
    - **supplier_id**: Unique supplier identifier
    - **product_id**: Product SKU or ID
    - **quantity**: Order quantity (must be positive)
    """
    cache_key = f"lead_time:{lead_time_req.supplier_id}:{lead_time_req.product_id}"
    
    # Try to get from cache
    cached = False
    if redis_client:
        try:
            cached_value = await redis_client.get(cache_key)
            if cached_value:
                logger.info(f"Lead time cache hit for {cache_key}")
                import json
                data = json.loads(cached_value)
                return LeadTimeResponse(**data, cached=True)
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
    
    # Calculate lead time (business logic)
    # In production, this would call actual lead time calculation service
    estimated_days = 7  # Default baseline
    
    # Simple algorithm based on quantity
    if lead_time_req.quantity > 100:
        estimated_days += 3
    elif lead_time_req.quantity > 50:
        estimated_days += 1
    
    response = LeadTimeResponse(
        supplier_id=lead_time_req.supplier_id,
        product_id=lead_time_req.product_id,
        estimated_days=estimated_days,
        confidence=0.85,
        cached=cached
    )
    
    # Cache the result
    if redis_client:
        try:
            import json
            await redis_client.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(response.model_dump(exclude={'cached'}))
            )
            logger.info(f"Cached lead time for {cache_key}")
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    return response


@app.get("/api/v1/inventory/{product_id}", response_model=InventoryStatus)
@limiter.limit("60/minute")
async def get_inventory_status(
    request: Request,
    product_id: str
) -> InventoryStatus:
    """
    Get current inventory status for a product.
    Rate limited to 60 requests per minute.
    
    - **product_id**: Product SKU or ID
    """
    if not product_id or not product_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product ID cannot be empty"
        )
    
    cache_key = f"inventory:{product_id}"
    
    # Try cache first
    if redis_client:
        try:
            cached_value = await redis_client.get(cache_key)
            if cached_value:
                import json
                logger.info(f"Inventory cache hit for {product_id}")
                return InventoryStatus(**json.loads(cached_value))
        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
    
    # Mock inventory data (in production, fetch from database)
    available = 150
    reserved = 20
    incoming = 50
    
    # Determine status
    if available > 50:
        inventory_status = "in_stock"
    elif available > 0:
        inventory_status = "low_stock"
    else:
        inventory_status = "out_of_stock"
    
    response = InventoryStatus(
        product_id=product_id,
        available=available,
        reserved=reserved,
        incoming=incoming,
        status=inventory_status
    )
    
    # Cache result
    if redis_client:
        try:
            import json
            await redis_client.setex(
                cache_key,
                300,  # 5 minutes for inventory
                json.dumps(response.model_dump())
            )
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")
    
    return response


@app.get("/api/v1/bundles/{product_id}", response_model=BundleRecommendation)
@limiter.limit("30/minute")
async def get_bundle_recommendations(
    request: Request,
    product_id: str
) -> BundleRecommendation:
    """
    Get bundle recommendations for a product.
    Rate limited to 30 requests per minute.
    
    - **product_id**: Product SKU or ID
    """
    if not product_id or not product_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product ID cannot be empty"
        )
    
    # Mock recommendations (in production, use ML model or recommendation engine)
    recommendations = [
        f"{product_id}-accessory-1",
        f"{product_id}-accessory-2",
        f"{product_id}-related"
    ]
    
    return BundleRecommendation(
        main_product_id=product_id,
        recommended_products=recommendations,
        discount_percentage=10.0,
        reason="Frequently bought together"
    )


@app.get("/api/v1/metrics")
@limiter.limit("10/minute")
async def get_metrics(request: Request):
    """
    Get API metrics (for monitoring).
    Rate limited to 10 requests per minute.
    """
    # In production, integrate with Prometheus or similar
    metrics = {
        "uptime_seconds": time.time(),
        "requests_total": "N/A",  # Would come from metrics collector
        "cache_hit_rate": "N/A",
        "average_response_time": "N/A"
    }
    return metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )

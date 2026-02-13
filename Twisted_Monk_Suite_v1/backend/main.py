from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, validator
from redis import Redis
from redis.exceptions import RedisError

from .config import Settings, get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InMemoryCache:
    """Minimal Redis-compatible cache used when Redis is unavailable."""

    def __init__(self) -> None:
        self._store: Dict[str, str] = {}
        self._expiry: Dict[str, datetime] = {}

    def _prune(self) -> None:
        now = datetime.utcnow()
        expired = [key for key, exp in self._expiry.items() if exp <= now]
        for key in expired:
            self._store.pop(key, None)
            self._expiry.pop(key, None)

    def ping(self) -> bool:
        self._prune()
        return True

    def get(self, key: str) -> Optional[str]:
        self._prune()
        return self._store.get(key)

    def setex(self, key: str, seconds: int, value: str) -> None:
        self._store[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=seconds)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._expiry.pop(key, None)

    def incr(self, key: str) -> int:
        self._prune()
        current = int(self._store.get(key, "0")) + 1
        self._store[key] = str(current)
        return current

    def expire(self, key: str, seconds: int) -> None:
        if key in self._store:
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=seconds)


def _create_cache(settings: Settings):
    try:
        client = Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
            decode_responses=True,
        )
        client.ping()
        logger.info("Connected to Redis server")
        return client
    except (RedisError, OSError) as exc:
        logger.warning("Redis unavailable, falling back to in-memory cache: %s", exc)
        return InMemoryCache()


settings = get_settings()
cache = _create_cache(settings)

app = FastAPI(
    title="Twisted Monk Inventory API",
    description="Real-time inventory management and bundle recommendations",
    version="2.0.0",
)

security = HTTPBearer(auto_error=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InventoryUpdate(BaseModel):
    product_id: str
    variant_id: str
    quantity: int
    location_id: str

    @validator("quantity")
    def validate_quantity(cls, value: int) -> int:  # noqa: D417
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        return value


class BundleRecommendationRequest(BaseModel):
    product_id: str
    customer_id: Optional[str] = None
    limit: int = 4

    @validator("limit")
    def validate_limit(cls, value: int) -> int:  # noqa: D417
        if value < 1 or value > 10:
            raise ValueError("limit must be between 1 and 10")
        return value


class BundleRecommendation(BaseModel):
    product_id: str
    title: str
    handle: str
    image_url: str
    price: str
    reason: str
    score: float


async def get_shopify_client() -> httpx.AsyncClient:
    settings = get_settings()
    headers = {
        "X-Shopify-Access-Token": settings.shopify_access_token,
        "Content-Type": "application/json",
    }
    return httpx.AsyncClient(
        base_url=f"https://{settings.shopify_store_domain}",
        headers=headers,
        timeout=30.0,
    )


async def rate_limit_check(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    key = f"rate_limit:{credentials.credentials}"
    current = cache.incr(key)
    if current == 1:
        cache.expire(key, 3600)
    if current > settings.api_rate_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    return credentials.credentials


@app.get("/")
async def root() -> Dict[str, str]:
    return {"status": "healthy", "service": "Twisted Monk Inventory API"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    try:
        cache.ping()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://{settings.shopify_store_domain}/admin/api/2023-10/products/count.json",
                headers={"X-Shopify-Access-Token": settings.shopify_access_token},
            )
            response.raise_for_status()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "redis": "connected",
            "shopify": "connected",
        }
    except httpx.HTTPError as exc:
        logger.error("Shopify connectivity failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        logger.error("Health check failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy",
        ) from exc


@app.get("/inventory/{product_id}")
async def get_inventory(
    product_id: str,
    api_key: str = Depends(rate_limit_check),
) -> Dict[str, object]:  # noqa: ARG001
    cache_key = f"inventory:{product_id}"
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    async with await get_shopify_client() as client:
        try:
            response = await client.get(
                f"/admin/api/2023-10/products/{product_id}.json",
                params={"fields": "id,title,variants,inventory_quantity"},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Shopify API error for %s: %s - %s",
                product_id,
                exc.response.status_code,
                exc.response.text,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to fetch inventory from Shopify",
            ) from exc

    product_data = response.json()["product"]
    inventory_data = {
        "product_id": str(product_id),
        "title": product_data.get("title", ""),
        "total_quantity": sum(
            variant.get("inventory_quantity", 0) for variant in product_data.get("variants", [])
        ),
        "variants": [
            {
                "id": variant.get("id"),
                "quantity": variant.get("inventory_quantity", 0),
                "available": variant.get("inventory_quantity", 0) > 0,
            }
            for variant in product_data.get("variants", [])
        ],
        "last_updated": datetime.utcnow().isoformat(),
    }
    cache.setex(cache_key, 120, json.dumps(inventory_data))
    return inventory_data


@app.post("/inventory/update")
async def update_inventory(
    update: InventoryUpdate,
    api_key: str = Depends(rate_limit_check),
) -> Dict[str, object]:  # noqa: ARG001
    cache.delete(f"inventory:{update.product_id}")

    async with await get_shopify_client() as client:
        payload = {
            "location_id": update.location_id,
            "inventory_item_id": update.variant_id,
            "available": update.quantity,
        }
        try:
            response = await client.post(
                "/admin/api/2023-10/inventory_levels/set.json",
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Inventory update failed for %s: %s - %s",
                update.product_id,
                exc.response.status_code,
                exc.response.text,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inventory update failed",
            ) from exc

    logger.info("Inventory updated: %s -> %s", update.product_id, update.quantity)
    return {
        "status": "success",
        "message": "Inventory updated successfully",
        "product_id": update.product_id,
        "new_quantity": update.quantity,
    }


@app.post("/recommendations/bundle")
async def get_bundle_recommendations(
    request: BundleRecommendationRequest,
    api_key: str = Depends(rate_limit_check),
) -> List[BundleRecommendation]:  # noqa: ARG001
    cache_key = f"recommendations:{request.product_id}:{request.limit}"
    cached = cache.get(cache_key)
    if cached:
        parsed = json.loads(cached)
        return [BundleRecommendation(**item) for item in parsed]

    async with await get_shopify_client() as client:
        try:
            product_response = await client.get(
                f"/admin/api/2023-10/products/{request.product_id}.json"
            )
            product_response.raise_for_status()
            all_products_response = await client.get(
                "/admin/api/2023-10/products.json",
                params={
                    "limit": 50,
                    "fields": "id,title,handle,images,variants,tags,product_type",
                },
            )
            all_products_response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error("Recommendation fetch failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate recommendations",
            ) from exc

    current_product = product_response.json()["product"]
    all_products = all_products_response.json().get("products", [])
    recommendations = generate_recommendations(current_product, all_products, request.limit)
    cache.setex(cache_key, 3600, json.dumps([rec.dict() for rec in recommendations]))
    return recommendations


def generate_recommendations(
    current_product: Dict,
    all_products: List[Dict],
    limit: int,
) -> List[BundleRecommendation]:
    current_tags = set(filter(None, current_product.get("tags", "").split(", ")))
    current_type = current_product.get("product_type", "")
    recommendations: List[BundleRecommendation] = []

    for product in all_products:
        if product.get("id") == current_product.get("id"):
            continue

        variants = product.get("variants", [])
        total_inventory = sum(v.get("inventory_quantity", 0) for v in variants)
        if total_inventory <= 0:
            continue

        score = 0.0
        product_tags = set(filter(None, product.get("tags", "").split(", ")))
        tag_overlap = len(current_tags.intersection(product_tags))
        if current_tags:
            score += (tag_overlap / len(current_tags)) * 0.4

        if product.get("product_type") and product.get("product_type") == current_type:
            score += 0.3

        score += 0.2  # availability weight

        current_price = float(current_product.get("variants", [{}])[0].get("price", 0) or 0)
        product_price = float(variants[0].get("price", 0) or 0) if variants else 0
        if current_price > 0 and product_price > 0:
            price_ratio = min(current_price, product_price) / max(current_price, product_price)
            score += price_ratio * 0.1

        if score <= 0.2:
            continue

        image_url = ""
        if product.get("images"):
            image_url = product["images"][0].get("src", "")

        recommendations.append(
            BundleRecommendation(
                product_id=str(product.get("id")),
                title=product.get("title", ""),
                handle=product.get("handle", ""),
                image_url=image_url,
                price=str(variants[0].get("price", "0.00")) if variants else "0.00",
                reason=generate_reason(score, tag_overlap, current_type),
                score=round(score, 2),
            )
        )

    recommendations.sort(key=lambda rec: rec.score, reverse=True)
    return recommendations[:limit]


def generate_reason(score: float, tag_overlap: int, product_type: str) -> str:
    if score > 0.7:
        return "Frequently purchased together"
    if tag_overlap > 2:
        return "Similar style and features"
    if product_type:
        return f"Complements your {product_type}"
    return "Customers also love"


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        log_level="info",
    )

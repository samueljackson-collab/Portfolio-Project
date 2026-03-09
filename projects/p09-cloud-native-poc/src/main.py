#!/usr/bin/env python3
"""
FastAPI Cloud-Native POC Application.
"""
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cloud-Native POC API",
    description="Proof-of-concept cloud-native application with FastAPI",
    version="1.0.0",
)


# Pydantic models
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    version: str


# In-memory database (replace with SQLAlchemy in production)
items_db: dict[int, Item] = {}
next_id = 1


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for liveness probe."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/ready", response_model=HealthResponse)
async def readiness_check():
    """Readiness check endpoint."""
    # Add database connectivity check here
    return HealthResponse(status="ready", version="1.0.0")


@app.get("/api/items", response_model=List[Item])
async def list_items():
    """List all items."""
    logger.info("Listing all items")
    return list(items_db.values())


@app.post("/api/items", response_model=Item, status_code=201)
async def create_item(item: ItemBase):
    """Create a new item."""
    global next_id
    new_item = Item(id=next_id, **item.dict())
    items_db[next_id] = new_item
    logger.info(f"Created item: {next_id}")
    next_id += 1
    return new_item


@app.get("/api/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get item by ID."""
    if item_id not in items_db:
        logger.warning(f"Item not found: {item_id}")
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.put("/api/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemBase):
    """Update an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = Item(id=item_id, **item.dict())
    items_db[item_id] = updated_item
    logger.info(f"Updated item: {item_id}")
    return updated_item


@app.delete("/api/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del items_db[item_id]
    logger.info(f"Deleted item: {item_id}")
    return None


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

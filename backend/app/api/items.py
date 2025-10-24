"""Item-related API endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db
from ..models import Item, ItemCreate, ItemOut, User

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Item:
    """Create an item owned by the authenticated user."""
    item = Item(title=item_in.title, description=item_in.description, owner_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=List[ItemOut])
def list_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[Item]:
    """List all items owned by the authenticated user."""
    return db.query(Item).filter(Item.owner_id == current_user.id).order_by(Item.created_at.desc()).all()


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Item:
    """Retrieve a single item by ID for the authenticated user."""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

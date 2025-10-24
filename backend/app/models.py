"""Data models for the FastAPI backend."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base


class User(Base):
    """SQLAlchemy model representing a user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")


class Item(Base):
    """SQLAlchemy model representing an item owned by a user."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="items")


class UserBase(BaseModel):
    """Shared properties for user models."""

    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    """Model for creating a new user."""

    password: str = Field(..., min_length=8, max_length=128)


class UserOut(UserBase):
    """Public representation of a user."""

    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ItemBase(BaseModel):
    """Shared properties for item models."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)


class ItemCreate(ItemBase):
    """Model for creating a new item."""


class ItemOut(ItemBase):
    """Public representation of an item."""

    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ─── Product Schemas ──────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    sku: str

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("price must be greater than 0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("stock cannot be negative")
        return v


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str]
    sku: str

    model_config = {"from_attributes": True}


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Order Schemas ────────────────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be at least 1")
        return v


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = {"from_attributes": True}


# ─── Booking Schemas ──────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    user_id: int
    resource_name: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def end_must_be_after_start(cls, v: datetime, info) -> datetime:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class BookingResponse(BaseModel):
    id: int
    user_id: int
    resource_name: str
    start_time: datetime
    end_time: datetime
    status: str
    notes: Optional[str]

    model_config = {"from_attributes": True}


# ─── Generic Response Schemas ─────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    database: str
    version: str

"""
Pydantic schemas for request validation and response serialization.
Provides type safety and automatic validation.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


# Content schemas
class ContentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    body: Optional[str] = None
    is_published: bool = False


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    body: Optional[str] = None
    is_published: Optional[bool] = None


class Content(ContentBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

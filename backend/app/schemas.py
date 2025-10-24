from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class ContentBase(BaseModel):
    title: str
    body: Optional[str] = None
    is_published: bool = False


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    is_published: Optional[bool] = None


class ContentOut(ContentBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

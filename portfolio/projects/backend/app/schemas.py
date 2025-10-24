from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class ContentBase(BaseModel):
    title: constr(min_length=1, max_length=255)
    body: constr(min_length=1)


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: Optional[constr(min_length=1, max_length=255)] = None
    body: Optional[constr(min_length=1)] = None


class ContentRead(ContentBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True

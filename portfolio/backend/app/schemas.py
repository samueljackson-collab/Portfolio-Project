from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True


class ContentBase(BaseModel):
    title: str
    slug: str
    body: str


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    body: str | None = None


class ContentRead(ContentBase):
    id: int
    owner_id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True

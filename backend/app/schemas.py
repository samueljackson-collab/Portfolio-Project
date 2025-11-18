from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    title: str
    slug: str
    description: str
    category: str
    tags: List[str] = []
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    featured: bool = False

    @field_validator("tags", mode="before")
    @classmethod
    def ensure_list(cls, value):
        if isinstance(value, str):
            return [tag for tag in value.split(",") if tag]
        return value


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    featured: Optional[bool] = None


class ProjectRead(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

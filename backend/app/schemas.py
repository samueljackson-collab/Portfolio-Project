"""Pydantic schemas for validating and serialising API payloads."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


class TimestampMixin(BaseModel):
    """Mixin providing timestamp fields with ISO8601 serialisation."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(json_encoders={datetime: lambda value: value.isoformat()})


class UserBase(BaseModel):
    """Fields common to multiple user-related payloads."""

    email: EmailStr = Field(..., description="User email address")

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        return value.lower().strip()


class UserCreate(UserBase):
    """Payload for creating a user account."""

    password: str = Field(..., min_length=8, max_length=100, description="User password")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        return value


class UserLogin(BaseModel):
    """Payload for user login attempts."""

    email: EmailStr
    password: str


class UserResponse(UserBase, TimestampMixin):
    """User details returned by the API."""

    id: UUID = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Account activity flag")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Payload for partial user profile updates."""

    email: Optional[EmailStr] = Field(default=None, description="Updated email address")
    password: Optional[str] = Field(default=None, min_length=8, description="Updated password")

    @field_validator("password")
    @classmethod
    def validate_optional_password(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return UserCreate.validate_password_strength(value)


class Token(BaseModel):
    """Response structure for OAuth2-compatible access tokens."""

    access_token: str
    token_type: str = Field(default="bearer")
    expires_in: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
            }
        }
    )


class TokenData(BaseModel):
    """Decoded token payload fields utilised internally."""

    email: Optional[str] = None
    user_id: Optional[UUID] = None


class ContentBase(BaseModel):
    """Fields common across content operations."""

    title: str = Field(..., min_length=1, max_length=255)
    body: Optional[str] = Field(default=None, max_length=10000)
    is_published: bool = Field(default=False)


class ContentCreate(ContentBase):
    """Payload for creating new content entries."""

    pass


class ContentUpdate(BaseModel):
    """Payload for updating existing content entries."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    body: Optional[str] = Field(default=None, max_length=10000)
    is_published: Optional[bool] = None


class ContentResponse(ContentBase, TimestampMixin):
    """Content item returned by the API."""

    id: UUID
    owner_id: UUID
    owner: UserResponse

    model_config = ConfigDict(from_attributes=True)


class ContentListResponse(BaseModel):
    """Paginated response for content listings."""

    items: list[ContentResponse]
    total: int
    page: int
    page_size: int
    pages: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 10,
                "pages": 0,
            }
        }
    )


class ErrorDetail(BaseModel):
    """Detailed validation error information."""

    loc: list[str]
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    detail: str | list[ErrorDetail]


class HealthResponse(BaseModel):
    """Payload returned by health check endpoints."""

    status: str
    version: str
    database: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected",
            }
        }
    )

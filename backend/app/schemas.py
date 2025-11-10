"""
Pydantic schemas for request/response validation and serialization.

Schemas define the structure of data exchanged via API:
- Request bodies (what clients send)
- Response bodies (what server returns)
- Query parameters
- Path parameters
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


# ============================================================================
# Base Schemas (common fields)
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v: str) -> str:
        """Ensure email is lowercase for consistency."""
        return v.lower().strip()


class UserCreate(UserBase):
    """Schema for user registration requests."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (8-100 characters)",
        examples=["SecureP@ss123"]
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")

        return v


class UserLogin(BaseModel):
    """Schema for login requests."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(UserBase, TimestampMixin):
    """Schema for user data in API responses."""
    id: UUID = Field(..., description="User unique identifier")
    is_active: bool = Field(..., description="Account active status")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="New password"
    )

    @field_validator("password")
    @classmethod
    def validate_password_if_provided(cls, v: Optional[str]) -> Optional[str]:
        """Apply password strength validation if password is provided."""
        if v is not None:
            return UserCreate.password_must_be_strong(v)
        return v


# ============================================================================
# Token Schemas
# ============================================================================

class Token(BaseModel):
    """Schema for authentication token responses."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class TokenData(BaseModel):
    """Schema for decoded token data (internal use)."""
    email: Optional[str] = None
    user_id: Optional[UUID] = None


# ============================================================================
# Content Schemas
# ============================================================================

class ContentBase(BaseModel):
    """Base content schema with common fields."""
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Content title",
        examples=["My First Blog Post"]
    )
    body: Optional[str] = Field(
        None,
        max_length=10000,
        description="Content body text",
        examples=["This is the content body..."]
    )
    is_published: bool = Field(
        default=False,
        description="Publication status"
    )


class ContentCreate(ContentBase):
    """Schema for creating new content."""
    pass


class ContentUpdate(BaseModel):
    """Schema for updating existing content."""
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated title"
    )
    body: Optional[str] = Field(None, description="Updated body")
    is_published: Optional[bool] = Field(None, description="Updated status")


class ContentResponse(ContentBase, TimestampMixin):
    """Schema for content in API responses."""
    id: UUID = Field(..., description="Content unique identifier")
    owner_id: UUID = Field(..., description="Owner user ID")
    owner: UserResponse = Field(..., description="Content owner details")

    model_config = ConfigDict(from_attributes=True)


class ContentListResponse(BaseModel):
    """Schema for paginated content list responses."""
    items: list[ContentResponse] = Field(..., description="Content items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 42,
                "page": 1,
                "page_size": 10,
                "pages": 5
            }
        }
    )


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorDetail(BaseModel):
    """Schema for detailed error information."""
    loc: list[str] = Field(..., description="Error location path")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str | list[ErrorDetail] = Field(
        ...,
        description="Error details"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Invalid credentials"
            }
        }
    )


# ============================================================================
# Health Check Schema
# ============================================================================

class HealthResponse(BaseModel):
    """Schema for health check responses."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected"
            }
        }
    )

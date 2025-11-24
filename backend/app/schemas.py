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


# ============================================================================
# Album Schemas
# ============================================================================

class AlbumBase(BaseModel):
    """Base album schema with common fields."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Album name",
        examples=["San Francisco, CA"]
    )
    type: str = Field(
        default="custom",
        description="Album type: location, date, or custom",
        examples=["location", "date", "custom"]
    )


class AlbumCreate(AlbumBase):
    """Schema for creating new album."""
    pass


class AlbumUpdate(BaseModel):
    """Schema for updating existing album."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    cover_photo_id: Optional[UUID] = Field(None, description="Cover photo ID")


class AlbumResponse(AlbumBase, TimestampMixin):
    """Schema for album in API responses."""
    id: UUID = Field(..., description="Album unique identifier")
    owner_id: UUID = Field(..., description="Owner user ID")
    photo_count: int = Field(..., description="Number of photos in album")
    cover_photo_id: Optional[UUID] = Field(None, description="Cover photo ID")

    model_config = ConfigDict(from_attributes=True)


class AlbumListResponse(BaseModel):
    """Schema for paginated album list responses."""
    items: list[AlbumResponse] = Field(..., description="Album items")
    total: int = Field(..., description="Total number of albums")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


# ============================================================================
# Photo Schemas
# ============================================================================

class PhotoBase(BaseModel):
    """Base photo schema with common fields."""
    filename: str = Field(..., description="Original filename")
    album_id: Optional[UUID] = Field(None, description="Album ID")


class PhotoCreate(PhotoBase):
    """Schema for creating new photo (internal use after upload)."""
    file_path: str = Field(..., description="Storage path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(default="image/jpeg", description="MIME type")
    width: Optional[int] = None
    height: Optional[int] = None
    capture_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None


class PhotoUpdate(BaseModel):
    """Schema for updating existing photo."""
    filename: Optional[str] = Field(None, description="Updated filename")
    album_id: Optional[UUID] = Field(None, description="Move to different album")


class PhotoResponse(TimestampMixin):
    """Schema for photo in API responses."""
    id: UUID = Field(..., description="Photo unique identifier")
    owner_id: UUID = Field(..., description="Owner user ID")
    album_id: Optional[UUID] = Field(None, description="Album ID")
    filename: str = Field(..., description="Filename")
    file_path: str = Field(..., description="Storage path")
    thumbnail_path: Optional[str] = Field(None, description="Thumbnail path")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    width: Optional[int] = Field(None, description="Image width")
    height: Optional[int] = Field(None, description="Image height")
    capture_date: Optional[datetime] = Field(None, description="Date taken")
    upload_date: datetime = Field(..., description="Upload date")
    latitude: Optional[float] = Field(None, description="GPS latitude")
    longitude: Optional[float] = Field(None, description="GPS longitude")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State/region")
    country: Optional[str] = Field(None, description="Country")
    camera_make: Optional[str] = Field(None, description="Camera make")
    camera_model: Optional[str] = Field(None, description="Camera model")

    model_config = ConfigDict(from_attributes=True)


class PhotoListResponse(BaseModel):
    """Schema for paginated photo list responses."""
    items: list[PhotoResponse] = Field(..., description="Photo items")
    total: int = Field(..., description="Total number of photos")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class PhotoUploadResponse(BaseModel):
    """Schema for photo upload success response."""
    photo: PhotoResponse = Field(..., description="Uploaded photo details")
    album: Optional[AlbumResponse] = Field(None, description="Auto-assigned album")
    message: str = Field(
        default="Photo uploaded successfully",
        description="Success message"
    )


class CalendarDateResponse(BaseModel):
    """Schema for calendar view - photo count by date."""
    date: datetime = Field(..., description="Date")
    photo_count: int = Field(..., description="Number of photos on this date")
    preview_photos: list[PhotoResponse] = Field(
        default=[],
        max_length=4,
        description="Preview thumbnails (max 4)"
    )


class CalendarMonthResponse(BaseModel):
    """Schema for calendar month view."""
    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    dates: list[CalendarDateResponse] = Field(..., description="Dates with photos")
    total_photos: int = Field(..., description="Total photos in month")


# =============================================================================
# Deployment / Operations Schemas
# =============================================================================


class DeploymentBase(BaseModel):
    service_name: str = Field(..., max_length=100, description="Logical service name")
    region: str = Field(..., max_length=50, description="AWS region of deployment")
    cluster: str = Field(..., max_length=120, description="Kubernetes cluster name")
    version: str = Field(..., max_length=50, description="Application version or tag")
    status: str = Field(default="Progressing", description="Deployment status")
    git_commit: Optional[str] = Field(None, max_length=64, description="Git SHA deployed")
    desired_replicas: int = Field(default=1, ge=0, le=50)
    available_replicas: int = Field(default=0, ge=0, le=50)


class DeploymentCreate(DeploymentBase):
    """Schema for creating new deployment records."""


class DeploymentResponse(DeploymentBase, TimestampMixin):
    """Schema returned for deployment record endpoints."""

    id: UUID = Field(..., description="Deployment record identifier")
    created_by: Optional[UUID] = Field(None, description="User who created the record")

    model_config = ConfigDict(from_attributes=True)


class RegionRollup(BaseModel):
    """Aggregated deployment health by region."""

    region: str
    services: int
    desired_replicas: int
    available_replicas: int
    healthy: int


class DeploymentDashboardResponse(BaseModel):
    """Payload consumed by the operator console for rollups."""

    regions: list[RegionRollup]
    latest_releases: list[DeploymentResponse]

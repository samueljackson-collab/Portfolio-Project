"""
Pydantic schemas for request/response validation and serialization.

Schemas define the structure of data exchanged via API:
- Request bodies (what clients send)
- Response bodies (what server returns)
- Query parameters
- Path parameters
"""

from datetime import datetime
from typing import Optional, Dict, List, Literal
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


# ============================================================================
# Base Schemas (common fields)
# ============================================================================


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})


# ============================================================================
# User Schemas
# ============================================================================


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(
        ..., description="User email address", examples=["user@example.com"]
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
        examples=["SecureP@ss123"],
    )

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

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
    password: Optional[str] = Field(None, min_length=8, description="New password")

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
                "expires_in": 1800,
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
        examples=["My First Blog Post"],
    )
    body: Optional[str] = Field(
        None,
        max_length=10000,
        description="Content body text",
        examples=["This is the content body..."],
    )
    is_published: bool = Field(default=False, description="Publication status")


class ContentCreate(ContentBase):
    """Schema for creating new content."""

    pass


class ContentUpdate(BaseModel):
    """Schema for updating existing content."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Updated title"
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
                "pages": 5,
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

    detail: str | list[ErrorDetail] = Field(..., description="Error details")

    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Invalid credentials"}}
    )


# ============================================================================
# Health Check Schema
# ============================================================================


class HealthResponse(BaseModel):
    """Schema for health check responses."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    database: str = Field(..., description="Database connection status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Health check timestamp"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "database": "connected",
                "service": "Portfolio API",
                "timestamp": "2024-01-01T00:00:00Z",
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
        examples=["San Francisco, CA"],
    )
    type: str = Field(
        default="custom",
        description="Album type: location, date, or custom",
        examples=["location", "date", "custom"],
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
        default="Photo uploaded successfully", description="Success message"
    )


class CalendarDateResponse(BaseModel):
    """Schema for calendar view - photo count by date."""

    date: datetime = Field(..., description="Date")
    photo_count: int = Field(..., description="Number of photos on this date")
    preview_photos: list[PhotoResponse] = Field(
        default=[], max_length=4, description="Preview thumbnails (max 4)"
    )


class CalendarMonthResponse(BaseModel):
    """Schema for calendar month view."""

    year: int = Field(..., description="Year")
    month: int = Field(..., description="Month (1-12)")
    dates: list[CalendarDateResponse] = Field(..., description="Dates with photos")
    total_photos: int = Field(..., description="Total photos in month")


# ============================================================================
# Orchestration Schemas
# ============================================================================


class OrchestrationPlan(BaseModel):
    """Immutable description of how we deploy an environment."""

    id: str = Field(..., description="Unique identifier for the plan")
    name: str = Field(..., description="Human readable plan name")
    environment: str = Field(..., description="Target environment (dev/staging/prod)")
    description: str = Field(..., description="Purpose of the plan")
    playbook_path: str = Field(..., description="Ansible playbook used for rollout")
    tfvars_file: str = Field(
        ..., description="Terraform variables file driving the plan"
    )
    runbook: str = Field(..., description="Runbook documenting the procedure")


class OrchestrationRunRequest(BaseModel):
    """Request payload for starting a deployment run."""

    plan_id: str = Field(..., description="Plan identifier to execute")
    parameters: Dict[str, str] = Field(
        default_factory=dict, description="Override variables"
    )


class OrchestrationRun(BaseModel):
    """Recorded orchestration execution."""

    id: str = Field(..., description="Run identifier")
    plan_id: str = Field(..., description="Plan executed")
    environment: str = Field(..., description="Environment targeted by the run")
    status: Literal["running", "succeeded", "failed"] = Field(
        ..., description="Run outcome"
    )
    requested_by: str = Field(..., description="User who requested the run")
    parameters: Dict[str, str] = Field(
        default_factory=dict, description="Parameters used"
    )
    started_at: datetime = Field(..., description="Start timestamp")
    finished_at: Optional[datetime] = Field(None, description="Completion timestamp")
    logs: List[str] = Field(default_factory=list, description="Progress log entries")
    artifacts: Dict[str, str] = Field(
        default_factory=dict, description="Artifact references"
    )
    summary: Optional[str] = Field(None, description="Short description of the changes")


# ============================================================================
# Project 5 - Full-Scope Red Team Operation Simulator
# ============================================================================


class OperationCreate(BaseModel):
    name: str = Field(..., description="Campaign name")
    objective: Optional[str] = Field(
        None, description="Primary objective for the operation"
    )
    start_date: Optional[datetime] = Field(
        None, description="Start timestamp; defaults to now"
    )
    stealth_factor: float = Field(
        0.6, ge=0, le=1, description="Probability of staying covert"
    )


class OperationEventCreate(BaseModel):
    timestamp: Optional[datetime] = Field(
        None, description="Event timestamp; defaults to sequence day"
    )
    description: str = Field(..., description="Action performed")
    category: str = Field(..., description="Action category (e.g., lateral movement)")
    detected: bool = Field(False, description="Whether blue team detected the action")
    day: Optional[int] = Field(
        None, description="Day in campaign; defaults to next day"
    )
    detection_confidence: float = Field(
        0.5, ge=0, le=1, description="How noisy the event was"
    )


class OperationEventResponse(OperationEventCreate):
    id: UUID
    operation_id: UUID

    model_config = ConfigDict(from_attributes=True)


class OperationResponse(OperationCreate):
    id: UUID
    days_elapsed: int
    undetected_streak: int
    first_detection_at: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime
    events: list[OperationEventResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Project 6 - Ransomware Incident Response & Recovery
# ============================================================================


class IncidentCreate(BaseModel):
    name: str = Field(..., description="Incident display name")
    severity: str = Field("high", description="Business impact")


class IncidentEventCreate(BaseModel):
    type: str = Field(..., description="Lifecycle stage")
    details: str = Field(..., description="Narrative for the event")
    timestamp: Optional[datetime] = Field(None, description="When the event occurred")


class IncidentEventResponse(IncidentEventCreate):
    id: UUID
    incident_id: UUID
    sequence: int

    model_config = ConfigDict(from_attributes=True)


class IncidentResponse(BaseModel):
    id: UUID
    name: str
    status: str
    severity: str
    created_at: datetime
    resolved_at: Optional[datetime]
    events: list[IncidentEventResponse] = []
    warning: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Project 7 - SOC Implementation Portal
# ============================================================================


class SocAlertCreate(BaseModel):
    title: str
    description: str
    severity: str = Field("medium", description="Alert severity level")
    source: str = Field("sensor", description="Alert origin")
    status: str = Field("open", description="Alert triage status")
    case_id: Optional[UUID] = None


class SocAlertResponse(SocAlertCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SocCaseCreate(BaseModel):
    title: str
    assigned_to: Optional[str] = None
    playbook_id: Optional[UUID] = None
    alert_ids: list[UUID] = Field(
        default_factory=list, description="Alerts to associate"
    )


class SocCaseUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    playbook_id: Optional[UUID] = None


class SocCaseResponse(BaseModel):
    id: UUID
    title: str
    status: str
    assigned_to: Optional[str]
    playbook_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    alerts: list[SocAlertResponse] = []

    model_config = ConfigDict(from_attributes=True)


class SocPlaybookResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    steps: Optional[list[str]]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Project 8 - Threat Hunting Program Management
# ============================================================================


class HypothesisCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = Field("open", description="Current hypothesis state")


class HypothesisResponse(HypothesisCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FindingCreate(BaseModel):
    severity: str = Field("medium", description="Impact level")
    details: str
    status: str = Field("new", description="Investigation status")


class FindingResponse(FindingCreate):
    id: UUID
    hypothesis_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DetectionRuleCreate(BaseModel):
    name: str
    query: str
    status: str = Field("Draft", description="Lifecycle status")
    source_finding_id: Optional[UUID] = None


class DetectionRuleResponse(DetectionRuleCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Project 9 - Advanced Malware Analysis & Reverse Engineering
# ============================================================================


class MalwareSampleCreate(BaseModel):
    name: str
    file_hash: str
    sample_type: str = Field("unknown", description="File type or platform")
    family: Optional[str] = None


class MalwareSampleResponse(MalwareSampleCreate):
    id: UUID
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisReportResponse(BaseModel):
    id: UUID
    sample_id: UUID
    static_analysis: str
    dynamic_analysis: str
    iocs: Optional[list[str]]
    yara_rule: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MalwareDetailResponse(BaseModel):
    sample: MalwareSampleResponse
    report: Optional[AnalysisReportResponse]


# ============================================================================
# Project 10 - Enterprise EDR Platform Simulation
# ============================================================================


class EndpointCreate(BaseModel):
    hostname: str
    operating_system: str
    agent_version: str


class EndpointResponse(EndpointCreate):
    id: UUID
    last_checkin: datetime
    online: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EndpointCheckin(BaseModel):
    agent_version: Optional[str] = None
    note: Optional[str] = None


class EndpointPolicyResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    enabled: bool

    model_config = ConfigDict(from_attributes=True)


class EndpointPolicyUpdate(BaseModel):
    enabled: bool


class EndpointAlertCreate(BaseModel):
    endpoint_id: Optional[UUID] = None
    severity: str = Field("medium", description="Alert severity")
    description: str
    status: str = Field("open", description="Alert status")


class EndpointAlertResponse(EndpointAlertCreate):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeploymentSummary(BaseModel):
    total_endpoints: int
    online: int
    outdated_agents: int
    coverage: float
    active_policies: int

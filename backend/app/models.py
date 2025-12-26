"""
SQLAlchemy ORM models for database tables.

Models define the structure of database tables and relationships between them.
Each model class represents a table, and each attribute represents a column.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    Index,
    Integer,
    Float,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.compiler import compiles


@compiles(UUID, "sqlite")
def compile_sqlite_uuid(type_, compiler, **kw):
    """Render UUID columns as CHAR(36) for SQLite-based tests."""
    return "CHAR(36)"

from app.database import Base


class User(Base):
    """
    User model for authentication and authorization.

    Attributes:
        id: UUID primary key (auto-generated)
        email: Unique email address
        hashed_password: Bcrypt hashed password
        is_active: Account status flag
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
        content_items: Related Content items (relationship)
    """
    __tablename__ = "users"

    # Primary key with UUID
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="User unique identifier"
    )

    # Authentication fields
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,  # Index for faster lookups
        comment="User email address"
    )

    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password"
    )

    # Status fields
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Account active status"
    )

    # Timestamps with automatic updates
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Account creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationship to Content (one-to-many)
    content_items = relationship(
        "Content",
        back_populates="owner",
        cascade="all, delete-orphan",  # Delete content when user is deleted
        lazy="selectin"  # Eager load content items
    )

    # Relationship to Photos (one-to-many)
    photos = relationship(
        "Photo",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # Relationship to Albums (one-to-many)
    albums = relationship(
        "Album",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class Content(Base):
    """
    Content model for user-generated content items.

    Attributes:
        id: UUID primary key (auto-generated)
        title: Content title
        body: Content body text
        owner_id: Foreign key to User.id
        is_published: Publication status
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        owner: Related User (relationship)
    """
    __tablename__ = "content"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Content unique identifier"
    )

    # Content fields
    title = Column(
        String(255),
        nullable=False,
        comment="Content title"
    )

    body = Column(
        Text,
        nullable=True,
        comment="Content body text"
    )

    # Foreign key to User
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Index for faster joins
        comment="Content owner user ID"
    )

    # Status fields
    is_published = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Publication status"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,  # Index for sorting by date
        comment="Content creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationship to User (many-to-one)
    owner = relationship(
        "User",
        back_populates="content_items"
    )

    # Composite index for common queries
    __table_args__ = (
        Index("ix_content_owner_created", "owner_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Content(id={self.id}, title={self.title})>"


class Album(Base):
    """
    Album model for organizing photos by location or date.

    Auto-generated albums organize photos by city/location or time period.
    Users can also create custom albums for events or themes.

    Attributes:
        id: UUID primary key
        owner_id: Foreign key to User.id
        name: Album name (e.g., "San Francisco, CA" or "Summer 2024")
        type: Album type (location, date, custom)
        photo_count: Cached count of photos in album
        cover_photo_id: UUID of photo to use as album cover
        created_at: Creation timestamp
        updated_at: Last modification timestamp
        owner: Related User (relationship)
        photos: Related Photos (relationship)
    """
    __tablename__ = "albums"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Album unique identifier"
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Album owner user ID"
    )

    name = Column(
        String(255),
        nullable=False,
        comment="Album name"
    )

    type = Column(
        String(50),
        nullable=False,
        default="custom",
        comment="Album type: location, date, or custom"
    )

    photo_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Cached count of photos in album"
    )

    cover_photo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("photos.id", ondelete="SET NULL"),
        nullable=True,
        comment="Cover photo ID"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Album creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    owner = relationship("User", back_populates="albums")
    photos = relationship(
        "Photo",
        back_populates="album",
        foreign_keys="Photo.album_id"
    )
    cover_photo = relationship(
        "Photo",
        foreign_keys=[cover_photo_id],
        post_update=True
    )

    __table_args__ = (
        Index("ix_albums_owner_type", "owner_id", "type"),
        Index("ix_albums_owner_updated", "owner_id", "updated_at"),
        UniqueConstraint("owner_id", "name", name="uq_albums_owner_name"),
    )

    def __repr__(self) -> str:
        return f"<Album(id={self.id}, name={self.name}, type={self.type})>"


class Photo(Base):
    """
    Photo model for storing photo metadata and file information.

    Stores EXIF metadata including GPS coordinates, capture date, camera info.
    Location data is reverse-geocoded to provide city/state/country names.

    Attributes:
        id: UUID primary key
        owner_id: Foreign key to User.id
        album_id: Foreign key to Album.id (auto-organized)
        filename: Original filename
        file_path: Storage path on server
        thumbnail_path: Path to generated thumbnail
        file_size: File size in bytes
        mime_type: Image MIME type (image/jpeg, image/png, etc.)
        width: Image width in pixels
        height: Image height in pixels
        capture_date: Date photo was taken (from EXIF)
        upload_date: Date photo was uploaded
        latitude: GPS latitude (from EXIF)
        longitude: GPS longitude (from EXIF)
        city: City name (reverse geocoded)
        state: State/region name (reverse geocoded)
        country: Country name (reverse geocoded)
        camera_make: Camera manufacturer (from EXIF)
        camera_model: Camera model (from EXIF)
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
        owner: Related User (relationship)
        album: Related Album (relationship)
    """
    __tablename__ = "photos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Photo unique identifier"
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Photo owner user ID"
    )

    album_id = Column(
        UUID(as_uuid=True),
        ForeignKey("albums.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Album ID (auto-organized)"
    )

    # File information
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename"
    )

    file_path = Column(
        String(512),
        nullable=False,
        unique=True,
        comment="Storage path on server"
    )

    thumbnail_path = Column(
        String(512),
        nullable=True,
        comment="Thumbnail storage path"
    )

    file_size = Column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )

    mime_type = Column(
        String(50),
        nullable=False,
        default="image/jpeg",
        comment="Image MIME type"
    )

    # Image dimensions
    width = Column(
        Integer,
        nullable=True,
        comment="Image width in pixels"
    )

    height = Column(
        Integer,
        nullable=True,
        comment="Image height in pixels"
    )

    # Date information
    capture_date = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Date photo was taken (from EXIF)"
    )

    upload_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Date photo was uploaded"
    )

    # GPS and location data
    latitude = Column(
        Float,
        nullable=True,
        comment="GPS latitude"
    )

    longitude = Column(
        Float,
        nullable=True,
        comment="GPS longitude"
    )

    city = Column(
        String(255),
        nullable=True,
        index=True,
        comment="City name (reverse geocoded)"
    )

    state = Column(
        String(255),
        nullable=True,
        comment="State/region name"
    )

    country = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Country name"
    )

    # Camera information
    camera_make = Column(
        String(100),
        nullable=True,
        comment="Camera manufacturer"
    )

    camera_model = Column(
        String(100),
        nullable=True,
        comment="Camera model"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    owner = relationship("User", back_populates="photos")
    album = relationship("Album", back_populates="photos", foreign_keys=[album_id])

    __table_args__ = (
        Index("ix_photos_owner_capture", "owner_id", "capture_date"),
        Index("ix_photos_owner_city", "owner_id", "city"),
        Index("ix_photos_album_capture", "album_id", "capture_date"),
        Index("ix_photos_location", "latitude", "longitude"),
    )

    def __repr__(self) -> str:
        return f"<Photo(id={self.id}, filename={self.filename}, city={self.city})>"


# =============================================================================
# Project 5 - Full-Scope Red Team Operation Simulator
# =============================================================================


class Operation(Base):
    """Red team operation representing a long-lived campaign."""

    __tablename__ = "operations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    objective = Column(String(255), nullable=True)
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    stealth_factor = Column(Float, default=0.6, nullable=False)
    days_elapsed = Column(Integer, default=0, nullable=False)
    undetected_streak = Column(Integer, default=0, nullable=False)
    first_detection_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="in_progress", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    events = relationship("OperationEvent", back_populates="operation", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Operation(id={self.id}, name={self.name}, stealth={self.stealth_factor})>"


class OperationEvent(Base):
    """Daily timeline entry for an operation."""

    __tablename__ = "operation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_id = Column(UUID(as_uuid=True), ForeignKey("operations.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    day = Column(Integer, default=1, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    detected = Column(Boolean, default=False, nullable=False)
    detection_confidence = Column(Float, default=0.5, nullable=False)

    operation = relationship("Operation", back_populates="events")

    __table_args__ = (
        Index("ix_operation_event_day", "operation_id", "day"),
    )

    def __repr__(self) -> str:
        return f"<OperationEvent(op={self.operation_id}, day={self.day}, detected={self.detected})>"


# =============================================================================
# Project 6 - Ransomware Incident Response & Recovery
# =============================================================================


class Incident(Base):
    """Incident lifecycle container for ransomware simulations."""

    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    status = Column(String(50), default="ongoing", nullable=False)
    severity = Column(String(30), default="high", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    events = relationship("IncidentEvent", back_populates="incident", cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Incident(id={self.id}, status={self.status})>"


class IncidentEvent(Base):
    """Individual event in an incident response timeline."""

    __tablename__ = "incident_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    type = Column(String(50), nullable=False)
    details = Column(Text, nullable=False)
    sequence = Column(Integer, default=0, nullable=False)

    incident = relationship("Incident", back_populates="events")

    __table_args__ = (
        Index("ix_incident_event_sequence", "incident_id", "sequence"),
    )


# =============================================================================
# Project 7 - SOC Implementation Portal
# =============================================================================


class SocPlaybook(Base):
    """SOC playbook describing steps for a case."""

    __tablename__ = "soc_playbooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    steps = Column(JSON, nullable=True)

    cases = relationship("SocCase", back_populates="playbook")


class SocCase(Base):
    """Case for grouping alerts and response actions."""

    __tablename__ = "soc_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(160), nullable=False)
    status = Column(String(40), default="open", nullable=False)
    assigned_to = Column(String(100), nullable=True)
    playbook_id = Column(UUID(as_uuid=True), ForeignKey("soc_playbooks.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    playbook = relationship("SocPlaybook", back_populates="cases")
    alerts = relationship("SocAlert", back_populates="case", cascade="all", lazy="selectin")


class SocAlert(Base):
    """Alert tracked inside the SOC portal."""

    __tablename__ = "soc_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium", nullable=False)
    status = Column(String(40), default="open", nullable=False)
    source = Column(String(80), default="sensor", nullable=False)
    case_id = Column(UUID(as_uuid=True), ForeignKey("soc_cases.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    case = relationship("SocCase", back_populates="alerts")

    __table_args__ = (
        Index("ix_soc_alert_status", "status"),
    )


# =============================================================================
# Project 8 - Threat Hunting Program Management
# =============================================================================


class HuntHypothesis(Base):
    """Hunt hypothesis capturing a question or suspicion."""

    __tablename__ = "hunt_hypotheses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(40), default="open", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    findings = relationship("HuntFinding", back_populates="hypothesis", cascade="all, delete-orphan", lazy="selectin")


class HuntFinding(Base):
    """Evidence discovered during a hunt."""

    __tablename__ = "hunt_findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hypothesis_id = Column(UUID(as_uuid=True), ForeignKey("hunt_hypotheses.id", ondelete="CASCADE"), nullable=False)
    severity = Column(String(30), default="medium", nullable=False)
    details = Column(Text, nullable=False)
    status = Column(String(40), default="new", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    hypothesis = relationship("HuntHypothesis", back_populates="findings")
    detection_rule = relationship("DetectionRule", back_populates="source_finding", uselist=False)


class DetectionRule(Base):
    """Detection rule drafted or deployed from findings."""

    __tablename__ = "detection_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(180), nullable=False)
    query = Column(Text, nullable=False)
    status = Column(String(30), default="Draft", nullable=False)
    source_finding_id = Column(UUID(as_uuid=True), ForeignKey("hunt_findings.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    source_finding = relationship("HuntFinding", back_populates="detection_rule")


# =============================================================================
# Project 9 - Advanced Malware Analysis & Reverse Engineering
# =============================================================================


class MalwareSample(Base):
    """Malware sample metadata."""

    __tablename__ = "malware_samples"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    file_hash = Column(String(128), unique=True, nullable=False)
    sample_type = Column(String(80), default="unknown", nullable=False)
    family = Column(String(120), nullable=True)
    status = Column(String(40), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    report = relationship("AnalysisReport", back_populates="sample", uselist=False, cascade="all, delete-orphan")


class AnalysisReport(Base):
    """Simulated analysis results including heuristics and YARA rules."""

    __tablename__ = "analysis_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("malware_samples.id", ondelete="CASCADE"), nullable=False)
    static_analysis = Column(Text, nullable=False)
    dynamic_analysis = Column(Text, nullable=False)
    iocs = Column(JSON, nullable=True)
    yara_rule = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sample = relationship("MalwareSample", back_populates="report")


# =============================================================================
# Project 10 - Enterprise EDR Platform Simulation
# =============================================================================


class EndpointAsset(Base):
    """Endpoint managed by the simulated EDR platform."""

    __tablename__ = "endpoint_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname = Column(String(120), nullable=False, unique=True)
    operating_system = Column(String(80), nullable=False)
    agent_version = Column(String(40), nullable=False)
    last_checkin = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    online = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    alerts = relationship("EndpointAlert", back_populates="endpoint", cascade="all, delete-orphan", lazy="selectin")


class EndpointPolicy(Base):
    """Policy that can be toggled for endpoints."""

    __tablename__ = "endpoint_policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)


class EndpointAlert(Base):
    """Alert generated for an endpoint heartbeat or registration."""

    __tablename__ = "endpoint_alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoint_assets.id", ondelete="CASCADE"), nullable=True)
    severity = Column(String(20), default="medium", nullable=False)
    status = Column(String(40), default="open", nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    endpoint = relationship("EndpointAsset", back_populates="alerts")

    __table_args__ = (
        Index("ix_endpoint_alert_status", "status"),
    )

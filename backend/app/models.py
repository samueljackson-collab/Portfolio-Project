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
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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
        UniqueConstraint("owner_id", "name", name="uq_albums_owner_name"),
        Index("ix_albums_owner_type", "owner_id", "type"),
        Index("ix_albums_owner_updated", "owner_id", "updated_at"),
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

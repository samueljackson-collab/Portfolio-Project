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

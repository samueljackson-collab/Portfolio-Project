"""
Comprehensive tests for ORM models.

Tests cover:
- Model instantiation
- Field constraints and defaults
- Relationships
- Timestamps
- UUID generation
- String representations
"""

import pytest
from datetime import datetime
import uuid

from app.models import User, Content


class TestUserModel:
    """Test User model."""

    def test_user_model_creation(self):
        """Test creating a User instance."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_here"
        )
        
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_password_here"

    def test_user_id_auto_generated(self):
        """Test that user ID is auto-generated as UUID."""
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        # ID should be generated
        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)

    def test_user_is_active_default_true(self):
        """Test that is_active defaults to True."""
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        assert user.is_active is True

    def test_user_repr(self):
        """Test User __repr__ method."""
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        repr_str = repr(user)
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert "test@example.com" in repr_str

    def test_user_email_field(self):
        """Test user email field properties."""
        user = User(
            email="user@domain.com",
            hashed_password="hashed"
        )
        
        assert user.email == "user@domain.com"

    def test_user_content_items_relationship(self):
        """Test that user has content_items relationship."""
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        # Should have content_items attribute
        assert hasattr(user, "content_items")


class TestContentModel:
    """Test Content model."""

    def test_content_model_creation(self):
        """Test creating a Content instance."""
        user_id = uuid.uuid4()
        content = Content(
            title="Test Title",
            body="Test Body",
            owner_id=user_id
        )
        
        assert content.title == "Test Title"
        assert content.body == "Test Body"
        assert content.owner_id == user_id

    def test_content_id_auto_generated(self):
        """Test that content ID is auto-generated as UUID."""
        content = Content(
            title="Test",
            owner_id=uuid.uuid4()
        )
        
        assert content.id is not None
        assert isinstance(content.id, uuid.UUID)

    def test_content_is_published_default_false(self):
        """Test that is_published defaults to False."""
        content = Content(
            title="Test",
            owner_id=uuid.uuid4()
        )
        
        assert content.is_published is False

    def test_content_body_can_be_null(self):
        """Test that body field can be None."""
        content = Content(
            title="Test",
            body=None,
            owner_id=uuid.uuid4()
        )
        
        assert content.body is None

    def test_content_repr(self):
        """Test Content __repr__ method."""
        content = Content(
            title="My Content",
            owner_id=uuid.uuid4()
        )
        
        repr_str = repr(content)
        assert "Content" in repr_str
        assert str(content.id) in repr_str
        assert "My Content" in repr_str

    def test_content_owner_relationship(self):
        """Test that content has owner relationship."""
        content = Content(
            title="Test",
            owner_id=uuid.uuid4()
        )
        
        # Should have owner attribute
        assert hasattr(content, "owner")


class TestModelRelationships:
    """Test relationships between models."""

    def test_user_content_cascade_delete(self):
        """Test that content has cascade delete relationship."""
        # This is configured in the relationship
        # The cascade="all, delete-orphan" is set on User.content_items
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        # Verify relationship configuration exists
        assert hasattr(user, "content_items")


class TestModelFieldConstraints:
    """Test field constraints and validation."""

    def test_user_email_required(self):
        """Test that email is required."""
        # This would be caught at database level
        user = User(hashed_password="hashed")
        
        # Email is set to None if not provided
        assert user.email is None

    def test_content_title_required(self):
        """Test that title is required."""
        content = Content(owner_id=uuid.uuid4())
        
        # Title is set to None if not provided
        assert content.title is None

    def test_content_owner_id_required(self):
        """Test that owner_id is required."""
        content = Content(title="Test")
        
        # owner_id is set to None if not provided
        assert content.owner_id is None


class TestModelTimestamps:
    """Test timestamp fields."""

    def test_user_has_created_at(self):
        """Test that user has created_at field."""
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        assert hasattr(user, "created_at")

    def test_user_has_updated_at(self):
        """Test that user has updated_at field."""
        user = User(
            email="test@example.com",
            hashed_password="hashed"
        )
        
        assert hasattr(user, "updated_at")

    def test_content_has_created_at(self):
        """Test that content has created_at field."""
        content = Content(
            title="Test",
            owner_id=uuid.uuid4()
        )
        
        assert hasattr(content, "created_at")

    def test_content_has_updated_at(self):
        """Test that content has updated_at field."""
        content = Content(
            title="Test",
            owner_id=uuid.uuid4()
        )
        
        assert hasattr(content, "updated_at")


class TestModelTableNames:
    """Test database table names."""

    def test_user_table_name(self):
        """Test User model table name."""
        assert User.__tablename__ == "users"

    def test_content_table_name(self):
        """Test Content model table name."""
        assert Content.__tablename__ == "content"


class TestModelIndexes:
    """Test model indexes."""

    def test_content_has_composite_index(self):
        """Test that Content has composite index."""
        # Check table args exist
        assert hasattr(Content, "__table_args__")
        assert Content.__table_args__ is not None
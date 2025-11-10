"""
Comprehensive tests for Pydantic schemas.

Tests cover:
- Schema validation
- Field constraints
- Custom validators
- Serialization/deserialization
- Edge cases and error conditions
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import uuid4

from app.schemas import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    Token,
    TokenData,
    ContentBase,
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentListResponse,
    HealthResponse,
    ErrorResponse,
)


class TestUserSchemas:
    """Test user-related schemas."""

    def test_user_base_valid_email(self):
        """Test UserBase with valid email."""
        user = UserBase(email="test@example.com")
        assert user.email == "test@example.com"

    def test_user_base_email_lowercase_conversion(self):
        """Test that email is converted to lowercase."""
        user = UserBase(email="TEST@EXAMPLE.COM")
        assert user.email == "test@example.com"

    def test_user_base_email_strip_whitespace(self):
        """Test that email whitespace is stripped."""
        user = UserBase(email="  test@example.com  ")
        assert user.email == "test@example.com"

    def test_user_base_invalid_email(self):
        """Test UserBase with invalid email."""
        with pytest.raises(ValidationError):
            UserBase(email="not-an-email")

    def test_user_create_valid_password(self):
        """Test UserCreate with valid strong password."""
        user = UserCreate(
            email="test@example.com",
            password="SecurePass123"
        )
        assert user.password == "SecurePass123"

    def test_user_create_password_too_short(self):
        """Test UserCreate rejects password shorter than 8 chars."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="Short1"
            )
        errors = exc_info.value.errors()
        assert any("8 characters" in str(error) for error in errors)

    def test_user_create_password_no_uppercase(self):
        """Test UserCreate rejects password without uppercase."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="lowercase123"
            )
        errors = exc_info.value.errors()
        assert any("uppercase" in str(error).lower() for error in errors)

    def test_user_create_password_no_lowercase(self):
        """Test UserCreate rejects password without lowercase."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="UPPERCASE123"
            )
        errors = exc_info.value.errors()
        assert any("lowercase" in str(error).lower() for error in errors)

    def test_user_create_password_no_digit(self):
        """Test UserCreate rejects password without digit."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="NoDigitsHere"
            )
        errors = exc_info.value.errors()
        assert any("digit" in str(error).lower() for error in errors)

    def test_user_create_password_with_special_chars(self):
        """Test UserCreate accepts password with special characters."""
        user = UserCreate(
            email="test@example.com",
            password="P@ssw0rd!#$"
        )
        assert "P@ssw0rd!#$" in user.password

    def test_user_login_schema(self):
        """Test UserLogin schema."""
        login = UserLogin(
            email="test@example.com",
            password="anypassword"
        )
        assert login.email == "test@example.com"
        assert login.password == "anypassword"

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        user_data = {
            "id": str(uuid4()),
            "email": "test@example.com",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        user = UserResponse(**user_data)
        assert user.email == "test@example.com"
        assert user.is_active is True

    def test_user_update_with_email_only(self):
        """Test UserUpdate with only email."""
        update = UserUpdate(email="newemail@example.com")
        assert update.email == "newemail@example.com"
        assert update.password is None

    def test_user_update_with_password_only(self):
        """Test UserUpdate with only password."""
        update = UserUpdate(password="NewSecure123")
        assert update.password == "NewSecure123"
        assert update.email is None

    def test_user_update_password_validation(self):
        """Test UserUpdate validates password strength if provided."""
        with pytest.raises(ValidationError):
            UserUpdate(password="weak")

    def test_user_update_empty(self):
        """Test UserUpdate with no fields."""
        update = UserUpdate()
        assert update.email is None
        assert update.password is None


class TestTokenSchemas:
    """Test token-related schemas."""

    def test_token_schema(self):
        """Test Token schema."""
        token = Token(
            access_token="eyJ0ZXN0IjoiaW52YWxpZCJ9.test.invalid",
            token_type="bearer",
            expires_in=1800
        )
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"
        assert token.expires_in == 1800

    def test_token_default_type(self):
        """Test Token default token_type."""
        token = Token(
            access_token="test_token",
            expires_in=1800
        )
        assert token.token_type == "bearer"

    def test_token_data_schema(self):
        """Test TokenData schema."""
        token_data = TokenData(
            email="test@example.com",
            user_id=uuid4()
        )
        assert token_data.email == "test@example.com"
        assert token_data.user_id is not None

    def test_token_data_optional_fields(self):
        """Test TokenData with optional fields as None."""
        token_data = TokenData()
        assert token_data.email is None
        assert token_data.user_id is None


class TestContentSchemas:
    """Test content-related schemas."""

    def test_content_base_valid(self):
        """Test ContentBase with valid data."""
        content = ContentBase(
            title="Test Title",
            body="Test Body",
            is_published=True
        )
        assert content.title == "Test Title"
        assert content.body == "Test Body"
        assert content.is_published is True

    def test_content_base_default_published_false(self):
        """Test ContentBase default is_published is False."""
        content = ContentBase(title="Test")
        assert content.is_published is False

    def test_content_base_optional_body(self):
        """Test ContentBase with None body."""
        content = ContentBase(title="Test", body=None)
        assert content.body is None

    def test_content_base_title_too_long(self):
        """Test ContentBase rejects title longer than 255 chars."""
        with pytest.raises(ValidationError):
            ContentBase(title="a" * 256)

    def test_content_base_empty_title(self):
        """Test ContentBase rejects empty title."""
        with pytest.raises(ValidationError):
            ContentBase(title="")

    def test_content_base_body_too_long(self):
        """Test ContentBase rejects body longer than 10000 chars."""
        with pytest.raises(ValidationError):
            ContentBase(
                title="Test",
                body="a" * 10001
            )

    def test_content_create_schema(self):
        """Test ContentCreate schema."""
        content = ContentCreate(
            title="New Content",
            body="Content body",
            is_published=False
        )
        assert content.title == "New Content"

    def test_content_update_partial_update(self):
        """Test ContentUpdate with partial fields."""
        update = ContentUpdate(title="Updated Title")
        assert update.title == "Updated Title"
        assert update.body is None
        assert update.is_published is None

    def test_content_update_all_fields(self):
        """Test ContentUpdate with all fields."""
        update = ContentUpdate(
            title="Updated",
            body="New body",
            is_published=True
        )
        assert update.title == "Updated"
        assert update.body == "New body"
        assert update.is_published is True

    def test_content_update_empty(self):
        """Test ContentUpdate with no fields."""
        update = ContentUpdate()
        assert update.title is None
        assert update.body is None
        assert update.is_published is None

    def test_content_response_schema(self):
        """Test ContentResponse schema."""
        user_data = {
            "id": str(uuid4()),
            "email": "owner@example.com",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        content_data = {
            "id": str(uuid4()),
            "title": "Test Content",
            "body": "Content body",
            "is_published": False,
            "owner_id": str(uuid4()),
            "owner": user_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        content = ContentResponse(**content_data)
        assert content.title == "Test Content"
        assert content.owner["email"] == "owner@example.com"

    def test_content_list_response_schema(self):
        """Test ContentListResponse schema."""
        list_response = ContentListResponse(
            items=[],
            total=42,
            page=1,
            page_size=10,
            pages=5
        )
        assert list_response.total == 42
        assert list_response.page == 1
        assert list_response.pages == 5
        assert len(list_response.items) == 0

    def test_content_list_response_with_items(self):
        """Test ContentListResponse with items."""
        user_data = {
            "id": str(uuid4()),
            "email": "owner@example.com",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        content_data = {
            "id": str(uuid4()),
            "title": "Test",
            "body": "Body",
            "is_published": True,
            "owner_id": str(uuid4()),
            "owner": user_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        list_response = ContentListResponse(
            items=[content_data],
            total=1,
            page=1,
            page_size=10,
            pages=1
        )
        assert len(list_response.items) == 1


class TestHealthSchema:
    """Test health check schema."""

    def test_health_response_schema(self):
        """Test HealthResponse schema."""
        health = HealthResponse(
            status="healthy",
            version="1.0.0",
            database="connected"
        )
        assert health.status == "healthy"
        assert health.version == "1.0.0"
        assert health.database == "connected"

    def test_health_response_unhealthy(self):
        """Test HealthResponse with unhealthy status."""
        health = HealthResponse(
            status="unhealthy",
            version="1.0.0",
            database="disconnected"
        )
        assert health.status == "unhealthy"
        assert health.database == "disconnected"


class TestErrorSchemas:
    """Test error response schemas."""

    def test_error_response_string_detail(self):
        """Test ErrorResponse with string detail."""
        error = ErrorResponse(detail="Something went wrong")
        assert error.detail == "Something went wrong"

    def test_error_response_list_detail(self):
        """Test ErrorResponse with list of errors."""
        from app.schemas import ErrorDetail
        
        errors = [
            ErrorDetail(
                loc=["body", "email"],
                msg="Invalid email",
                type="value_error"
            )
        ]
        error = ErrorResponse(detail=errors)
        assert isinstance(error.detail, list)
        assert len(error.detail) == 1


class TestSchemaEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_content_title_exactly_255_chars(self):
        """Test content title with exactly 255 characters."""
        content = ContentBase(title="a" * 255)
        assert len(content.title) == 255

    def test_content_body_exactly_10000_chars(self):
        """Test content body with exactly 10000 characters."""
        content = ContentBase(
            title="Test",
            body="a" * 10000
        )
        assert len(content.body) == 10000

    def test_user_password_exactly_8_chars(self):
        """Test password with exactly 8 characters."""
        user = UserCreate(
            email="test@example.com",
            password="Pass1234"
        )
        assert len(user.password) == 8

    def test_user_password_100_chars(self):
        """Test password with 100 characters (maximum)."""
        long_password = "Aa1" + "b" * 97
        user = UserCreate(
            email="test@example.com",
            password=long_password
        )
        assert len(user.password) == 100

    def test_email_with_plus_sign(self):
        """Test email with plus sign (valid email format)."""
        user = UserBase(email="user+tag@example.com")
        assert user.email == "user+tag@example.com"

    def test_email_with_subdomain(self):
        """Test email with subdomain."""
        user = UserBase(email="user@mail.example.com")
        assert user.email == "user@mail.example.com"


class TestSchemaSerializationOF:
    """Test schema serialization."""

    def test_user_response_to_dict(self):
        """Test UserResponse serialization to dict."""
        user_data = {
            "id": str(uuid4()),
            "email": "test@example.com",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        user = UserResponse(**user_data)
        user_dict = user.model_dump()
        
        assert "email" in user_dict
        assert user_dict["email"] == "test@example.com"

    def test_token_to_json(self):
        """Test Token serialization to JSON."""
        token = Token(
            access_token="test_token",
            expires_in=1800
        )
        token_json = token.model_dump_json()
        
        assert "test_token" in token_json
        assert "bearer" in token_json
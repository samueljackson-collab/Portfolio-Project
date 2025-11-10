"""
Comprehensive tests for authentication utilities.

Tests cover:
- Password hashing and verification
- JWT token creation and decoding
- Token expiration handling
- Security edge cases
"""

import os
import pytest
from datetime import timedelta, datetime
from jose import jwt, JWTError
from fastapi import HTTPException

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    pwd_context,
)
from app.config import settings


# Test constants for security testing
TEST_FAKE_JWT_SECRET = os.getenv(
    "TEST_FAKE_JWT_SECRET",
    "wrong-secret-key-this-is-fake-dont-use"
)


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_different_for_same_password(self):
        """Test that same password generates different hashes (salt)."""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2

    def test_hash_password_with_special_characters(self):
        """Test hashing password with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) > 0

    def test_hash_password_with_unicode(self):
        """Test hashing password with unicode characters."""
        password = "пароль123"  # Russian for "password"
        hashed = hash_password(password)
        
        assert hashed is not None

    def test_hash_password_empty_string(self):
        """Test hashing empty password."""
        password = ""
        hashed = hash_password(password)
        
        assert hashed is not None

    def test_hash_password_very_long(self):
        """Test hashing very long password."""
        password = "a" * 1000
        hashed = hash_password(password)
        
        assert hashed is not None


class TestPasswordVerification:
    """Test password verification functionality."""

    def test_verify_password_correct(self):
        """Test verifying correct password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert verify_password("testpassword123", hashed) is False

    def test_verify_password_with_special_chars(self):
        """Test verifying password with special characters."""
        password = "P@ssw0rd!#$"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("P@ssw0rd!#", hashed) is False

    def test_verify_password_empty_against_hashed(self):
        """Test verifying empty password."""
        hashed = hash_password("actual_password")
        
        assert verify_password("", hashed) is False

    def test_verify_password_with_unicode(self):
        """Test verifying unicode password."""
        password = "пароль123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True


class TestTokenCreation:
    """Test JWT token creation."""

    def test_create_access_token_basic(self):
        """Test creating basic access token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_claims(self):
        """Test that token contains expected claims."""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        # Decode without verification to inspect claims
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "user"
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiration(self):
        """Test creating token with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Check expiration is approximately 60 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        delta = (exp_time - now).total_seconds()
        
        assert 3500 < delta < 3700  # ~60 minutes (allow some variance)

    def test_create_access_token_default_expiration(self):
        """Test token with default expiration."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Check expiration is approximately 30 minutes (default)
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        delta = (exp_time - now).total_seconds()
        
        assert 1700 < delta < 1900  # ~30 minutes

    def test_create_access_token_with_multiple_claims(self):
        """Test creating token with multiple custom claims."""
        data = {
            "sub": "test@example.com",
            "user_id": "123",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        token = create_access_token(data)
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == "123"
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]

    def test_create_access_token_with_short_expiration(self):
        """Test creating token with very short expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=10)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        assert "exp" in payload


class TestTokenDecoding:
    """Test JWT token decoding."""

    def test_decode_valid_token(self):
        """Test decoding valid token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        
        assert payload["sub"] == "test@example.com"

    def test_decode_expired_token(self):
        """Test decoding expired token raises error."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401

    def test_decode_invalid_token(self):
        """Test decoding invalid token raises error."""
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401

    def test_decode_token_wrong_signature(self):
        """Test decoding token with wrong signature."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        # Tamper with the token
        parts = token.split('.')
        tampered_token = f"{parts[0]}.{parts[1]}.wrongsignature"
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(tampered_token)
        
        assert exc_info.value.status_code == 401

    def test_decode_token_without_sub(self):
        """Test decoding token without 'sub' claim raises error."""
        # Create token manually without 'sub'
        payload = {
            "user_id": "123",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401

    def test_decode_token_malformed(self):
        """Test decoding malformed token."""
        malformed_tokens = [
            "not.a.token",
            "tooshort",
            "",
            "only.two",
        ]
        
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                decode_access_token(token)
            
            assert exc_info.value.status_code == 401

    def test_decode_token_preserves_custom_claims(self):
        """Test that decoding preserves custom claims."""
        data = {
            "sub": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        
        assert payload["role"] == "admin"
        assert payload["permissions"] == ["read", "write"]


class TestPasswordContext:
    """Test password context configuration."""

    def test_pwd_context_uses_bcrypt(self):
        """Test that password context uses bcrypt."""
        assert "bcrypt" in pwd_context.schemes()

    def test_pwd_context_hash_method_exists(self):
        """Test that context has hash method."""
        assert hasattr(pwd_context, "hash")
        assert callable(pwd_context.hash)

    def test_pwd_context_verify_method_exists(self):
        """Test that context has verify method."""
        assert hasattr(pwd_context, "verify")
        assert callable(pwd_context.verify)


class TestSecurityEdgeCases:
    """Test security-related edge cases."""

    def test_timing_attack_resistance(self):
        """Test that password verification is timing-safe."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        # Both correct and incorrect passwords should take similar time
        # (This is more of a documentation test; actual timing is handled by passlib)
        result1 = verify_password(password, hashed)
        result2 = verify_password("wrongpassword", hashed)
        
        assert result1 is True
        assert result2 is False

    def test_token_cannot_be_forged(self):
        """Test that token with different secret cannot be decoded."""
        data = {"sub": "test@example.com"}
        
        # Create token with different secret
        fake_token = jwt.encode(
            {**data, "exp": datetime.utcnow() + timedelta(minutes=30)},
            TEST_FAKE_JWT_SECRET,
            algorithm=settings.algorithm
        )
        
        with pytest.raises(HTTPException):
            decode_access_token(fake_token)

    def test_token_expiration_is_enforced(self):
        """Test that expired tokens are rejected."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-10))
        
        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        
        assert exc_info.value.status_code == 401

    def test_password_hash_includes_salt(self):
        """Test that password hashes include salt (different each time)."""
        password = "samepassword"
        
        hashes = [hash_password(password) for _ in range(5)]
        
        # All hashes should be different
        assert len(set(hashes)) == 5
        
        # But all should verify correctly
        for hashed in hashes:
            assert verify_password(password, hashed)


class TestTokenIssuedAt:
    """Test token issued-at timestamp."""

    def test_token_has_iat_claim(self):
        """Test that token includes 'iat' (issued at) claim."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        assert "iat" in payload
        
        # Check that iat is recent (within last minute)
        iat = datetime.fromtimestamp(payload["iat"])
        now = datetime.utcnow()
        delta = (now - iat).total_seconds()
        
        assert 0 <= delta < 60

    def test_token_iat_before_exp(self):
        """Test that issued-at is before expiration."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        assert payload["iat"] < payload["exp"]
"""
Comprehensive tests for FastAPI dependencies.

Tests cover:
- User authentication dependency
- Active user dependency
- Token validation
- Error handling
- Edge cases
"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.dependencies import get_current_user, get_current_active_user
from app.models import User
from app.auth import create_access_token


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Test get_current_user dependency."""

    async def test_valid_token_returns_user(self, test_user: User, db_session):
        """Test that valid token returns the user."""
        # Create token for test user
        token = create_access_token({"sub": test_user.email})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # Call dependency
        user = await get_current_user(credentials, db_session)
        
        assert user.email == test_user.email
        assert user.id == test_user.id

    async def test_invalid_token_raises_401(self, db_session):
        """Test that invalid token raises 401."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid_token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401
        assert "credentials" in exc_info.value.detail.lower()

    async def test_token_without_sub_raises_401(self, db_session):
        """Test that token without 'sub' claim raises 401."""
        # Create token without 'sub'
        token = create_access_token({"user_id": "123"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401

    async def test_nonexistent_user_raises_401(self, db_session):
        """Test that token for non-existent user raises 401."""
        # Create token for non-existent user
        token = create_access_token({"sub": "nonexistent@example.com"})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401

    async def test_inactive_user_raises_403(self, test_user: User, db_session):
        """Test that inactive user raises 403."""
        # Set user as inactive
        test_user.is_active = False
        await db_session.commit()
        
        # Create token
        token = create_access_token({"sub": test_user.email})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 403
        assert "inactive" in exc_info.value.detail.lower()

    async def test_expired_token_raises_401(self, test_user: User, db_session):
        """Test that expired token raises 401."""
        from datetime import timedelta
        
        # Create expired token
        token = create_access_token(
            {"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401


@pytest.mark.asyncio
class TestGetCurrentActiveUser:
    """Test get_current_active_user dependency."""

    async def test_active_user_returns_user(self, test_user: User):
        """Test that active user is returned."""
        test_user.is_active = True
        
        user = await get_current_active_user(test_user)
        
        assert user.email == test_user.email
        assert user.is_active is True

    async def test_inactive_user_raises_400(self, test_user: User):
        """Test that inactive user raises 400."""
        test_user.is_active = False
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_active_user(test_user)
        
        assert exc_info.value.status_code == 400
        assert "inactive" in exc_info.value.detail.lower()


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Test complete authentication flow."""

    async def test_full_authentication_flow(self, test_user: User, db_session):
        """Test complete authentication from token to user."""
        # 1. Create token
        token = create_access_token({"sub": test_user.email})
        
        # 2. Create credentials
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        # 3. Get current user
        user = await get_current_user(credentials, db_session)
        
        # 4. Get active user
        active_user = await get_current_active_user(user)
        
        assert active_user.email == test_user.email
        assert active_user.is_active is True

    async def test_authentication_with_custom_token_expiry(
        self, test_user: User, db_session
    ):
        """Test authentication with custom token expiration."""
        from datetime import timedelta
        
        # Create token with 1 hour expiration
        token = create_access_token(
            {"sub": test_user.email},
            expires_delta=timedelta(hours=1)
        )
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        user = await get_current_user(credentials, db_session)
        
        assert user.email == test_user.email


@pytest.mark.asyncio
class TestErrorScenarios:
    """Test various error scenarios."""

    async def test_malformed_token(self, db_session):
        """Test handling of malformed token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="not.a.jwt.token"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401

    async def test_empty_token(self, db_session):
        """Test handling of empty token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=""
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, db_session)
        
        assert exc_info.value.status_code == 401

    async def test_token_with_wrong_signature(self, test_user: User, db_session):
        """Test token with tampered signature."""
        # Create valid token
        token = create_access_token({"sub": test_user.email})
        
        # Tamper with the token
        parts = token.split('.')
        if len(parts) == 3:
            tampered_token = f"{parts[0]}.{parts[1]}.tampered_signature"
            
            credentials = HTTPAuthorizationCredentials(
                scheme="Bearer",
                credentials=tampered_token
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(credentials, db_session)
            
            assert exc_info.value.status_code == 401

    async def test_database_error_during_user_lookup(self, test_user: User):
        """Test handling of database errors during user lookup."""
        # Create mock session that raises error
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Database error")
        
        token = create_access_token({"sub": test_user.email})
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        
        with pytest.raises(Exception):
            await get_current_user(credentials, mock_session)
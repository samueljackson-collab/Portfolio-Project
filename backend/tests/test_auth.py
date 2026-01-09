"""
Tests for authentication endpoints.

This module tests:
- User registration
- User login with JWT tokens
- Current user retrieval
- Authentication errors
"""

import pytest
from httpx import AsyncClient
from app.models import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, sample_user_data: dict):
    """Test successful user registration."""
    response = await client.post("/auth/register", json=sample_user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == sample_user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, test_user: User, sample_user_data: dict
):
    """Test registration with duplicate email fails."""
    # Try to register with existing email
    sample_user_data["email"] = test_user.email

    response = await client.post("/auth/register", json=sample_user_data)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email format."""
    response = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "securepassword123"},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    """Test registration with password that's too short."""
    response = await client.post(
        "/auth/register", json={"email": "test@example.com", "password": "short"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login with valid credentials."""
    response = await client.post(
        "/auth/login", data={"username": test_user.email, "password": "testpassword123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """Test login with incorrect password."""
    response = await client.post(
        "/auth/login", data={"username": test_user.email, "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent email."""
    response = await client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "anypassword"},
    )

    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user(authenticated_client: AsyncClient, test_user: User):
    """Test retrieving current user information with valid token."""
    response = await authenticated_client.get("/auth/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == str(test_user.id)
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test accessing protected endpoint without authentication."""
    response = await client.get("/auth/me")

    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test accessing protected endpoint with invalid token."""
    client.headers.update({"Authorization": "Bearer invalid_token_here"})
    response = await client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_form_data(client: AsyncClient, test_user: User):
    """Test login accepts form data (OAuth2 spec compliance)."""
    response = await client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "testpassword123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

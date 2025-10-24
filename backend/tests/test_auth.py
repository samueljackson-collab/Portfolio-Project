"""Authentication flow tests covering registration and login endpoints."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.auth import create_access_token, decode_access_token, hash_password, verify_password
from app.models import User


@pytest.mark.auth
def test_hash_and_verify_password_round_trip() -> None:
    """Plain passwords should hash and verify using bcrypt."""
    plain = "StrongPass123!"
    hashed = hash_password(plain)

    assert hashed != plain
    assert hashed.startswith("$2b$")
    assert verify_password(plain, hashed)


@pytest.mark.auth
async def test_register_and_login_flow(client, session_factory) -> None:
    """Register a user, log in, and fetch the authenticated profile."""
    payload = {"email": "flow@example.com", "password": "FlowPass123!"}

    register_response = await client.post("/auth/register", json=payload)
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["email"] == payload["email"].lower()
    assert register_body["is_active"] is True

    async with session_factory() as session:
        result = await session.execute(select(User).where(User.email == payload["email"].lower()))
        user = result.scalar_one()
        assert user.hashed_password != payload["password"]

    login_response = await client.post("/auth/login", json=payload)
    assert login_response.status_code == 200
    token_payload = login_response.json()
    token = token_payload["access_token"]
    assert token_payload["token_type"] == "bearer"

    decoded = decode_access_token(token)
    assert decoded["sub"] == payload["email"].lower()

    profile_response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_response.status_code == 200
    profile_body = profile_response.json()
    assert profile_body["email"] == payload["email"].lower()


@pytest.mark.auth
async def test_login_rejects_invalid_credentials(client, create_user) -> None:
    """An incorrect password should yield HTTP 401."""
    user, _ = await create_user(email="existing@example.com")

    response = await client.post(
        "/auth/login",
        json={"email": user.email, "password": "WrongPassword999!"},
    )
    assert response.status_code == 401


@pytest.mark.auth
async def test_register_rejects_duplicate_email(client, create_user) -> None:
    """Attempting to reuse an email address should raise HTTP 400."""
    user, password = await create_user(email="duplicate@example.com")

    duplicate_attempt = await client.post(
        "/auth/register",
        json={"email": user.email, "password": password},
    )
    assert duplicate_attempt.status_code == 400


@pytest.mark.auth
def test_decode_access_token_with_invalid_signature() -> None:
    """Tokens signed with the wrong secret should raise HTTP 401."""
    token = create_access_token({"sub": "user@example.com"})

    with pytest.raises(HTTPException):
        decode_access_token(token + "tampered")

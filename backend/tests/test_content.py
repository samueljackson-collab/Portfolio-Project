"""Tests for content CRUD API endpoints."""

from __future__ import annotations

import pytest
from sqlalchemy import select

from app.auth import create_access_token
from app.models import Content


@pytest.mark.content
async def test_create_content_requires_authentication(client) -> None:
    """Unauthenticated users should receive 401 when creating content."""
    response = await client.post(
        "/content",
        json={"title": "Unauthorized", "body": "Should fail", "is_published": True},
    )
    assert response.status_code == 401


@pytest.mark.content
async def test_create_content_persists_and_returns_item(client, authenticated_user) -> None:
    """Authenticated users can create content and receive persisted data."""
    user, headers = authenticated_user
    payload = {"title": "First Post", "body": "Hello", "is_published": True}

    response = await client.post("/content", json=payload, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == payload["title"]
    assert body["owner_id"] == str(user.id)


@pytest.mark.content
async def test_list_content_filters_unpublished_for_anonymous_users(
    client, create_content, create_user
) -> None:
    """Anonymous requests should not see unpublished content from others."""
    owner, _ = await create_user(email="owner@example.com")
    await create_content(owner=owner, title="Draft", is_published=False)
    await create_content(owner=owner, title="Published", is_published=True)

    response = await client.get("/content")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Published"


@pytest.mark.content
async def test_list_content_includes_unpublished_for_owner(
    client, authenticated_user, create_content
) -> None:
    """Authenticated owners should see their unpublished drafts."""
    user, headers = authenticated_user
    await create_content(owner=user, title="Draft", is_published=False)

    response = await client.get("/content", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Draft"


@pytest.mark.content
async def test_update_content_requires_ownership(
    client, authenticated_user, create_content, create_user
) -> None:
    """Updating content should be limited to the owner."""
    owner, owner_headers = authenticated_user
    content = await create_content(owner=owner, title="Original", is_published=True)

    intruder, _ = await create_user(email="intruder@example.com")
    intruder_token = create_access_token({"sub": intruder.email})
    intruder_headers = {"Authorization": f"Bearer {intruder_token}"}

    forbidden = await client.put(
        f"/content/{content.id}",
        json={"title": "Hacked"},
        headers=intruder_headers,
    )
    assert forbidden.status_code == 403

    allowed = await client.put(
        f"/content/{content.id}",
        json={"title": "Updated"},
        headers=owner_headers,
    )
    assert allowed.status_code == 200
    assert allowed.json()["title"] == "Updated"


@pytest.mark.content
async def test_delete_content_removes_record(
    client, authenticated_user, create_content, session_factory
) -> None:
    """Owners can delete their content permanently."""
    user, headers = authenticated_user
    content = await create_content(owner=user, title="Disposable", is_published=True)

    response = await client.delete(f"/content/{content.id}", headers=headers)
    assert response.status_code == 204

    async with session_factory() as session:
        result = await session.execute(select(Content).where(Content.id == content.id))
        assert result.scalar_one_or_none() is None

"""
Tests for content CRUD endpoints.

This module tests:
- Content listing with pagination
- Content retrieval
- Content creation (authenticated)
- Content update (owner only)
- Content deletion (owner only)
- Authorization checks
"""

import pytest
from httpx import AsyncClient
from app.models import User, Content


@pytest.mark.asyncio
async def test_list_content_empty(client: AsyncClient):
    """Test listing content when database is empty."""
    response = await client.get("/content")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_content(client: AsyncClient, test_content: Content):
    """Test listing content items."""
    response = await client.get("/content")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert data["total"] >= 1
    assert any(item["id"] == str(test_content.id) for item in data["items"])


@pytest.mark.asyncio
async def test_list_content_pagination(
    client: AsyncClient,
    test_db,
    test_user: User
):
    """Test content listing with pagination."""
    # Create multiple content items
    for i in range(15):
        content = Content(
            title=f"Content {i}",
            body=f"Body {i}",
            owner_id=test_user.id,
            is_published=True
        )
        test_db.add(content)
    await test_db.commit()

    # Test first page
    response = await client.get("/content", params={"page": 1, "page_size": 10})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10

    # Test second page
    response = await client.get("/content", params={"page": 2, "page_size": 10})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5  # Remaining items


@pytest.mark.asyncio
async def test_get_content_by_id(client: AsyncClient, test_content: Content):
    """Test retrieving a specific content item by ID."""
    response = await client.get(f"/content/{test_content.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_content.id)
    assert data["title"] == test_content.title
    assert data["body"] == test_content.body


@pytest.mark.asyncio
async def test_public_content_accessible_without_auth(
    client: AsyncClient,
    test_content: Content
):
    """Ensure published content is accessible without credentials."""

    list_response = await client.get("/content")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert any(item["id"] == str(test_content.id) for item in list_data["items"])

    detail_response = await client.get(f"/content/{test_content.id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == str(test_content.id)


@pytest.mark.asyncio
async def test_private_content_requires_auth(
    client: AsyncClient,
    authenticated_client: AsyncClient,
    test_db,
    test_user: User
):
    """Verify private content stays hidden without authentication."""

    private_content = Content(
        title="Private Article",
        body="Hidden text",
        owner_id=test_user.id,
        is_published=False
    )
    test_db.add(private_content)
    await test_db.commit()
    await test_db.refresh(private_content)

    # Unauthenticated users should not see the private item in listings
    list_response = await client.get("/content", params={"page": 1, "page_size": 10, "published_only": False})
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert all(item["id"] != str(private_content.id) for item in list_data["items"])

    # Unauthenticated detail requests should return 404
    detail_response = await client.get(f"/content/{private_content.id}")
    assert detail_response.status_code == 404

    # Owner can access after authenticating
    authed_detail = await authenticated_client.get(f"/content/{private_content.id}")
    assert authed_detail.status_code == 200
    assert authed_detail.json()["id"] == str(private_content.id)


@pytest.mark.asyncio
async def test_get_content_not_found(client: AsyncClient):
    """Test retrieving non-existent content returns 404."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/content/{fake_uuid}")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_content_invalid_uuid(client: AsyncClient):
    """Test retrieving content with invalid UUID format."""
    response = await client.get("/content/not-a-uuid")

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_content(
    authenticated_client: AsyncClient,
    sample_content_data: dict
):
    """Test creating new content (authenticated user)."""
    response = await authenticated_client.post(
        "/content",
        json=sample_content_data
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_content_data["title"]
    assert data["body"] == sample_content_data["body"]
    assert data["is_published"] == sample_content_data["is_published"]
    assert "id" in data
    assert "owner_id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_content_unauthorized(
    client: AsyncClient,
    sample_content_data: dict
):
    """Test creating content without authentication fails."""
    response = await client.post("/content", json=sample_content_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_content_missing_title(authenticated_client: AsyncClient):
    """Test creating content without required title field."""
    response = await authenticated_client.post(
        "/content",
        json={
            "body": "Content body",
            "is_published": False
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_update_content(
    authenticated_client: AsyncClient,
    test_content: Content
):
    """Test updating content by owner."""
    update_data = {
        "title": "Updated Title",
        "body": "Updated body content",
        "is_published": True
    }

    response = await authenticated_client.put(
        f"/content/{test_content.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["body"] == update_data["body"]
    assert data["is_published"] == update_data["is_published"]


@pytest.mark.asyncio
async def test_update_content_partial(
    authenticated_client: AsyncClient,
    test_content: Content
):
    """Test partial update of content."""
    update_data = {
        "title": "Only Update Title"
    }

    response = await authenticated_client.put(
        f"/content/{test_content.id}",
        json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["body"] == test_content.body  # Original body unchanged


@pytest.mark.asyncio
async def test_update_content_unauthorized(
    client: AsyncClient,
    test_content: Content
):
    """Test updating content without authentication fails."""
    response = await client.put(
        f"/content/{test_content.id}",
        json={"title": "New Title"}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_content_not_owner(
    client: AsyncClient,
    test_db,
    test_content: Content,
    sample_user_data: dict
):
    """Test updating content by non-owner fails."""
    # Create another user
    from app.auth import get_password_hash
    from app.models import User

    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    test_db.add(other_user)
    await test_db.commit()

    # Login as other user
    response = await client.post(
        "/auth/login",
        data={
            "username": other_user.email,
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

    # Try to update original user's content
    client.headers.update({"Authorization": f"Bearer {token}"})
    response = await client.put(
        f"/content/{test_content.id}",
        json={"title": "Hacked Title"}
    )

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_content(
    authenticated_client: AsyncClient,
    test_content: Content
):
    """Test deleting content by owner."""
    response = await authenticated_client.delete(f"/content/{test_content.id}")

    assert response.status_code == 204

    # Verify content is deleted
    get_response = await authenticated_client.get(f"/content/{test_content.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_content_unauthorized(
    client: AsyncClient,
    test_content: Content
):
    """Test deleting content without authentication fails."""
    response = await client.delete(f"/content/{test_content.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_content_not_owner(
    client: AsyncClient,
    test_db,
    test_content: Content
):
    """Test deleting content by non-owner fails."""
    # Create another user
    from app.auth import get_password_hash
    from app.models import User

    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    test_db.add(other_user)
    await test_db.commit()

    # Login as other user
    response = await client.post(
        "/auth/login",
        data={
            "username": other_user.email,
            "password": "password123"
        }
    )
    token = response.json()["access_token"]

    # Try to delete original user's content
    client.headers.update({"Authorization": f"Bearer {token}"})
    response = await client.delete(f"/content/{test_content.id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_content_not_found(authenticated_client: AsyncClient):
    """Test deleting non-existent content."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = await authenticated_client.delete(f"/content/{fake_uuid}")

    assert response.status_code == 404

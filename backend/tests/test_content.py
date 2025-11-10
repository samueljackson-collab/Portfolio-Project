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
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_content(client: AsyncClient, test_content: Content):
    """Test listing content items."""
    response = await client.get("/content")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["id"] == str(test_content.id)
    assert data[0]["title"] == test_content.title


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

    # Test with limit
    response = await client.get("/content?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

    # Test with skip
    response = await client.get("/content?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5  # Remaining items


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


@pytest.mark.asyncio
async def test_create_content_with_very_long_title(
    authenticated_client: AsyncClient
):
    """Test creating content with maximum title length."""
    response = await authenticated_client.post(
        "/content",
        json={
            "title": "a" * 255,  # Maximum length
            "body": "Test body",
            "is_published": False
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert len(data["title"]) == 255


@pytest.mark.asyncio
async def test_create_content_title_too_long(
    authenticated_client: AsyncClient
):
    """Test creating content with title exceeding maximum length."""
    response = await authenticated_client.post(
        "/content",
        json={
            "title": "a" * 256,  # Exceeds maximum
            "body": "Test body",
            "is_published": False
        }
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_content_partial_fields(
    authenticated_client: AsyncClient,
    test_content
):
    """Test updating content with only some fields."""
    response = await authenticated_client.put(
        f"/content/{test_content.id}",
        json={"is_published": True}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_published"] is True
    assert data["title"] == test_content.title  # Unchanged


@pytest.mark.asyncio
async def test_list_content_pagination_beyond_available(
    authenticated_client: AsyncClient
):
    """Test listing content with skip beyond available items."""
    response = await authenticated_client.get(
        "/content?skip=1000&limit=10"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_delete_content_twice(
    authenticated_client: AsyncClient,
    test_content
):
    """Test deleting the same content twice."""
    # First delete
    response = await authenticated_client.delete(f"/content/{test_content.id}")
    assert response.status_code == 204
    
    # Second delete
    response = await authenticated_client.delete(f"/content/{test_content.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_content_without_body(
    authenticated_client: AsyncClient
):
    """Test creating content with null body."""
    response = await authenticated_client.post(
        "/content",
        json={
            "title": "Title Only",
            "body": None,
            "is_published": False
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["body"] is None
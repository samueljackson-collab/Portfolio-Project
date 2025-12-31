"""
Integration tests for end-to-end API workflows.

These tests verify that multiple endpoints work together correctly
and that the database operations are properly integrated.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserContentWorkflow:
    """Test complete user registration and content management workflow."""

    async def test_full_user_workflow(self, client: AsyncClient):
        """Test: register -> login -> create content -> read content -> delete."""
        # 1. Register new user
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "workflow_test@example.com",
                "password": "workflowpass123"
            }
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # 2. Login with the new user
        login_response = await client.post(
            "/auth/login",
            data={
                "username": "workflow_test@example.com",
                "password": "workflowpass123"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # 3. Create content
        content_response = await client.post(
            "/content/",
            json={
                "title": "Integration Test Content",
                "body": "This is content created during integration testing",
                "is_published": True
            },
            headers=auth_headers
        )
        assert content_response.status_code == 201
        content_id = content_response.json()["id"]

        # 4. Read the created content
        get_response = await client.get(
            f"/content/{content_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Integration Test Content"

        # 5. Update the content
        update_response = await client.put(
            f"/content/{content_id}",
            json={
                "title": "Updated Integration Test Content",
                "body": "Updated body",
                "is_published": True
            },
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Integration Test Content"

        # 6. Delete the content
        delete_response = await client.delete(
            f"/content/{content_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204

        # 7. Verify content is deleted
        verify_response = await client.get(
            f"/content/{content_id}",
            headers=auth_headers
        )
        assert verify_response.status_code == 404


@pytest.mark.asyncio
class TestAPIRateLimitingAndErrors:
    """Test API error handling and edge cases."""

    async def test_invalid_token_rejected(self, client: AsyncClient):
        """Test that invalid tokens are properly rejected."""
        response = await client.get(
            "/content/",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401

    async def test_missing_auth_header(self, client: AsyncClient):
        """Test that requests without auth header are rejected for protected routes."""
        response = await client.post(
            "/content/",
            json={"title": "Test", "body": "Test body"}
        )
        assert response.status_code == 401

    async def test_malformed_request_body(self, client: AsyncClient, test_user_token: str):
        """Test that malformed request bodies return validation errors."""
        response = await client.post(
            "/content/",
            json={"invalid_field": "value"},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 422

    async def test_not_found_returns_404(self, client: AsyncClient, test_user_token: str):
        """Test that accessing non-existent resources returns 404."""
        response = await client.get(
            "/content/nonexistent-uuid-12345",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        # Should be 404 or 422 (if UUID validation fails)
        assert response.status_code in [404, 422]


@pytest.mark.asyncio
class TestDatabaseTransactions:
    """Test database transaction handling."""

    async def test_concurrent_content_creation(
        self,
        authenticated_client: AsyncClient
    ):
        """Test that concurrent content creation works correctly."""
        import asyncio

        async def create_content(index: int):
            return await authenticated_client.post(
                "/content/",
                json={
                    "title": f"Concurrent Content {index}",
                    "body": f"Body for content {index}",
                    "is_published": True
                }
            )

        # Create 5 content items concurrently
        results = await asyncio.gather(*[create_content(i) for i in range(5)])

        # All should succeed
        for result in results:
            assert result.status_code == 201

    async def test_user_can_only_modify_own_content(
        self,
        client: AsyncClient,
        test_content,
        test_user
    ):
        """Test that users cannot modify content they don't own."""
        # Register a different user
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "other_user@example.com",
                "password": "otherpass123"
            }
        )
        assert register_response.status_code == 201

        # Login as the other user
        login_response = await client.post(
            "/auth/login",
            data={
                "username": "other_user@example.com",
                "password": "otherpass123"
            }
        )
        other_token = login_response.json()["access_token"]

        # Try to delete content owned by test_user
        delete_response = await client.delete(
            f"/content/{test_content.id}",
            headers={"Authorization": f"Bearer {other_token}"}
        )

        # Should be forbidden or not found
        assert delete_response.status_code in [403, 404]


@pytest.mark.asyncio
class TestHealthAndMetrics:
    """Test health check and monitoring endpoints."""

    async def test_health_endpoint(self, client: AsyncClient):
        """Test that health endpoint returns expected format."""
        response = await client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data

    async def test_root_endpoint(self, client: AsyncClient):
        """Test that root endpoint returns API information."""
        response = await client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "message" in data
        assert "version" in data

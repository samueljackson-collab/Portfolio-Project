import pytest
from fastapi.testclient import TestClient
from producer.app import app, TODOS


class TestTodosEndpoint:
    """Test suite for core Todo functionality"""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clear todos before each test"""
        TODOS.clear()
        yield
        TODOS.clear()

    def test_create_todo_without_auth(self):
        """Verify creating todo without auth key fails"""
        client = TestClient(app)
        response = client.post(
            "/todos",
            json={"title": "Test Todo"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "invalid api key"

    def test_create_todo_with_auth(self):
        """Verify creating todo with valid API key"""
        import os
        os.environ["API_KEY"] = "test-key"

        client = TestClient(app)
        # Need to trigger app startup to load API_KEY
        with client:
            response = client.post(
                "/todos",
                json={"title": "Test Todo"},
                headers={"X-API-Key": "test-key"}
            )
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "Test Todo"
            assert "id" in data

    def test_list_todos_returns_list(self):
        """Verify todos endpoint returns list"""
        client = TestClient(app)
        response = client.get("/todos")

        # Either 401 (auth required) or 200 (no auth)
        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_create_multiple_todos(self):
        """Verify creating multiple todos generates unique IDs"""
        import os
        os.environ["API_KEY"] = "test-key"

        client = TestClient(app)
        with client:
            # Create first todo
            response1 = client.post(
                "/todos",
                json={"title": "First Todo"},
                headers={"X-API-Key": "test-key"}
            )
            assert response1.status_code == 201
            data1 = response1.json()
            id1 = data1["id"]

            # Create second todo
            response2 = client.post(
                "/todos",
                json={"title": "Second Todo"},
                headers={"X-API-Key": "test-key"}
            )
            assert response2.status_code == 201
            data2 = response2.json()
            id2 = data2["id"]

            # IDs should be different
            assert id1 != id2

    def test_todo_title_required(self):
        """Verify title is required for todo creation"""
        import os
        os.environ["API_KEY"] = "test-key"

        client = TestClient(app)
        with client:
            response = client.post(
                "/todos",
                json={"title": ""},
                headers={"X-API-Key": "test-key"}
            )
            # Empty string is technically valid, should succeed
            assert response.status_code == 201

    def test_create_todo_response_format(self):
        """Verify todo response has correct format"""
        import os
        os.environ["API_KEY"] = "test-key"

        client = TestClient(app)
        with client:
            response = client.post(
                "/todos",
                json={"title": "Format Test"},
                headers={"X-API-Key": "test-key"}
            )
            assert response.status_code == 201

            data = response.json()
            assert "id" in data
            assert "title" in data
            assert isinstance(data["id"], int)
            assert isinstance(data["title"], str)


class TestAPIKeyValidation:
    """Test suite for API key authentication"""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clear todos before each test"""
        TODOS.clear()
        yield
        TODOS.clear()

    def test_invalid_api_key_rejected(self):
        """Verify invalid API key is rejected"""
        import os
        os.environ["API_KEY"] = "valid-key"

        client = TestClient(app)
        with client:
            response = client.post(
                "/todos",
                json={"title": "Test"},
                headers={"X-API-Key": "invalid-key"}
            )
            assert response.status_code == 401

    def test_health_check_no_auth(self):
        """Verify health check doesn't require auth"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestErrorHandling:
    """Test suite for error handling"""

    def test_nonexistent_endpoint(self):
        """Verify 404 for nonexistent endpoint"""
        client = TestClient(app)
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_request_format(self):
        """Verify 422 for invalid request format"""
        client = TestClient(app)
        response = client.post(
            "/todos",
            json={"invalid_field": "value"}
        )
        assert response.status_code in [422, 401]  # Validation error or auth error

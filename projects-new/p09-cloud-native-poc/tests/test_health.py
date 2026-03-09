import pytest
from fastapi.testclient import TestClient
from producer.app import app


class TestHealthEndpoint:
    """Test suite for health check endpoints"""

    def test_health_check_returns_200(self):
        """Verify health endpoint returns 200 OK"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self):
        """Verify health endpoint returns 'ok' status"""
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_check_response_type(self):
        """Verify health endpoint response is valid JSON"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_health_check_includes_status_field(self):
        """Verify health response includes required fields"""
        client = TestClient(app)
        response = client.get("/health")
        data = response.json()
        assert "status" in data

    def test_health_endpoint_no_auth_required(self):
        """Verify health endpoint doesn't require authentication"""
        client = TestClient(app)
        # Should work without API key
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_time(self):
        """Verify health check responds quickly"""
        client = TestClient(app)
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in less than 1 second


class TestLivenessProbe:
    """Test suite for liveness probe simulation"""

    def test_liveness_endpoint_ready(self):
        """Verify service is alive and responsive"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestReadinessProbe:
    """Test suite for readiness probe simulation"""

    def test_readiness_check(self):
        """Verify service is ready to accept traffic"""
        client = TestClient(app)
        response = client.get("/health")

        # Should be ready
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_readiness_with_basic_operation(self):
        """Verify readiness by performing basic operation"""
        client = TestClient(app)

        # Try to list todos - should work if ready
        response = client.get("/todos")
        # Note: 401 means API is working but auth failed (expected without API key)
        # 200 means both API and todos are accessible
        assert response.status_code in [200, 401]

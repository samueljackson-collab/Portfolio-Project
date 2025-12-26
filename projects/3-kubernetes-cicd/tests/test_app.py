"""Tests for the Flask application."""

import pytest
import json
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_endpoint(self, client):
        """Test /health endpoint."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'uptime_seconds' in data
        assert 'timestamp' in data

    def test_ready_endpoint(self, client):
        """Test /ready endpoint."""
        response = client.get('/ready')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['ready'] is True
        assert 'version' in data


class TestAPIEndpoints:
    """Test API endpoints."""

    def test_home_endpoint(self, client):
        """Test / endpoint."""
        response = client.get('/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'message' in data
        assert 'version' in data
        assert 'hostname' in data
        assert 'timestamp' in data

    def test_info_endpoint(self, client):
        """Test /api/info endpoint."""
        response = client.get('/api/info')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['name'] == 'k8s-cicd-demo'
        assert 'version' in data
        assert 'environment' in data
        assert 'python_version' in data
        assert 'uptime_seconds' in data

    def test_echo_endpoint(self, client):
        """Test /api/echo endpoint."""
        test_data = {'message': 'hello', 'number': 42}

        response = client.post(
            '/api/echo',
            data=json.dumps(test_data),
            content_type='application/json'
        )

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['received'] == test_data
        assert 'timestamp' in data
        assert 'processed_by' in data


class TestMetrics:
    """Test metrics endpoint."""

    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert response.content_type.startswith('text/plain')

        metrics = response.data.decode('utf-8')
        assert 'app_uptime_seconds' in metrics
        assert 'app_version' in metrics


class TestErrorHandlers:
    """Test error handlers."""

    def test_404_handler(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert data['status'] == 404
        assert 'error' in data
        assert 'message' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

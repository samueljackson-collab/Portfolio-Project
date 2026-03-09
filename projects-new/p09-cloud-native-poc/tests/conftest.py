import os
import pytest
from fastapi.testclient import TestClient
from producer.app import app


@pytest.fixture(scope="session")
def base_url():
    """Get base URL from environment or use default"""
    return os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def api_key():
    """Get API key from environment or use default"""
    return os.getenv("API_KEY", "test-key-123")


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def client_with_auth_headers(api_key):
    """Create a test client with default auth headers"""
    client = TestClient(app)
    client.headers = {"X-API-Key": api_key}
    return client

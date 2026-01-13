"""
Pytest configuration and fixtures for API tests

Provides:
- API client fixture setup
- Environment configuration
- Authentication setup
- Test data factories
"""

import pytest
import requests
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get base URL for API from environment or use default"""
    return os.getenv("API_BASE_URL", "http://localhost:8080")


@pytest.fixture(scope="session")
def valid_credentials() -> Dict[str, str]:
    """Get valid credentials for authentication"""
    return {
        "client_id": os.getenv("API_CLIENT_ID", "demo"),
        "client_secret": os.getenv("API_CLIENT_SECRET", "secret")
    }


@pytest.fixture(scope="session")
def auth_token(base_url, valid_credentials) -> str:
    """Generate authentication token for test session"""
    auth_url = f"{base_url}/auth/token"

    try:
        response = requests.post(
            auth_url,
            json=valid_credentials,
            headers={"Content-Type": "application/json"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                return token
            else:
                pytest.skip("Could not retrieve auth token")

        else:
            pytest.skip(f"Authentication failed with status {response.status_code}")

    except requests.exceptions.RequestException as e:
        pytest.skip(f"Could not connect to API: {e}")


@pytest.fixture(scope="session")
def api_health_check(base_url):
    """Check API health before running tests"""
    health_endpoints = [
        f"{base_url}/health",
        f"{base_url}/status",
        f"{base_url}/",
    ]

    for endpoint in health_endpoints:
        try:
            response = requests.get(endpoint, timeout=3)
            if response.status_code < 500:  # Not a server error
                return True
        except requests.exceptions.RequestException:
            continue

    pytest.skip(f"API at {base_url} is not accessible")


@pytest.fixture
def http_client():
    """Create HTTP session for tests"""
    client = requests.Session()
    yield client
    client.close()


@pytest.fixture
def api_client(base_url, auth_token):
    """Create authenticated API client"""
    from api_client import APIClient
    client = APIClient(base_url, auth_token)
    yield client
    client.close()


# Pytest configuration hooks

def pytest_configure(config):
    """Configure pytest"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add integration marker to all tests by default
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment(api_health_check):
    """Setup test environment and ensure API is healthy before running tests"""
    # API health check is performed by the api_health_check fixture
    # Additional setup can be added here if needed (e.g., database seeding)
    yield
    # Teardown actions can be added here if needed


@pytest.fixture
def order_factory():
    """Factory for creating test orders"""
    counter = {"value": 0}

    def create_order(customer_id=None, num_items=1):
        counter["value"] += 1
        customer_id = customer_id or f"CUST{counter['value']:03d}"

        items = []
        for i in range(num_items):
            items.append({
                "product_id": f"PROD{(i + 1):03d}",
                "quantity": i + 1,
                "price": (i + 1) * 10.00
            })

        return {
            "customer_id": customer_id,
            "items": items,
            "shipping_address": {
                "street": f"{100 + counter['value']} Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }

    return create_order


@pytest.fixture
def product_factory():
    """Factory for creating test products"""
    counter = {"value": 0}

    def create_product(name=None, category=None, price=None):
        counter["value"] += 1
        name = name or f"Product {counter['value']}"
        category = category or "general"
        price = price or (counter["value"] * 10.00)

        return {
            "id": f"PROD{counter['value']:03d}",
            "name": name,
            "category": category,
            "price": price,
            "description": f"Test product {counter['value']}"
        }

    return create_product


# Test markers and custom assertions

class APIAssertions:
    """Helper class for API-specific assertions"""

    @staticmethod
    def assert_valid_json_response(response):
        """Assert response is valid JSON"""
        try:
            response.json()
        except ValueError:
            raise AssertionError("Response is not valid JSON")

    @staticmethod
    def assert_status_code(response, expected_codes):
        """Assert response status code matches expected"""
        if isinstance(expected_codes, int):
            expected_codes = [expected_codes]

        assert response.status_code in expected_codes, \
            f"Expected status code {expected_codes}, got {response.status_code}"

    @staticmethod
    def assert_required_fields(data, fields):
        """Assert data contains all required fields"""
        for field in fields:
            assert field in data, f"Missing required field: {field}"

    @staticmethod
    def assert_field_type(data, field, expected_type):
        """Assert field has expected type"""
        assert isinstance(data[field], expected_type), \
            f"Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}"


@pytest.fixture
def api_assertions():
    """Provide API assertion helpers"""
    return APIAssertions()

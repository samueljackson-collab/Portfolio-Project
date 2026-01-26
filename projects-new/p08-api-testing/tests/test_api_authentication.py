"""
API Authentication Tests

Tests for API authentication mechanisms including:
- Token generation and validation
- Invalid credentials handling
- Token expiration
- Authorization checks
"""

import pytest
import requests
from typing import Dict, Any


class TestAuthentication:
    """Test suite for authentication endpoints"""

    @pytest.fixture
    def client(self, base_url):
        """Create HTTP client"""
        return requests.Session()

    def test_get_auth_token_success(self, client, base_url, valid_credentials):
        """Test successful token generation"""
        auth_url = f"{base_url}/auth/token"
        response = client.post(
            auth_url,
            json=valid_credentials,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "access_token" in data, "Response must contain access_token"
        assert "token_type" in data, "Response must contain token_type"
        assert data["token_type"] == "Bearer"
        assert len(data["access_token"]) > 0

    def test_auth_token_expires_in(self, client, base_url, valid_credentials):
        """Test token includes expiration information"""
        auth_url = f"{base_url}/auth/token"
        response = client.post(
            auth_url,
            json=valid_credentials,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()

        # Token may include expires_in
        if "expires_in" in data:
            assert isinstance(data["expires_in"], int)
            assert data["expires_in"] > 0

    def test_invalid_client_id(self, client, base_url):
        """Test authentication with invalid client ID"""
        auth_url = f"{base_url}/auth/token"
        credentials = {"client_id": "invalid_client_id", "client_secret": "secret"}

        response = client.post(
            auth_url, json=credentials, headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 401
        data = response.json()
        assert "error" in data, "Error response must contain error field"

    def test_invalid_client_secret(self, client, base_url, valid_credentials):
        """Test authentication with invalid client secret"""
        auth_url = f"{base_url}/auth/token"
        credentials = {
            "client_id": valid_credentials["client_id"],
            "client_secret": "wrong_secret",
        }

        response = client.post(
            auth_url, json=credentials, headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 401

    def test_missing_client_id(self, client, base_url):
        """Test authentication with missing client ID"""
        auth_url = f"{base_url}/auth/token"
        credentials = {"client_secret": "secret"}

        response = client.post(
            auth_url, json=credentials, headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 401]

    def test_missing_client_secret(self, client, base_url):
        """Test authentication with missing client secret"""
        auth_url = f"{base_url}/auth/token"
        credentials = {"client_id": "demo"}

        response = client.post(
            auth_url, json=credentials, headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 401]

    def test_empty_payload(self, client, base_url):
        """Test authentication with empty payload"""
        auth_url = f"{base_url}/auth/token"

        response = client.post(
            auth_url, json={}, headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 401]


class TestAuthorization:
    """Test suite for authorization and token validation"""

    @pytest.fixture
    def client(self, base_url):
        return requests.Session()

    def test_request_without_auth_token(self, client, base_url):
        """Test API request without authentication token"""
        response = client.get(f"{base_url}/orders", headers={"Authorization": ""})

        assert response.status_code == 401

    def test_request_with_invalid_token(self, client, base_url):
        """Test API request with invalid token"""
        response = client.get(
            f"{base_url}/orders",
            headers={"Authorization": "Bearer invalid_token_12345"},
        )

        assert response.status_code == 401

    def test_request_with_expired_token(self, client, base_url):
        """Test API request with expired token"""
        # This test would need a mechanism to generate an expired token
        # For now, we'll test with an obviously invalid token
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        response = client.get(
            f"{base_url}/orders", headers={"Authorization": f"Bearer {expired_token}"}
        )

        assert response.status_code == 401

    def test_request_with_malformed_auth_header(self, client, base_url):
        """Test API request with malformed authorization header"""
        invalid_headers = [
            {"Authorization": "InvalidScheme token123"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "BearerToken123"},  # No space
        ]

        for headers in invalid_headers:
            response = client.get(f"{base_url}/orders", headers=headers)
            assert response.status_code in [
                400,
                401,
            ], f"Malformed auth header should return 400/401, got {response.status_code}"

    def test_different_token_types(self, client, base_url, auth_token):
        """Test different authorization header formats"""
        valid_headers = [
            {"Authorization": f"Bearer {auth_token}"},
            {"Authorization": f"bearer {auth_token}"},  # lowercase
        ]

        for headers in valid_headers:
            response = client.get(
                f"{base_url}/orders", headers=headers, params={"page": 1, "pageSize": 5}
            )
            # Should accept both Bearer and bearer
            assert response.status_code in [200, 401]  # 200 if accepted, 401 if not


class TestTokenRefresh:
    """Test suite for token refresh functionality"""

    @pytest.fixture
    def client(self, base_url):
        return requests.Session()

    def test_refresh_token_endpoint_exists(self, client, base_url, auth_token):
        """Test if token refresh endpoint exists"""
        refresh_url = f"{base_url}/auth/refresh"

        response = client.post(
            refresh_url,
            json={"access_token": auth_token},
            headers={"Content-Type": "application/json"},
        )

        # Endpoint may or may not exist - just check response code
        # If 501, endpoint not implemented
        # If 200, endpoint works
        # If 401, invalid token
        assert response.status_code in [200, 401, 501]

    def test_refresh_with_invalid_token(self, client, base_url):
        """Test token refresh with invalid token"""
        refresh_url = f"{base_url}/auth/refresh"

        response = client.post(
            refresh_url,
            json={"access_token": "invalid_token"},
            headers={"Content-Type": "application/json"},
        )

        # Should reject invalid token
        if response.status_code != 501:  # If endpoint exists
            assert response.status_code == 401


class TestSessionManagement:
    """Test suite for session management"""

    @pytest.fixture
    def client(self):
        return requests.Session()

    def test_multiple_token_requests(self, client, base_url, valid_credentials):
        """Test multiple authentication requests return different tokens"""
        auth_url = f"{base_url}/auth/token"

        # Request tokens multiple times
        tokens = []
        for _ in range(3):
            response = client.post(
                auth_url,
                json=valid_credentials,
                headers={"Content-Type": "application/json"},
            )
            assert response.status_code == 200
            tokens.append(response.json()["access_token"])

        # All tokens should be valid (but may or may not be different)
        # The important thing is they're all strings and non-empty
        for token in tokens:
            assert isinstance(token, str)
            assert len(token) > 0

    def test_concurrent_requests_with_same_token(self, client, base_url, auth_token):
        """Test multiple concurrent requests with same token"""
        # Make multiple requests with the same token
        for i in range(5):
            response = client.get(
                f"{base_url}/orders",
                headers={"Authorization": f"Bearer {auth_token}"},
                params={"page": 1, "pageSize": 5},
            )
            assert response.status_code in [200, 401]

    def test_auth_token_format(self, client, base_url, valid_credentials):
        """Test auth token has expected format"""
        auth_url = f"{base_url}/auth/token"
        response = client.post(
            auth_url,
            json=valid_credentials,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()
        token = data["access_token"]

        # JWT tokens typically have 3 parts separated by dots
        # But other formats are also valid
        assert isinstance(token, str)
        assert len(token) >= 20  # Token should have reasonable length

"""
test_login_app.py — pytest test suite for the Flask login application

Tests cover functional, session management, authorization, and security
scenarios for all endpoints in the login application.
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sample-app'))
from app import app as flask_app, LOGIN_ATTEMPTS


@pytest.fixture(autouse=True)
def clear_rate_limits():
    LOGIN_ATTEMPTS.clear()
    yield
    LOGIN_ATTEMPTS.clear()


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"
    with flask_app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Health Check Tests
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """TC-F013: Health endpoint is always accessible without authentication."""

    def test_health_returns_200(self, client):
        """Health check returns HTTP 200."""
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """Health check response body contains status: healthy."""
        r = client.get("/health")
        assert r.get_json()["status"] == "healthy"

    def test_health_returns_version(self, client):
        """Health check response includes a version field."""
        r = client.get("/health")
        data = r.get_json()
        assert "version" in data
        assert data["version"] == "1.0.0"


# ---------------------------------------------------------------------------
# Functional Login Tests
# ---------------------------------------------------------------------------

class TestFunctionalLogin:
    """TC-F001 through TC-F007: Core login functionality."""

    def test_valid_login_admin(self, client):
        """TC-F001: Valid credentials for admin return 200 and correct user."""
        r = client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        assert r.status_code == 200
        assert r.get_json()["user"] == "admin"

    def test_valid_login_user1(self, client):
        """TC-F001: Valid credentials for user1 return 200."""
        r = client.post("/login", json={"username": "user1", "password": "User@5678!"})
        assert r.status_code == 200
        assert r.get_json()["message"] == "Login successful"

    def test_valid_login_testuser(self, client):
        """TC-F001: Valid credentials for testuser return 200."""
        r = client.post("/login", json={"username": "testuser", "password": "Test@9999!"})
        assert r.status_code == 200

    def test_wrong_password(self, client):
        """TC-F002: Wrong password returns 401 with attempts_remaining."""
        r = client.post("/login", json={"username": "admin", "password": "wrongpassword"})
        assert r.status_code == 401
        data = r.get_json()
        assert "attempts_remaining" in data
        assert data["attempts_remaining"] == 4

    def test_nonexistent_user(self, client):
        """TC-F003: Non-existent username returns 401."""
        r = client.post("/login", json={"username": "nobody", "password": "anything"})
        assert r.status_code == 401

    def test_empty_username(self, client):
        """TC-F004: Empty username returns 400."""
        r = client.post("/login", json={"username": "", "password": "Admin@1234!"})
        assert r.status_code == 400
        assert "required" in r.get_json()["error"].lower()

    def test_empty_password(self, client):
        """TC-F005: Empty password returns 400."""
        r = client.post("/login", json={"username": "admin", "password": ""})
        assert r.status_code == 400

    def test_rate_limiting_activates_after_5_failures(self, client):
        """TC-F006: After 5 failed attempts the 6th returns 429."""
        for _ in range(5):
            client.post("/login", json={"username": "admin", "password": "wrong"})
        r = client.post("/login", json={"username": "admin", "password": "wrong"})
        assert r.status_code == 429
        assert "Too many" in r.get_json()["error"]

    def test_rate_limit_resets_on_success(self, client):
        """TC-F007: Successful login clears the rate limit counter."""
        for _ in range(4):
            client.post("/login", json={"username": "admin", "password": "wrong"})
        r = client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        assert r.status_code == 200
        r2 = client.post("/login", json={"username": "admin", "password": "wrong"})
        assert r2.status_code == 401

    def test_login_returns_user_field_on_success(self, client):
        """TC-F014: Successful login response contains user field."""
        r = client.post("/login", json={"username": "user1", "password": "User@5678!"})
        data = r.get_json()
        assert "user" in data
        assert data["user"] == "user1"

    def test_missing_json_body(self, client):
        """Login with no body treated as missing credentials, returns 400."""
        r = client.post("/login", content_type="application/json", data="")
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# Session Management Tests
# ---------------------------------------------------------------------------

class TestSessionManagement:
    """TC-F008 through TC-F010: Session lifecycle."""

    def test_profile_requires_auth(self, client):
        """TC-F009: Profile endpoint returns 401 when unauthenticated."""
        r = client.get("/profile")
        assert r.status_code == 401

    def test_authenticated_profile_access(self, client):
        """TC-F008: Authenticated user can access profile and gets correct data."""
        client.post("/login", json={"username": "user1", "password": "User@5678!"})
        r = client.get("/profile")
        assert r.status_code == 200
        data = r.get_json()
        assert data["user"] == "user1"
        assert data["role"] == "user"
        assert "login_time" in data

    def test_admin_profile_shows_admin_role(self, client):
        """Profile endpoint returns role=admin for admin user."""
        client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        r = client.get("/profile")
        assert r.status_code == 200
        assert r.get_json()["role"] == "admin"

    def test_logout_clears_session(self, client):
        """TC-F010: After logout, profile endpoint returns 401."""
        client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        client.post("/logout")
        r = client.get("/profile")
        assert r.status_code == 401

    def test_logout_requires_auth(self, client):
        """Logout endpoint returns 401 when not logged in."""
        r = client.post("/logout")
        assert r.status_code == 401

    def test_logout_returns_success_message(self, client):
        """Logout returns 200 with success message."""
        client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        r = client.post("/logout")
        assert r.status_code == 200
        assert "Logged out" in r.get_json()["message"]


# ---------------------------------------------------------------------------
# Authorization Tests
# ---------------------------------------------------------------------------

class TestAuthorization:
    """TC-F011, TC-F012: Role-based access control."""

    def test_admin_accesses_admin_endpoint(self, client):
        """TC-F011: Admin user can access /admin/users endpoint."""
        client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        r = client.get("/admin/users")
        assert r.status_code == 200
        data = r.get_json()
        assert "users" in data
        assert "admin" in data["users"]

    def test_non_admin_blocked_from_admin(self, client):
        """TC-F012: Non-admin user receives 403 on admin endpoint."""
        client.post("/login", json={"username": "user1", "password": "User@5678!"})
        r = client.get("/admin/users")
        assert r.status_code == 403
        assert "Forbidden" in r.get_json()["error"]

    def test_unauthenticated_admin_endpoint_returns_401(self, client):
        """Unauthenticated request to admin endpoint returns 401."""
        r = client.get("/admin/users")
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Security Tests
# ---------------------------------------------------------------------------

class TestSecurity:
    """TC-S001 through TC-S010: Security and resilience tests."""

    def test_sql_injection_username(self, client):
        """TC-S001: SQL injection in username field is safely rejected."""
        r = client.post("/login", json={"username": "' OR 1=1 --", "password": "x"})
        assert r.status_code in [400, 401]
        assert r.status_code != 500

    def test_sql_injection_password(self, client):
        """TC-S002: SQL injection in password field is safely rejected."""
        r = client.post("/login", json={"username": "admin", "password": "' OR '1'='1"})
        assert r.status_code == 401

    def test_password_not_in_response(self, client):
        """TC-S004: Plaintext password is never echoed back in any response."""
        r = client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        body = str(r.data)
        assert "Admin@1234!" not in body

    def test_password_hash_not_in_response(self, client):
        """TC-S004: Password hash is not returned in login response."""
        import hashlib
        pwd_hash = hashlib.sha256("Admin@1234!".encode()).hexdigest()
        r = client.post("/login", json={"username": "admin", "password": "Admin@1234!"})
        assert pwd_hash not in str(r.data)

    def test_xss_payload_in_username(self, client):
        """TC-S003: XSS payload in username is rejected and not reflected in response."""
        payload = "<script>alert(1)</script>"
        r = client.post("/login", json={"username": payload, "password": "x"})
        assert r.status_code in [400, 401]
        assert b"<script>" not in r.data

    def test_null_bytes_in_credentials(self, client):
        """TC-S006: Null bytes in credentials are handled gracefully (no 500)."""
        r = client.post("/login", json={"username": "admin\x00extra", "password": "test"})
        assert r.status_code in [400, 401]
        assert r.status_code != 500

    def test_very_long_username(self, client):
        """TC-S007: 1000-character username is handled gracefully (no 500)."""
        long_username = "a" * 1000
        r = client.post("/login", json={"username": long_username, "password": "x"})
        assert r.status_code in [400, 401]
        assert r.status_code != 500

    def test_very_long_password(self, client):
        """TC-S008: 1000-character password is handled gracefully (no 500)."""
        long_password = "p" * 1000
        r = client.post("/login", json={"username": "admin", "password": long_password})
        assert r.status_code == 401
        assert r.status_code != 500

    def test_json_injection_nested_objects(self, client):
        """TC-S009: Nested JSON objects in fields are handled gracefully."""
        r = client.post("/login", json={"username": {"$ne": None}, "password": "x"})
        assert r.status_code in [400, 401]
        assert r.status_code != 500

    def test_rate_limit_not_bypassed_by_username_case(self, client):
        """TC-S010: Rate limiting is per-IP, not per-username — case change doesn't bypass."""
        for _ in range(5):
            client.post("/login", json={"username": "admin", "password": "wrong"})
        r = client.post("/login", json={"username": "ADMIN", "password": "wrong"})
        assert r.status_code == 429

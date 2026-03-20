import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-key"
    with flask_app.test_client() as c:
        yield c


class TestLoginFunctionality:
    def test_login_page_loads(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200
        assert b"Sign In" in resp.data

    def test_valid_login_redirects_to_dashboard(self, client):
        resp = client.post("/login", data={"username": "admin", "password": "Admin@1234"}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Dashboard" in resp.data

    def test_invalid_password_shows_error(self, client):
        resp = client.post("/login", data={"username": "admin", "password": "wrongpassword"}, follow_redirects=True)
        assert resp.status_code == 200
        assert b"Invalid username or password" in resp.data

    def test_invalid_username_shows_error(self, client):
        resp = client.post("/login", data={"username": "notauser", "password": "anything"}, follow_redirects=True)
        assert b"Invalid username or password" in resp.data

    def test_empty_credentials_rejected(self, client):
        resp = client.post("/login", data={"username": "", "password": ""}, follow_redirects=True)
        assert b"Invalid" in resp.data


class TestSessionManagement:
    def test_dashboard_requires_auth(self, client):
        resp = client.get("/dashboard", follow_redirects=True)
        assert b"Sign In" in resp.data

    def test_profile_requires_auth(self, client):
        resp = client.get("/profile", follow_redirects=True)
        assert b"Sign In" in resp.data

    def test_logout_clears_session(self, client):
        client.post("/login", data={"username": "admin", "password": "Admin@1234"})
        client.get("/logout")
        resp = client.get("/dashboard", follow_redirects=True)
        assert b"Sign In" in resp.data


class TestNavigation:
    def test_root_redirects_to_login_when_unauthenticated(self, client):
        resp = client.get("/", follow_redirects=True)
        assert b"Sign In" in resp.data

    def test_root_redirects_to_dashboard_when_authenticated(self, client):
        client.post("/login", data={"username": "demo", "password": "Demo@5678"})
        resp = client.get("/", follow_redirects=True)
        assert b"Dashboard" in resp.data

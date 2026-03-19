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


def test_login_form_has_required_fields(client):
    """Verify the login page renders username, password inputs and submit button."""
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b'id="username"' in resp.data
    assert b'id="password"' in resp.data
    assert b'id="login-btn"' in resp.data


def test_dashboard_shows_username_after_login(client):
    """Verify the dashboard displays the logged-in username."""
    client.post("/login", data={"username": "admin", "password": "Admin@1234"})
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"admin" in resp.data


def test_dashboard_nav_links_present(client):
    """Verify Profile, Settings, and Logout nav links exist on dashboard."""
    client.post("/login", data={"username": "admin", "password": "Admin@1234"})
    resp = client.get("/dashboard")
    assert b'id="nav-profile"' in resp.data
    assert b'id="nav-settings"' in resp.data
    assert b'id="nav-logout"' in resp.data


def test_profile_page_accessible_when_logged_in(client):
    """Verify the /profile route returns 200 for authenticated users."""
    client.post("/login", data={"username": "test", "password": "Test@9999"})
    resp = client.get("/profile")
    assert resp.status_code == 200
    assert b"test" in resp.data


def test_all_users_can_login(client):
    """Verify each user in USERS dict can authenticate successfully."""
    credentials = [
        ("admin", "Admin@1234"),
        ("demo", "Demo@5678"),
        ("test", "Test@9999"),
    ]
    for username, password in credentials:
        with flask_app.test_client() as c:
            resp = c.post(
                "/login",
                data={"username": username, "password": password},
                follow_redirects=True,
            )
            assert resp.status_code == 200
            assert b"Dashboard" in resp.data, f"Login failed for user: {username}"


def test_logout_redirects_to_login(client):
    """Verify /logout sends the user back to the login page."""
    client.post("/login", data={"username": "demo", "password": "Demo@5678"})
    resp = client.get("/logout", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Sign In" in resp.data


def test_welcome_message_contains_username(client):
    """Verify the welcome heading on the dashboard includes the username."""
    client.post("/login", data={"username": "demo", "password": "Demo@5678"})
    resp = client.get("/dashboard")
    assert b"Welcome, demo!" in resp.data

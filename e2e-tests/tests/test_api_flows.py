import os

import pytest
import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


@pytest.mark.integration
def test_full_flow():
    register = requests.post(f"{BASE_URL}/auth/register", json={"email": "e2e@example.com", "password": "secret"})
    assert register.status_code in (201, 400)  # allow reruns

    login = requests.post(f"{BASE_URL}/auth/login", json={"email": "e2e@example.com", "password": "secret"})
    assert login.status_code == 200
    tokens = login.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    create = requests.post(
        f"{BASE_URL}/content/",
        json={"title": "E2E", "body": "created via pytest", "is_published": True},
        headers=headers,
    )
    assert create.status_code == 201

    listing = requests.get(f"{BASE_URL}/content/", headers=headers)
    assert listing.status_code == 200
    data = listing.json()
    assert isinstance(data, list) and len(data) >= 1

from __future__ import annotations

import os

import requests

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def test_full_user_flow():
    email = "e2e-user@example.com"
    payload = {"email": email, "password": "password123"}
    register = requests.post(f"{BASE_URL}/auth/register", json=payload)
    assert register.status_code in (200, 201)

    login = requests.post(f"{BASE_URL}/auth/login", json=payload)
    assert login.status_code == 200
    tokens = login.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    create = requests.post(
        f"{BASE_URL}/content/",
        json={"title": "E2E", "body": "Flow", "is_published": True},
        headers=headers,
    )
    assert create.status_code == 201

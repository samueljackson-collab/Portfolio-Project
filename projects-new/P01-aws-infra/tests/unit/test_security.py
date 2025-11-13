"""Tests for security helpers."""

import pytest
from fastapi import HTTPException

from src.config import reset_settings_cache
from src.security import apply_security_headers, verify_api_key


@pytest.fixture(autouse=True)
def setup_api_key(monkeypatch):
    monkeypatch.setenv("API_KEYS", "expected")
    reset_settings_cache()
    yield
    reset_settings_cache()


def test_verify_api_key_success():
    assert verify_api_key(x_api_key="expected") == "expected"


def test_verify_api_key_failure():
    with pytest.raises(HTTPException):
        verify_api_key(x_api_key="bad")


def test_verify_api_key_missing_header():
    with pytest.raises(HTTPException):
        verify_api_key(x_api_key=None)


def test_apply_security_headers_sets_defaults():
    headers = apply_security_headers({})
    assert headers["X-Frame-Options"] == "DENY"
    assert "Strict-Transport-Security" in headers

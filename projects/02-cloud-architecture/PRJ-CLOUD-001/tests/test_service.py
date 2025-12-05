"""Lightweight tests to validate the scaffolded service module."""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import service  # type: ignore  # noqa: E402


def test_health_check_contains_status_and_metadata():
    result = service.health_check()
    assert result["status"] == "ok"
    assert result["name"] == "cloud-architecture"
    assert "owner" in result and "description" in result

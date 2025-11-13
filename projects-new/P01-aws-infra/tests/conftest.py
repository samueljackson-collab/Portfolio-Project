"""Shared pytest fixtures for the AWS infra project."""

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import reset_settings_cache


class FakeAWSService:
    """Test double that mimics the AWSResourceService behavior."""

    def list_s3_buckets(self):
        return [{"name": "demo", "creation_date": "2024-01-01T00:00:00"}]

    def publish_custom_metric(self, metric_name: str, value: float, unit: str):
        return {"metric_name": metric_name, "value": value, "unit": unit}

    def describe_secret(self, secret_id: str):
        return {"name": secret_id, "rotation_enabled": True, "tags": [], "last_rotated": None}


@pytest.fixture(autouse=True)
def configure_env(monkeypatch):
    monkeypatch.setenv("API_KEYS", "test-key")
    reset_settings_cache()
    yield
    reset_settings_cache()


@pytest.fixture()
def fake_service():
    return FakeAWSService()

"""Integration-style tests that exercise route handlers with fake services."""

from src.config import get_settings, reset_settings_cache
from src.main import (
    PublishMetricPayload,
    health,
    prometheus_metrics,
    publish_metric,
    s3_buckets,
    secret_metadata,
)


def test_health_endpoint(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "qa")
    reset_settings_cache()
    settings = get_settings()
    response = health(settings=settings)
    assert response.status == "healthy"
    assert response.environment == "qa"


def test_s3_buckets_handler(fake_service):
    payload = s3_buckets("test-key", fake_service)
    assert payload["buckets"][0]["name"] == "demo"


def test_metrics_endpoint(fake_service):  # fake_service unused but keeps fixture order
    response = prometheus_metrics()
    assert response.status_code == 200
    assert "aws_infra_requests_total" in response.body.decode()


def test_secret_metadata_endpoint(fake_service):
    result = secret_metadata("my-secret", "test-key", fake_service)
    assert result.body
    assert "my-secret" in result.body.decode()


def test_publish_metric(fake_service):
    payload = PublishMetricPayload(metric_name="Latency", value=123.0, unit="Milliseconds")
    result = publish_metric(payload, "test-key", fake_service)
    assert result["metric_name"] == "Latency"

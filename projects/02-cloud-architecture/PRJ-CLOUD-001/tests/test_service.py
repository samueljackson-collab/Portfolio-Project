"""Tests to validate the cloud architecture service module."""

import service


def test_health_check_degraded_when_required_fields_missing(monkeypatch):
    monkeypatch.delenv("CLOUD_ARCH_ORG_ID", raising=False)
    monkeypatch.delenv("CLOUD_ARCH_AUDIT_BUCKET", raising=False)
    monkeypatch.delenv("CLOUD_ARCH_SSO_ARN", raising=False)

    result = service.health_check()
    assert result["status"] == "degraded"
    checks = {check["name"]: check for check in result["checks"]}
    assert checks["organizations_id"]["status"] == "fail"
    assert checks["cloudtrail_bucket"]["status"] == "fail"
    assert checks["sso_instance_arn"]["status"] == "fail"
    assert result["config_summary"]["org_id"] == ""


def test_health_check_ok_when_configured(monkeypatch):
    monkeypatch.setenv("CLOUD_ARCH_ORG_ID", "o-123456")
    monkeypatch.setenv("CLOUD_ARCH_AUDIT_BUCKET", "cloudtrail-audit-logs")
    monkeypatch.setenv("CLOUD_ARCH_SSO_ARN", "arn:aws:sso:::instance/ssoins-123")
    monkeypatch.setenv("CLOUD_ARCH_ACCOUNT_COUNT", "12")
    monkeypatch.setenv("CLOUD_ARCH_LOG_RETENTION_DAYS", "120")

    result = service.health_check()

    assert result["status"] == "ok"
    assert result["metadata"]["name"] == "cloud-architecture"
    assert result["metadata"]["owner"] == "platform-team"

    checks = {check["name"]: check for check in result["checks"]}
    assert checks["account_inventory"]["status"] == "pass"
    assert checks["log_retention_days"]["status"] == "pass"
    assert result["config_summary"]["org_id"].startswith("o-12")
    assert result["config_summary"]["sso_instance_arn"].startswith("arn:")


def test_health_check_flags_invalid_bucket(monkeypatch):
    monkeypatch.setenv("CLOUD_ARCH_ORG_ID", "o-123456")
    monkeypatch.setenv("CLOUD_ARCH_AUDIT_BUCKET", "Invalid_Bucket")
    monkeypatch.setenv("CLOUD_ARCH_SSO_ARN", "arn:aws:sso:::instance/ssoins-123")

    result = service.health_check()
    checks = {check["name"]: check for check in result["checks"]}

    assert result["status"] == "degraded"
    assert checks["cloudtrail_bucket"]["status"] == "fail"


def test_service_metadata_includes_dependencies():
    metadata = service.service_metadata()
    assert "aws-organizations" in metadata.dependencies

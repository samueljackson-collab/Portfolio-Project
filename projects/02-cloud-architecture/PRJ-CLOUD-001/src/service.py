"""Cloud architecture service module.

Provides metadata and configuration-aware health checks for the landing zone
control plane.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List


@dataclass(frozen=True)
class ServiceMetadata:
    name: str
    owner: str
    description: str
    environment: str
    version: str
    runbook_url: str
    data_classification: str
    dependencies: List[str]

    def as_dict(self) -> Dict[str, object]:
        """Return the metadata as a plain dictionary for logging or reporting."""
        return {
            "name": self.name,
            "owner": self.owner,
            "description": self.description,
            "environment": self.environment,
            "version": self.version,
            "runbook_url": self.runbook_url,
            "data_classification": self.data_classification,
            "dependencies": list(self.dependencies),
        }


@dataclass(frozen=True)
class ServiceConfig:
    org_id: str
    audit_log_bucket: str
    sso_instance_arn: str
    region: str
    account_count: int
    log_retention_days: int


def load_config() -> ServiceConfig:
    """Load configuration from environment variables."""
    return ServiceConfig(
        org_id=os.getenv("CLOUD_ARCH_ORG_ID", ""),
        audit_log_bucket=os.getenv("CLOUD_ARCH_AUDIT_BUCKET", ""),
        sso_instance_arn=os.getenv("CLOUD_ARCH_SSO_ARN", ""),
        region=os.getenv("CLOUD_ARCH_REGION", "us-east-1"),
        account_count=int(os.getenv("CLOUD_ARCH_ACCOUNT_COUNT", "0")),
        log_retention_days=int(os.getenv("CLOUD_ARCH_LOG_RETENTION_DAYS", "90")),
    )


def service_metadata() -> ServiceMetadata:
    """Return metadata for the landing zone service."""
    return ServiceMetadata(
        name="cloud-architecture",
        owner="platform-team",
        description="Landing zone guardrails and account factory operations",
        environment=os.getenv("CLOUD_ARCH_ENVIRONMENT", "production"),
        version=os.getenv("CLOUD_ARCH_VERSION", "1.0.0"),
        runbook_url=os.getenv(
            "CLOUD_ARCH_RUNBOOK_URL",
            "https://wiki.example.com/runbooks/cloud-architecture",
        ),
        data_classification="internal",
        dependencies=[
            "aws-organizations",
            "aws-iam-identity-center",
            "aws-cloudtrail",
            "aws-config",
        ],
    )


def _check_org_id(org_id: str) -> Dict[str, str]:
    if not org_id:
        return {"name": "organizations_id", "status": "fail", "details": "missing"}
    if not org_id.startswith("o-") or len(org_id) < 6:
        return {
            "name": "organizations_id",
            "status": "fail",
            "details": "invalid format",
        }
    return {"name": "organizations_id", "status": "pass", "details": "configured"}


def _check_bucket_name(bucket: str) -> Dict[str, str]:
    if not bucket:
        return {"name": "cloudtrail_bucket", "status": "fail", "details": "missing"}
    pattern = re.compile(r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$")
    if not pattern.match(bucket):
        return {
            "name": "cloudtrail_bucket",
            "status": "fail",
            "details": "invalid bucket name",
        }
    return {"name": "cloudtrail_bucket", "status": "pass", "details": "configured"}


def _check_sso_arn(arn: str) -> Dict[str, str]:
    if not arn:
        return {"name": "sso_instance_arn", "status": "fail", "details": "missing"}
    if not arn.startswith("arn:") or "sso" not in arn or "instance/" not in arn:
        return {"name": "sso_instance_arn", "status": "fail", "details": "invalid arn"}
    return {"name": "sso_instance_arn", "status": "pass", "details": "configured"}


def _check_account_inventory(account_count: int) -> Dict[str, str]:
    status = "pass" if account_count >= 1 else "warn"
    return {
        "name": "account_inventory",
        "status": status,
        "details": f"{account_count} accounts tracked",
    }


def _check_log_retention(log_retention_days: int) -> Dict[str, str]:
    if log_retention_days >= 90:
        status = "pass"
    elif log_retention_days >= 30:
        status = "warn"
    else:
        status = "fail"
    return {
        "name": "log_retention_days",
        "status": status,
        "details": f"{log_retention_days} days",
    }


def _mask_value(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def health_check() -> Dict[str, object]:
    """Return health status for the cloud architecture service."""
    metadata = service_metadata()
    config = load_config()

    checks = [
        _check_org_id(config.org_id),
        _check_bucket_name(config.audit_log_bucket),
        _check_sso_arn(config.sso_instance_arn),
        _check_account_inventory(config.account_count),
        _check_log_retention(config.log_retention_days),
    ]

    required_ok = all(check["status"] == "pass" for check in checks[:3])
    has_failures = any(check["status"] == "fail" for check in checks)
    has_warnings = any(check["status"] == "warn" for check in checks)
    if not required_ok or has_failures:
        status = "degraded"
    elif has_warnings:
        status = "warning"
    else:
        status = "ok"

    return {
        "status": status,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "region": config.region,
        "metadata": metadata.as_dict(),
        "config_summary": {
            "org_id": _mask_value(config.org_id),
            "audit_log_bucket": config.audit_log_bucket,
            "sso_instance_arn": _mask_value(config.sso_instance_arn),
            "account_count": config.account_count,
            "log_retention_days": config.log_retention_days,
        },
        "checks": checks,
    }

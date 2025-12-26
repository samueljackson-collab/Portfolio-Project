"""Cloud architecture service module.

Provides metadata and configuration-aware health checks for the landing zone
control plane.
"""
from __future__ import annotations

import os
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


def _check_required(value: str, label: str) -> Dict[str, str]:
    status = "pass" if value else "fail"
    details = "configured" if value else "missing"
    return {"name": label, "status": status, "details": details}


def health_check() -> Dict[str, object]:
    """Return health status for the cloud architecture service."""
    metadata = service_metadata()
    config = load_config()

    checks = [
        _check_required(config.org_id, "organizations_id"),
        _check_required(config.audit_log_bucket, "cloudtrail_bucket"),
        _check_required(config.sso_instance_arn, "sso_instance_arn"),
        {
            "name": "account_inventory",
            "status": "pass" if config.account_count > 0 else "warn",
            "details": f"{config.account_count} accounts tracked",
        },
        {
            "name": "log_retention_days",
            "status": "pass" if config.log_retention_days >= 90 else "warn",
            "details": f"{config.log_retention_days} days",
        },
    ]

    required_ok = all(check["status"] == "pass" for check in checks[:3])
    status = "ok" if required_ok else "degraded"

    return {
        "status": status,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "region": config.region,
        "metadata": metadata.as_dict(),
        "checks": checks,
    }

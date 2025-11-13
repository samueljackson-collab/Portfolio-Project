"""AWS service integrations."""

from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.metrics import record_aws_call


class AWSServiceError(RuntimeError):
    """Raised when AWS SDK requests fail."""


class AWSResourceService:
    """Wrapper around boto3 clients to keep business logic testable."""

    def __init__(
        self,
        *,
        region: str,
        s3_client: Optional[Any] = None,
        secrets_client: Optional[Any] = None,
        cloudwatch_client: Optional[Any] = None,
    ) -> None:
        self.region = region
        self.s3_client = s3_client or boto3.client("s3", region_name=region)
        self.secrets_client = secrets_client or boto3.client("secretsmanager", region_name=region)
        self.cloudwatch_client = cloudwatch_client or boto3.client("cloudwatch", region_name=region)

    def list_s3_buckets(self) -> List[Dict[str, str]]:
        """Return metadata for all accessible S3 buckets."""

        try:
            response = self.s3_client.list_buckets()
            record_aws_call("s3", "list_buckets", True)
        except (ClientError, BotoCoreError) as exc:  # pragma: no cover - defensive
            record_aws_call("s3", "list_buckets", False)
            raise AWSServiceError("Unable to list S3 buckets") from exc

        buckets = []
        for bucket in response.get("Buckets", []):
            creation = bucket.get("CreationDate")
            creation_iso = creation.isoformat() if isinstance(creation, dt.datetime) else None
            buckets.append({
                "name": bucket.get("Name", "unknown"),
                "creation_date": creation_iso,
            })
        return buckets

    def describe_secret(self, secret_id: str) -> Dict[str, Any]:
        """Return metadata for a secret without exposing the value."""

        try:
            response = self.secrets_client.describe_secret(SecretId=secret_id)
            record_aws_call("secretsmanager", "describe_secret", True)
        except (ClientError, BotoCoreError) as exc:  # pragma: no cover - defensive
            record_aws_call("secretsmanager", "describe_secret", False)
            raise AWSServiceError("Unable to describe secret") from exc

        return {
            "name": response.get("Name"),
            "rotation_enabled": response.get("RotationEnabled", False),
            "tags": response.get("Tags", []),
            "last_rotated": response.get("LastRotatedDate").isoformat()
            if isinstance(response.get("LastRotatedDate"), dt.datetime)
            else None,
        }

    def publish_custom_metric(self, metric_name: str, value: float, unit: str = "Count") -> Dict[str, Any]:
        """Send a single metric data point to CloudWatch."""

        try:
            response = self.cloudwatch_client.put_metric_data(
                Namespace="AWSInfra/Custom",
                MetricData=[
                    {
                        "MetricName": metric_name,
                        "Timestamp": dt.datetime.utcnow(),
                        "Value": value,
                        "Unit": unit,
                    }
                ],
            )
            record_aws_call("cloudwatch", "put_metric_data", True)
        except (ClientError, BotoCoreError) as exc:  # pragma: no cover - defensive
            record_aws_call("cloudwatch", "put_metric_data", False)
            raise AWSServiceError("Unable to publish CloudWatch metric") from exc

        return {"metric_name": metric_name, "value": value, "unit": unit, "response_metadata": response.get("ResponseMetadata", {})}

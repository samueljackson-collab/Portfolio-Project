"""Tests for AWSResourceService."""

import datetime as dt

import boto3
from botocore.stub import Stubber

from src.services import AWSResourceService


def test_list_s3_buckets_returns_normalized():
    client = boto3.client("s3", region_name="us-east-1")
    stubber = Stubber(client)
    stubber.add_response(
        "list_buckets",
        {
            "Buckets": [
                {"Name": "demo", "CreationDate": dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)}
            ]
        },
    )

    with stubber:
        service = AWSResourceService(region="us-east-1", s3_client=client)
        buckets = service.list_s3_buckets()

    assert buckets == [{"name": "demo", "creation_date": "2024-01-01T00:00:00+00:00"}]


def test_publish_metric_returns_shape():
    client = boto3.client("cloudwatch", region_name="us-east-1")
    stubber = Stubber(client)
    stubber.add_response(
        "put_metric_data",
        {"ResponseMetadata": {"HTTPStatusCode": 200}},
    )

    with stubber:
        service = AWSResourceService(region="us-east-1", cloudwatch_client=client)
        response = service.publish_custom_metric("Latency", 1.0, "Milliseconds")

    assert response["metric_name"] == "Latency"
    assert response["value"] == 1.0
    assert response["unit"] == "Milliseconds"

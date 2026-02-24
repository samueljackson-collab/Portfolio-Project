"""Tests for the serverless data processing lambda handlers.

Uses unittest.mock to replace boto3 clients so tests run without AWS credentials.
"""
from __future__ import annotations

import json
import os
from decimal import Decimal
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# Provide required environment variables before importing the module
os.environ.setdefault("CURATED_TABLE", "test-table")
os.environ.setdefault("WORKFLOW_ARN", "arn:aws:states:us-east-1:123456789012:stateMachine:test")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from src.lambda_pipeline import (
    _decimalify,
    _enrich_payload,
    _validate_payload,
    analytics_handler,
    ingestion_handler,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_event(data: Dict[str, Any]) -> Dict[str, Any]:
    return data


def _make_valid_payload(**overrides) -> Dict[str, Any]:
    base = {
        "id": "evt-001",
        "user_id": "usr-42",
        "timestamp": "2024-01-01T00:00:00Z",
        "event_type": "purchase",
        "amount": 99.99,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# _decimalify
# ---------------------------------------------------------------------------

def test_decimalify_float():
    result = _decimalify(3.14)
    assert isinstance(result, Decimal)
    assert result == Decimal("3.14")


def test_decimalify_dict():
    result = _decimalify({"price": 1.5, "name": "item"})
    assert isinstance(result["price"], Decimal)
    assert result["name"] == "item"


def test_decimalify_list():
    result = _decimalify([1.0, 2.5])
    assert all(isinstance(v, Decimal) for v in result)


def test_decimalify_nested():
    result = _decimalify({"nested": {"value": 7.7}})
    assert isinstance(result["nested"]["value"], Decimal)


def test_decimalify_passthrough():
    assert _decimalify("hello") == "hello"
    assert _decimalify(42) == 42


# ---------------------------------------------------------------------------
# _validate_payload
# ---------------------------------------------------------------------------

def test_validate_payload_valid():
    payload = _make_valid_payload()
    result = _validate_payload(payload)
    assert result["id"] == "evt-001"


def test_validate_payload_missing_field():
    payload = {"id": "x", "user_id": "y", "timestamp": "t"}  # missing event_type
    with pytest.raises(ValueError, match="Missing fields"):
        _validate_payload(payload)


def test_validate_payload_empty():
    with pytest.raises(ValueError, match="Missing fields"):
        _validate_payload({})


# ---------------------------------------------------------------------------
# _enrich_payload
# ---------------------------------------------------------------------------

def test_enrich_payload_adds_defaults():
    payload = _make_valid_payload()
    del payload["amount"]
    enriched = _enrich_payload(payload)
    assert "ingested_at" in enriched
    assert enriched["amount"] == 0.0
    assert enriched["channel"] == "api"


def test_enrich_payload_preserves_existing():
    payload = _make_valid_payload(amount=500.0, channel="web")
    enriched = _enrich_payload(payload)
    assert enriched["amount"] == 500.0
    assert enriched["channel"] == "web"


# ---------------------------------------------------------------------------
# analytics_handler
# ---------------------------------------------------------------------------

def test_analytics_handler_basic():
    records = [
        {"user_id": "u1", "amount": 10.0},
        {"user_id": "u2", "amount": 20.0},
        {"user_id": "u1", "amount": 5.0},
    ]
    event = {"records": records}
    response = analytics_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["total_records"] == 3
    assert body["total_amount"] == 35.0
    assert body["unique_users"] == 2


def test_analytics_handler_empty():
    response = analytics_handler({"records": []}, None)
    body = json.loads(response["body"])
    assert body["total_records"] == 0
    assert body["total_amount"] == 0.0
    assert body["unique_users"] == 0


def test_analytics_handler_missing_amounts():
    records = [{"user_id": "u1"}, {"user_id": "u2"}]
    response = analytics_handler({"records": records}, None)
    body = json.loads(response["body"])
    assert body["total_amount"] == 0.0


def test_analytics_handler_timestamp_present():
    response = analytics_handler({"records": []}, None)
    body = json.loads(response["body"])
    assert "generated_at" in body


# ---------------------------------------------------------------------------
# ingestion_handler (mocked boto3)
# ---------------------------------------------------------------------------

@patch("src.lambda_pipeline.step_functions")
@patch("src.lambda_pipeline.dynamodb")
def test_ingestion_handler_direct_event(mock_dynamodb, mock_sfn):
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_sfn.start_execution.return_value = {}

    payload = _make_valid_payload()
    response = ingestion_handler(payload, None)

    assert response["statusCode"] == 202
    body = json.loads(response["body"])
    assert body["records"] == 1
    mock_table.put_item.assert_called_once()


@patch("src.lambda_pipeline.step_functions")
@patch("src.lambda_pipeline.dynamodb")
def test_ingestion_handler_json_body(mock_dynamodb, mock_sfn):
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table
    mock_sfn.start_execution.return_value = {}

    payload = _make_valid_payload()
    event = {"body": json.dumps(payload)}
    response = ingestion_handler(event, None)

    assert response["statusCode"] == 202


@patch("src.lambda_pipeline.step_functions")
@patch("src.lambda_pipeline.dynamodb")
def test_ingestion_handler_starts_workflow(mock_dynamodb, mock_sfn):
    mock_table = MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    payload = _make_valid_payload()
    ingestion_handler(payload, None)

    mock_sfn.start_execution.assert_called_once()
    call_kwargs = mock_sfn.start_execution.call_args[1]
    assert call_kwargs["stateMachineArn"] == os.environ["WORKFLOW_ARN"]

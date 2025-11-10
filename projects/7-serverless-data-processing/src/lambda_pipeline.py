"""Lambda handlers for the serverless data processing pipeline."""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List

import boto3

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")
step_functions = boto3.client("stepfunctions")


def _decimalify(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _decimalify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_decimalify(v) for v in value]
    return value


def ingestion_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    """Process API Gateway or S3 events and dispatch to Step Functions."""
    LOGGER.info("Received ingestion event", extra={"event": event})

    payloads: List[Dict[str, Any]]
    if "Records" in event:  # S3 trigger
        payloads = [_load_from_s3(record) for record in event["Records"]]
    else:  # direct/API invocation
        body = event.get("body", event)
        payloads = [json.loads(body) if isinstance(body, str) else body]

    table = dynamodb.Table(os.environ["CURATED_TABLE"])
    for payload in payloads:
        validated = _validate_payload(payload)
        enriched = _enrich_payload(validated)
        table.put_item(Item=_decimalify(enriched))
        _start_workflow(enriched)

    return {"statusCode": 202, "body": json.dumps({"records": len(payloads)})}


def analytics_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    """Aggregate enriched events and compute rolling KPIs."""
    LOGGER.info("Running analytics", extra={"event": event})
    records = event.get("records", [])
    total_amount = sum(record.get("amount", 0.0) for record in records)
    unique_users = {record.get("user_id") for record in records}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "total_records": len(records),
                "total_amount": total_amount,
                "unique_users": len(unique_users),
                "generated_at": datetime.utcnow().isoformat(),
            }
        ),
    }


def _load_from_s3(record: Dict[str, Any]) -> Dict[str, Any]:
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]
    response = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response["Body"].read())


def _validate_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = {"id", "user_id", "timestamp", "event_type"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    return payload


def _enrich_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    payload.setdefault("ingested_at", datetime.utcnow().isoformat())
    payload.setdefault("amount", 0.0)
    payload.setdefault("channel", "api")
    return payload


def _start_workflow(payload: Dict[str, Any]) -> None:
    state_machine = os.environ["WORKFLOW_ARN"]
    step_functions.start_execution(
        stateMachineArn=state_machine,
        input=json.dumps({"payload": payload, "received_at": datetime.utcnow().isoformat()}),
    )


__all__ = ["ingestion_handler", "analytics_handler"]

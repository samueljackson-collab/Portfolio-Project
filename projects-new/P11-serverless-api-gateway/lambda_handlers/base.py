"""Base utilities for Lambda handlers."""
import json
import logging
import os
from typing import Any, Dict, Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

TABLE_NAME = os.environ.get("TABLE_NAME", "items-table")

# Lazy initialization of dynamodb to support mocking in tests
_dynamodb = None


def _get_dynamodb():
    """Get or initialize DynamoDB resource (lazy initialization)."""
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    return _dynamodb


def get_table():
    """Get DynamoDB table resource."""
    return _get_dynamodb().Table(TABLE_NAME)


def response(status_code: int, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict:
    """Format Lambda response for API Gateway."""
    default_headers = {
        "Content-Type": "application/json",
        "X-Service": "serverless-api-gateway",
    }
    if headers:
        default_headers.update(headers)

    return {
        "statusCode": status_code,
        "headers": default_headers,
        "body": json.dumps(body) if isinstance(body, dict) else body,
    }


def error_response(status_code: int, message: str) -> Dict:
    """Format error response."""
    return response(status_code, {"error": message})


def parse_json_body(event: Dict) -> Optional[Dict]:
    """Parse JSON body from API Gateway event."""
    try:
        body = event.get("body", "")
        if isinstance(body, str):
            return json.loads(body) if body else {}
        return body or {}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {e}")
        return None


def validate_required_fields(data: Dict, required_fields: list) -> Optional[str]:
    """Validate that required fields are present in data."""
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return f"Missing required field: {field}"
    return None


def log_event(event: Dict, operation: str) -> None:
    """Log API event details."""
    logger.info(
        f"Operation: {operation} | "
        f"Path: {event.get('path')} | "
        f"Method: {event.get('httpMethod')} | "
        f"RequestID: {event.get('requestContext', {}).get('requestId', 'N/A')}"
    )

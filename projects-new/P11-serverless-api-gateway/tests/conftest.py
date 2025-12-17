"""Pytest configuration and fixtures."""
import json
import os
import sys
from pathlib import Path
import pytest
import boto3
from moto import mock_aws

# Add lambda_handlers to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lambda_handlers"))

# Environment setup for testing
os.environ["TABLE_NAME"] = "items-table-test"
os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture
def dynamodb_table():
    """Create a mock DynamoDB table for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table(
            TableName="items-table-test",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        yield table


@pytest.fixture
def api_event_base():
    """Base API Gateway event structure."""
    return {
        "httpMethod": "GET",
        "path": "/items",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer dev-key-12345",
        },
        "requestContext": {
            "requestId": "test-request-id",
            "accountId": "123456789012",
            "stage": "test",
        },
        "queryStringParameters": None,
        "pathParameters": None,
        "body": None,
    }


@pytest.fixture
def sample_item():
    """Sample item for testing."""
    return {
        "id": "test-item-123",
        "name": "Test Item",
        "description": "A test item for testing",
        "price": 29.99,
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }

"""Unit tests for CREATE Lambda handler."""
import json
import sys
import os
from pathlib import Path
from moto import mock_aws
import boto3
import pytest

# Add lambda_handlers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lambda_handlers"))

os.environ["TABLE_NAME"] = "items-table-test"


@mock_aws
def test_create_item_success(api_event_base, sample_item):
    """Test successful item creation."""
    from create import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "POST"
    event["path"] = "/items"
    event["body"] = json.dumps({
        "name": "Test Item",
        "description": "A test item",
        "price": 29.99
    })

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["name"] == "Test Item"
    assert body["description"] == "A test item"
    assert body["price"] == 29.99
    assert body["status"] == "active"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


@mock_aws
def test_create_item_missing_name(api_event_base):
    """Test creation fails when name is missing."""
    from create import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "POST"
    event["body"] = json.dumps({
        "description": "Missing name",
        "price": 19.99
    })

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body


@mock_aws
def test_create_item_invalid_price(api_event_base):
    """Test creation fails with invalid price."""
    from create import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "POST"
    event["body"] = json.dumps({
        "name": "Test Item",
        "description": "Test",
        "price": "not-a-number"
    })

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400


@mock_aws
def test_create_item_invalid_json(api_event_base):
    """Test creation fails with invalid JSON."""
    from create import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "POST"
    event["body"] = "invalid json {"

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body

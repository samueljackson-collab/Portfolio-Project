"""Unit tests for READ Lambda handler."""

import json
import sys
import os
from pathlib import Path
from moto import mock_aws
import boto3
import pytest
from decimal import Decimal

# Add lambda_handlers to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lambda_handlers"))

os.environ["TABLE_NAME"] = "items-table-test"


@mock_aws
def test_read_item_by_id(api_event_base, sample_item):
    """Test retrieving a specific item by ID."""
    from read import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    table.put_item(Item=sample_item)

    event = api_event_base.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/items/test-item-123"
    event["pathParameters"] = {"item_id": "test-item-123"}

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["id"] == "test-item-123"
    assert body["name"] == "Test Item"


@mock_aws
def test_read_item_not_found(api_event_base):
    """Test reading non-existent item returns 404."""
    from read import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/items/non-existent"
    event["pathParameters"] = {"item_id": "non-existent"}

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert "error" in body


@mock_aws
def test_list_items(api_event_base, sample_item):
    """Test listing all items."""
    from read import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    # Insert multiple items
    for i in range(3):
        item = sample_item.copy()
        item["id"] = f"test-item-{i}"
        item["name"] = f"Item {i}"
        table.put_item(Item=item)

    event = api_event_base.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/items"
    event["pathParameters"] = None

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "items" in body
    assert "count" in body
    assert body["count"] == 3


@mock_aws
def test_list_items_with_limit(api_event_base, sample_item):
    """Test listing items with limit parameter."""
    from read import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    # Insert multiple items
    for i in range(5):
        item = sample_item.copy()
        item["id"] = f"test-item-{i}"
        item["name"] = f"Item {i}"
        table.put_item(Item=item)

    event = api_event_base.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/items"
    event["queryStringParameters"] = {"limit": "2"}

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] <= 2


@mock_aws
def test_list_items_invalid_limit(api_event_base):
    """Test listing items with invalid limit parameter."""
    from read import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "GET"
    event["path"] = "/items"
    event["queryStringParameters"] = {"limit": "invalid"}

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body

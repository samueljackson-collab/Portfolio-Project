"""Unit tests for UPDATE Lambda handler."""
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
def test_update_item_success(api_event_base, sample_item):
    """Test successful item update."""
    from update import lambda_handler

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
    event["httpMethod"] = "PUT"
    event["path"] = "/items/test-item-123"
    event["pathParameters"] = {"item_id": "test-item-123"}
    event["body"] = json.dumps({
        "name": "Updated Name",
        "price": 39.99
    })

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["name"] == "Updated Name"
    assert body["price"] == 39.99
    assert body["description"] == sample_item["description"]  # Unchanged


@mock_aws
def test_update_item_not_found(api_event_base):
    """Test updating non-existent item returns 404."""
    from update import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "PUT"
    event["path"] = "/items/non-existent"
    event["pathParameters"] = {"item_id": "non-existent"}
    event["body"] = json.dumps({"name": "Updated"})

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 404


@mock_aws
def test_update_item_missing_id(api_event_base):
    """Test update fails when item_id is missing."""
    from update import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "PUT"
    event["body"] = json.dumps({"name": "Updated"})
    event["pathParameters"] = None

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400


@mock_aws
def test_update_item_empty_body(api_event_base, sample_item):
    """Test update fails with empty body."""
    from update import lambda_handler

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
    event["httpMethod"] = "PUT"
    event["pathParameters"] = {"item_id": "test-item-123"}
    event["body"] = "{}"

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400


@mock_aws
def test_update_item_invalid_price(api_event_base, sample_item):
    """Test update fails with invalid price."""
    from update import lambda_handler

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
    event["httpMethod"] = "PUT"
    event["pathParameters"] = {"item_id": "test-item-123"}
    event["body"] = json.dumps({"price": "invalid"})

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400


@mock_aws
def test_update_item_status(api_event_base, sample_item):
    """Test updating item status."""
    from update import lambda_handler

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
    event["httpMethod"] = "PUT"
    event["pathParameters"] = {"item_id": "test-item-123"}
    event["body"] = json.dumps({"status": "inactive"})

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "inactive"

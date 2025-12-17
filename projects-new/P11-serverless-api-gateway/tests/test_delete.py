"""Unit tests for DELETE Lambda handler."""
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
def test_delete_item_success(api_event_base, sample_item):
    """Test successful item deletion."""
    from delete import lambda_handler

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
    event["httpMethod"] = "DELETE"
    event["path"] = "/items/test-item-123"
    event["pathParameters"] = {"item_id": "test-item-123"}

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 204

    # Verify item is deleted
    result = table.get_item(Key={"id": "test-item-123"})
    assert "Item" not in result


@mock_aws
def test_delete_item_not_found(api_event_base):
    """Test deleting non-existent item returns 404."""
    from delete import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "DELETE"
    event["path"] = "/items/non-existent"
    event["pathParameters"] = {"item_id": "non-existent"}

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 404
    body = json.loads(response["body"])
    assert "error" in body


@mock_aws
def test_delete_item_missing_id(api_event_base):
    """Test delete fails when item_id is missing."""
    from delete import lambda_handler

    # Setup
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    event = api_event_base.copy()
    event["httpMethod"] = "DELETE"
    event["path"] = "/items/"
    event["pathParameters"] = None

    # Execute
    response = lambda_handler(event, None)

    # Assert
    assert response["statusCode"] == 400

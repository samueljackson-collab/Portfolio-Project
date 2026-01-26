"""Integration tests for P11 Serverless API Gateway."""

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


def create_api_event(
    method, path, body=None, path_parameters=None, query_parameters=None
):
    """Helper to create API Gateway events."""
    return {
        "httpMethod": method,
        "path": path,
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer dev-key-12345",
        },
        "requestContext": {
            "requestId": f"test-{method}-{path}",
            "accountId": "123456789012",
            "stage": "test",
        },
        "queryStringParameters": query_parameters,
        "pathParameters": path_parameters,
        "body": json.dumps(body) if body else None,
    }


@mock_aws
def test_full_crud_workflow():
    """Test complete CRUD workflow: Create -> Read -> Update -> Delete."""
    from create import lambda_handler as create_handler
    from read import lambda_handler as read_handler
    from update import lambda_handler as update_handler
    from delete import lambda_handler as delete_handler

    # Setup DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    # Step 1: CREATE
    create_event = create_api_event(
        "POST",
        "/items",
        {"name": "Integration Test Item", "description": "Test item", "price": 99.99},
    )
    create_response = create_handler(create_event, None)
    assert create_response["statusCode"] == 201
    created_item = json.loads(create_response["body"])
    item_id = created_item["id"]
    assert created_item["name"] == "Integration Test Item"

    # Step 2: READ (Get specific item)
    read_event = create_api_event(
        "GET", f"/items/{item_id}", path_parameters={"item_id": item_id}
    )
    read_response = read_handler(read_event, None)
    assert read_response["statusCode"] == 200
    read_item = json.loads(read_response["body"])
    assert read_item["id"] == item_id
    assert read_item["name"] == "Integration Test Item"

    # Step 3: UPDATE
    update_event = create_api_event(
        "PUT",
        f"/items/{item_id}",
        {"name": "Updated Integration Item", "price": 149.99},
        path_parameters={"item_id": item_id},
    )
    update_response = update_handler(update_event, None)
    assert update_response["statusCode"] == 200
    updated_item = json.loads(update_response["body"])
    assert updated_item["name"] == "Updated Integration Item"
    assert updated_item["price"] == 149.99

    # Step 4: DELETE
    delete_event = create_api_event(
        "DELETE", f"/items/{item_id}", path_parameters={"item_id": item_id}
    )
    delete_response = delete_handler(delete_event, None)
    assert delete_response["statusCode"] == 204

    # Verify item is deleted
    verify_event = create_api_event(
        "GET", f"/items/{item_id}", path_parameters={"item_id": item_id}
    )
    verify_response = read_handler(verify_event, None)
    assert verify_response["statusCode"] == 404


@mock_aws
def test_list_items_after_multiple_creates():
    """Test listing items after creating multiple items."""
    from create import lambda_handler as create_handler
    from read import lambda_handler as read_handler

    # Setup DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    # Create multiple items
    for i in range(3):
        event = create_api_event(
            "POST",
            "/items",
            {"name": f"Item {i}", "description": f"Description {i}", "price": 10.0 + i},
        )
        response = create_handler(event, None)
        assert response["statusCode"] == 201

    # List items
    list_event = create_api_event("GET", "/items")
    list_response = read_handler(list_event, None)
    assert list_response["statusCode"] == 200
    items_data = json.loads(list_response["body"])
    assert items_data["count"] == 3
    assert len(items_data["items"]) == 3


@mock_aws
def test_concurrent_operations():
    """Test handling multiple concurrent-like operations."""
    from create import lambda_handler as create_handler
    from read import lambda_handler as read_handler

    # Setup DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    # Create first item
    event1 = create_api_event(
        "POST", "/items", {"name": "Item 1", "description": "First", "price": 19.99}
    )
    response1 = create_handler(event1, None)
    item1_id = json.loads(response1["body"])["id"]

    # Create second item
    event2 = create_api_event(
        "POST", "/items", {"name": "Item 2", "description": "Second", "price": 29.99}
    )
    response2 = create_handler(event2, None)
    item2_id = json.loads(response2["body"])["id"]

    # Read first item
    read1_event = create_api_event(
        "GET", f"/items/{item1_id}", path_parameters={"item_id": item1_id}
    )
    read1_response = read_handler(read1_event, None)
    assert read1_response["statusCode"] == 200

    # Read second item
    read2_event = create_api_event(
        "GET", f"/items/{item2_id}", path_parameters={"item_id": item2_id}
    )
    read2_response = read_handler(read2_event, None)
    assert read2_response["statusCode"] == 200

    # Verify both items exist
    both_items = [
        json.loads(read1_response["body"]),
        json.loads(read2_response["body"]),
    ]
    assert len(both_items) == 2
    assert both_items[0]["name"] == "Item 1"
    assert both_items[1]["name"] == "Item 2"


@mock_aws
def test_error_scenarios():
    """Test various error scenarios."""
    from create import lambda_handler as create_handler
    from read import lambda_handler as read_handler
    from update import lambda_handler as update_handler

    # Setup DynamoDB
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="items-table-test",
        KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

    # Test 1: Create with missing fields
    create_event = create_api_event(
        "POST", "/items", {"name": "Incomplete Item"}  # Missing description and price
    )
    create_response = create_handler(create_event, None)
    assert create_response["statusCode"] == 400

    # Test 2: Read non-existent item
    read_event = create_api_event(
        "GET", "/items/nonexistent", path_parameters={"item_id": "nonexistent"}
    )
    read_response = read_handler(read_event, None)
    assert read_response["statusCode"] == 404

    # Test 3: Update non-existent item
    update_event = create_api_event(
        "PUT",
        "/items/nonexistent",
        {"name": "Updated"},
        path_parameters={"item_id": "nonexistent"},
    )
    update_response = update_handler(update_event, None)
    assert update_response["statusCode"] == 404

    # Test 4: Invalid JSON
    create_event_bad_json = create_api_event("POST", "/items")
    create_event_bad_json["body"] = "invalid json {"
    create_response = create_handler(create_event_bad_json, None)
    assert create_response["statusCode"] == 400

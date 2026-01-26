"""Lambda handler for UPDATE operations."""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from decimal import Decimal

try:
    from base import (
        get_table,
        response,
        error_response,
        parse_json_body,
        log_event,
    )
except ImportError:
    from lambda_handlers.base import (
        get_table,
        response,
        error_response,
        parse_json_body,
        log_event,
    )

logger = logging.getLogger(__name__)


def decimal_to_json(obj):
    """Convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """
    Handle PUT/PATCH requests to update existing items.

    Expected JSON body (all fields optional):
    {
        "name": "Updated Name",
        "description": "Updated Description",
        "price": 49.99,
        "status": "inactive"
    }
    """
    log_event(event, "UPDATE")

    try:
        path_parameters = event.get("pathParameters", {})
        if not path_parameters or "item_id" not in path_parameters:
            return error_response(400, "Missing item_id in path")

        item_id = path_parameters["item_id"]

        # Parse request body
        body = parse_json_body(event)
        if body is None:
            return error_response(400, "Invalid JSON in request body")

        if not body:
            return error_response(400, "Request body cannot be empty")

        table = get_table()

        # Check if item exists
        response_obj = table.get_item(Key={"id": item_id})
        if "Item" not in response_obj:
            logger.warning(f"Item not found for update: {item_id}")
            return error_response(404, f"Item not found: {item_id}")

        # Build update expression
        update_expression = "SET updated_at = :updated_at"
        expression_values = {
            ":updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        expression_names = {}

        # Add allowed fields to update
        allowed_fields = ["name", "description", "price", "status"]
        for field in allowed_fields:
            if field in body:
                if field == "price":
                    try:
                        body[field] = float(body[field])
                    except (ValueError, TypeError):
                        return error_response(400, f"Invalid value for {field}")
                elif field in ["name", "description", "status"]:
                    body[field] = str(body[field]).strip()
                    if not body[field]:
                        return error_response(400, f"Field {field} cannot be empty")

                update_expression += f", #{field} = :{field}"
                expression_names[f"#{field}"] = field
                expression_values[f":{field}"] = body[field]

        # Execute update
        table.update_item(
            Key={"id": item_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW",
        )

        # Retrieve updated item
        updated = table.get_item(Key={"id": item_id})
        item = updated.get("Item", {})

        logger.info(f"Item updated successfully: {item_id}")
        return response(200, json.loads(json.dumps(item, default=decimal_to_json)))

    except Exception as e:
        logger.error(f"Error updating item: {str(e)}", exc_info=True)
        return error_response(500, "Internal server error")


if __name__ == "__main__":
    # Local testing
    test_event = {
        "httpMethod": "PUT",
        "path": "/items/123",
        "pathParameters": {"item_id": "123"},
        "body": json.dumps({"name": "Updated Item", "price": 39.99}),
        "requestContext": {"requestId": "test-789"},
    }
    print(json.dumps(lambda_handler(test_event, None), indent=2))

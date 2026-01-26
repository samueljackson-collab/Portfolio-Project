"""Lambda handler for CREATE operations."""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

try:
    # When deployed in Lambda
    from base import (
        get_table,
        response,
        error_response,
        parse_json_body,
        validate_required_fields,
        log_event,
    )
except ImportError:
    # When running locally for testing
    from lambda_handlers.base import (
        get_table,
        response,
        error_response,
        parse_json_body,
        validate_required_fields,
        log_event,
    )

logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """
    Handle POST requests to create new items.

    Expected JSON body:
    {
        "name": "Item Name",
        "description": "Item Description",
        "price": 99.99
    }
    """
    log_event(event, "CREATE")

    # Parse request body
    body = parse_json_body(event)
    if body is None:
        return error_response(400, "Invalid JSON in request body")

    # Validate required fields
    error = validate_required_fields(body, ["name", "description", "price"])
    if error:
        return error_response(400, error)

    try:
        # Generate item ID and timestamps
        item_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Prepare item with metadata
        item = {
            "id": item_id,
            "name": body["name"].strip(),
            "description": body["description"].strip(),
            "price": float(body["price"]),
            "created_at": now,
            "updated_at": now,
            "status": "active",
        }

        # Store in DynamoDB
        table = get_table()
        table.put_item(Item=item)

        logger.info(f"Item created successfully: {item_id}")
        return response(201, item)

    except (ValueError, TypeError) as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(400, f"Invalid input: {str(e)}")

    except Exception as e:
        logger.error(f"Error creating item: {str(e)}", exc_info=True)
        return error_response(500, "Internal server error")


if __name__ == "__main__":
    # Local testing
    test_event = {
        "httpMethod": "POST",
        "path": "/items",
        "body": json.dumps(
            {"name": "Test Item", "description": "A test item", "price": 29.99}
        ),
        "requestContext": {"requestId": "test-123"},
    }
    print(json.dumps(lambda_handler(test_event, None), indent=2))

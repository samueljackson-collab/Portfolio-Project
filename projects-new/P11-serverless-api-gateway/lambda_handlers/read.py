"""Lambda handler for READ operations."""
import json
import logging
from typing import Dict, Any
from decimal import Decimal

try:
    from base import get_table, response, error_response, log_event
except ImportError:
    from lambda_handlers.base import get_table, response, error_response, log_event

logger = logging.getLogger(__name__)


def decimal_to_json(obj):
    """Convert Decimal objects to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """
    Handle GET requests to retrieve items.

    Can retrieve:
    - GET /items/{id} - Get a specific item
    - GET /items - List all items (with optional pagination)
    """
    log_event(event, "READ")

    try:
        path = event.get("path", "")
        path_parameters = event.get("pathParameters", {})

        table = get_table()

        # If item_id is provided, get specific item
        if path_parameters and "item_id" in path_parameters:
            item_id = path_parameters["item_id"]
            response_obj = table.get_item(Key={"id": item_id})

            if "Item" not in response_obj:
                logger.warning(f"Item not found: {item_id}")
                return error_response(404, f"Item not found: {item_id}")

            item = response_obj["Item"]
            logger.info(f"Item retrieved successfully: {item_id}")
            return response(200, json.loads(json.dumps(item, default=decimal_to_json)))

        # Otherwise, list all items
        else:
            limit = 100  # Default limit
            query_params = event.get("queryStringParameters") or {}
            if "limit" in query_params:
                try:
                    limit = min(int(query_params["limit"]), 1000)
                except ValueError:
                    return error_response(400, "Invalid limit parameter")

            scan_response = table.scan(Limit=limit)
            items = scan_response.get("Items", [])
            last_key = scan_response.get("LastEvaluatedKey")

            result = {
                "items": json.loads(json.dumps(items, default=decimal_to_json)),
                "count": len(items),
                "last_key": last_key,
            }

            logger.info(f"Retrieved {len(items)} items")
            return response(200, result)

    except Exception as e:
        logger.error(f"Error retrieving items: {str(e)}", exc_info=True)
        return error_response(500, "Internal server error")


if __name__ == "__main__":
    # Local testing - list items
    test_event = {
        "httpMethod": "GET",
        "path": "/items",
        "requestContext": {"requestId": "test-456"}
    }
    print(json.dumps(lambda_handler(test_event, None), indent=2))

    # Local testing - get specific item
    test_event_single = {
        "httpMethod": "GET",
        "path": "/items/123",
        "pathParameters": {"item_id": "123"},
        "requestContext": {"requestId": "test-457"}
    }
    print("\n---\n")
    print(json.dumps(lambda_handler(test_event_single, None), indent=2))

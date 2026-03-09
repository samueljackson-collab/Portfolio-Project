"""Lambda handler for DELETE operations."""

import json
import logging
from typing import Dict, Any

try:
    from base import get_table, response, error_response, log_event
except ImportError:
    from lambda_handlers.base import get_table, response, error_response, log_event

logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict:
    """
    Handle DELETE requests to remove items.

    DELETE /items/{id}
    """
    log_event(event, "DELETE")

    try:
        path_parameters = event.get("pathParameters", {})
        if not path_parameters or "item_id" not in path_parameters:
            return error_response(400, "Missing item_id in path")

        item_id = path_parameters["item_id"]

        table = get_table()

        # Check if item exists
        response_obj = table.get_item(Key={"id": item_id})
        if "Item" not in response_obj:
            logger.warning(f"Item not found for deletion: {item_id}")
            return error_response(404, f"Item not found: {item_id}")

        # Delete the item
        table.delete_item(Key={"id": item_id})

        logger.info(f"Item deleted successfully: {item_id}")
        return response(204, {})

    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}", exc_info=True)
        return error_response(500, "Internal server error")


if __name__ == "__main__":
    # Local testing
    test_event = {
        "httpMethod": "DELETE",
        "path": "/items/123",
        "pathParameters": {"item_id": "123"},
        "requestContext": {"requestId": "test-999"},
    }
    print(json.dumps(lambda_handler(test_event, None), indent=2))

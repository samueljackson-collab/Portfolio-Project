"""Lambda functions for Step Functions workflow tasks."""

import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def validate_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Validate input data.

    Args:
        event: Input event
        context: Lambda context

    Returns:
        Validated event with metadata
    """
    logger.info(f"Validating input: {json.dumps(event)}")

    # Required fields
    required_fields = ["id", "data"]

    # Validation
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing required field: {field}")

    # Add validation metadata
    event["validated_at"] = datetime.utcnow().isoformat()
    event["validation_status"] = "passed"

    logger.info("Validation successful")
    return event


def transform_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Transform data.

    Args:
        event: Input event
        context: Lambda context

    Returns:
        Transformed data
    """
    logger.info("Transforming data")

    data = event.get("data", {})

    # Example transformations
    transformed = {
        "original": data,
        "normalized": {k: str(v).lower() for k, v in data.items()},
        "transformed_at": datetime.utcnow().isoformat(),
    }

    logger.info("Transformation complete")
    return transformed


def enrich_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enrich data with additional information.

    Args:
        event: Input event
        context: Lambda context

    Returns:
        Enriched data
    """
    logger.info("Enriching data")

    data = event.get("data", {})

    # Example enrichment
    enriched = {
        "original": data,
        "metadata": {
            "source": event.get("source", "unknown"),
            "timestamp": datetime.utcnow().isoformat(),
            "enrichment_version": "1.0",
        },
        "enriched_at": datetime.utcnow().isoformat(),
    }

    logger.info("Enrichment complete")
    return enriched


def aggregate_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Aggregate parallel processing results.

    Args:
        event: Input event with processed results
        context: Lambda context

    Returns:
        Aggregated results
    """
    logger.info("Aggregating results")

    processed = event.get("processed", [])

    # Combine results from parallel branches
    aggregated = {
        "id": event.get("id"),
        "timestamp": datetime.utcnow().isoformat(),
        "transform_result": processed[0] if len(processed) > 0 else {},
        "enrich_result": processed[1] if len(processed) > 1 else {},
        "aggregated_at": datetime.utcnow().isoformat(),
    }

    # Calculate quality score (example logic)
    quality_score = 0.9  # Replace with actual quality check logic
    aggregated["quality_score"] = quality_score

    logger.info(f"Aggregation complete. Quality score: {quality_score}")
    return aggregated


def reject_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle rejected data.

    Args:
        event: Input event
        context: Lambda context

    Returns:
        Rejection details
    """
    logger.info("Handling data rejection")

    rejection = {
        "id": event.get("id"),
        "reason": f"Quality score {event.get('quality_score')} below threshold",
        "rejected_at": datetime.utcnow().isoformat(),
        "data": event.get("processed"),
    }

    # Store rejection details (implement actual storage logic)
    logger.info(f"Data rejected: {json.dumps(rejection)}")

    return rejection


def error_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle workflow errors.

    Args:
        event: Input event with error details
        context: Lambda context

    Returns:
        Error handling result
    """
    logger.error(f"Handling workflow error: {json.dumps(event)}")

    error = event.get("error", {})

    error_details = {
        "error_type": error.get("Error", "Unknown"),
        "error_message": error.get("Cause", "No details available"),
        "original_input": event,
        "handled_at": datetime.utcnow().isoformat(),
    }

    # Implement error notification logic here
    logger.error(f"Error details: {json.dumps(error_details)}")

    return error_details

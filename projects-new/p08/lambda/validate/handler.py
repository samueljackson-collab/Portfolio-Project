"""Lambda handler for validation step.
Validates S3 file content against JSON schema, routes invalid records to DLQ.

Environment Variables:
    METADATA_TABLE: DynamoDB table name for ETL metadata
    DLQ_URL: SQS Dead Letter Queue URL for validation failures
    SCHEMA_BUCKET: S3 bucket containing JSON schema definitions
    REGION: AWS region (default: us-east-1)

Usage:
    Invoked by Step Functions with ingest Lambda output payload.
"""
from __future__ import annotations
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError
import jsonschema
from jsonschema import validate, ValidationError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
metadata_table = dynamodb.Table(os.environ['METADATA_TABLE'])
dlq_url = os.environ['DLQ_URL']
schema_bucket = os.environ.get('SCHEMA_BUCKET', 'etl-schemas')

# Cache for JSON schemas (reduce S3 reads)
SCHEMA_CACHE: Dict[str, Dict] = {}


def load_schema(schema_name: str) -> Dict:
    """
    Load JSON Schema from S3 (with caching).

    Args:
        schema_name: Schema file name (e.g., 'customer_event.json')

    Returns:
        JSON Schema as dict
    """
    if schema_name in SCHEMA_CACHE:
        return SCHEMA_CACHE[schema_name]

    try:
        logger.info(f"Loading schema from S3: s3://{schema_bucket}/{schema_name}")
        response = s3_client.get_object(Bucket=schema_bucket, Key=schema_name)
        schema = json.loads(response['Body'].read().decode('utf-8'))
        SCHEMA_CACHE[schema_name] = schema
        return schema
    except ClientError as e:
        logger.error(f"Failed to load schema {schema_name}: {e}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Validate S3 file content against JSON schema.

    Args:
        event: Output from ingest Lambda (contains bucket, key, execution_id)
        context: Lambda context object

    Returns:
        Dict with validation results (valid: true/false, schema_version, error_details)

    Raises:
        ValidationError: If schema validation fails (caught and routed to DLQ)
    """
    execution_id = event['execution_id']
    event_timestamp = event['timestamp']  # Numeric timestamp from ingest Lambda (DynamoDB RANGE key)
    bucket = event['bucket']
    key = event['key']
    version_id = event.get('version_id')

    logger.info(f"Validating file: s3://{bucket}/{key} (execution_id: {execution_id})")

    try:
        # Determine schema based on file key pattern (e.g., customer_events/*.json uses customer_event.json)
        schema_name = infer_schema_name(key)
        schema = load_schema(schema_name)

        # Read S3 file content
        try:
            response = s3_client.get_object(
                Bucket=bucket,
                Key=key,
                VersionId=version_id if version_id else None
            )
            file_content = response['Body'].read().decode('utf-8')
        except ClientError as e:
            logger.error(f"Failed to read S3 object: {e}")
            raise

        # Parse JSON
        try:
            data = json.loads(file_content)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {e}"
            logger.error(error_msg)
            send_to_dlq(event, error_msg, "JSONDecodeError")
            update_metadata_status(execution_id, event_timestamp, 'validation_failed', error_msg)
            raise ValidationError(error_msg)

        # Validate against schema
        try:
            validate(instance=data, schema=schema)
            logger.info(f"Validation passed for {execution_id}")
        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation failed: {e.message} at path {list(e.path)}"
            logger.error(error_msg)
            send_to_dlq(event, error_msg, "SchemaValidationError")
            update_metadata_status(execution_id, event_timestamp, 'validation_failed', error_msg)
            raise ValidationError(error_msg)

        # Additional business rule validations
        validation_errors = []

        # Example: Check timestamp is not in future
        if 'timestamp' in data:
            try:
                event_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                if event_time > datetime.utcnow():
                    validation_errors.append(f"Timestamp in future: {data['timestamp']}")
            except ValueError:
                validation_errors.append(f"Invalid timestamp format: {data['timestamp']}")

        # Example: Check required business fields
        if data.get('event_type') not in ['create', 'update', 'delete']:
            validation_errors.append(f"Invalid event_type: {data.get('event_type')}")

        if validation_errors:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Business rule validation failed: {error_msg}")
            send_to_dlq(event, error_msg, "BusinessRuleViolation")
            update_metadata_status(execution_id, event_timestamp, 'validation_failed', error_msg)
            raise ValidationError(error_msg)

        # Update DynamoDB: validation succeeded
        update_metadata_status(execution_id, event_timestamp, 'validated', None)

        # Return payload for next state (transform)
        return {
            **event,  # Pass through all previous fields
            'valid': True,
            'schema_name': schema_name,
            'schema_version': schema.get('$id', 'unknown'),
            'record_count': 1,  # For batch processing, count records
            'validation_timestamp': datetime.utcnow().isoformat()
        }

    except ValidationError:
        # Validation errors already logged and sent to DLQ, re-raise for Step Functions catch
        raise
    except Exception as e:
        logger.error(f"Validation failed with unexpected error: {e}", exc_info=True)
        update_metadata_status(execution_id, event_timestamp, 'validation_failed', str(e))
        raise


def infer_schema_name(key: str) -> str:
    """
    Infer JSON Schema file name based on S3 key pattern.

    Args:
        key: S3 object key (e.g., 'customer_events/2024/12/03/event_001.json')

    Returns:
        Schema file name (e.g., 'customer_event_schema.json')
    """
    # Simple pattern matching (extend for multiple sources)
    if key.startswith('customer_events/'):
        return 'customer_event_schema.json'
    elif key.startswith('product_updates/'):
        return 'product_update_schema.json'
    else:
        # Default schema
        return 'default_schema.json'


def send_to_dlq(event: Dict[str, Any], error_message: str, error_type: str) -> None:
    """
    Send validation failure to DLQ for manual review.

    Args:
        event: Original event payload
        error_message: Validation error description
        error_type: Error classification (JSONDecodeError, SchemaValidationError, etc.)
    """
    try:
        dlq_message = {
            'execution_id': event['execution_id'],
            'bucket': event['bucket'],
            'key': event['key'],
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.utcnow().isoformat(),
            'original_event': event
        }

        sqs_client.send_message(
            QueueUrl=dlq_url,
            MessageBody=json.dumps(dlq_message),
            MessageAttributes={
                'ErrorType': {'StringValue': error_type, 'DataType': 'String'},
                'ExecutionId': {'StringValue': event['execution_id'], 'DataType': 'String'}
            }
        )
        logger.info(f"Sent to DLQ: {event['execution_id']} (error: {error_type})")
    except ClientError as e:
        logger.error(f"Failed to send message to DLQ: {e}")
        # Don't raise - DLQ failure shouldn't block error handling


def update_metadata_status(execution_id: str, event_timestamp: int, status: str, error_message: Optional[str]) -> None:
    """
    Update DynamoDB metadata table with validation status.

    Args:
        execution_id: Unique execution identifier
        event_timestamp: Numeric timestamp (DynamoDB RANGE key)
        status: New status (validated, validation_failed)
        error_message: Error description if failed
    """
    try:
        update_expression = 'SET #status = :status, validation_timestamp = :validation_timestamp'
        expression_values = {
            ':status': status,
            ':validation_timestamp': datetime.utcnow().isoformat()
        }

        if error_message:
            update_expression += ', error_message = :error'
            expression_values[':error'] = error_message

        metadata_table.update_item(
            Key={'execution_id': execution_id, 'timestamp': event_timestamp},
            UpdateExpression=update_expression,
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues=expression_values
        )
    except ClientError as e:
        logger.error(f"Failed to update DynamoDB: {e}")
        # Don't raise - metadata update failure shouldn't block processing

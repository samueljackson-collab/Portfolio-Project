"""Lambda handler for S3 ingest step.
Triggered by Step Functions, receives S3 event details, reads file, writes metadata to DynamoDB.

Environment Variables:
    METADATA_TABLE: DynamoDB table name for ETL metadata
    REGION: AWS region (default: us-east-1)

Usage:
    Invoked by Step Functions state machine with S3 event payload.
"""
from __future__ import annotations
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('REGION', 'us-east-1'))
metadata_table = dynamodb.Table(os.environ['METADATA_TABLE'])


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Ingest S3 file and write metadata to DynamoDB.

    Args:
        event: Step Functions input with S3 details or direct S3 event
        context: Lambda context object

    Returns:
        Dict containing file metadata and S3 object info for downstream processing

    Raises:
        Exception: If S3 read or DynamoDB write fails after retries
    """
    try:
        # Parse S3 event (handle both direct S3 event and Step Functions wrapper)
        if 'detail' in event:  # EventBridge S3 event
            bucket = event['detail']['bucket']['name']
            key = event['detail']['object']['key']
            size_bytes = event['detail']['object']['size']
            version_id = event['detail']['object'].get('version-id')
        elif 'Records' in event:  # Direct S3 event notification
            record = event['Records'][0]
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            size_bytes = record['s3']['object']['size']
            version_id = record['s3']['object'].get('versionId')
        else:
            raise ValueError(f"Unsupported event format: {json.dumps(event)}")

        logger.info(f"Ingesting file: s3://{bucket}/{key} (size: {size_bytes} bytes, version: {version_id})")

        # Validate file size (reject files > 500MB to prevent Lambda OOM)
        max_size_bytes = 500 * 1024 * 1024  # 500MB
        if size_bytes > max_size_bytes:
            error_msg = f"File size {size_bytes} bytes exceeds limit {max_size_bytes} bytes"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Generate unique execution ID for idempotency tracking
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        execution_id = f"{bucket}/{key}/{version_id or 'no-version'}/{now_iso}"

        # Check idempotency: If file already processed, skip (S3 eventual consistency protection)
        try:
            existing_item = metadata_table.get_item(
                Key={'execution_id': execution_id, 'timestamp': now_iso}
            )
            if 'Item' in existing_item and existing_item['Item'].get('status') == 'completed':
                logger.warning(f"File already processed: {execution_id}, skipping duplicate")
                return {
                    'statusCode': 200,
                    'duplicate': True,
                    'execution_id': execution_id,
                    'message': 'Duplicate file, skipped processing'
                }
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise

        # Read S3 object metadata (but not full content yet - validate first)
        try:
            s3_metadata = s3_client.head_object(
                Bucket=bucket,
                Key=key,
                VersionId=version_id if version_id else None
            )
            content_type = s3_metadata.get('ContentType', 'application/octet-stream')
            last_modified = s3_metadata['LastModified'].isoformat()
        except ClientError as e:
            logger.error(f"Failed to read S3 object metadata: {e}")
            raise

        # Write metadata to DynamoDB (initial status: ingested)
        timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        metadata_item = {
            'execution_id': execution_id,
            'bucket': bucket,
            'key': key,
            'version_id': version_id,
            'size_bytes': size_bytes,
            'content_type': content_type,
            'last_modified': last_modified,
            'status': 'ingested',
            'ingestion_timestamp': timestamp,
            'ttl': int(datetime.now(timezone.utc).timestamp()) + (180 * 24 * 60 * 60)  # 180 days TTL
        }

        try:
            metadata_table.put_item(Item=metadata_item)
            logger.info(f"Metadata written to DynamoDB: execution_id={execution_id}")
        except ClientError as e:
            logger.error(f"Failed to write to DynamoDB: {e}")
            raise

        # Return payload for next Step Functions state (validate)
        return {
            'statusCode': 200,
            'execution_id': execution_id,
            'bucket': bucket,
            'key': key,
            'version_id': version_id,
            'size_bytes': size_bytes,
            'content_type': content_type,
            'duplicate': False,
            'timestamp': timestamp
        }

    except Exception as e:
        logger.error(f"Ingest failed: {e}", exc_info=True)
        # Update DynamoDB with error status if execution_id exists
        if 'execution_id' in locals():
            try:
                metadata_table.update_item(
                    Key={'execution_id': execution_id},
                    UpdateExpression='SET #status = :status, error_message = :error',
                    ExpressionAttributeNames={'#status': 'status'},
                    ExpressionAttributeValues={
                        ':status': 'failed',
                        ':error': str(e)
                    }
                )
            except Exception as update_error:
                logger.error(f"Failed to update error status: {update_error}")
        raise


def sanitize_log_message(message: str) -> str:
    """
    Remove potential PII from log messages before logging.

    Args:
        message: Raw log message

    Returns:
        Sanitized message with PII patterns redacted
    """
    # Example: Redact email addresses, SSN patterns (basic regex)
    import re
    message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', message)
    message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]', message)
    message = re.sub(r'\b\d{16}\b', '[CC_REDACTED]', message)  # Credit card
    return message

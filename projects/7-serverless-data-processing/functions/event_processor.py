"""
Event Processing Lambda Handler.

Processes events from various sources (S3, SQS, EventBridge),
validates, transforms, and forwards to downstream systems.
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

# AWS clients
s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')
sns_client = boto3.client('sns')

# Environment variables
OUTPUT_BUCKET = os.getenv('OUTPUT_BUCKET')
DLQ_URL = os.getenv('DLQ_URL')
METRICS_TABLE = os.getenv('METRICS_TABLE')
NOTIFICATION_TOPIC = os.getenv('NOTIFICATION_TOPIC')


class EventValidator:
    """Validate incoming events."""

    @staticmethod
    def validate_structure(event: Dict) -> bool:
        """Validate event has required fields."""
        required_fields = ['event_type', 'timestamp', 'data']
        return all(field in event for field in required_fields)

    @staticmethod
    def validate_timestamp(timestamp: str) -> bool:
        """Validate timestamp format."""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_event_type(event_type: str) -> bool:
        """Validate event type is allowed."""
        allowed_types = [
            'user_action',
            'system_event',
            'metric_update',
            'error_event',
            'audit_log'
        ]
        return event_type in allowed_types


class EventTransformer:
    """Transform events into standardized format."""

    @staticmethod
    def transform(event: Dict) -> Dict:
        """Transform event to standard schema."""
        transformed = {
            'event_id': event.get('event_id', generate_event_id()),
            'event_type': event['event_type'],
            'timestamp': event['timestamp'],
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'data': event['data'],
            'metadata': {
                'source': event.get('source', 'unknown'),
                'version': event.get('version', '1.0'),
                'environment': os.getenv('ENVIRONMENT', 'production')
            }
        }

        # Add enrichment data
        if event['event_type'] == 'user_action':
            transformed['data']['enriched'] = True
            transformed['data']['processed_by'] = 'lambda-processor'

        return transformed

    @staticmethod
    def batch_transform(events: List[Dict]) -> List[Dict]:
        """Transform multiple events."""
        return [EventTransformer.transform(event) for event in events]


def generate_event_id() -> str:
    """Generate unique event ID."""
    import uuid
    return str(uuid.uuid4())


def send_to_dlq(event: Dict, error: str):
    """Send failed event to Dead Letter Queue."""
    try:
        message = {
            'original_event': event,
            'error': error,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'retry_count': event.get('retry_count', 0) + 1
        }

        sqs_client.send_message(
            QueueUrl=DLQ_URL,
            MessageBody=json.dumps(message)
        )

        logger.warning(f"Sent event to DLQ: {error}")

    except Exception as e:
        logger.error(f"Failed to send to DLQ: {e}")


def record_metric(metric_name: str, value: float, event_type: str):
    """Record processing metric to DynamoDB."""
    if not METRICS_TABLE:
        return

    try:
        table = dynamodb.Table(METRICS_TABLE)
        table.put_item(
            Item={
                'metric_id': f"{metric_name}#{datetime.now(timezone.utc).isoformat()}",
                'metric_name': metric_name,
                'value': value,
                'event_type': event_type,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'ttl': int(datetime.now(timezone.utc).timestamp()) + (7 * 24 * 3600)  # 7 days
            }
        )
    except Exception as e:
        logger.error(f"Failed to record metric: {e}")


def save_to_s3(data: Dict, prefix: str = 'processed'):
    """Save processed data to S3."""
    if not OUTPUT_BUCKET:
        logger.warning("OUTPUT_BUCKET not configured")
        return

    try:
        # Generate S3 key with date partitioning
        now = datetime.now(timezone.utc)
        key = f"{prefix}/year={now.year}/month={now.month:02d}/day={now.day:02d}/{generate_event_id()}.json"

        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType='application/json'
        )

        logger.info(f"Saved to S3: s3://{OUTPUT_BUCKET}/{key}")
        return key

    except ClientError as e:
        logger.error(f"Failed to save to S3: {e}")
        raise


def send_notification(subject: str, message: str):
    """Send SNS notification."""
    if not NOTIFICATION_TOPIC:
        return

    try:
        sns_client.publish(
            TopicArn=NOTIFICATION_TOPIC,
            Subject=subject,
            Message=message
        )
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")


def process_s3_event(record: Dict) -> Dict:
    """Process S3 event notification."""
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']

    logger.info(f"Processing S3 object: s3://{bucket}/{key}")

    # Download and process object
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        data = json.loads(response['Body'].read())

        # Validate and transform
        validator = EventValidator()
        if not validator.validate_structure(data):
            raise ValueError("Invalid event structure")

        transformed = EventTransformer.transform(data)
        return transformed

    except Exception as e:
        logger.error(f"Error processing S3 event: {e}")
        raise


def process_sqs_event(record: Dict) -> Dict:
    """Process SQS message."""
    message_body = record['body']

    try:
        data = json.loads(message_body)

        # Validate
        validator = EventValidator()
        if not validator.validate_structure(data):
            raise ValueError("Invalid event structure")

        if not validator.validate_timestamp(data['timestamp']):
            raise ValueError("Invalid timestamp")

        if not validator.validate_event_type(data['event_type']):
            raise ValueError(f"Invalid event type: {data['event_type']}")

        # Transform
        transformed = EventTransformer.transform(data)
        return transformed

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in SQS message: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing SQS event: {e}")
        raise


def lambda_handler(event: Dict, context: Any) -> Dict:
    """
    Main Lambda handler for event processing.

    Supports multiple event sources:
    - S3 event notifications
    - SQS messages
    - Direct invocations
    - EventBridge events
    """
    logger.info(f"Received event: {json.dumps(event)}")

    processed_count = 0
    failed_count = 0
    results = []

    try:
        # Determine event source
        if 'Records' in event:
            records = event['Records']

            for record in records:
                try:
                    # S3 Event
                    if 's3' in record:
                        processed = process_s3_event(record)
                        results.append(processed)
                        save_to_s3(processed)
                        processed_count += 1

                    # SQS Event
                    elif 'eventSource' in record and record['eventSource'] == 'aws:sqs':
                        processed = process_sqs_event(record)
                        results.append(processed)
                        save_to_s3(processed)
                        processed_count += 1

                except Exception as e:
                    logger.error(f"Failed to process record: {e}")
                    send_to_dlq(record, str(e))
                    failed_count += 1

        # Direct invocation
        else:
            try:
                validator = EventValidator()
                if not validator.validate_structure(event):
                    raise ValueError("Invalid event structure")

                transformed = EventTransformer.transform(event)
                save_to_s3(transformed)
                results.append(transformed)
                processed_count += 1

            except Exception as e:
                logger.error(f"Failed to process direct invocation: {e}")
                send_to_dlq(event, str(e))
                failed_count += 1

        # Record metrics
        record_metric('events_processed', processed_count, 'batch')
        record_metric('events_failed', failed_count, 'batch')

        # Send notification if there were failures
        if failed_count > 0:
            send_notification(
                'Event Processing Failures',
                f"Failed to process {failed_count} events. Check DLQ for details."
            )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed': processed_count,
                'failed': failed_count,
                'results': results[:10]  # Return first 10 results
            })
        }

    except Exception as e:
        logger.error(f"Handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'processed': processed_count,
                'failed': failed_count
            })
        }

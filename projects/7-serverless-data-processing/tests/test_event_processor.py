"""
Comprehensive tests for Event Processor Lambda.

Tests cover:
- Event validation
- Event transformation
- S3 event processing
- SQS event processing
- Error handling and DLQ
"""

import pytest
import json
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import sys

# Add functions directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'functions'))

from event_processor import (
    EventValidator,
    EventTransformer,
    lambda_handler,
    generate_event_id,
    process_sqs_event,
)


class TestEventValidator:
    """Test EventValidator class."""

    def test_validate_structure_valid(self):
        """Test validation of valid event structure."""
        event = {
            'event_type': 'user_action',
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'user_id': '123', 'action': 'click'}
        }
        assert EventValidator.validate_structure(event) is True

    def test_validate_structure_missing_event_type(self):
        """Test validation fails when event_type missing."""
        event = {
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'user_id': '123'}
        }
        assert EventValidator.validate_structure(event) is False

    def test_validate_structure_missing_timestamp(self):
        """Test validation fails when timestamp missing."""
        event = {
            'event_type': 'user_action',
            'data': {'user_id': '123'}
        }
        assert EventValidator.validate_structure(event) is False

    def test_validate_structure_missing_data(self):
        """Test validation fails when data missing."""
        event = {
            'event_type': 'user_action',
            'timestamp': '2024-01-15T10:30:00Z'
        }
        assert EventValidator.validate_structure(event) is False

    def test_validate_timestamp_valid_iso(self):
        """Test validation of valid ISO timestamp."""
        assert EventValidator.validate_timestamp('2024-01-15T10:30:00Z') is True
        assert EventValidator.validate_timestamp('2024-01-15T10:30:00+00:00') is True

    def test_validate_timestamp_invalid(self):
        """Test validation of invalid timestamp."""
        assert EventValidator.validate_timestamp('invalid-date') is False
        assert EventValidator.validate_timestamp('2024/01/15') is False
        assert EventValidator.validate_timestamp(None) is False

    def test_validate_event_type_valid(self):
        """Test validation of allowed event types."""
        allowed_types = ['user_action', 'system_event', 'metric_update', 'error_event', 'audit_log']
        for event_type in allowed_types:
            assert EventValidator.validate_event_type(event_type) is True

    def test_validate_event_type_invalid(self):
        """Test validation of invalid event type."""
        assert EventValidator.validate_event_type('unknown_type') is False
        assert EventValidator.validate_event_type('') is False


class TestEventTransformer:
    """Test EventTransformer class."""

    def test_transform_basic_event(self):
        """Test transformation of basic event."""
        event = {
            'event_type': 'user_action',
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'user_id': '123', 'action': 'click'}
        }

        result = EventTransformer.transform(event)

        assert result['event_type'] == 'user_action'
        assert result['timestamp'] == '2024-01-15T10:30:00Z'
        assert result['data']['user_id'] == '123'
        assert 'event_id' in result
        assert 'processed_at' in result
        assert 'metadata' in result

    def test_transform_with_existing_event_id(self):
        """Test transformation preserves existing event_id."""
        event = {
            'event_id': 'existing-id-123',
            'event_type': 'user_action',
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'user_id': '123'}
        }

        result = EventTransformer.transform(event)
        assert result['event_id'] == 'existing-id-123'

    def test_transform_user_action_enrichment(self):
        """Test that user_action events get enriched."""
        event = {
            'event_type': 'user_action',
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'user_id': '123'}
        }

        result = EventTransformer.transform(event)
        assert result['data']['enriched'] is True
        assert result['data']['processed_by'] == 'lambda-processor'

    def test_transform_non_user_action_no_enrichment(self):
        """Test that non-user_action events don't get enriched."""
        event = {
            'event_type': 'system_event',
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'system': 'test'}
        }

        result = EventTransformer.transform(event)
        assert 'enriched' not in result['data']

    def test_batch_transform(self):
        """Test batch transformation of multiple events."""
        events = [
            {'event_type': 'user_action', 'timestamp': '2024-01-15T10:30:00Z', 'data': {'id': '1'}},
            {'event_type': 'system_event', 'timestamp': '2024-01-15T10:31:00Z', 'data': {'id': '2'}},
        ]

        results = EventTransformer.batch_transform(events)
        assert len(results) == 2
        assert results[0]['data']['id'] == '1'
        assert results[1]['data']['id'] == '2'


class TestGenerateEventId:
    """Test event ID generation."""

    def test_generate_event_id_format(self):
        """Test generated ID is valid UUID format."""
        event_id = generate_event_id()
        assert len(event_id) == 36  # UUID format: 8-4-4-4-12
        assert event_id.count('-') == 4

    def test_generate_event_id_unique(self):
        """Test generated IDs are unique."""
        ids = [generate_event_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestProcessSQSEvent:
    """Test SQS event processing."""

    def test_process_sqs_event_valid(self):
        """Test processing valid SQS event."""
        record = {
            'body': json.dumps({
                'event_type': 'user_action',
                'timestamp': '2024-01-15T10:30:00Z',
                'data': {'user_id': '123'}
            })
        }

        result = process_sqs_event(record)
        assert result['event_type'] == 'user_action'
        assert 'processed_at' in result

    def test_process_sqs_event_invalid_json(self):
        """Test processing invalid JSON raises error."""
        record = {'body': 'not valid json'}

        with pytest.raises(json.JSONDecodeError):
            process_sqs_event(record)

    def test_process_sqs_event_invalid_structure(self):
        """Test processing event with invalid structure raises error."""
        record = {
            'body': json.dumps({'invalid': 'structure'})
        }

        with pytest.raises(ValueError, match="Invalid event structure"):
            process_sqs_event(record)

    def test_process_sqs_event_invalid_timestamp(self):
        """Test processing event with invalid timestamp raises error."""
        record = {
            'body': json.dumps({
                'event_type': 'user_action',
                'timestamp': 'invalid',
                'data': {}
            })
        }

        with pytest.raises(ValueError, match="Invalid timestamp"):
            process_sqs_event(record)

    def test_process_sqs_event_invalid_event_type(self):
        """Test processing event with invalid event_type raises error."""
        record = {
            'body': json.dumps({
                'event_type': 'unknown_type',
                'timestamp': '2024-01-15T10:30:00Z',
                'data': {}
            })
        }

        with pytest.raises(ValueError, match="Invalid event type"):
            process_sqs_event(record)


class TestLambdaHandler:
    """Test main Lambda handler."""

    @patch('event_processor.save_to_s3')
    @patch('event_processor.record_metric')
    def test_handler_direct_invocation(self, mock_metric, mock_s3):
        """Test direct invocation of Lambda handler."""
        event = {
            'event_type': 'user_action',
            'timestamp': '2024-01-15T10:30:00Z',
            'data': {'user_id': '123'}
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['processed'] == 1
        assert body['failed'] == 0

    @patch('event_processor.save_to_s3')
    @patch('event_processor.record_metric')
    @patch('event_processor.send_to_dlq')
    def test_handler_sqs_records(self, mock_dlq, mock_metric, mock_s3):
        """Test processing SQS records."""
        event = {
            'Records': [
                {
                    'eventSource': 'aws:sqs',
                    'body': json.dumps({
                        'event_type': 'user_action',
                        'timestamp': '2024-01-15T10:30:00Z',
                        'data': {'user_id': '123'}
                    })
                }
            ]
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['processed'] == 1

    @patch('event_processor.save_to_s3')
    @patch('event_processor.record_metric')
    @patch('event_processor.send_to_dlq')
    @patch('event_processor.send_notification')
    def test_handler_invalid_event_sends_to_dlq(self, mock_notify, mock_dlq, mock_metric, mock_s3):
        """Test invalid event is sent to DLQ."""
        event = {
            'invalid': 'structure'
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['failed'] == 1
        mock_dlq.assert_called_once()

    @patch('event_processor.save_to_s3')
    @patch('event_processor.record_metric')
    def test_handler_multiple_records(self, mock_metric, mock_s3):
        """Test processing multiple records."""
        event = {
            'Records': [
                {
                    'eventSource': 'aws:sqs',
                    'body': json.dumps({
                        'event_type': 'user_action',
                        'timestamp': '2024-01-15T10:30:00Z',
                        'data': {'id': '1'}
                    })
                },
                {
                    'eventSource': 'aws:sqs',
                    'body': json.dumps({
                        'event_type': 'system_event',
                        'timestamp': '2024-01-15T10:31:00Z',
                        'data': {'id': '2'}
                    })
                }
            ]
        }

        response = lambda_handler(event, None)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['processed'] == 2
        assert body['failed'] == 0


class TestIntegration:
    """Integration tests (require LocalStack)."""

    @pytest.mark.integration
    @patch.dict(os.environ, {
        'AWS_ENDPOINT_URL': 'http://localhost:4566',
        'AWS_DEFAULT_REGION': 'us-east-1',
        'OUTPUT_BUCKET': 'processed-events'
    })
    def test_full_processing_flow(self):
        """Test complete event processing flow."""
        # This test requires LocalStack to be running
        event = {
            'event_type': 'user_action',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {'user_id': 'test-123', 'action': 'test'}
        }

        response = lambda_handler(event, None)
        assert response['statusCode'] == 200

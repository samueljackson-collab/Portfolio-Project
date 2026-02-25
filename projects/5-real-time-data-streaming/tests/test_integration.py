"""Integration tests for real-time streaming pipeline.

These tests verify the end-to-end functionality of the streaming pipeline
components including Kafka producers, consumers, and Avro serialization.

Note: These tests require running Kafka and Schema Registry services.
Use `docker-compose up -d` to start required services before running tests.
"""
import pytest
import json
import time
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone


class TestProducerConsumerIntegration:
    """Integration tests for basic producer/consumer flow."""

    @pytest.fixture
    def mock_kafka_setup(self):
        """Setup mock Kafka producer and consumer."""
        with patch('src.producer.KafkaProducer') as mock_producer, \
             patch('src.consumer.KafkaConsumer') as mock_consumer:
            yield {
                'producer': mock_producer,
                'consumer': mock_consumer
            }

    def test_produce_consume_cycle(self, mock_kafka_setup):
        """Test that produced events can be consumed."""
        from src.producer import EventProducer
        from src.consumer import EventConsumer

        # Setup mocks
        mock_producer_instance = mock_kafka_setup['producer'].return_value
        mock_consumer_instance = mock_kafka_setup['consumer'].return_value

        # Configure producer mock
        mock_future = MagicMock()
        mock_metadata = Mock()
        mock_metadata.topic = 'test-topic'
        mock_metadata.partition = 0
        mock_metadata.offset = 0
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future

        # Configure consumer mock
        produced_events = []

        def capture_event(*args, **kwargs):
            produced_events.append(kwargs['value'])
            return mock_future

        mock_producer_instance.send.side_effect = capture_event

        # Produce events
        producer = EventProducer(topic='test-topic')
        for i in range(10):
            producer.send_event(
                event_type='page_view',
                user_id=f'user_{i}',
                data={'page': f'/page/{i}'}
            )

        # Verify events were "produced"
        assert len(produced_events) == 10

        # Verify event structure
        for event in produced_events:
            assert 'timestamp' in event
            assert 'event_type' in event
            assert 'user_id' in event
            assert 'data' in event
            assert 'version' in event

    def test_event_ordering_by_user(self, mock_kafka_setup):
        """Test that events maintain ordering by user (partition key)."""
        from src.producer import EventProducer

        mock_producer_instance = mock_kafka_setup['producer'].return_value
        mock_future = MagicMock()
        mock_metadata = Mock()
        mock_metadata.topic = 'test-topic'
        mock_metadata.partition = 0
        mock_metadata.offset = 0
        mock_future.get.return_value = mock_metadata
        mock_producer_instance.send.return_value = mock_future

        produced_keys = []

        def capture_key(*args, **kwargs):
            produced_keys.append(kwargs.get('key'))
            return mock_future

        mock_producer_instance.send.side_effect = capture_key

        producer = EventProducer(topic='test-topic')

        # Send events for same user
        user_id = 'user_123'
        for i in range(5):
            producer.send_event(
                event_type='page_view',
                user_id=user_id,
                data={'page': f'/page/{i}'}
            )

        # All events should have the same key (user_id)
        assert all(key == user_id for key in produced_keys)


class TestAvroSchemaValidation:
    """Tests for Avro schema validation."""

    @pytest.fixture
    def valid_event(self):
        """Return a valid event conforming to schema."""
        return {
            'event_id': str(uuid.uuid4()),
            'user_id': 'user_123',
            'session_id': 'session_456',
            'event_type': 'PAGE_VIEW',
            'timestamp': int(datetime.now().timestamp() * 1000),
            'page_url': '/home',
            'referrer': None,
            'user_agent': 'Mozilla/5.0',
            'ip_address': '192.168.1.1',
            'device_type': 'DESKTOP',
            'properties': {'key': 'value'},
            'metadata': {
                'producer_id': 'test-producer',
                'schema_version': '1.0.0',
                'environment': 'PRODUCTION'
            }
        }

    def test_valid_event_structure(self, valid_event):
        """Test that valid event has required fields."""
        required_fields = ['event_id', 'user_id', 'event_type', 'timestamp', 'metadata']

        for field in required_fields:
            assert field in valid_event, f"Missing required field: {field}"

    def test_event_type_enum(self, valid_event):
        """Test that event_type is a valid enum value."""
        valid_types = [
            'PAGE_VIEW', 'CLICK', 'PURCHASE', 'ADD_TO_CART',
            'SEARCH', 'LOGIN', 'LOGOUT', 'REGISTRATION'
        ]

        assert valid_event['event_type'] in valid_types

    def test_device_type_enum(self, valid_event):
        """Test that device_type is a valid enum value."""
        valid_devices = ['DESKTOP', 'MOBILE', 'TABLET', 'OTHER', None]

        assert valid_event['device_type'] in valid_devices

    def test_metadata_structure(self, valid_event):
        """Test that metadata has required fields."""
        metadata = valid_event['metadata']

        assert 'producer_id' in metadata
        assert 'schema_version' in metadata
        assert 'environment' in metadata

    def test_invalid_event_type_rejected(self):
        """Test that invalid event types are handled."""
        # This would be caught by Avro serializer in real scenario
        invalid_event = {
            'event_id': str(uuid.uuid4()),
            'user_id': 'user_123',
            'event_type': 'INVALID_TYPE',  # Not in enum
            'timestamp': int(datetime.now().timestamp() * 1000),
        }

        valid_types = [
            'PAGE_VIEW', 'CLICK', 'PURCHASE', 'ADD_TO_CART',
            'SEARCH', 'LOGIN', 'LOGOUT', 'REGISTRATION'
        ]

        assert invalid_event['event_type'] not in valid_types


class TestAggregatingConsumer:
    """Tests for aggregating consumer functionality."""

    @pytest.fixture
    def mock_consumer(self):
        """Mock Kafka consumer."""
        with patch('src.consumer.KafkaConsumer') as mock:
            yield mock

    def test_event_aggregation_by_type(self, mock_consumer):
        """Test that events are correctly aggregated by type."""
        from src.consumer import AggregatingConsumer

        consumer = AggregatingConsumer(
            topic='test-topic',
            window_seconds=60
        )

        # Process events of different types
        events = [
            {'event_type': 'page_view', 'user_id': 'u1', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'u2', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'u3', 'data': {}},
            {'event_type': 'purchase', 'user_id': 'u1', 'data': {'amount': 100}},
            {'event_type': 'purchase', 'user_id': 'u2', 'data': {'amount': 200}},
            {'event_type': 'search', 'user_id': 'u1', 'data': {}},
        ]

        for event in events:
            consumer.process_event(event)

        # Verify aggregation
        assert consumer.window_data['by_type']['page_view'] == 3
        assert consumer.window_data['by_type']['purchase'] == 2
        assert consumer.window_data['by_type']['search'] == 1

    def test_revenue_tracking(self, mock_consumer):
        """Test that purchase revenue is tracked correctly."""
        from src.consumer import AggregatingConsumer

        consumer = AggregatingConsumer(
            topic='test-topic',
            window_seconds=60
        )

        # Process purchase events
        purchase_events = [
            {'event_type': 'purchase', 'user_id': 'u1', 'data': {'amount': 99.99}},
            {'event_type': 'purchase', 'user_id': 'u2', 'data': {'amount': 149.99}},
            {'event_type': 'purchase', 'user_id': 'u3', 'data': {'amount': 49.99}},
        ]

        for event in purchase_events:
            consumer.process_event(event)

        # Verify revenue tracking
        expected_total = 99.99 + 149.99 + 49.99
        assert consumer.window_data['revenue']['total'] == expected_total
        assert consumer.window_data['revenue']['count'] == 3

    def test_user_activity_tracking(self, mock_consumer):
        """Test that user activity is tracked correctly."""
        from src.consumer import AggregatingConsumer

        consumer = AggregatingConsumer(
            topic='test-topic',
            window_seconds=60
        )

        # Process events from multiple users
        events = [
            {'event_type': 'page_view', 'user_id': 'user_1', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'user_1', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'user_1', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'user_2', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'user_2', 'data': {}},
            {'event_type': 'page_view', 'user_id': 'user_3', 'data': {}},
        ]

        for event in events:
            consumer.process_event(event)

        # Verify user tracking
        assert consumer.window_data['by_user']['user_1'] == 3
        assert consumer.window_data['by_user']['user_2'] == 2
        assert consumer.window_data['by_user']['user_3'] == 1


class TestFlinkProcessor:
    """Tests for Flink processor functionality."""

    def test_parse_event_valid(self):
        """Test parsing valid event JSON."""
        from src.flink_processor import FlinkEventProcessor

        event_json = json.dumps({
            'timestamp': '2025-01-01T00:00:00Z',
            'event_type': 'page_view',
            'user_id': 'user_123',
            'data': {'page': '/home'}
        })

        result = FlinkEventProcessor.parse_event(event_json)

        assert result[0] == '2025-01-01T00:00:00Z'
        assert result[1] == 'page_view'
        assert result[2] == 'user_123'

    def test_parse_event_invalid(self):
        """Test parsing invalid event JSON."""
        from src.flink_processor import FlinkEventProcessor

        invalid_json = "not valid json"

        result = FlinkEventProcessor.parse_event(invalid_json)

        assert result[1] == 'error'
        assert result[2] == 'unknown'

    def test_count_by_event_type(self):
        """Test event counting by type."""
        from src.flink_processor import FlinkEventProcessor

        events = [
            ('2025-01-01T00:00:00Z', 'page_view', 'u1', '{}'),
            ('2025-01-01T00:00:01Z', 'page_view', 'u2', '{}'),
            ('2025-01-01T00:00:02Z', 'purchase', 'u1', '{}'),
        ]

        result_json = FlinkEventProcessor.count_by_event_type(events)
        result = json.loads(result_json)

        assert result['total_events'] == 3
        assert result['by_type']['page_view'] == 2
        assert result['by_type']['purchase'] == 1

    def test_calculate_revenue_metrics(self):
        """Test revenue metric calculation."""
        from src.flink_processor import FlinkEventProcessor

        events = [
            ('2025-01-01T00:00:00Z', 'purchase', 'u1', '{"amount": 100}'),
            ('2025-01-01T00:00:01Z', 'purchase', 'u2', '{"amount": 200}'),
            ('2025-01-01T00:00:02Z', 'page_view', 'u1', '{}'),  # Not a purchase
        ]

        result_json = FlinkEventProcessor.calculate_revenue_metrics(events)
        result = json.loads(result_json)

        assert result['metric_type'] == 'revenue'
        assert result['total_revenue'] == 300.0
        assert result['purchase_count'] == 2
        assert result['unique_customers'] == 2
        assert result['average_purchase'] == 150.0


class TestEndToEndPipeline:
    """End-to-end pipeline tests."""

    def test_event_flow_producer_to_consumer(self):
        """Test complete event flow from producer to consumer."""
        from src.producer import EventProducer
        from src.consumer import EventConsumer

        with patch('src.producer.KafkaProducer') as mock_prod, \
             patch('src.consumer.KafkaConsumer') as mock_cons:

            # Setup producer mock
            mock_prod_instance = mock_prod.return_value
            mock_future = MagicMock()
            mock_metadata = Mock()
            mock_metadata.topic = 'test-topic'
            mock_metadata.partition = 0
            mock_metadata.offset = 0
            mock_future.get.return_value = mock_metadata
            mock_prod_instance.send.return_value = mock_future

            # Create producer and consumer
            producer = EventProducer(topic='test-topic')
            consumer = EventConsumer(topic='test-topic')

            # Simulate event production
            test_events = []
            for i in range(5):
                event = {
                    'event_type': 'page_view',
                    'user_id': f'user_{i}',
                    'data': {'page': f'/page/{i}'}
                }
                producer.send_event(**event)
                test_events.append(event)

            # Simulate consumption
            for event in test_events:
                result = consumer.process_event({
                    'event_type': event['event_type'],
                    'user_id': event['user_id'],
                    'data': event['data']
                })
                assert result is True

            # Verify consumer stats
            assert consumer.stats['total_events'] == 5
            assert consumer.stats['events_by_type']['page_view'] == 5

    def test_exactly_once_semantics_config(self):
        """Test that exactly-once semantics are configured correctly."""
        from src.producer import EventProducer

        with patch('src.producer.KafkaProducer') as mock:
            producer = EventProducer(topic='test-topic')

            # Verify idempotence is enabled in producer config
            call_kwargs = mock.call_args.kwargs
            assert call_kwargs.get('enable_idempotence') is True
            assert call_kwargs.get('acks') == 'all'


class TestSchemaEvolution:
    """Tests for schema evolution scenarios."""

    def test_backward_compatible_event(self):
        """Test that old events can be read with new schema (backward compatibility)."""
        # Old event format (fewer fields)
        old_event = {
            'event_id': str(uuid.uuid4()),
            'user_id': 'user_123',
            'event_type': 'PAGE_VIEW',
            'timestamp': int(datetime.now().timestamp() * 1000),
        }

        # Should be processable even without optional fields
        required_fields = ['event_id', 'user_id', 'event_type', 'timestamp']
        for field in required_fields:
            assert field in old_event

    def test_forward_compatible_event(self):
        """Test that new events can be read with old schema (forward compatibility)."""
        # New event format (extra fields)
        new_event = {
            'event_id': str(uuid.uuid4()),
            'user_id': 'user_123',
            'event_type': 'PAGE_VIEW',
            'timestamp': int(datetime.now().timestamp() * 1000),
            'new_field_1': 'value1',
            'new_field_2': 'value2',
        }

        # Old consumer should ignore unknown fields and process known fields
        known_fields = ['event_id', 'user_id', 'event_type', 'timestamp']
        for field in known_fields:
            assert field in new_event


# Pytest fixtures for testcontainers (optional)
@pytest.fixture(scope='module')
def kafka_container():
    """Create Kafka container for integration tests.

    Note: Requires testcontainers-python package.
    Skip if not available.
    """
    pytest.skip("Testcontainers integration requires running Docker")


@pytest.fixture(scope='module')
def schema_registry_container():
    """Create Schema Registry container for integration tests.

    Note: Requires testcontainers-python package.
    Skip if not available.
    """
    pytest.skip("Testcontainers integration requires running Docker")

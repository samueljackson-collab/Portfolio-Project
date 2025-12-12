"""Tests for Kafka producer."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.producer import EventProducer


@pytest.fixture
def mock_kafka_producer():
    """Mock Kafka producer."""
    with patch('src.producer.KafkaProducer') as mock:
        yield mock


def test_producer_initialization(mock_kafka_producer):
    """Test producer initializes correctly."""
    producer = EventProducer(
        bootstrap_servers=['localhost:9092'],
        topic='test-topic'
    )

    assert producer.topic == 'test-topic'
    assert producer.bootstrap_servers == ['localhost:9092']
    mock_kafka_producer.assert_called_once()


def test_send_event_success(mock_kafka_producer):
    """Test successful event sending."""
    # Setup
    mock_instance = mock_kafka_producer.return_value
    mock_future = MagicMock()
    mock_metadata = Mock()
    mock_metadata.topic = 'test-topic'
    mock_metadata.partition = 0
    mock_metadata.offset = 42
    mock_future.get.return_value = mock_metadata
    mock_instance.send.return_value = mock_future

    producer = EventProducer(topic='test-topic')

    # Execute
    result = producer.send_event(
        event_type='page_view',
        user_id='user_123',
        data={'page': '/home'}
    )

    # Assert
    assert result is True
    mock_instance.send.assert_called_once()


def test_send_event_failure(mock_kafka_producer):
    """Test event sending failure handling."""
    # Setup
    mock_instance = mock_kafka_producer.return_value
    mock_future = MagicMock()
    mock_future.get.side_effect = Exception("Kafka error")
    mock_instance.send.return_value = mock_future

    producer = EventProducer(topic='test-topic')

    # Execute
    result = producer.send_event(
        event_type='page_view',
        user_id='user_123',
        data={'page': '/home'}
    )

    # Assert
    assert result is False


def test_simulate_user_events(mock_kafka_producer):
    """Test user event simulation."""
    # Setup
    mock_instance = mock_kafka_producer.return_value
    mock_future = MagicMock()
    mock_metadata = Mock()
    mock_metadata.topic = 'test-topic'
    mock_metadata.partition = 0
    mock_metadata.offset = 42
    mock_future.get.return_value = mock_metadata
    mock_instance.send.return_value = mock_future

    producer = EventProducer(topic='test-topic')

    # Execute
    producer.simulate_user_events(count=10, delay=0.01)

    # Assert - should have sent 10 events
    assert mock_instance.send.call_count == 10


def test_context_manager(mock_kafka_producer):
    """Test producer works as context manager."""
    mock_instance = mock_kafka_producer.return_value

    with EventProducer(topic='test-topic') as producer:
        assert producer is not None

    # Verify close was called
    mock_instance.flush.assert_called()
    mock_instance.close.assert_called()


def test_event_structure(mock_kafka_producer):
    """Test that events have correct structure."""
    mock_instance = mock_kafka_producer.return_value
    mock_future = MagicMock()
    mock_metadata = Mock()
    mock_future.get.return_value = mock_metadata
    mock_instance.send.return_value = mock_future

    producer = EventProducer(topic='test-topic')

    producer.send_event(
        event_type='purchase',
        user_id='user_456',
        data={'product': 'laptop', 'price': 999.99}
    )

    # Get the call arguments
    call_args = mock_instance.send.call_args

    # Verify the event structure
    event = call_args.kwargs['value']
    assert 'timestamp' in event
    assert event['event_type'] == 'purchase'
    assert event['user_id'] == 'user_456'
    assert event['data']['product'] == 'laptop'
    assert event['version'] == '1.0'

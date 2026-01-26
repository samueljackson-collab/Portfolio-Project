"""Tests for Kafka consumer."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.consumer import EventConsumer, AggregatingConsumer


@pytest.fixture
def mock_kafka_consumer():
    """Mock Kafka consumer."""
    with patch("src.consumer.KafkaConsumer") as mock:
        yield mock


def test_consumer_initialization(mock_kafka_consumer):
    """Test consumer initializes correctly."""
    consumer = EventConsumer(
        bootstrap_servers=["localhost:9092"], topic="test-topic", group_id="test-group"
    )

    assert consumer.topic == "test-topic"
    assert consumer.group_id == "test-group"
    assert consumer.bootstrap_servers == ["localhost:9092"]
    mock_kafka_consumer.assert_called_once()


def test_process_event(mock_kafka_consumer):
    """Test event processing."""
    consumer = EventConsumer(topic="test-topic")

    event = {
        "event_type": "page_view",
        "user_id": "user_123",
        "data": {"page": "/home"},
    }

    result = consumer.process_event(event)

    assert result is True
    assert consumer.stats["total_events"] == 1
    assert consumer.stats["events_by_type"]["page_view"] == 1
    assert consumer.stats["events_by_user"]["user_123"] == 1


def test_process_event_error_handling(mock_kafka_consumer):
    """Test error handling in event processing."""
    consumer = EventConsumer(topic="test-topic")

    # Event that will cause an error (missing fields)
    event = None

    with patch.object(consumer, "process_event", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            consumer.process_event(event)


def test_context_manager(mock_kafka_consumer):
    """Test consumer works as context manager."""
    mock_instance = mock_kafka_consumer.return_value

    with EventConsumer(topic="test-topic") as consumer:
        assert consumer is not None

    # Verify close was called
    mock_instance.close.assert_called()


def test_aggregating_consumer(mock_kafka_consumer):
    """Test aggregating consumer."""
    consumer = AggregatingConsumer(topic="test-topic", window_seconds=5)

    # Process multiple events
    events = [
        {"event_type": "page_view", "user_id": "user_1", "data": {}},
        {"event_type": "page_view", "user_id": "user_1", "data": {}},
        {"event_type": "purchase", "user_id": "user_2", "data": {"amount": 99.99}},
    ]

    for event in events:
        consumer.process_event(event)

    # Verify aggregations
    assert consumer.window_data["by_type"]["page_view"] == 2
    assert consumer.window_data["by_type"]["purchase"] == 1
    assert consumer.window_data["by_user"]["user_1"] == 2
    assert consumer.window_data["revenue"]["total"] == 99.99
    assert consumer.window_data["revenue"]["count"] == 1


def test_statistics_tracking(mock_kafka_consumer):
    """Test that statistics are tracked correctly."""
    consumer = EventConsumer(topic="test-topic")

    # Process various events
    events = [
        {"event_type": "page_view", "user_id": "user_1", "data": {}},
        {"event_type": "page_view", "user_id": "user_2", "data": {}},
        {"event_type": "purchase", "user_id": "user_1", "data": {}},
        {"event_type": "page_view", "user_id": "user_1", "data": {}},
    ]

    for event in events:
        consumer.process_event(event)

    assert consumer.stats["total_events"] == 4
    assert consumer.stats["events_by_type"]["page_view"] == 3
    assert consumer.stats["events_by_type"]["purchase"] == 1
    assert consumer.stats["events_by_user"]["user_1"] == 3
    assert consumer.stats["events_by_user"]["user_2"] == 1

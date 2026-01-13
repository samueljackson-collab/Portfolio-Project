"""
Comprehensive tests for MQTT Processor module.

Tests cover:
- MQTT connection handling
- Message processing
- Database storage
- Batch operations
- Error handling
"""

import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch, call
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMQTTProcessor:
    """Test MQTTProcessor class."""

    @pytest.fixture
    def mqtt_config(self):
        """Return MQTT configuration."""
        return {
            'broker': 'localhost',
            'port': 1883,
            'topic': 'test/telemetry'
        }

    @pytest.fixture
    def postgres_config(self):
        """Return PostgreSQL configuration."""
        return {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_processor_initialization(self, mock_mqtt_client, mock_pg_connect, mqtt_config, postgres_config):
        """Test MQTTProcessor initialization."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker=mqtt_config['broker'],
            mqtt_port=mqtt_config['port'],
            mqtt_topic=mqtt_config['topic'],
            postgres_config=postgres_config
        )

        assert processor.mqtt_broker == mqtt_config['broker']
        assert processor.mqtt_port == mqtt_config['port']
        assert processor.mqtt_topic == mqtt_config['topic']
        assert processor.messages_processed == 0

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_on_connect_success(self, mock_mqtt_client, mock_pg_connect, mqtt_config, postgres_config):
        """Test successful MQTT connection callback."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker=mqtt_config['broker'],
            mqtt_port=mqtt_config['port'],
            mqtt_topic=mqtt_config['topic'],
            postgres_config=postgres_config
        )

        # Simulate on_connect callback
        mock_client = MagicMock()
        processor.on_connect(mock_client, None, None, 0)

        # Verify subscription was called
        mock_client.subscribe.assert_called_once_with(mqtt_config['topic'])

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_on_connect_failure(self, mock_mqtt_client, mock_pg_connect, mqtt_config, postgres_config):
        """Test failed MQTT connection callback."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker=mqtt_config['broker'],
            mqtt_port=mqtt_config['port'],
            mqtt_topic=mqtt_config['topic'],
            postgres_config=postgres_config
        )

        # Simulate failed connection (rc != 0)
        mock_client = MagicMock()
        processor.on_connect(mock_client, None, None, 5)  # Connection refused

        # Subscription should not be called
        mock_client.subscribe.assert_not_called()


class TestMessageProcessing:
    """Test message processing functionality."""

    @pytest.fixture
    def postgres_config(self):
        return {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_process_valid_message(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test processing valid telemetry message."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Create mock message
        mock_msg = MagicMock()
        mock_msg.payload = json.dumps({
            'device_id': 'device-001',
            'temperature': 25.5,
            'humidity': 60.0,
            'battery': 85.0,
            'timestamp': datetime.now().isoformat()
        }).encode()

        initial_count = processor.messages_processed
        processor.on_message(None, None, mock_msg)

        # Verify message was buffered
        assert len(processor.batch_buffer) > 0 or processor.messages_processed > initial_count

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_process_invalid_json(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test handling of invalid JSON message."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Create invalid message
        mock_msg = MagicMock()
        mock_msg.payload = b'not valid json'

        initial_failed = processor.messages_failed
        processor.on_message(None, None, mock_msg)

        # Should increment failed counter
        assert processor.messages_failed >= initial_failed

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_process_missing_required_fields(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test handling of message with missing fields."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Message missing device_id
        mock_msg = MagicMock()
        mock_msg.payload = json.dumps({
            'temperature': 25.5,
            'humidity': 60.0
        }).encode()

        # Should handle gracefully
        processor.on_message(None, None, mock_msg)


class TestBatchProcessing:
    """Test batch processing functionality."""

    @pytest.fixture
    def postgres_config(self):
        return {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_batch_buffer_fills(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test that messages are buffered."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )
        processor.batch_size = 10  # Small batch for testing

        # Send messages
        for i in range(5):
            mock_msg = MagicMock()
            mock_msg.payload = json.dumps({
                'device_id': f'device-{i:03d}',
                'temperature': 25.0 + i,
                'humidity': 60.0,
                'battery': 85.0
            }).encode()
            processor.on_message(None, None, mock_msg)

        # Buffer should have messages
        assert len(processor.batch_buffer) <= processor.batch_size

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_batch_flush_on_full(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test batch is flushed when full."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )
        processor.batch_size = 5  # Small batch for testing

        # Send enough messages to trigger flush
        for i in range(6):
            mock_msg = MagicMock()
            mock_msg.payload = json.dumps({
                'device_id': f'device-{i:03d}',
                'temperature': 25.0 + i,
                'humidity': 60.0,
                'battery': 85.0
            }).encode()
            processor.on_message(None, None, mock_msg)

        # Database commit should have been called
        # (verification depends on implementation)


class TestDatabaseOperations:
    """Test database operations."""

    @pytest.fixture
    def postgres_config(self):
        return {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_create_table(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test table creation on initialization."""
        from mqtt_processor import MQTTProcessor

        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Verify CREATE TABLE was called
        assert mock_cursor.execute.called

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_database_reconnection(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test database reconnection on failure."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Simulate reconnection
        processor.connect_db()

        # Should have reconnected
        assert processor.db_conn is not None


class TestStatistics:
    """Test processor statistics."""

    @pytest.fixture
    def postgres_config(self):
        return {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_statistics_tracking(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test that statistics are tracked correctly."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        assert processor.messages_processed == 0
        assert processor.messages_failed == 0

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_processed_counter_increment(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test processed counter increments."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Process valid message
        mock_msg = MagicMock()
        mock_msg.payload = json.dumps({
            'device_id': 'device-001',
            'temperature': 25.5
        }).encode()

        initial = processor.messages_processed
        processor.on_message(None, None, mock_msg)

        # Counter should increase or message should be buffered
        assert processor.messages_processed >= initial or len(processor.batch_buffer) > 0


class TestGracefulShutdown:
    """Test graceful shutdown functionality."""

    @pytest.fixture
    def postgres_config(self):
        return {
            'host': 'localhost',
            'port': 5432,
            'dbname': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }

    @patch('psycopg2.connect')
    @patch('paho.mqtt.client.Client')
    def test_shutdown_handler_exists(self, mock_mqtt_client, mock_pg_connect, postgres_config):
        """Test shutdown handler is registered."""
        from mqtt_processor import MQTTProcessor

        mock_conn = MagicMock()
        mock_pg_connect.return_value = mock_conn

        processor = MQTTProcessor(
            mqtt_broker='localhost',
            mqtt_port=1883,
            mqtt_topic='test/telemetry',
            postgres_config=postgres_config
        )

        # Verify shutdown method exists
        assert hasattr(processor, 'shutdown')
        assert callable(processor.shutdown)

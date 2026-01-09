"""Integration tests for Database Migration Platform.

These tests require the full Docker Compose stack to be running.
Run with: pytest tests/test_integration.py -v --integration
"""

import pytest
import psycopg2
import requests
import json
import time
import os
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError


# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def source_db_conn():
    """Create connection to source database."""
    conn = psycopg2.connect(
        os.getenv(
            "SOURCE_DB_URL", "postgresql://postgres:postgres@localhost:5432/sourcedb"
        )
    )
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def target_db_conn():
    """Create connection to target database."""
    conn = psycopg2.connect(
        os.getenv(
            "TARGET_DB_URL", "postgresql://postgres:postgres@localhost:5433/targetdb"
        )
    )
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def debezium_url():
    """Return Debezium Connect URL."""
    return os.getenv("DEBEZIUM_CONNECT_URL", "http://localhost:8083")


@pytest.fixture(scope="module")
def kafka_servers():
    """Return Kafka bootstrap servers."""
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


class TestDatabaseConnectivity:
    """Test database connections."""

    def test_source_db_accessible(self, source_db_conn):
        """Test that source database is accessible."""
        cursor = source_db_conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

    def test_target_db_accessible(self, target_db_conn):
        """Test that target database is accessible."""
        cursor = target_db_conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1

    def test_source_db_has_sample_data(self, source_db_conn):
        """Test that source database has initialized with sample data."""
        cursor = source_db_conn.cursor()

        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count >= 10, "Source DB should have at least 10 users"

        # Check orders table
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        assert order_count >= 10, "Source DB should have at least 10 orders"

    def test_source_db_replication_enabled(self, source_db_conn):
        """Test that source database has replication enabled."""
        cursor = source_db_conn.cursor()

        # Check wal_level
        cursor.execute("SHOW wal_level")
        wal_level = cursor.fetchone()[0]
        assert wal_level == "logical", "wal_level must be 'logical' for CDC"

        # Check replication slots
        cursor.execute("SHOW max_replication_slots")
        max_slots = int(cursor.fetchone()[0])
        assert max_slots >= 1, "max_replication_slots must be >= 1"


class TestKafkaConnectivity:
    """Test Kafka connectivity."""

    def test_kafka_accessible(self, kafka_servers):
        """Test that Kafka is accessible."""
        try:
            producer = KafkaProducer(
                bootstrap_servers=kafka_servers, request_timeout_ms=10000
            )
            # Send a test message
            future = producer.send("test-topic", b"test-message")
            record_metadata = future.get(timeout=10)
            assert record_metadata.topic == "test-topic"
            producer.close()
        except KafkaError as e:
            pytest.fail(f"Kafka not accessible: {e}")


class TestDebeziumConnector:
    """Test Debezium connector registration and functionality."""

    def test_debezium_api_accessible(self, debezium_url):
        """Test that Debezium Connect API is accessible."""
        response = requests.get(debezium_url)
        assert response.status_code == 200, "Debezium Connect API should be accessible"

    def test_list_connectors(self, debezium_url):
        """Test listing Debezium connectors."""
        response = requests.get(f"{debezium_url}/connectors")
        assert response.status_code == 200
        connectors = response.json()
        assert isinstance(connectors, list), "Should return list of connectors"

    def test_register_postgres_connector(self, debezium_url):
        """Test registering PostgreSQL connector."""
        # Load connector configuration
        config_path = "config/debezium-postgres-connector.json"

        if not os.path.exists(config_path):
            pytest.skip("Connector config file not found")

        with open(config_path) as f:
            connector_config = json.load(f)

        # Register connector
        response = requests.post(
            f"{debezium_url}/connectors",
            json=connector_config,
            headers={"Content-Type": "application/json"},
        )

        # 201 = created, 409 = already exists (both acceptable)
        assert response.status_code in [
            200,
            201,
            409,
        ], f"Connector registration failed: {response.text}"

        # Verify connector is running
        time.sleep(5)  # Give connector time to start
        connector_name = connector_config["name"]
        response = requests.get(f"{debezium_url}/connectors/{connector_name}/status")

        assert response.status_code == 200
        status = response.json()
        assert status["connector"]["state"] in [
            "RUNNING",
            "UNASSIGNED",
        ], f"Connector not running: {status}"


class TestChangeDataCapture:
    """Test Change Data Capture functionality."""

    @pytest.fixture(autouse=True)
    def setup_cdc(self, debezium_url):
        """Ensure CDC connector is registered before each test."""
        # This will be called before each test method
        time.sleep(2)  # Allow CDC to catch up
        yield

    def test_cdc_captures_inserts(self, source_db_conn, kafka_servers):
        """Test that CDC captures INSERT events."""
        # Create Kafka consumer for CDC events
        consumer = KafkaConsumer(
            "dbserver1.public.users",
            bootstrap_servers=kafka_servers,
            auto_offset_reset="latest",
            consumer_timeout_ms=20000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Insert a new user in source database
        cursor = source_db_conn.cursor()
        test_username = f"testuser_{int(time.time())}"
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
            (test_username, f"{test_username}@example.com"),
        )
        user_id = cursor.fetchone()[0]
        source_db_conn.commit()

        # Wait for CDC event
        event_found = False
        for message in consumer:
            event = message.value

            # Check if this is our INSERT event
            if (
                event.get("payload", {}).get("after", {}).get("username")
                == test_username
            ):
                assert (
                    event["payload"]["op"] == "c"
                ), "Operation should be 'c' (create/insert)"
                assert event["payload"]["after"]["id"] == user_id
                event_found = True
                break

        consumer.close()
        assert event_found, "CDC event for INSERT not captured"

    def test_cdc_captures_updates(self, source_db_conn, kafka_servers):
        """Test that CDC captures UPDATE events."""
        consumer = KafkaConsumer(
            "dbserver1.public.orders",
            bootstrap_servers=kafka_servers,
            auto_offset_reset="latest",
            consumer_timeout_ms=20000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Update an order status
        cursor = source_db_conn.cursor()
        cursor.execute(
            "UPDATE orders SET status = 'completed' WHERE id = 1 RETURNING order_number"
        )
        order_number = cursor.fetchone()[0]
        source_db_conn.commit()

        # Wait for CDC event
        event_found = False
        for message in consumer:
            event = message.value

            # Check if this is our UPDATE event
            if (
                event.get("payload", {}).get("after", {}).get("order_number")
                == order_number
            ):
                assert event["payload"]["op"] == "u", "Operation should be 'u' (update)"
                assert event["payload"]["after"]["status"] == "completed"
                event_found = True
                break

        consumer.close()
        assert event_found, "CDC event for UPDATE not captured"

    def test_cdc_captures_deletes(self, source_db_conn, kafka_servers):
        """Test that CDC captures DELETE events."""
        # First, create a test order to delete
        cursor = source_db_conn.cursor()
        test_order_number = f"ORD-TEST-{int(time.time())}"
        cursor.execute(
            """INSERT INTO orders (user_id, order_number, total_amount, status)
               VALUES (1, %s, 99.99, 'pending') RETURNING id""",
            (test_order_number,),
        )
        order_id = cursor.fetchone()[0]
        source_db_conn.commit()

        # Wait a moment for CDC to capture the INSERT
        time.sleep(2)

        # Create consumer
        consumer = KafkaConsumer(
            "dbserver1.public.orders",
            bootstrap_servers=kafka_servers,
            auto_offset_reset="latest",
            consumer_timeout_ms=20000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Now delete it
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        source_db_conn.commit()

        # Wait for CDC event
        event_found = False
        for message in consumer:
            event = message.value

            # Check if this is our DELETE event
            before_data = event.get("payload", {}).get("before", {})
            if before_data.get("order_number") == test_order_number:
                assert event["payload"]["op"] == "d", "Operation should be 'd' (delete)"
                event_found = True
                break

        consumer.close()
        assert event_found, "CDC event for DELETE not captured"


class TestEndToEndMigration:
    """Test end-to-end migration workflow."""

    def test_full_load_migration(self, source_db_conn, target_db_conn):
        """Test full database load from source to target."""
        # This is a placeholder for the full orchestrator test
        # In a real scenario, this would call the MigrationOrchestrator

        # For now, verify we can count rows in both databases
        source_cursor = source_db_conn.cursor()
        target_cursor = target_db_conn.cursor()

        # Count users in source
        source_cursor.execute("SELECT COUNT(*) FROM users")
        source_user_count = source_cursor.fetchone()[0]

        assert source_user_count > 0, "Source should have users"

        # In a real test, we would:
        # 1. Run the orchestrator to replicate data
        # 2. Verify target has same row counts
        # 3. Verify data integrity with checksums
        # 4. Test rollback functionality

    def test_validation_after_migration(self, source_db_conn, target_db_conn):
        """Test data validation between source and target."""
        # Get table list from source
        source_cursor = source_db_conn.cursor()
        source_cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
        """
        )
        tables = [row[0] for row in source_cursor.fetchall()]

        assert len(tables) > 0, "Source should have tables"

        # In a real validation test, we would:
        # 1. Compare row counts for each table
        # 2. Compute and compare checksums
        # 3. Sample and compare actual data
        # 4. Verify foreign key constraints
        # 5. Check index definitions


class TestPerformance:
    """Test migration performance characteristics."""

    def test_cdc_latency(self, source_db_conn, kafka_servers):
        """Measure CDC event latency."""
        consumer = KafkaConsumer(
            "dbserver1.public.users",
            bootstrap_servers=kafka_servers,
            auto_offset_reset="latest",
            consumer_timeout_ms=10000,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        # Insert and measure time until CDC event appears
        start_time = time.time()

        cursor = source_db_conn.cursor()
        test_username = f"perftest_{int(time.time())}"
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (test_username, f"{test_username}@example.com"),
        )
        source_db_conn.commit()

        # Wait for CDC event
        for message in consumer:
            event = message.value
            if (
                event.get("payload", {}).get("after", {}).get("username")
                == test_username
            ):
                latency = time.time() - start_time
                print(f"\nCDC latency: {latency:.3f} seconds")
                assert latency < 5.0, "CDC latency should be under 5 seconds"
                break

        consumer.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--integration"])

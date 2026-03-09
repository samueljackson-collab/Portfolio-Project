"""
CDC Integration Tests with Testcontainers

These tests spin up the full CDC stack (MySQL, PostgreSQL, Kafka, Debezium)
using testcontainers and verify end-to-end data migration.

Requirements:
    pip install testcontainers pytest kafka-python mysql-connector-python psycopg2-binary requests

Run with:
    pytest tests/test_cdc_integration.py -v --integration
"""

import json
import time
import pytest
import requests
from typing import Generator

# Testcontainers imports
from testcontainers.mysql import MySqlContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

import mysql.connector
import psycopg2
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError


# Mark all tests as integration tests
pytestmark = pytest.mark.integration


class DebeziumContainer(DockerContainer):
    """Custom testcontainer for Debezium Connect."""

    def __init__(self, kafka_bootstrap_servers: str):
        super().__init__(image="debezium/connect:2.3")
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.with_exposed_ports(8083)
        self.with_env("BOOTSTRAP_SERVERS", kafka_bootstrap_servers)
        self.with_env("GROUP_ID", "test-connect-cluster")
        self.with_env("CONFIG_STORAGE_TOPIC", "test_configs")
        self.with_env("OFFSET_STORAGE_TOPIC", "test_offsets")
        self.with_env("STATUS_STORAGE_TOPIC", "test_statuses")
        self.with_env("CONFIG_STORAGE_REPLICATION_FACTOR", "1")
        self.with_env("OFFSET_STORAGE_REPLICATION_FACTOR", "1")
        self.with_env("STATUS_STORAGE_REPLICATION_FACTOR", "1")
        self.with_env("KEY_CONVERTER", "org.apache.kafka.connect.json.JsonConverter")
        self.with_env("VALUE_CONVERTER", "org.apache.kafka.connect.json.JsonConverter")
        self.with_env("KEY_CONVERTER_SCHEMAS_ENABLE", "false")
        self.with_env("VALUE_CONVERTER_SCHEMAS_ENABLE", "false")

    def get_connect_url(self) -> str:
        """Get Debezium Connect REST API URL."""
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(8083)}"

    def wait_for_ready(self, timeout: int = 60):
        """Wait for Debezium Connect to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.get_connect_url()}/connectors")
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        raise TimeoutError("Debezium Connect did not become ready")


@pytest.fixture(scope="module")
def mysql_container() -> Generator[MySqlContainer, None, None]:
    """Start MySQL container with CDC configuration."""
    with MySqlContainer(
        image="mysql:8.0",
        username="debezium",
        password="dbzpass",
        dbname="sourcedb"
    ) as mysql:
        # Configure MySQL for CDC
        conn = mysql.connector.connect(
            host=mysql.get_container_host_ip(),
            port=mysql.get_exposed_port(3306),
            user="root",
            password=mysql.root_password
        )
        cursor = conn.cursor()

        # Grant replication privileges
        cursor.execute("GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'debezium'@'%'")
        cursor.execute("GRANT SELECT ON *.* TO 'debezium'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        conn.commit()

        # Create test tables
        cursor.execute("USE sourcedb")
        cursor.execute("""
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                status ENUM('active', 'inactive') DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_number VARCHAR(50) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Insert sample data
        cursor.execute("INSERT INTO users (username, email) VALUES ('testuser1', 'test1@example.com')")
        cursor.execute("INSERT INTO users (username, email) VALUES ('testuser2', 'test2@example.com')")
        cursor.execute("INSERT INTO orders (user_id, order_number, total_amount) VALUES (1, 'ORD-001', 99.99)")
        conn.commit()

        cursor.close()
        conn.close()

        yield mysql


@pytest.fixture(scope="module")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start PostgreSQL container as migration target."""
    with PostgresContainer(
        image="postgres:15",
        user="postgres",
        password="postgres",
        dbname="targetdb"
    ) as postgres:
        # Create target schema
        conn = psycopg2.connect(
            host=postgres.get_container_host_ip(),
            port=postgres.get_exposed_port(5432),
            user=postgres.username,
            password=postgres.password,
            database=postgres.dbname
        )
        cursor = conn.cursor()

        # Create ENUM types
        cursor.execute("CREATE TYPE user_status AS ENUM ('active', 'inactive')")
        cursor.execute("CREATE TYPE order_status AS ENUM ('pending', 'completed', 'cancelled')")

        # Create tables
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                email VARCHAR(100) NOT NULL,
                status user_status DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES users(id),
                order_number VARCHAR(50) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                status order_status DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()

        yield postgres


@pytest.fixture(scope="module")
def kafka_container() -> Generator[KafkaContainer, None, None]:
    """Start Kafka container."""
    with KafkaContainer() as kafka:
        yield kafka


@pytest.fixture(scope="module")
def debezium_container(kafka_container: KafkaContainer) -> Generator[DebeziumContainer, None, None]:
    """Start Debezium Connect container."""
    bootstrap_servers = kafka_container.get_bootstrap_server()

    debezium = DebeziumContainer(bootstrap_servers)
    debezium.start()

    try:
        debezium.wait_for_ready(timeout=90)
        yield debezium
    finally:
        debezium.stop()


class TestMySQLConnectivity:
    """Test MySQL container setup."""

    def test_mysql_connection(self, mysql_container: MySqlContainer):
        """Verify MySQL is accessible."""
        conn = mysql.connector.connect(
            host=mysql_container.get_container_host_ip(),
            port=mysql_container.get_exposed_port(3306),
            user="debezium",
            password="dbzpass",
            database="sourcedb"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1
        cursor.close()
        conn.close()

    def test_mysql_has_sample_data(self, mysql_container: MySqlContainer):
        """Verify MySQL has the sample data."""
        conn = mysql.connector.connect(
            host=mysql_container.get_container_host_ip(),
            port=mysql_container.get_exposed_port(3306),
            user="debezium",
            password="dbzpass",
            database="sourcedb"
        )
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        assert cursor.fetchone()[0] >= 2

        cursor.execute("SELECT COUNT(*) FROM orders")
        assert cursor.fetchone()[0] >= 1

        cursor.close()
        conn.close()


class TestPostgreSQLConnectivity:
    """Test PostgreSQL container setup."""

    def test_postgres_connection(self, postgres_container: PostgresContainer):
        """Verify PostgreSQL is accessible."""
        conn = psycopg2.connect(
            host=postgres_container.get_container_host_ip(),
            port=postgres_container.get_exposed_port(5432),
            user=postgres_container.username,
            password=postgres_container.password,
            database=postgres_container.dbname
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1
        cursor.close()
        conn.close()

    def test_postgres_schema_exists(self, postgres_container: PostgresContainer):
        """Verify PostgreSQL has the target schema."""
        conn = psycopg2.connect(
            host=postgres_container.get_container_host_ip(),
            port=postgres_container.get_exposed_port(5432),
            user=postgres_container.username,
            password=postgres_container.password,
            database=postgres_container.dbname
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = {row[0] for row in cursor.fetchall()}

        assert 'users' in tables
        assert 'orders' in tables

        cursor.close()
        conn.close()


class TestKafkaConnectivity:
    """Test Kafka container setup."""

    def test_kafka_connection(self, kafka_container: KafkaContainer):
        """Verify Kafka is accessible."""
        producer = KafkaProducer(
            bootstrap_servers=kafka_container.get_bootstrap_server(),
            request_timeout_ms=10000
        )

        future = producer.send('test-topic', b'test-message')
        record_metadata = future.get(timeout=10)

        assert record_metadata.topic == 'test-topic'
        producer.close()


class TestDebeziumConnector:
    """Test Debezium connector functionality."""

    def test_debezium_api_accessible(self, debezium_container: DebeziumContainer):
        """Verify Debezium Connect API is accessible."""
        response = requests.get(f"{debezium_container.get_connect_url()}/connectors")
        assert response.status_code == 200

    def test_register_mysql_connector(
        self,
        debezium_container: DebeziumContainer,
        mysql_container: MySqlContainer,
        kafka_container: KafkaContainer
    ):
        """Test registering MySQL connector."""
        connector_config = {
            "name": "test-mysql-connector",
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "tasks.max": "1",
                "database.hostname": mysql_container.get_container_host_ip(),
                "database.port": str(mysql_container.get_exposed_port(3306)),
                "database.user": "debezium",
                "database.password": "dbzpass",
                "database.server.id": "184054",
                "topic.prefix": "testdb",
                "database.include.list": "sourcedb",
                "schema.history.internal.kafka.bootstrap.servers": kafka_container.get_bootstrap_server(),
                "schema.history.internal.kafka.topic": "schema-changes.sourcedb"
            }
        }

        response = requests.post(
            f"{debezium_container.get_connect_url()}/connectors",
            json=connector_config,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [200, 201, 409]

        # Wait for connector to start
        time.sleep(10)

        # Check connector status
        response = requests.get(
            f"{debezium_container.get_connect_url()}/connectors/test-mysql-connector/status"
        )
        assert response.status_code == 200
        status = response.json()
        assert status['connector']['state'] in ['RUNNING', 'UNASSIGNED']


class TestCDCCapture:
    """Test CDC event capture functionality."""

    @pytest.fixture(autouse=True)
    def setup_connector(
        self,
        debezium_container: DebeziumContainer,
        mysql_container: MySqlContainer,
        kafka_container: KafkaContainer
    ):
        """Ensure connector is registered before tests."""
        connector_config = {
            "name": "cdc-test-connector",
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "tasks.max": "1",
                "database.hostname": mysql_container.get_container_host_ip(),
                "database.port": str(mysql_container.get_exposed_port(3306)),
                "database.user": "debezium",
                "database.password": "dbzpass",
                "database.server.id": "184055",
                "topic.prefix": "cdctest",
                "database.include.list": "sourcedb",
                "schema.history.internal.kafka.bootstrap.servers": kafka_container.get_bootstrap_server(),
                "schema.history.internal.kafka.topic": "cdc-schema-changes"
            }
        }

        requests.post(
            f"{debezium_container.get_connect_url()}/connectors",
            json=connector_config,
            headers={"Content-Type": "application/json"}
        )
        time.sleep(15)  # Wait for initial snapshot

    def test_cdc_captures_insert(
        self,
        mysql_container: MySqlContainer,
        kafka_container: KafkaContainer
    ):
        """Test that CDC captures INSERT events."""
        # Create consumer
        consumer = KafkaConsumer(
            'cdctest.sourcedb.users',
            bootstrap_servers=kafka_container.get_bootstrap_server(),
            auto_offset_reset='latest',
            consumer_timeout_ms=30000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None
        )

        # Insert new user
        conn = mysql.connector.connect(
            host=mysql_container.get_container_host_ip(),
            port=mysql_container.get_exposed_port(3306),
            user="debezium",
            password="dbzpass",
            database="sourcedb"
        )
        cursor = conn.cursor()
        test_username = f"cdctest_{int(time.time())}"
        cursor.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s)",
            (test_username, f"{test_username}@example.com")
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Wait for CDC event
        event_found = False
        for message in consumer:
            if message.value:
                payload = message.value.get('payload', message.value)
                after = payload.get('after', {})
                if after.get('username') == test_username:
                    event_found = True
                    break

        consumer.close()
        assert event_found, "CDC event for INSERT not captured"

    def test_cdc_captures_update(
        self,
        mysql_container: MySqlContainer,
        kafka_container: KafkaContainer
    ):
        """Test that CDC captures UPDATE events."""
        consumer = KafkaConsumer(
            'cdctest.sourcedb.users',
            bootstrap_servers=kafka_container.get_bootstrap_server(),
            auto_offset_reset='latest',
            consumer_timeout_ms=30000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None
        )

        # Update user
        conn = mysql.connector.connect(
            host=mysql_container.get_container_host_ip(),
            port=mysql_container.get_exposed_port(3306),
            user="debezium",
            password="dbzpass",
            database="sourcedb"
        )
        cursor = conn.cursor()
        new_email = f"updated_{int(time.time())}@example.com"
        cursor.execute("UPDATE users SET email = %s WHERE id = 1", (new_email,))
        conn.commit()
        cursor.close()
        conn.close()

        # Wait for CDC event
        event_found = False
        for message in consumer:
            if message.value:
                payload = message.value.get('payload', message.value)
                after = payload.get('after', {})
                if after.get('email') == new_email:
                    op = payload.get('op', '')
                    if op == 'u':
                        event_found = True
                        break

        consumer.close()
        assert event_found, "CDC event for UPDATE not captured"


class TestEndToEndMigration:
    """Test complete migration workflow."""

    def test_data_migration_consistency(
        self,
        mysql_container: MySqlContainer,
        postgres_container: PostgresContainer
    ):
        """Test that data can be migrated consistently."""
        # Get source data
        mysql_conn = mysql.connector.connect(
            host=mysql_container.get_container_host_ip(),
            port=mysql_container.get_exposed_port(3306),
            user="debezium",
            password="dbzpass",
            database="sourcedb"
        )
        mysql_cursor = mysql_conn.cursor(dictionary=True)
        mysql_cursor.execute("SELECT * FROM users ORDER BY id")
        source_users = mysql_cursor.fetchall()
        mysql_cursor.close()
        mysql_conn.close()

        # Insert into target
        pg_conn = psycopg2.connect(
            host=postgres_container.get_container_host_ip(),
            port=postgres_container.get_exposed_port(5432),
            user=postgres_container.username,
            password=postgres_container.password,
            database=postgres_container.dbname
        )
        pg_cursor = pg_conn.cursor()

        for user in source_users:
            pg_cursor.execute(
                "INSERT INTO users (id, username, email, status) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                (user['id'], user['username'], user['email'], user['status'])
            )
        pg_conn.commit()

        # Verify target data
        pg_cursor.execute("SELECT COUNT(*) FROM users")
        target_count = pg_cursor.fetchone()[0]

        pg_cursor.close()
        pg_conn.close()

        assert target_count >= len(source_users)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--integration'])

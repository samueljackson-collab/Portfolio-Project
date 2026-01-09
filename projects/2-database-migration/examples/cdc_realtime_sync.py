#!/usr/bin/env python3
"""
Example: CDC Real-Time Synchronization Demo

This script demonstrates real-time Change Data Capture (CDC) synchronization
between MySQL and PostgreSQL using Debezium and Kafka.

Features:
- Configure Debezium MySQL connector
- Consume CDC events from Kafka
- Apply changes to PostgreSQL in real-time
- Monitor replication lag

Usage:
    python cdc_realtime_sync.py --duration 300
"""

import argparse
import json
import logging
import signal
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import requests
import psycopg2
from psycopg2.extras import execute_values
from kafka import KafkaConsumer
from kafka.errors import KafkaError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CDCConfig:
    """Configuration for CDC synchronization."""
    # Kafka settings
    kafka_bootstrap_servers: str = "localhost:29092"
    kafka_topic_prefix: str = "mysql-source"
    kafka_consumer_group: str = "cdc-sync-demo"

    # Debezium settings
    debezium_url: str = "http://localhost:8083"
    connector_name: str = "mysql-source-connector"

    # MySQL source (for connector config)
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "sourcedb"
    mysql_user: str = "debezium"
    mysql_password: str = "dbzpass"

    # PostgreSQL target
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_database: str = "targetdb"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"


@dataclass
class SyncStats:
    """Statistics for CDC synchronization."""
    events_received: int = 0
    inserts: int = 0
    updates: int = 0
    deletes: int = 0
    errors: int = 0
    start_time: Optional[datetime] = None
    last_event_time: Optional[datetime] = None

    @property
    def events_per_second(self) -> float:
        if self.start_time and self.events_received > 0:
            duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            return self.events_received / duration if duration > 0 else 0
        return 0.0


class DebeziumConnectorManager:
    """Manages Debezium connector configuration."""

    def __init__(self, config: CDCConfig):
        self.config = config
        self.connector_config = self._build_connector_config()

    def _build_connector_config(self) -> Dict[str, Any]:
        """Build Debezium MySQL connector configuration."""
        return {
            "name": self.config.connector_name,
            "config": {
                "connector.class": "io.debezium.connector.mysql.MySqlConnector",
                "tasks.max": "1",
                "database.hostname": self.config.mysql_host,
                "database.port": str(self.config.mysql_port),
                "database.user": self.config.mysql_user,
                "database.password": self.config.mysql_password,
                "database.server.id": "184054",
                "topic.prefix": self.config.kafka_topic_prefix,
                "database.include.list": self.config.mysql_database,
                "schema.history.internal.kafka.bootstrap.servers": self.config.kafka_bootstrap_servers,
                "schema.history.internal.kafka.topic": "schema-changes.sourcedb",
                "include.schema.changes": "true",
                "snapshot.mode": "initial",
                "transforms": "unwrap",
                "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
                "transforms.unwrap.drop.tombstones": "false",
                "transforms.unwrap.delete.handling.mode": "rewrite",
                "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                "key.converter.schemas.enable": "false",
                "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                "value.converter.schemas.enable": "false"
            }
        }

    def register_connector(self) -> bool:
        """Register the Debezium connector."""
        url = f"{self.config.debezium_url}/connectors"

        try:
            # Check if connector exists
            response = requests.get(f"{url}/{self.config.connector_name}")
            if response.status_code == 200:
                logger.info(f"Connector '{self.config.connector_name}' already exists")
                return True

            # Create connector
            response = requests.post(
                url,
                json=self.connector_config,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code in [200, 201]:
                logger.info(f"Connector '{self.config.connector_name}' registered successfully")
                return True
            else:
                logger.error(f"Failed to register connector: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Debezium: {e}")
            return False

    def get_connector_status(self) -> Optional[Dict[str, Any]]:
        """Get connector status."""
        url = f"{self.config.debezium_url}/connectors/{self.config.connector_name}/status"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting connector status: {e}")

        return None

    def delete_connector(self) -> bool:
        """Delete the connector."""
        url = f"{self.config.debezium_url}/connectors/{self.config.connector_name}"

        try:
            response = requests.delete(url)
            return response.status_code in [200, 204]
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting connector: {e}")
            return False


class CDCEventProcessor:
    """Processes CDC events and applies them to PostgreSQL."""

    # Mapping of MySQL tables to PostgreSQL tables
    TABLE_MAPPINGS = {
        "users": "users",
        "products": "products",
        "orders": "orders",
        "order_items": "order_items",
        "inventory_log": "inventory_log"
    }

    def __init__(self, config: CDCConfig):
        self.config = config
        self.stats = SyncStats()

    def get_postgres_connection(self):
        """Create PostgreSQL connection."""
        return psycopg2.connect(
            host=self.config.postgres_host,
            port=self.config.postgres_port,
            database=self.config.postgres_database,
            user=self.config.postgres_user,
            password=self.config.postgres_password
        )

    def process_event(self, topic: str, event: Dict[str, Any]) -> bool:
        """Process a single CDC event."""
        try:
            # Extract table name from topic (format: prefix.database.table)
            parts = topic.split(".")
            if len(parts) < 3:
                return False

            table_name = parts[-1]
            if table_name not in self.TABLE_MAPPINGS:
                logger.debug(f"Skipping unmapped table: {table_name}")
                return True

            target_table = self.TABLE_MAPPINGS[table_name]

            # Determine operation type
            op = event.get("__op", event.get("op"))

            if op == "c" or op == "r":  # Create/Read (snapshot)
                return self._handle_insert(target_table, event)
            elif op == "u":  # Update
                return self._handle_update(target_table, event)
            elif op == "d":  # Delete
                return self._handle_delete(target_table, event)
            else:
                logger.warning(f"Unknown operation: {op}")
                return False

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            self.stats.errors += 1
            return False

    def _handle_insert(self, table: str, event: Dict[str, Any]) -> bool:
        """Handle INSERT operation."""
        conn = self.get_postgres_connection()
        cursor = conn.cursor()

        try:
            # Get column names and values from event
            data = {k: v for k, v in event.items() if not k.startswith("__")}

            columns = list(data.keys())
            values = [self._convert_value(v) for v in data.values()]

            # Build INSERT query with ON CONFLICT
            cols_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(values))

            query = f"""
                INSERT INTO {table} ({cols_str})
                VALUES ({placeholders})
                ON CONFLICT (id) DO UPDATE SET
                {', '.join(f"{c} = EXCLUDED.{c}" for c in columns if c != 'id')}
            """

            cursor.execute(query, values)
            conn.commit()
            self.stats.inserts += 1
            return True

        except Exception as e:
            logger.error(f"Insert failed for {table}: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def _handle_update(self, table: str, event: Dict[str, Any]) -> bool:
        """Handle UPDATE operation."""
        conn = self.get_postgres_connection()
        cursor = conn.cursor()

        try:
            data = {k: v for k, v in event.items() if not k.startswith("__")}

            if "id" not in data:
                logger.warning(f"Update event missing 'id' for {table}")
                return False

            row_id = data.pop("id")
            set_clause = ", ".join(f"{k} = %s" for k in data.keys())
            values = [self._convert_value(v) for v in data.values()]
            values.append(row_id)

            query = f"UPDATE {table} SET {set_clause} WHERE id = %s"
            cursor.execute(query, values)
            conn.commit()
            self.stats.updates += 1
            return True

        except Exception as e:
            logger.error(f"Update failed for {table}: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def _handle_delete(self, table: str, event: Dict[str, Any]) -> bool:
        """Handle DELETE operation."""
        conn = self.get_postgres_connection()
        cursor = conn.cursor()

        try:
            # For deletes, we need the key (id)
            row_id = event.get("id")
            if not row_id:
                logger.warning(f"Delete event missing 'id' for {table}")
                return False

            query = f"DELETE FROM {table} WHERE id = %s"
            cursor.execute(query, (row_id,))
            conn.commit()
            self.stats.deletes += 1
            return True

        except Exception as e:
            logger.error(f"Delete failed for {table}: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def _convert_value(self, value: Any) -> Any:
        """Convert value for PostgreSQL compatibility."""
        if isinstance(value, dict):
            return json.dumps(value)
        return value


class CDCSyncRunner:
    """Main runner for CDC synchronization."""

    def __init__(self, config: CDCConfig, duration_seconds: int = 0):
        self.config = config
        self.duration = duration_seconds
        self.connector_manager = DebeziumConnectorManager(config)
        self.event_processor = CDCEventProcessor(config)
        self.running = True

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received")
        self.running = False

    def run(self):
        """Run the CDC synchronization."""
        logger.info("=" * 60)
        logger.info("CDC REAL-TIME SYNC DEMO")
        logger.info("=" * 60)

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Register Debezium connector
        logger.info("Registering Debezium connector...")
        if not self.connector_manager.register_connector():
            logger.error("Failed to register connector")
            return

        # Wait for connector to start
        logger.info("Waiting for connector to initialize...")
        time.sleep(10)

        # Check connector status
        status = self.connector_manager.get_connector_status()
        if status:
            logger.info(f"Connector status: {status.get('connector', {}).get('state', 'UNKNOWN')}")

        # Create Kafka consumer
        topics = [
            f"{self.config.kafka_topic_prefix}.{self.config.mysql_database}.{table}"
            for table in CDCEventProcessor.TABLE_MAPPINGS.keys()
        ]

        logger.info(f"Subscribing to topics: {topics}")

        try:
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                group_id=self.config.kafka_consumer_group,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                consumer_timeout_ms=1000
            )
        except KafkaError as e:
            logger.error(f"Failed to create Kafka consumer: {e}")
            return

        # Start processing
        self.event_processor.stats.start_time = datetime.now(timezone.utc)
        start_time = time.time()

        logger.info("Starting CDC event processing...")
        logger.info(f"Duration: {'unlimited' if self.duration == 0 else f'{self.duration}s'}")

        try:
            while self.running:
                # Check duration limit
                if self.duration > 0 and (time.time() - start_time) >= self.duration:
                    logger.info("Duration limit reached")
                    break

                # Poll for messages
                for message in consumer:
                    if not self.running:
                        break

                    if message.value:
                        self.event_processor.stats.events_received += 1
                        self.event_processor.stats.last_event_time = datetime.now(timezone.utc)

                        success = self.event_processor.process_event(message.topic, message.value)

                        if self.event_processor.stats.events_received % 100 == 0:
                            self._print_progress()

        except Exception as e:
            logger.error(f"Error during sync: {e}")
        finally:
            consumer.close()

        # Print final stats
        self._print_final_stats()

    def _print_progress(self):
        """Print progress update."""
        stats = self.event_processor.stats
        logger.info(
            f"Progress: {stats.events_received} events | "
            f"I:{stats.inserts} U:{stats.updates} D:{stats.deletes} E:{stats.errors} | "
            f"{stats.events_per_second:.1f} events/s"
        )

    def _print_final_stats(self):
        """Print final statistics."""
        stats = self.event_processor.stats
        logger.info("=" * 60)
        logger.info("SYNC COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total events processed: {stats.events_received}")
        logger.info(f"  Inserts: {stats.inserts}")
        logger.info(f"  Updates: {stats.updates}")
        logger.info(f"  Deletes: {stats.deletes}")
        logger.info(f"  Errors: {stats.errors}")
        logger.info(f"Average throughput: {stats.events_per_second:.2f} events/second")


def main():
    parser = argparse.ArgumentParser(description="CDC Real-Time Sync Demo")
    parser.add_argument(
        "--duration", type=int, default=0,
        help="Duration to run in seconds (0 = unlimited)"
    )
    parser.add_argument("--kafka-servers", default="localhost:29092")
    parser.add_argument("--debezium-url", default="http://localhost:8083")
    args = parser.parse_args()

    config = CDCConfig(
        kafka_bootstrap_servers=args.kafka_servers,
        debezium_url=args.debezium_url
    )

    runner = CDCSyncRunner(config, args.duration)
    runner.run()


if __name__ == "__main__":
    main()

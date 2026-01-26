"""MQTT to TimescaleDB processor for IoT telemetry data."""

from __future__ import annotations

import json
import logging
import os
import signal
import sys
from datetime import datetime
from typing import Any, Dict

import paho.mqtt.client as mqtt
import psycopg2
from psycopg2.extras import execute_values

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MQTTProcessor:
    """Process MQTT messages and store in TimescaleDB."""

    def __init__(
        self,
        mqtt_broker: str,
        mqtt_port: int,
        mqtt_topic: str,
        postgres_config: Dict[str, Any],
    ):
        """
        Initialize MQTT processor.

        Args:
            mqtt_broker: MQTT broker hostname
            mqtt_port: MQTT broker port
            mqtt_topic: MQTT topic to subscribe to
            postgres_config: PostgreSQL connection parameters
        """
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.postgres_config = postgres_config

        # Statistics
        self.messages_processed = 0
        self.messages_failed = 0
        self.batch_buffer = []
        self.batch_size = 100

        # Initialize database connection
        self.db_conn = None
        self.connect_db()

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def connect_db(self):
        """Connect to PostgreSQL/TimescaleDB."""
        try:
            self.db_conn = psycopg2.connect(**self.postgres_config)
            self.db_conn.autocommit = False
            logger.info(f"Connected to TimescaleDB at {self.postgres_config['host']}")

            # Create table if it doesn't exist
            self.create_table()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            sys.exit(1)

    def create_table(self):
        """Create TimescaleDB hypertable for telemetry data."""
        try:
            cursor = self.db_conn.cursor()

            # Create telemetry table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS device_telemetry (
                    time TIMESTAMPTZ NOT NULL,
                    device_id TEXT NOT NULL,
                    firmware_version TEXT,
                    temperature DOUBLE PRECISION,
                    humidity DOUBLE PRECISION,
                    battery DOUBLE PRECISION,
                    raw_data JSONB
                )
            """
            )

            # Convert to hypertable (idempotent)
            cursor.execute(
                """
                SELECT create_hypertable('device_telemetry', 'time',
                    if_not_exists => TRUE
                )
            """
            )

            # Create indexes
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_device_telemetry_device_id
                ON device_telemetry (device_id, time DESC)
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_device_telemetry_time
                ON device_telemetry (time DESC)
            """
            )

            self.db_conn.commit()
            logger.info("TimescaleDB hypertable created successfully")

        except Exception as e:
            logger.error(f"Failed to create table: {e}")
            self.db_conn.rollback()
            raise

    def on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection."""
        if rc == 0:
            logger.info(
                f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}"
            )
            client.subscribe(self.mqtt_topic)
            logger.info(f"Subscribed to topic: {self.mqtt_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection."""
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker: {rc}")

    def on_message(self, client, userdata, msg):
        """
        Callback for MQTT message.

        Args:
            client: MQTT client
            userdata: User data
            msg: MQTT message
        """
        try:
            # Parse message
            payload = json.loads(msg.payload.decode("utf-8"))

            # Add to batch buffer
            self.batch_buffer.append(payload)

            # Process batch if buffer is full
            if len(self.batch_buffer) >= self.batch_size:
                self.flush_batch()

            self.messages_processed += 1

            if self.messages_processed % 100 == 0:
                logger.info(
                    f"Processed {self.messages_processed} messages "
                    f"({self.messages_failed} failed)"
                )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message: {e}")
            self.messages_failed += 1
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.messages_failed += 1

    def flush_batch(self):
        """Flush batch buffer to database."""
        if not self.batch_buffer:
            return

        try:
            cursor = self.db_conn.cursor()

            # Prepare batch insert
            records = []
            for payload in self.batch_buffer:
                record = (
                    datetime.fromtimestamp(payload.get("timestamp", 0)),
                    payload.get("device_id"),
                    payload.get("firmware"),
                    payload.get("temperature"),
                    payload.get("humidity"),
                    payload.get("battery"),
                    json.dumps(payload),
                )
                records.append(record)

            # Batch insert
            execute_values(
                cursor,
                """
                INSERT INTO device_telemetry
                (time, device_id, firmware_version, temperature, humidity, battery, raw_data)
                VALUES %s
                """,
                records,
            )

            self.db_conn.commit()
            logger.debug(f"Flushed {len(records)} records to database")

            # Clear buffer
            self.batch_buffer = []

        except Exception as e:
            logger.error(f"Failed to flush batch: {e}")
            self.db_conn.rollback()
            self.batch_buffer = []  # Clear buffer to prevent retry loops

    def run(self):
        """Start the processor."""
        logger.info("Starting MQTT processor...")

        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)

            # Start MQTT loop
            self.mqtt_client.loop_forever()

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.shutdown(None, None)

    def shutdown(self, signum, frame):
        """Graceful shutdown."""
        logger.info("Shutting down...")

        # Flush remaining messages
        if self.batch_buffer:
            logger.info(f"Flushing remaining {len(self.batch_buffer)} messages...")
            self.flush_batch()

        # Disconnect MQTT
        self.mqtt_client.disconnect()

        # Close database connection
        if self.db_conn:
            self.db_conn.close()

        logger.info(
            f"Shutdown complete. Processed {self.messages_processed} messages "
            f"({self.messages_failed} failed)"
        )

        sys.exit(0)


def main():
    """Main entry point."""
    # Load configuration from environment
    mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_topic = os.getenv("MQTT_TOPIC", "portfolio/telemetry")

    postgres_config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "iot_analytics"),
        "user": os.getenv("POSTGRES_USER", "iot"),
        "password": os.getenv("POSTGRES_PASSWORD", "iot_password"),
    }

    # Create and run processor
    processor = MQTTProcessor(
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port,
        mqtt_topic=mqtt_topic,
        postgres_config=postgres_config,
    )

    processor.run()


if __name__ == "__main__":
    main()

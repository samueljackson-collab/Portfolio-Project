#!/usr/bin/env python3
"""Avro consumer with Schema Registry validation."""
from __future__ import annotations

import json
import logging
import signal
import argparse
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable

from confluent_kafka import DeserializingConsumer, KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import StringDeserializer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AvroEventConsumer:
    """
    Avro event consumer with Schema Registry validation.

    Consumes events from Kafka with Avro deserialization and automatic
    schema validation via Confluent Schema Registry.
    """

    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        schema_registry_url: str = 'http://localhost:8081',
        topic: str = 'user-events-avro',
        group_id: str = 'avro-consumer-group',
        auto_offset_reset: str = 'earliest',
        consumer_id: Optional[str] = None
    ):
        """
        Initialize Avro consumer.

        Args:
            bootstrap_servers: Kafka bootstrap servers
            schema_registry_url: Schema Registry URL
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
            consumer_id: Consumer identifier
        """
        self.topic = topic
        self.group_id = group_id
        self.consumer_id = consumer_id or f"consumer-{uuid.uuid4().hex[:8]}"

        # Initialize Schema Registry client
        logger.info(f"Connecting to Schema Registry: {schema_registry_url}")
        self.schema_registry_client = SchemaRegistryClient({
            'url': schema_registry_url
        })

        # Create Avro deserializer
        # The deserializer will automatically fetch the schema from registry
        self.avro_deserializer = AvroDeserializer(
            self.schema_registry_client,
            from_dict=lambda obj, ctx: obj  # Return dict directly
        )

        # Configure consumer
        consumer_config = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': auto_offset_reset,
            'key.deserializer': StringDeserializer('utf_8'),
            'value.deserializer': self.avro_deserializer,
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 5000,
            'session.timeout.ms': 30000,
            'max.poll.interval.ms': 300000,
        }

        self.consumer = DeserializingConsumer(consumer_config)
        self.consumer.subscribe([topic])

        # Statistics
        self.stats = {
            'total_events': 0,
            'events_by_type': Counter(),
            'events_by_user': Counter(),
            'events_by_device': Counter(),
            'schema_validation_errors': 0,
            'processing_errors': 0,
            'start_time': datetime.now(timezone.utc),
        }

        # Setup graceful shutdown
        self.running = True
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        logger.info(f"Avro consumer initialized: {self.consumer_id}")
        logger.info(f"Topic: {topic}, Group: {group_id}")

    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single event.

        Args:
            event: Deserialized event dictionary

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Validate required fields
            if not event:
                logger.warning("Received empty event")
                return False

            event_id = event.get('event_id', 'unknown')
            user_id = event.get('user_id', 'unknown')
            event_type = event.get('event_type', 'UNKNOWN')
            timestamp = event.get('timestamp')
            device_type = event.get('device_type')

            # Update statistics
            self.stats['total_events'] += 1
            self.stats['events_by_type'][event_type] += 1
            self.stats['events_by_user'][user_id] += 1
            if device_type:
                self.stats['events_by_device'][device_type] += 1

            # Log event details
            logger.debug(
                f"Processed event: id={event_id}, type={event_type}, "
                f"user={user_id}, device={device_type}"
            )

            # Process event-specific logic
            self._process_event_by_type(event)

            return True

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            self.stats['processing_errors'] += 1
            return False

    def _process_event_by_type(self, event: Dict[str, Any]):
        """Process event based on its type."""
        event_type = event.get('event_type')
        properties = event.get('properties', {})

        if event_type == 'PURCHASE':
            amount = properties.get('amount')
            product_id = properties.get('product_id')
            if amount:
                logger.info(
                    f"Purchase event: user={event.get('user_id')}, "
                    f"product={product_id}, amount=${amount}"
                )

        elif event_type == 'SEARCH':
            query = properties.get('query')
            results = properties.get('results_count')
            if query:
                logger.debug(f"Search event: query='{query}', results={results}")

        elif event_type == 'LOGIN':
            logger.info(f"User login: {event.get('user_id')}")

        elif event_type == 'LOGOUT':
            logger.info(f"User logout: {event.get('user_id')}")

    def consume(
        self,
        max_messages: Optional[int] = None,
        timeout: float = 1.0,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Start consuming messages.

        Args:
            max_messages: Maximum number of messages to process (None for unlimited)
            timeout: Consumer poll timeout in seconds
            callback: Optional callback function for each event
        """
        logger.info(f"Starting Avro consumer: {self.consumer_id}")
        logger.info(f"Consuming from topic: {self.topic}")
        messages_processed = 0

        try:
            while self.running:
                # Poll for message
                msg = self.consumer.poll(timeout=timeout)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.debug(
                            f"Reached end of partition {msg.partition()} "
                            f"at offset {msg.offset()}"
                        )
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                    continue

                try:
                    # Get deserialized value
                    event = msg.value()

                    if event is None:
                        logger.warning("Received null message value")
                        continue

                    # Process event
                    success = self.process_event(event)

                    # Call custom callback if provided
                    if callback and success:
                        callback(event)

                    messages_processed += 1

                    # Log progress
                    if messages_processed % 100 == 0:
                        self._print_progress(messages_processed)

                    # Check message limit
                    if max_messages and messages_processed >= max_messages:
                        logger.info(f"Reached message limit: {max_messages}")
                        break

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    self.stats['processing_errors'] += 1

        except KeyboardInterrupt:
            logger.info("Interrupted by user")

        finally:
            self._print_final_stats(messages_processed)
            self.close()

    def _print_progress(self, count: int):
        """Print consumption progress."""
        elapsed = (datetime.now(timezone.utc) - self.stats['start_time']).total_seconds()
        rate = count / elapsed if elapsed > 0 else 0
        logger.info(
            f"Progress: {count} messages processed "
            f"({rate:.2f} msg/sec)"
        )

    def _print_final_stats(self, total_processed: int):
        """Print final consumption statistics."""
        elapsed = (datetime.now(timezone.utc) - self.stats['start_time']).total_seconds()
        rate = total_processed / elapsed if elapsed > 0 else 0

        logger.info("\n" + "=" * 60)
        logger.info("CONSUMPTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Consumer ID: {self.consumer_id}")
        logger.info(f"Topic: {self.topic}")
        logger.info(f"Group: {self.group_id}")
        logger.info("-" * 60)
        logger.info(f"Total Messages: {total_processed}")
        logger.info(f"Duration: {elapsed:.2f}s")
        logger.info(f"Throughput: {rate:.2f} msg/sec")
        logger.info(f"Processing Errors: {self.stats['processing_errors']}")
        logger.info(f"Schema Validation Errors: {self.stats['schema_validation_errors']}")

        logger.info("\nEvents by Type:")
        for event_type, count in self.stats['events_by_type'].most_common(10):
            logger.info(f"  {event_type}: {count}")

        logger.info("\nTop Users:")
        for user_id, count in self.stats['events_by_user'].most_common(5):
            logger.info(f"  {user_id}: {count} events")

        logger.info("\nEvents by Device:")
        for device, count in self.stats['events_by_device'].most_common():
            logger.info(f"  {device}: {count}")

        logger.info("=" * 60)

    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the registered schema."""
        try:
            # Get latest schema for the topic
            subject = f"{self.topic}-value"
            schema_metadata = self.schema_registry_client.get_latest_version(subject)

            return {
                'subject': subject,
                'schema_id': schema_metadata.schema_id,
                'version': schema_metadata.version,
                'schema_type': schema_metadata.schema.schema_type,
            }
        except Exception as e:
            logger.error(f"Error fetching schema info: {e}")
            return {}

    def close(self):
        """Close consumer and release resources."""
        logger.info("Closing Avro consumer...")
        self.consumer.close()
        logger.info("Consumer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AvroAggregatingConsumer(AvroEventConsumer):
    """Avro consumer with real-time aggregation capabilities."""

    def __init__(
        self,
        *args,
        window_seconds: int = 60,
        **kwargs
    ):
        """
        Initialize aggregating consumer.

        Args:
            window_seconds: Time window for aggregation in seconds
        """
        super().__init__(*args, **kwargs)
        self.window_seconds = window_seconds
        self.window_start = datetime.now(timezone.utc)
        self.window_data = defaultdict(lambda: defaultdict(float))

    def process_event(self, event: Dict[str, Any]) -> bool:
        """Process event and aggregate data."""
        # Check if we need to flush the window
        now = datetime.now(timezone.utc)
        if (now - self.window_start).total_seconds() >= self.window_seconds:
            self._flush_window()
            self.window_start = now

        # Aggregate event data
        event_type = event.get('event_type', 'UNKNOWN')
        user_id = event.get('user_id', 'unknown')
        properties = event.get('properties', {})

        self.window_data['by_type'][event_type] += 1
        self.window_data['by_user'][user_id] += 1

        # Track purchase revenue
        if event_type == 'PURCHASE':
            amount_str = properties.get('amount', '0')
            try:
                amount = float(amount_str)
                self.window_data['revenue']['total'] += amount
                self.window_data['revenue']['count'] += 1
            except (ValueError, TypeError):
                pass

        return super().process_event(event)

    def _flush_window(self):
        """Flush aggregated window data."""
        if not self.window_data:
            return

        logger.info("\n" + "=" * 60)
        logger.info(f"WINDOW SUMMARY ({self.window_seconds}s)")
        logger.info("=" * 60)

        # Event type distribution
        logger.info("\nEvent Types:")
        for event_type, count in sorted(
            self.window_data['by_type'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            logger.info(f"  {event_type}: {int(count)}")

        # Top active users
        logger.info("\nTop Active Users:")
        top_users = sorted(
            self.window_data['by_user'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for user_id, count in top_users:
            logger.info(f"  {user_id}: {int(count)} events")

        # Revenue metrics
        if self.window_data['revenue']['count'] > 0:
            total_revenue = self.window_data['revenue']['total']
            num_purchases = self.window_data['revenue']['count']
            avg_purchase = total_revenue / num_purchases

            logger.info("\nRevenue Metrics:")
            logger.info(f"  Total Revenue: ${total_revenue:.2f}")
            logger.info(f"  Number of Purchases: {int(num_purchases)}")
            logger.info(f"  Average Purchase: ${avg_purchase:.2f}")

        logger.info("=" * 60 + "\n")

        # Reset window data
        self.window_data = defaultdict(lambda: defaultdict(float))


def main():
    """CLI for Avro event consumer."""
    parser = argparse.ArgumentParser(
        description='Avro Event Consumer with Schema Registry'
    )
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers'
    )
    parser.add_argument(
        '--schema-registry',
        default='http://localhost:8081',
        help='Schema Registry URL'
    )
    parser.add_argument(
        '--topic',
        default='user-events-avro',
        help='Kafka topic'
    )
    parser.add_argument(
        '--group-id',
        default='avro-consumer-group',
        help='Consumer group ID'
    )
    parser.add_argument(
        '--max-messages',
        type=int,
        help='Maximum number of messages to process'
    )
    parser.add_argument(
        '--aggregate',
        action='store_true',
        help='Use aggregating consumer'
    )
    parser.add_argument(
        '--window',
        type=int,
        default=60,
        help='Aggregation window in seconds'
    )
    parser.add_argument(
        '--consumer-id',
        help='Consumer identifier'
    )

    args = parser.parse_args()

    logger.info("Starting Avro Event Consumer")
    logger.info(f"Bootstrap servers: {args.bootstrap_servers}")
    logger.info(f"Schema Registry: {args.schema_registry}")
    logger.info(f"Topic: {args.topic}")
    logger.info(f"Group ID: {args.group_id}")

    try:
        # Choose consumer class
        if args.aggregate:
            consumer_class = AvroAggregatingConsumer
            kwargs = {'window_seconds': args.window}
        else:
            consumer_class = AvroEventConsumer
            kwargs = {}

        with consumer_class(
            bootstrap_servers=args.bootstrap_servers,
            schema_registry_url=args.schema_registry,
            topic=args.topic,
            group_id=args.group_id,
            consumer_id=args.consumer_id,
            **kwargs
        ) as consumer:
            # Print schema info
            schema_info = consumer.get_schema_info()
            if schema_info:
                logger.info(f"Schema Info: {schema_info}")

            # Start consuming
            consumer.consume(max_messages=args.max_messages)

    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()

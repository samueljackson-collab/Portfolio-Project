#!/usr/bin/env python3
"""Avro producer with Schema Registry integration."""
from __future__ import annotations

import json
import logging
import argparse
import uuid
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AvroEventProducer:
    """
    Avro event producer with Schema Registry.

    Produces events to Kafka using Avro serialization with schema validation
    via Confluent Schema Registry.
    """

    def __init__(
        self,
        bootstrap_servers: str = 'localhost:9092',
        schema_registry_url: str = 'http://localhost:8081',
        topic: str = 'user-events-avro',
        producer_id: Optional[str] = None
    ):
        """
        Initialize Avro producer.

        Args:
            bootstrap_servers: Kafka bootstrap servers
            schema_registry_url: Schema Registry URL
            topic: Kafka topic
            producer_id: Producer identifier
        """
        self.topic = topic
        self.producer_id = producer_id or f"producer-{uuid.uuid4().hex[:8]}"

        # Initialize Schema Registry client
        logger.info(f"Connecting to Schema Registry: {schema_registry_url}")
        self.schema_registry_client = SchemaRegistryClient({
            'url': schema_registry_url
        })

        # Load Avro schema
        schema_path = Path(__file__).parent.parent / 'schemas' / 'user_event.avsc'
        with open(schema_path, 'r') as f:
            schema_str = f.read()

        # Create Avro serializer
        self.avro_serializer = AvroSerializer(
            self.schema_registry_client,
            schema_str
        )

        # Configure producer
        producer_config = {
            'bootstrap.servers': bootstrap_servers,
            'key.serializer': StringSerializer('utf_8'),
            'value.serializer': self.avro_serializer,
            'acks': 'all',
            'enable.idempotence': True,
            'max.in.flight.requests.per.connection': 5,
            'compression.type': 'snappy',
            'batch.size': 16384,
            'linger.ms': 10,
        }

        self.producer = SerializingProducer(producer_config)

        logger.info(f"Avro producer initialized: {self.producer_id}")
        logger.info(f"Topic: {topic}")
        logger.info(f"Schema loaded from: {schema_path}")

    def _delivery_callback(self, err, msg):
        """Kafka delivery callback."""
        if err:
            logger.error(f"Delivery failed: {err}")
        else:
            logger.debug(
                f"Event delivered to {msg.topic()} "
                f"[{msg.partition()}] @ offset {msg.offset()}"
            )

    def create_event(
        self,
        user_id: str,
        event_type: str,
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Create an event dictionary conforming to Avro schema.

        Args:
            user_id: User identifier
            event_type: Type of event
            session_id: Optional session ID
            properties: Additional event properties

        Returns:
            Event dictionary
        """
        event_types = [
            'PAGE_VIEW', 'CLICK', 'PURCHASE', 'ADD_TO_CART',
            'SEARCH', 'LOGIN', 'LOGOUT', 'REGISTRATION'
        ]

        if event_type.upper() not in event_types:
            event_type = random.choice(event_types)
        else:
            event_type = event_type.upper()

        # Generate event
        event = {
            'event_id': str(uuid.uuid4()),
            'user_id': user_id,
            'session_id': session_id,
            'event_type': event_type,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'page_url': f"/page/{random.randint(1, 10)}",
            'referrer': None,
            'user_agent': 'Mozilla/5.0 (compatible; AvroProducer/1.0)',
            'ip_address': f"192.168.1.{random.randint(1, 255)}",
            'device_type': random.choice(['DESKTOP', 'MOBILE', 'TABLET']),
            'properties': properties or {},
            'metadata': {
                'producer_id': self.producer_id,
                'schema_version': '1.0.0',
                'environment': 'PRODUCTION'
            }
        }

        # Add event-specific properties
        if event_type == 'PURCHASE':
            event['properties']['amount'] = str(random.uniform(10.0, 500.0))
            event['properties']['currency'] = 'USD'
            event['properties']['product_id'] = f"prod-{random.randint(1, 100)}"

        elif event_type == 'SEARCH':
            search_terms = ['laptop', 'phone', 'headphones', 'camera', 'watch']
            event['properties']['query'] = random.choice(search_terms)
            event['properties']['results_count'] = str(random.randint(0, 100))

        return event

    def produce_event(
        self,
        user_id: str,
        event_type: str = 'PAGE_VIEW',
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None
    ):
        """
        Produce a single event to Kafka.

        Args:
            user_id: User identifier
            event_type: Type of event
            session_id: Optional session ID
            properties: Additional event properties
        """
        event = self.create_event(user_id, event_type, session_id, properties)

        try:
            # Produce to Kafka with user_id as key (for partitioning)
            self.producer.produce(
                topic=self.topic,
                key=user_id,
                value=event,
                on_delivery=self._delivery_callback
            )

            # Trigger callbacks
            self.producer.poll(0)

        except Exception as e:
            logger.error(f"Error producing event: {e}")
            raise

    def produce_batch(
        self,
        count: int = 100,
        num_users: int = 10,
        delay: float = 0.1
    ):
        """
        Produce a batch of events.

        Args:
            count: Number of events to produce
            num_users: Number of unique users to simulate
            delay: Delay between events in seconds
        """
        logger.info(f"Producing {count} events for {num_users} users...")

        users = [f"user-{i}" for i in range(num_users)]
        event_types = [
            'PAGE_VIEW', 'CLICK', 'PURCHASE', 'ADD_TO_CART',
            'SEARCH', 'LOGIN'
        ]

        produced = 0
        errors = 0

        start_time = time.time()

        try:
            for i in range(count):
                user_id = random.choice(users)
                event_type = random.choice(event_types)
                session_id = f"session-{random.randint(1, 100)}"

                try:
                    self.produce_event(user_id, event_type, session_id)
                    produced += 1

                    if (i + 1) % 100 == 0:
                        logger.info(f"Produced {i + 1}/{count} events...")

                except Exception as e:
                    logger.error(f"Error producing event {i}: {e}")
                    errors += 1

                time.sleep(delay)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")

        finally:
            # Flush remaining messages
            logger.info("Flushing remaining messages...")
            remaining = self.producer.flush(timeout=30)

            duration = time.time() - start_time

            logger.info("\n" + "=" * 60)
            logger.info("Production Summary")
            logger.info("=" * 60)
            logger.info(f"Total events produced: {produced}")
            logger.info(f"Errors: {errors}")
            logger.info(f"Messages remaining in queue: {remaining}")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"Throughput: {produced / duration:.2f} events/sec")
            logger.info("=" * 60)

    def close(self):
        """Close producer and flush remaining messages."""
        logger.info("Closing producer...")
        self.producer.flush()


def main():
    """CLI for Avro event producer."""
    parser = argparse.ArgumentParser(
        description='Avro Event Producer with Schema Registry'
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
        '--count',
        type=int,
        default=100,
        help='Number of events to produce'
    )
    parser.add_argument(
        '--users',
        type=int,
        default=10,
        help='Number of unique users to simulate'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between events (seconds)'
    )
    parser.add_argument(
        '--producer-id',
        help='Producer identifier'
    )

    args = parser.parse_args()

    logger.info("Starting Avro Event Producer")
    logger.info(f"Bootstrap servers: {args.bootstrap_servers}")
    logger.info(f"Schema Registry: {args.schema_registry}")
    logger.info(f"Topic: {args.topic}")

    try:
        producer = AvroEventProducer(
            bootstrap_servers=args.bootstrap_servers,
            schema_registry_url=args.schema_registry,
            topic=args.topic,
            producer_id=args.producer_id
        )

        producer.produce_batch(
            count=args.count,
            num_users=args.users,
            delay=args.delay
        )

        producer.close()

    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        exit(1)


if __name__ == '__main__':
    main()

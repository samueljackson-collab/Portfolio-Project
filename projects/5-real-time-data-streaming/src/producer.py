"""Kafka producer for generating real-time events."""
from __future__ import annotations

import json
import time
import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventProducer:
    """Produces events to Kafka topics."""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        topic: str = 'user-events'
    ):
        """
        Initialize the event producer.

        Args:
            bootstrap_servers: List of Kafka broker addresses
            topic: Default Kafka topic to publish to
        """
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.topic = topic

        # Initialize Kafka producer with retry and exactly-once semantics
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            retries=3,
            max_in_flight_requests_per_connection=1,  # Ensure ordering
            enable_idempotence=True,  # Exactly-once semantics
            compression_type='gzip'
        )

        logger.info(f"Producer initialized for topic '{topic}' on {self.bootstrap_servers}")

    def send_event(
        self,
        event_type: str,
        user_id: str,
        data: Dict[str, Any],
        partition_key: Optional[str] = None
    ) -> bool:
        """
        Send an event to Kafka.

        Args:
            event_type: Type of event (page_view, click, purchase, etc.)
            user_id: User identifier
            data: Event payload
            partition_key: Optional key for partitioning

        Returns:
            True if successful, False otherwise
        """
        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'data': data,
            'version': '1.0'
        }

        # Use user_id as partition key if not provided
        key = partition_key or user_id

        try:
            future = self.producer.send(
                self.topic,
                value=event,
                key=key
            )

            # Wait for confirmation (synchronous send)
            record_metadata = future.get(timeout=10)

            logger.debug(
                f"Event sent: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )

            return True

        except KafkaError as e:
            logger.error(f"Failed to send event: {e}")
            return False

    def simulate_user_events(self, count: int = 100, delay: float = 0.1):
        """
        Simulate user events for testing.

        Args:
            count: Number of events to generate
            delay: Delay between events in seconds
        """
        event_types = [
            'page_view',
            'button_click',
            'form_submit',
            'purchase',
            'add_to_cart',
            'remove_from_cart',
            'search',
            'login',
            'logout',
            'signup'
        ]

        pages = [
            '/', '/products', '/about', '/contact',
            '/checkout', '/cart', '/profile', '/settings'
        ]

        successful = 0
        failed = 0

        logger.info(f"Starting simulation of {count} events...")

        for i in range(count):
            event_type = random.choice(event_types)
            user_id = f"user_{random.randint(1, 1000)}"

            # Generate event-specific data
            data: Dict[str, Any] = {
                'session_id': f"session_{random.randint(1, 100)}",
                'device': random.choice(['mobile', 'desktop', 'tablet']),
                'browser': random.choice(['chrome', 'firefox', 'safari', 'edge'])
            }

            if event_type == 'page_view':
                data['page'] = random.choice(pages)
                data['referrer'] = random.choice(pages + ['external'])

            elif event_type in ['button_click', 'form_submit']:
                data['element_id'] = f"button_{random.randint(1, 20)}"
                data['page'] = random.choice(pages)

            elif event_type == 'purchase':
                data['product_id'] = f"prod_{random.randint(1, 100)}"
                data['amount'] = round(random.uniform(10, 500), 2)
                data['currency'] = 'USD'

            elif event_type in ['add_to_cart', 'remove_from_cart']:
                data['product_id'] = f"prod_{random.randint(1, 100)}"
                data['quantity'] = random.randint(1, 5)

            elif event_type == 'search':
                data['query'] = random.choice([
                    'laptop', 'phone', 'headphones', 'camera',
                    'keyboard', 'mouse', 'monitor', 'tablet'
                ])
                data['results_count'] = random.randint(0, 50)

            # Send event
            if self.send_event(event_type, user_id, data):
                successful += 1
            else:
                failed += 1

            if (i + 1) % 100 == 0:
                logger.info(f"Progress: {i + 1}/{count} events sent")

            time.sleep(delay)

        logger.info(
            f"Simulation complete: {successful} successful, "
            f"{failed} failed out of {count} total events"
        )

    def simulate_high_volume_stream(self, duration_seconds: int = 60, events_per_second: int = 100):
        """
        Simulate high-volume event stream.

        Args:
            duration_seconds: How long to run the simulation
            events_per_second: Target events per second
        """
        delay = 1.0 / events_per_second
        total_events = duration_seconds * events_per_second

        logger.info(
            f"Starting high-volume simulation: {events_per_second} events/sec "
            f"for {duration_seconds} seconds"
        )

        start_time = time.time()
        self.simulate_user_events(count=total_events, delay=delay)
        elapsed = time.time() - start_time

        actual_rate = total_events / elapsed
        logger.info(
            f"Actual throughput: {actual_rate:.2f} events/sec "
            f"(target: {events_per_second} events/sec)"
        )

    def flush(self):
        """Flush any pending messages."""
        self.producer.flush()
        logger.info("Producer flushed")

    def close(self):
        """Close the producer and release resources."""
        self.producer.flush()
        self.producer.close()
        logger.info("Producer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Kafka Event Producer')
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers (comma-separated)'
    )
    parser.add_argument(
        '--topic',
        default='user-events',
        help='Kafka topic to publish to'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1000,
        help='Number of events to generate'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between events in seconds'
    )
    parser.add_argument(
        '--high-volume',
        action='store_true',
        help='Run high-volume simulation'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Duration for high-volume simulation (seconds)'
    )
    parser.add_argument(
        '--rate',
        type=int,
        default=100,
        help='Events per second for high-volume simulation'
    )

    args = parser.parse_args()

    bootstrap_servers = args.bootstrap_servers.split(',')

    with EventProducer(bootstrap_servers=bootstrap_servers, topic=args.topic) as producer:
        if args.high_volume:
            producer.simulate_high_volume_stream(
                duration_seconds=args.duration,
                events_per_second=args.rate
            )
        else:
            producer.simulate_user_events(count=args.count, delay=args.delay)

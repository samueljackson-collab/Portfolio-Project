"""Kafka consumer for processing real-time events."""
from __future__ import annotations

import json
import logging
import signal
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable

from kafka import KafkaConsumer
from kafka.errors import KafkaError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes and processes events from Kafka topics."""

    def __init__(
        self,
        bootstrap_servers: List[str] = None,
        topic: str = 'user-events',
        group_id: str = 'event-consumer-group',
        auto_offset_reset: str = 'earliest'
    ):
        """
        Initialize the event consumer.

        Args:
            bootstrap_servers: List of Kafka broker addresses
            topic: Kafka topic to consume from
            group_id: Consumer group ID
            auto_offset_reset: Where to start reading ('earliest' or 'latest')
        """
        self.bootstrap_servers = bootstrap_servers or ['localhost:9092']
        self.topic = topic
        self.group_id = group_id

        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            auto_commit_interval_ms=5000,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda m: m.decode('utf-8') if m else None,
            max_poll_records=500,
            session_timeout_ms=30000
        )

        # Statistics
        self.stats = {
            'total_events': 0,
            'events_by_type': Counter(),
            'events_by_user': Counter(),
            'start_time': datetime.utcnow(),
            'errors': 0
        }

        # Setup graceful shutdown
        self.running = True
        signal.signal(signal.SIGINT, self._shutdown_handler)
        signal.signal(signal.SIGTERM, self._shutdown_handler)

        logger.info(
            f"Consumer initialized: topic='{topic}', "
            f"group='{group_id}', servers={self.bootstrap_servers}"
        )

    def _shutdown_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def process_event(self, event: Dict[str, Any]) -> bool:
        """
        Process a single event. Override this method for custom processing.

        Args:
            event: Event data

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Update statistics
            self.stats['total_events'] += 1
            self.stats['events_by_type'][event.get('event_type', 'unknown')] += 1
            self.stats['events_by_user'][event.get('user_id', 'unknown')] += 1

            # Log event (customize based on needs)
            logger.debug(
                f"Processed event: type={event.get('event_type')}, "
                f"user={event.get('user_id')}"
            )

            return True

        except Exception as e:
            logger.error(f"Error processing event: {e}")
            self.stats['errors'] += 1
            return False

    def consume(
        self,
        max_messages: Optional[int] = None,
        timeout_ms: int = 1000,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Start consuming messages.

        Args:
            max_messages: Maximum number of messages to process (None for unlimited)
            timeout_ms: Consumer poll timeout in milliseconds
            callback: Optional callback function for each event
        """
        logger.info("Starting to consume events...")
        messages_processed = 0

        try:
            while self.running:
                # Poll for messages
                message_batch = self.consumer.poll(timeout_ms=timeout_ms)

                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        try:
                            event = message.value

                            # Process event
                            self.process_event(event)

                            # Call custom callback if provided
                            if callback:
                                callback(event)

                            messages_processed += 1

                            # Check if we've hit the message limit
                            if max_messages and messages_processed >= max_messages:
                                logger.info(f"Reached message limit: {max_messages}")
                                self.running = False
                                break

                        except Exception as e:
                            logger.error(f"Error processing message: {e}")
                            self.stats['errors'] += 1

                    if not self.running:
                        break

                # Print periodic stats
                if messages_processed > 0 and messages_processed % 1000 == 0:
                    self._print_stats()

        except KeyboardInterrupt:
            logger.info("Interrupted by user")

        finally:
            self._print_stats()
            self.close()

        logger.info(f"Consumed {messages_processed} messages")

    def _print_stats(self):
        """Print consumption statistics."""
        elapsed = (datetime.utcnow() - self.stats['start_time']).total_seconds()
        rate = self.stats['total_events'] / elapsed if elapsed > 0 else 0

        logger.info("=" * 60)
        logger.info(f"Total Events: {self.stats['total_events']}")
        logger.info(f"Elapsed Time: {elapsed:.2f}s")
        logger.info(f"Event Rate: {rate:.2f} events/sec")
        logger.info(f"Errors: {self.stats['errors']}")

        logger.info("\nTop Event Types:")
        for event_type, count in self.stats['events_by_type'].most_common(5):
            logger.info(f"  {event_type}: {count}")

        logger.info("\nTop Users:")
        for user_id, count in self.stats['events_by_user'].most_common(5):
            logger.info(f"  {user_id}: {count}")

        logger.info("=" * 60)

    def close(self):
        """Close the consumer and release resources."""
        self.consumer.close()
        logger.info("Consumer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AggregatingConsumer(EventConsumer):
    """Consumer that aggregates events in real-time."""

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
        self.window_start = datetime.utcnow()
        self.window_data = defaultdict(lambda: defaultdict(int))

    def process_event(self, event: Dict[str, Any]) -> bool:
        """Process event and aggregate data."""
        # Check if we need to flush the window
        now = datetime.utcnow()
        if (now - self.window_start).total_seconds() >= self.window_seconds:
            self._flush_window()
            self.window_start = now

        # Aggregate event data
        event_type = event.get('event_type', 'unknown')
        user_id = event.get('user_id', 'unknown')

        self.window_data['by_type'][event_type] += 1
        self.window_data['by_user'][user_id] += 1

        # Track purchase amounts
        if event_type == 'purchase':
            amount = event.get('data', {}).get('amount', 0)
            self.window_data['revenue']['total'] += amount
            self.window_data['revenue']['count'] += 1

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
            logger.info(f"  {event_type}: {count}")

        # Top active users
        logger.info("\nTop Active Users:")
        top_users = sorted(
            self.window_data['by_user'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for user_id, count in top_users:
            logger.info(f"  {user_id}: {count} events")

        # Revenue metrics
        if self.window_data['revenue']['count'] > 0:
            total_revenue = self.window_data['revenue']['total']
            num_purchases = self.window_data['revenue']['count']
            avg_purchase = total_revenue / num_purchases

            logger.info("\nRevenue Metrics:")
            logger.info(f"  Total Revenue: ${total_revenue:.2f}")
            logger.info(f"  Number of Purchases: {num_purchases}")
            logger.info(f"  Average Purchase: ${avg_purchase:.2f}")

        logger.info("=" * 60 + "\n")

        # Reset window data
        self.window_data = defaultdict(lambda: defaultdict(int))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Kafka Event Consumer')
    parser.add_argument(
        '--bootstrap-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers (comma-separated)'
    )
    parser.add_argument(
        '--topic',
        default='user-events',
        help='Kafka topic to consume from'
    )
    parser.add_argument(
        '--group-id',
        default='event-consumer-group',
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

    args = parser.parse_args()

    bootstrap_servers = args.bootstrap_servers.split(',')

    # Choose consumer type
    if args.aggregate:
        consumer_class = AggregatingConsumer
        kwargs = {'window_seconds': args.window}
    else:
        consumer_class = EventConsumer
        kwargs = {}

    with consumer_class(
        bootstrap_servers=bootstrap_servers,
        topic=args.topic,
        group_id=args.group_id,
        **kwargs
    ) as consumer:
        consumer.consume(max_messages=args.max_messages)

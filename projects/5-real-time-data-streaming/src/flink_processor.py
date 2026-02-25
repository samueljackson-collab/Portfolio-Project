"""Apache Flink stream processing job for real-time analytics."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Tuple

try:
    from pyflink.datastream import StreamExecutionEnvironment, TimeCharacteristic
    from pyflink.datastream.window import TumblingEventTimeWindows, Time
    from pyflink.common import WatermarkStrategy, Duration
    from pyflink.common.serialization import SimpleStringSchema
    from pyflink.datastream.connectors.kafka import (
        KafkaSource,
        KafkaSink,
        KafkaRecordSerializationSchema
    )
    from pyflink.common.typeinfo import Types
    _PYFLINK_AVAILABLE = True
except ImportError:
    _PYFLINK_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FlinkEventProcessor:
    """Flink-based stream processing for user events."""

    def __init__(
        self,
        kafka_bootstrap_servers: str = 'localhost:9092',
        input_topic: str = 'user-events',
        output_topic: str = 'event-analytics',
        checkpoint_interval: int = 60000
    ):
        """
        Initialize Flink stream processor.

        Args:
            kafka_bootstrap_servers: Kafka broker addresses
            input_topic: Input Kafka topic
            output_topic: Output Kafka topic for results
            checkpoint_interval: Checkpoint interval in milliseconds
        """
        self.kafka_servers = kafka_bootstrap_servers
        self.input_topic = input_topic
        self.output_topic = output_topic
        self.checkpoint_interval = checkpoint_interval

        # Create execution environment
        self.env = StreamExecutionEnvironment.get_execution_environment()

        # Enable checkpointing for fault tolerance
        self.env.enable_checkpointing(checkpoint_interval)

        # Configure RocksDB state backend for large state
        from pyflink.datastream.state_backend import RocksDBStateBackend
        from pyflink.datastream.checkpoint_config import CheckpointingMode

        # Set RocksDB as state backend
        state_backend = RocksDBStateBackend(
            "file:///tmp/flink-checkpoints",
            enable_incremental_checkpointing=True
        )
        self.env.set_state_backend(state_backend)

        # Configure checkpoint settings
        checkpoint_config = self.env.get_checkpoint_config()
        checkpoint_config.set_checkpointing_mode(CheckpointingMode.EXACTLY_ONCE)
        checkpoint_config.set_min_pause_between_checkpoints(5000)
        checkpoint_config.set_checkpoint_timeout(600000)
        checkpoint_config.set_max_concurrent_checkpoints(1)

        # Set parallelism
        self.env.set_parallelism(2)

        logger.info(
            f"Flink processor initialized: input={input_topic}, "
            f"output={output_topic}, state_backend=RocksDB"
        )

    def setup_kafka_source(self) -> KafkaSource:
        """Configure Kafka source connector."""
        kafka_source = KafkaSource.builder() \
            .set_bootstrap_servers(self.kafka_servers) \
            .set_topics(self.input_topic) \
            .set_group_id('flink-consumer-group') \
            .set_starting_offsets_earliest() \
            .set_value_only_deserializer(SimpleStringSchema()) \
            .build()

        return kafka_source

    def setup_kafka_sink(self) -> KafkaSink:
        """Configure Kafka sink connector."""
        kafka_sink = KafkaSink.builder() \
            .set_bootstrap_servers(self.kafka_servers) \
            .set_record_serializer(
                KafkaRecordSerializationSchema.builder()
                .set_topic(self.output_topic)
                .set_value_serialization_schema(SimpleStringSchema())
                .build()
            ) \
            .build()

        return kafka_sink

    @staticmethod
    def parse_event(event_json: str) -> Tuple:
        """
        Parse JSON event string.

        Args:
            event_json: JSON string of event

        Returns:
            Tuple of (timestamp, event_type, user_id, data)
        """
        try:
            event = json.loads(event_json)
            return (
                event.get('timestamp', ''),
                event.get('event_type', 'unknown'),
                event.get('user_id', 'unknown'),
                json.dumps(event.get('data', {}))
            )
        except Exception as e:
            logger.error(f"Failed to parse event: {e}")
            return ('', 'error', 'unknown', '{}')

    @staticmethod
    def count_by_event_type(events) -> str:
        """
        Aggregate events by type.

        Args:
            events: Iterable of events

        Returns:
            JSON string of aggregated counts
        """
        event_counts = {}
        total = 0

        for event in events:
            _, event_type, _, _ = event
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            total += 1

        result = {
            'window_end': datetime.now(timezone.utc).isoformat(),
            'total_events': total,
            'by_type': event_counts
        }

        return json.dumps(result)

    @staticmethod
    def calculate_revenue_metrics(events) -> str:
        """
        Calculate revenue metrics from purchase events.

        Args:
            events: Iterable of events

        Returns:
            JSON string of revenue metrics
        """
        total_revenue = 0.0
        purchase_count = 0
        unique_users = set()

        for event in events:
            _, event_type, user_id, data_json = event

            if event_type == 'purchase':
                try:
                    data = json.loads(data_json)
                    amount = data.get('amount', 0)
                    total_revenue += amount
                    purchase_count += 1
                    unique_users.add(user_id)
                except Exception:
                    pass

        avg_purchase = total_revenue / purchase_count if purchase_count > 0 else 0

        result = {
            'window_end': datetime.now(timezone.utc).isoformat(),
            'metric_type': 'revenue',
            'total_revenue': round(total_revenue, 2),
            'purchase_count': purchase_count,
            'unique_customers': len(unique_users),
            'average_purchase': round(avg_purchase, 2)
        }

        return json.dumps(result)

    def run_event_count_job(self):
        """Run job that counts events by type in 1-minute windows."""
        logger.info("Starting event count job...")

        # Setup source and sink
        kafka_source = self.setup_kafka_source()
        kafka_sink = self.setup_kafka_sink()

        # Create data stream
        stream = self.env.from_source(
            kafka_source,
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5)),
            "kafka-source"
        )

        # Parse events
        parsed_stream = stream.map(
            lambda x: self.parse_event(x),
            output_type=Types.TUPLE([Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING()])
        )

        # Window and aggregate
        windowed = parsed_stream \
            .key_by(lambda x: "all") \
            .window(TumblingEventTimeWindows.of(Time.minutes(1))) \
            .apply(
                lambda key, window, events: self.count_by_event_type(events),
                output_type=Types.STRING()
            )

        # Sink to output topic
        windowed.sink_to(kafka_sink)

        # Execute
        self.env.execute("Event Count Job")

    def run_revenue_tracking_job(self):
        """Run job that tracks revenue metrics in real-time."""
        logger.info("Starting revenue tracking job...")

        # Setup source and sink
        kafka_source = self.setup_kafka_source()
        kafka_sink = self.setup_kafka_sink()

        # Create data stream
        stream = self.env.from_source(
            kafka_source,
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5)),
            "kafka-source"
        )

        # Parse events
        parsed_stream = stream.map(
            lambda x: self.parse_event(x),
            output_type=Types.TUPLE([Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING()])
        )

        # Filter for purchase events
        purchase_stream = parsed_stream.filter(lambda x: x[1] == 'purchase')

        # Window and calculate metrics
        windowed = purchase_stream \
            .key_by(lambda x: "all") \
            .window(TumblingEventTimeWindows.of(Time.minutes(5))) \
            .apply(
                lambda key, window, events: self.calculate_revenue_metrics(events),
                output_type=Types.STRING()
            )

        # Sink to output topic
        windowed.sink_to(kafka_sink)

        # Execute
        self.env.execute("Revenue Tracking Job")

    def run_user_session_analysis(self):
        """Run job that analyzes user session behavior."""
        logger.info("Starting user session analysis job...")

        # Setup source and sink
        kafka_source = self.setup_kafka_source()
        kafka_sink = self.setup_kafka_sink()

        # Create data stream
        stream = self.env.from_source(
            kafka_source,
            WatermarkStrategy.for_bounded_out_of_orderness(Duration.of_seconds(5)),
            "kafka-source"
        )

        # Parse events
        parsed_stream = stream.map(
            lambda x: self.parse_event(x),
            output_type=Types.TUPLE([Types.STRING(), Types.STRING(), Types.STRING(), Types.STRING()])
        )

        # Group by user and count events per session
        user_activity = parsed_stream \
            .key_by(lambda x: x[2]) \
            .window(TumblingEventTimeWindows.of(Time.minutes(30))) \
            .apply(
                lambda user_id, window, events: json.dumps({
                    'user_id': user_id,
                    'window_end': datetime.now(timezone.utc).isoformat(),
                    'event_count': len(list(events)),
                    'event_types': list(set(e[1] for e in events))
                }),
                output_type=Types.STRING()
            )

        # Sink to output topic
        user_activity.sink_to(kafka_sink)

        # Execute
        self.env.execute("User Session Analysis Job")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Flink Stream Processor')
    parser.add_argument(
        '--kafka-servers',
        default='localhost:9092',
        help='Kafka bootstrap servers'
    )
    parser.add_argument(
        '--input-topic',
        default='user-events',
        help='Input Kafka topic'
    )
    parser.add_argument(
        '--output-topic',
        default='event-analytics',
        help='Output Kafka topic'
    )
    parser.add_argument(
        '--job',
        choices=['event-count', 'revenue', 'sessions'],
        default='event-count',
        help='Job to run'
    )

    args = parser.parse_args()

    processor = FlinkEventProcessor(
        kafka_bootstrap_servers=args.kafka_servers,
        input_topic=args.input_topic,
        output_topic=args.output_topic
    )

    if args.job == 'event-count':
        processor.run_event_count_job()
    elif args.job == 'revenue':
        processor.run_revenue_tracking_job()
    elif args.job == 'sessions':
        processor.run_user_session_analysis()


if __name__ == '__main__':
    main()

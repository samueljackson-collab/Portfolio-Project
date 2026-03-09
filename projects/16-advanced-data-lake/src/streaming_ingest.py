"""Streaming data ingestion using Kafka consumer."""
from __future__ import annotations

import json
import logging
import signal
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty
from typing import Any, Callable, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

try:
    from confluent_kafka import Consumer, KafkaError, KafkaException
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    Consumer = None


@dataclass
class StreamConfig:
    """Configuration for streaming ingestion."""
    bootstrap_servers: str = "localhost:9092"
    group_id: str = "data-lake-ingest"
    topics: List[str] = field(default_factory=lambda: ["events"])
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    batch_size: int = 1000
    batch_timeout_seconds: float = 5.0
    output_path: str = "/data/bronze"
    output_format: str = "json"  # json, parquet


@dataclass
class IngestMetrics:
    """Metrics for streaming ingestion."""
    messages_received: int = 0
    messages_processed: int = 0
    batches_written: int = 0
    errors: int = 0
    last_message_time: Optional[datetime] = None
    start_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        runtime = 0
        if self.start_time:
            runtime = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "messages_received": self.messages_received,
            "messages_processed": self.messages_processed,
            "batches_written": self.batches_written,
            "errors": self.errors,
            "messages_per_second": self.messages_processed / runtime if runtime > 0 else 0,
            "runtime_seconds": runtime,
        }


class StreamingIngestor:
    """Kafka-based streaming data ingestion to bronze layer."""

    def __init__(self, config: StreamConfig):
        self.config = config
        self.metrics = IngestMetrics()
        self._running = False
        self._consumer: Optional[Consumer] = None
        self._batch: List[Dict] = []
        self._batch_start_time: Optional[float] = None
        self._message_handlers: List[Callable] = []
        self._shutdown_event = threading.Event()

    def add_handler(self, handler: Callable[[Dict], Dict]) -> "StreamingIngestor":
        """Add a message transformation handler."""
        self._message_handlers.append(handler)
        return self

    def start(self) -> None:
        """Start the streaming ingestor."""
        if not KAFKA_AVAILABLE:
            raise RuntimeError("confluent-kafka not installed")

        self._running = True
        self.metrics.start_time = datetime.utcnow()

        # Configure consumer
        consumer_config = {
            "bootstrap.servers": self.config.bootstrap_servers,
            "group.id": self.config.group_id,
            "auto.offset.reset": self.config.auto_offset_reset,
            "enable.auto.commit": self.config.enable_auto_commit,
        }

        self._consumer = Consumer(consumer_config)
        self._consumer.subscribe(self.config.topics)

        LOGGER.info(f"Starting streaming ingestor for topics: {self.config.topics}")

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            self._consume_loop()
        finally:
            self._cleanup()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        LOGGER.info(f"Received signal {signum}, initiating shutdown")
        self._running = False
        self._shutdown_event.set()

    def _consume_loop(self) -> None:
        """Main consumption loop."""
        while self._running:
            try:
                msg = self._consumer.poll(timeout=1.0)

                if msg is None:
                    self._check_batch_timeout()
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        LOGGER.error(f"Consumer error: {msg.error()}")
                        self.metrics.errors += 1
                        continue

                self._process_message(msg)

            except KafkaException as e:
                LOGGER.error(f"Kafka exception: {e}")
                self.metrics.errors += 1

    def _process_message(self, msg) -> None:
        """Process a single message."""
        self.metrics.messages_received += 1
        self.metrics.last_message_time = datetime.utcnow()

        try:
            # Decode message
            value = json.loads(msg.value().decode("utf-8"))

            # Add metadata
            value["_kafka_topic"] = msg.topic()
            value["_kafka_partition"] = msg.partition()
            value["_kafka_offset"] = msg.offset()
            value["_ingested_at"] = datetime.utcnow().isoformat()

            # Apply handlers
            for handler in self._message_handlers:
                value = handler(value)

            # Add to batch
            if self._batch_start_time is None:
                self._batch_start_time = time.time()

            self._batch.append(value)
            self.metrics.messages_processed += 1

            # Check if batch is ready
            if len(self._batch) >= self.config.batch_size:
                self._flush_batch()

        except json.JSONDecodeError as e:
            LOGGER.warning(f"Failed to decode message: {e}")
            self.metrics.errors += 1
        except Exception as e:
            LOGGER.error(f"Error processing message: {e}")
            self.metrics.errors += 1

    def _check_batch_timeout(self) -> None:
        """Check if batch should be flushed due to timeout."""
        if self._batch and self._batch_start_time:
            elapsed = time.time() - self._batch_start_time
            if elapsed >= self.config.batch_timeout_seconds:
                self._flush_batch()

    def _flush_batch(self) -> None:
        """Write current batch to bronze layer."""
        if not self._batch:
            return

        try:
            output_path = Path(self.config.output_path)
            output_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"batch_{timestamp}"

            if self.config.output_format == "parquet":
                import pandas as pd
                df = pd.DataFrame(self._batch)
                df.to_parquet(output_path / f"{filename}.parquet", index=False)
            else:
                with open(output_path / f"{filename}.json", "w") as f:
                    for record in self._batch:
                        f.write(json.dumps(record) + "\n")

            self.metrics.batches_written += 1
            LOGGER.info(f"Wrote batch with {len(self._batch)} records")

            # Commit offsets
            if not self.config.enable_auto_commit:
                self._consumer.commit(asynchronous=False)

        except Exception as e:
            LOGGER.error(f"Failed to flush batch: {e}")
            self.metrics.errors += 1

        finally:
            self._batch = []
            self._batch_start_time = None

    def _cleanup(self) -> None:
        """Clean up resources."""
        # Flush remaining batch
        if self._batch:
            self._flush_batch()

        # Close consumer
        if self._consumer:
            self._consumer.close()
            LOGGER.info("Consumer closed")

        LOGGER.info(f"Ingestor stopped. Metrics: {self.metrics.to_dict()}")

    def stop(self) -> None:
        """Stop the ingestor gracefully."""
        self._running = False
        self._shutdown_event.set()

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        return self.metrics.to_dict()


class MockStreamingIngestor:
    """Mock ingestor for testing without Kafka."""

    def __init__(self, config: StreamConfig):
        self.config = config
        self.metrics = IngestMetrics()
        self._running = False
        self._message_queue: Queue = Queue()

    def add_message(self, message: Dict) -> None:
        """Add a message to the queue (for testing)."""
        self._message_queue.put(message)

    def start(self, max_messages: int = 100) -> None:
        """Process messages from the queue."""
        self.metrics.start_time = datetime.utcnow()
        self._running = True
        batch = []

        while self._running and self.metrics.messages_processed < max_messages:
            try:
                msg = self._message_queue.get(timeout=1.0)
                msg["_ingested_at"] = datetime.utcnow().isoformat()
                batch.append(msg)
                self.metrics.messages_received += 1
                self.metrics.messages_processed += 1

                if len(batch) >= self.config.batch_size:
                    self._write_batch(batch)
                    batch = []

            except Empty:
                if batch:
                    self._write_batch(batch)
                    batch = []
                continue

        if batch:
            self._write_batch(batch)

    def _write_batch(self, batch: List[Dict]) -> None:
        """Write batch to output."""
        output_path = Path(self.config.output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")

        with open(output_path / f"batch_{timestamp}.json", "w") as f:
            for record in batch:
                f.write(json.dumps(record) + "\n")

        self.metrics.batches_written += 1
        LOGGER.info(f"Wrote mock batch with {len(batch)} records")

    def stop(self) -> None:
        self._running = False

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics.to_dict()


def create_ingestor(config: StreamConfig) -> StreamingIngestor:
    """Factory to create appropriate ingestor."""
    if KAFKA_AVAILABLE:
        return StreamingIngestor(config)
    else:
        LOGGER.warning("Kafka not available, using mock ingestor")
        return MockStreamingIngestor(config)

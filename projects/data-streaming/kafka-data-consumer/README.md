# Kafka Data Consumer

## Overview
Companion service to the producer that processes Kafka events, applies transformations, and forwards data to downstream systems (PostgreSQL, Elasticsearch, or REST webhooks).

## Architecture
- Python (FastAPI + `aiokafka`) or optional Rust variant for high-performance ingestion.
- Supports multiple sinks: database writer, REST forwarder, metrics aggregator.
- Idempotent processing using offset checkpoints stored in Redis or Kafka consumer groups.

## Features
- Dead-letter queue handling with retry strategies.
- Schema validation, PII masking, and data quality checks.
- Observability with Prometheus metrics and OpenTelemetry tracing.

## Usage
1. Install dependencies: `poetry install`.
2. Configure `config/consumer.yaml` for topics, sink types, and backpressure settings.
3. Start service: `poetry run consumer --config config/consumer.yaml`.
4. Optional API mode: `uvicorn app.main:app` exposes health + control plane endpoints.

## Testing & Reliability
- Contract tests verifying schema compatibility with upstream producers.
- Chaos experiments injecting broker outages and latency.
- Benchmarking harness using `kafka-producer-perf-test` for throughput validation.


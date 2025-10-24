# Kafka Data Producer

## Overview
Python-based streaming producer that emits task events, telemetry, and synthetic load to Kafka topics. Supports pluggable schemas and workload profiles for benchmarking downstream systems.

## Architecture
- Asyncio application using `aiokafka` for high-throughput publishing.
- Schema registry integration (Confluent/Redpanda) with Avro/JSON schemas versioned under `schemas/`.
- Workload profiles defined in YAML (e.g., bursty, steady-state, failure injection).

## Usage
1. Install dependencies: `poetry install`.
2. Configure brokers and security (SASL/SCRAM or TLS) in `config/producer.yaml`.
3. Run locally with dockerized Kafka via `docker compose -f compose.kafka.yml up -d`.
4. Start producer: `poetry run producer --config config/producer.yaml`.
5. Monitor metrics via Prometheus exporter on port 9200.

## Testing
- Unit tests mock Kafka to validate batching and retry logic.
- Integration tests executed against local cluster verifying schema compatibility.
- Load test scenarios captured in `tests/load/` using Locust or custom scripts.

## Operations
- Supports dynamic reconfiguration via SIGHUP or API for tuning throughput.
- Emits dead-letter queue events for failed serializations.
- Provides Grafana dashboards and alert thresholds for publish latency, error rate.


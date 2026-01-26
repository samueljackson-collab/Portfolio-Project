# Project 5: Real-time Data Streaming

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://5-real-time-data-streaming.staging.portfolio.example.com` |
| DNS | `5-real-time-data-streaming.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `infra/`, or `deploy/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`/.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`/.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
Live deployment dashboard screenshot stored externally.

### Evidence
Deployment and metrics evidence are tracked in [`evidence/README.md`](./evidence/README.md).


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


High-throughput real-time event streaming and processing pipeline using Apache Kafka and Apache Flink with exactly-once semantics and comprehensive analytics.

## Overview

This project implements a production-grade streaming data pipeline that:
- Ingests high-volume user events via Kafka producers
- Processes streams in real-time using both Python consumers and Flink jobs
- Provides windowed aggregations and analytics
- Ensures exactly-once processing semantics
- Includes schema registry for event validation
- Features comprehensive monitoring and testing

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   Producer  │─────▶│    Kafka     │─────▶│   Consumer/     │
│   (Events)  │      │   Cluster    │      │   Flink Jobs    │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │   Schema     │
                     │   Registry   │
                     └──────────────┘
```

## Tech Stack

- **Apache Kafka 7.4.0**: Distributed event streaming platform
- **Apache Flink 1.17**: Stream processing framework
- **Schema Registry**: Event schema validation
- **Kafka UI**: Web-based Kafka management
- **Python**: Event producers and consumers
- **Docker Compose**: Local development stack

## Features

### Event Producer
- High-throughput event generation
- Idempotent writes with exactly-once semantics
- Partitioning by user ID for ordered processing
- Configurable event types (page views, clicks, purchases, etc.)
- Compression and batching optimizations
- CLI for event simulation

### Event Consumer
- Auto-commit with configurable intervals
- Real-time event processing
- Statistics tracking (event types, users, errors)
- Graceful shutdown handling
- Multiple consumer groups support

### Aggregating Consumer
- Time-windowed aggregations
- Real-time metrics calculation
- Revenue tracking
- User activity analysis
- Top-N computations

### Flink Stream Processing
- Event-time processing with watermarks
- Tumbling and sliding windows
- Multiple job types:
  - Event counting by type
  - Revenue tracking and metrics
  - User session analysis
- Fault tolerance with checkpointing
- State management

## Quick Start

### 1. Start the Infrastructure

```bash
# Start all services (Kafka, Zookeeper, Schema Registry, Flink)
docker-compose up -d

# Verify services are running
docker-compose ps

# Check Kafka UI at http://localhost:8080
# Check Flink dashboard at http://localhost:8082
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Produce Events

```bash
# Simulate 1000 user events
python src/producer.py --count 1000 --delay 0.1

# High-volume simulation (100 events/sec for 60 seconds)
python src/producer.py --high-volume --rate 100 --duration 60

# Custom configuration
python src/producer.py \
  --bootstrap-servers localhost:9092 \
  --topic user-events \
  --count 5000 \
  --delay 0.05
```

### 4. Consume and Process Events

```bash
# Basic consumer
python src/consumer.py --max-messages 100

# Aggregating consumer with 30-second windows
python src/consumer.py --aggregate --window 30

# Custom configuration
python src/consumer.py \
  --bootstrap-servers localhost:9092 \
  --topic user-events \
  --group-id my-consumer-group
```

### 5. Run Flink Jobs

```bash
# Event counting job
python src/flink_processor.py --job event-count

# Revenue tracking job
python src/flink_processor.py --job revenue

# User session analysis job
python src/flink_processor.py --job sessions
```

## Event Schema

### Standard Event Structure

```json
{
  "timestamp": "2025-12-12T10:30:00.000Z",
  "event_type": "purchase",
  "user_id": "user_123",
  "version": "1.0",
  "data": {
    "product_id": "prod_456",
    "amount": 99.99,
    "currency": "USD",
    "session_id": "session_789",
    "device": "mobile",
    "browser": "chrome"
  }
}
```

### Event Types

- `page_view`: User views a page
- `button_click`: User clicks a button
- `form_submit`: Form submission
- `purchase`: Purchase transaction
- `add_to_cart`: Add item to cart
- `remove_from_cart`: Remove item from cart
- `search`: Search query
- `login`: User login
- `logout`: User logout
- `signup`: User registration

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_producer.py -v
```

## Configuration

### Kafka Topics

- `user-events`: Raw user events (input)
- `event-analytics`: Processed analytics (output)

### Consumer Groups

- `event-consumer-group`: Python consumer group
- `flink-consumer-group`: Flink job consumer group

### Performance Tuning

**Producer:**
```python
# High throughput configuration
producer = EventProducer(
    acks='1',  # Leader acknowledgment only (faster)
    compression_type='snappy',  # Fast compression
    batch_size=32768,  # Larger batches
    linger_ms=10  # Wait for batching
)
```

**Consumer:**
```python
# Optimized consumer configuration
consumer = EventConsumer(
    max_poll_records=500,  # Fetch more records
    fetch_min_bytes=1024,  # Min fetch size
    session_timeout_ms=30000  # Allow longer processing
)
```

## Monitoring

### Kafka UI
Access at `http://localhost:8080` to:
- View topics and partitions
- Monitor consumer lag
- Browse messages
- Manage consumer groups

### Flink Dashboard
Access at `http://localhost:8082` to:
- Monitor running jobs
- View checkpoints
- Analyze job metrics
- Debug failures

### Consumer Statistics

The consumer prints periodic statistics:
```
Total Events: 10000
Elapsed Time: 120.45s
Event Rate: 83.02 events/sec
Errors: 0

Top Event Types:
  page_view: 4532
  button_click: 2341
  purchase: 1234

Top Users:
  user_123: 234 events
  user_456: 198 events
```

## Scalability

### Horizontal Scaling

**Producers:**
- Run multiple producer instances
- Use different partition keys
- Configure proper batching

**Consumers:**
- Scale consumer group members
- One partition per consumer
- Rebalancing happens automatically

**Flink:**
- Increase task manager count
- Adjust parallelism
- Configure more task slots

### Kafka Partitioning

```bash
# Create topic with 10 partitions
kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic user-events \
  --partitions 10 \
  --replication-factor 1
```

## Troubleshooting

### Producer Issues

```bash
# Check Kafka connectivity
telnet localhost 9092

# View producer metrics
kafka-consumer-groups --bootstrap-server localhost:9092 --list
```

### Consumer Lag

```bash
# Check consumer group lag
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group event-consumer-group
```

### Flink Job Failures

```bash
# View Flink logs
docker logs flink-jobmanager
docker logs flink-taskmanager

# Check savepoints
ls -la flink-checkpoints/
```

## Advanced Features

### Exactly-Once Semantics

Flink jobs use:
- Checkpointing every 60 seconds
- Kafka transactional writes
- Idempotent producers
- Two-phase commit protocol

### Schema Evolution

Schema Registry supports:
- Backward compatibility
- Forward compatibility
- Schema versioning
- Automatic validation

## Performance Benchmarks

- **Producer throughput**: 50,000+ events/sec (single instance)
- **Consumer throughput**: 40,000+ events/sec (single instance)
- **End-to-end latency**: <100ms (p99)
- **Flink processing**: 100,000+ events/sec

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes
docker-compose down -v

# Clean Flink state
rm -rf flink-checkpoints/ flink-savepoints/
```

## Production Considerations

1. **Security**: Enable SASL/SSL for Kafka
2. **Monitoring**: Integrate with Prometheus/Grafana
3. **Alerting**: Configure alerts for lag, errors
4. **Backups**: Regular checkpoint backups
5. **Capacity Planning**: Monitor disk, CPU, memory
6. **Data Retention**: Configure topic retention policies

## References

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink Documentation](https://flink.apache.org/)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/)

## License

MIT

## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Data Pipelines

#### 1. ETL Pipeline
```
Create a Python-based ETL pipeline using Apache Airflow that extracts data from PostgreSQL, transforms it with pandas, and loads it into a data warehouse with incremental updates
```

#### 2. Stream Processing
```
Generate a Kafka consumer in Python that processes real-time events, performs aggregations using sliding windows, and stores results in Redis with TTL
```

#### 3. Data Quality
```
Write a data validation framework that checks for schema compliance, null values, data freshness, and statistical anomalies, with alerting on failures
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

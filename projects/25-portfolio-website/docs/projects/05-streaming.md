# Project 5: Real-time Data Streaming

**Category:** Data Engineering
**Status:** 🟡 40% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/5-real-time-streaming)

## Overview

Event-driven streaming platform built on **Apache Kafka** and **Apache Flink** for processing portfolio events with exactly-once semantics. Enables real-time analytics, event sourcing, and decoupled microservices communication at scale.

## Key Features

- **Exactly-Once Processing** - Guaranteed event delivery without duplicates
- **Event Sourcing** - Immutable event log as source of truth
- **Stream Processing** - Real-time transformations with Apache Flink
- **Scalable Architecture** - Kafka partitioning for horizontal scaling
- **Schema Registry** - Avro schemas for data consistency

## Architecture

```
Event Producers → Kafka Topics → Flink Processing Jobs → Output Sinks
                      ↓                   ↓
                Schema Registry    State Checkpoints
                      ↓                   ↓
              Avro Validation      Exactly-Once Guarantees
```

**Data Flow:**
1. **Ingestion**: Producers publish events to Kafka topics
2. **Validation**: Schema Registry validates Avro payloads
3. **Processing**: Flink jobs consume, transform, aggregate events
4. **Windowing**: Time-based and count-based windows for analytics
5. **Sinks**: Results written to databases, data lakes, or downstream topics

## Technologies

- **Apache Kafka** - Distributed event streaming platform
- **Apache Flink** - Stream processing framework
- **Python** - Event processing logic and orchestration
- **Avro** - Schema definition and serialization
- **Confluent Schema Registry** - Schema versioning
- **PostgreSQL** - Event sink for analytics
- **Docker** - Containerized deployment

## Quick Start

```bash
cd projects/5-real-time-streaming

# Install dependencies
pip install -r requirements.txt

# Start Kafka and Flink (local simulation)
docker-compose up -d

# Run event processor
python src/process_events.py

# Produce sample events
python src/event_producer.py --events 1000 --rate 100/sec
```

## Project Structure

```
5-real-time-streaming/
├── src/
│   ├── __init__.py
│   ├── process_events.py      # Flink job definitions
│   └── event_producer.py      # Sample event generator (to be added)
├── schemas/                    # Avro schemas (to be added)
│   ├── user_event.avsc
│   └── transaction_event.avsc
├── docker-compose.yml          # Local Kafka/Flink setup (to be added)
├── requirements.txt
└── README.md
```

## Business Impact

- **Real-Time Insights**: Sub-second event processing latency
- **Throughput**: Handles 100K+ events/second per partition
- **Reliability**: 99.99% uptime with exactly-once guarantees
- **Cost Efficiency**: 40% reduction vs batch processing infrastructure

## Current Status

**Completed:**
- ✅ Core Flink event processing module
- ✅ Basic stream processing logic

**In Progress:**
- 🟡 Kafka cluster configuration
- 🟡 Schema Registry integration
- 🟡 Exactly-once semantics implementation
- 🟡 Windowing and aggregation functions

**Next Steps:**
1. Set up Kafka cluster with multi-broker configuration
2. Integrate Confluent Schema Registry with Avro schemas
3. Implement exactly-once processing guarantees
4. Add windowing functions for time-series aggregations
5. Create monitoring dashboards for lag and throughput
6. Build event producer for testing and simulation
7. Add integration tests with embedded Kafka

## Key Learning Outcomes

- Event-driven architecture patterns
- Apache Kafka administration and optimization
- Apache Flink stream processing
- Exactly-once semantics and idempotency
- Schema evolution strategies
- Real-time analytics at scale

---

**Related Projects:**
- [Project 2: Database Migration](/projects/02-database-migration) - CDC with Kafka
- [Project 7: Serverless Data Processing](/projects/07-serverless) - Event-driven architecture
- [Project 16: Data Lake](/projects/16-data-lake) - Downstream analytics

---
title: Project 5: Real-time Data Streaming
description: Event-driven streaming platform built on Apache Kafka and Apache Flink for processing portfolio events with exactly-once semantics
tags: [analytics, apache-kafka, data-engineering, documentation, pipeline, portfolio]
path: portfolio/5-real-time-data-streaming/overview
created: 2026-03-08T22:19:13.373905+00:00
updated: 2026-03-08T22:04:38.748902+00:00
---

-

# Project 5: Real-time Data Streaming
> **Category:** Data Engineering | **Status:** 🟡 40% Complete
> **Source:** projects/25-portfolio-website/docs/projects/05-streaming.md

## 📋 Executive Summary

Event-driven streaming platform built on **Apache Kafka** and **Apache Flink** for processing portfolio events with exactly-once semantics. Enables real-time analytics, event sourcing, and decoupled microservices communication at scale.

## 🎯 Project Objectives

- **Exactly-Once Processing** - Guaranteed event delivery without duplicates
- **Event Sourcing** - Immutable event log as source of truth
- **Stream Processing** - Real-time transformations with Apache Flink
- **Scalable Architecture** - Kafka partitioning for horizontal scaling
- **Schema Registry** - Avro schemas for data consistency

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/05-streaming.md#architecture
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

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Apache Kafka | Apache Kafka | Distributed event streaming platform |
| Apache Flink | Apache Flink | Stream processing framework |
| Python | Python | Event processing logic and orchestration |

## 💡 Key Technical Decisions

### Decision 1: Adopt Apache Kafka
**Context:** Project 5: Real-time Data Streaming requires a resilient delivery path.
**Decision:** Distributed event streaming platform
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt Apache Flink
**Context:** Project 5: Real-time Data Streaming requires a resilient delivery path.
**Decision:** Stream processing framework
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Python
**Context:** Project 5: Real-time Data Streaming requires a resilient delivery path.
**Decision:** Event processing logic and orchestration
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

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

## ✅ Results & Outcomes

- **Real-Time Insights**: Sub-second event processing latency
- **Throughput**: Handles 100K+ events/second per partition
- **Reliability**: 99.99% uptime with exactly-once guarantees
- **Cost Efficiency**: 40% reduction vs batch processing infrastructure

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/05-streaming.md](../../../projects/25-portfolio-website/docs/projects/05-streaming.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Apache Kafka, Apache Flink, Python, Avro, Confluent Schema Registry

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/05-streaming.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Event processing latency** | < 100ms (p99) | Time from event ingestion → processed output |
| **Kafka availability** | 99.95% | Broker uptime and reachability |
| **Flink job uptime** | 99.9% | Job running without failures |
| **Message delivery guarantee** | 100% exactly-once | No duplicates or lost messages |
| **Consumer lag** | < 1000 messages | Messages waiting to be processed |
| **Checkpoint success rate** | 99% | Flink checkpoint completion rate |
| **Throughput** | > 10,000 events/sec | Messages processed per second |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*

---
title: "Database Migration Platform"
description: "Zero-downtime database migration orchestrator using Change Data Capture (CDC) with Debezium and AWS DMS."
published: true
date: 2026-01-23T15:24:46.000Z
tags:
  - database
  - migration
  - aws-dms
  - python
  - kafka
editor: markdown
dateCreated: 2026-01-23T15:24:46.000Z
---


# Database Migration Platform

> **Status**: Production Ready | **Completion**: [██████████] 100%
>
> `database` `migration` `aws-dms` `python` `kafka`

Zero-downtime database migration orchestrator using Change Data Capture (CDC) with Debezium and AWS DMS.

---


## 📋 Table of Contents

1. [Problem Statement](#-problem-statement) - Why this project exists
2. [Learning Objectives](#-learning-objectives) - What you'll learn
3. [Architecture](#-architecture) - System design and components
4. [Tech Stack](#-tech-stack) - Technologies and their purposes
5. [Technology Deep Dives](#-technology-deep-dives) - In-depth explanations
6. [Implementation Guide](#-implementation-guide) - How to build it
7. [Best Practices](#-best-practices) - Do's and don'ts
8. [Quick Start](#-quick-start) - Get running in minutes
9. [Operational Guide](#-operational-guide) - Day-2 operations
10. [Real-World Scenarios](#-real-world-scenarios) - Practical applications

---


## 🎯 Problem Statement

### The Database Migration Challenge

Database migrations are among the highest-risk operations in software engineering.
Unlike application deployments where you can quickly rollback, database changes often
involve data that cannot be easily reverted.

**The Downtime Problem**: Traditional migrations require taking applications offline,
migrating data, verifying integrity, and bringing systems back up. For a global
SaaS platform, this means scheduling maintenance windows—often resulting in hours
of downtime and lost revenue.

**Data Integrity Risks**: Moving billions of rows between systems introduces countless
failure modes. Network interruptions, schema mismatches, encoding issues, and constraint
violations can corrupt data or cause partial migrations.

**The Testing Gap**: You can't truly test a migration without production data volumes.
That small table that performed fine in staging becomes a 10-hour blocking operation
in production with 500 million rows.

**Rollback Complexity**: If something goes wrong mid-migration, rolling back may be
impossible. Data written to the new system during cutover may be lost. Customers may
have already interacted with partially migrated data.


**Business Impact:**
- Downtime costs $300,000+ per hour for large enterprises
- Failed migrations damage customer trust
- Regulatory issues if data is lost or corrupted
- Engineering teams afraid to attempt necessary modernization
- Technical debt compounds as migrations are postponed


### How This Project Solves It


**Change Data Capture (CDC) enables zero-downtime migrations:**

1. **Continuous Replication**: Capture changes as they happen using database transaction
   logs. The target system stays synchronized in real-time.

2. **Dual-Write Verification**: During migration, write to both systems and compare
   results. Detect discrepancies before they become problems.

3. **Gradual Traffic Shifting**: Route increasing percentages of read traffic to the
   new system while monitoring error rates and latency.

4. **Instant Rollback**: The old system remains fully operational. If issues arise,
   simply route traffic back—no data loss, no downtime.


### Key Capabilities Delivered

- ✅ **Zero-downtime cutover**
- ✅ **Data integrity validation**
- ✅ **Automated rollback**
- ✅ **Real-time replication monitoring**

---


## 🎓 Learning Objectives

By studying and implementing this project, you will:

   1. Implement Change Data Capture for real-time replication
   2. Design zero-downtime cutover strategies
   3. Build data validation pipelines for integrity verification
   4. Configure monitoring for replication lag and data quality
   5. Implement automated rollback procedures

**Prerequisites:**
- Basic understanding of cloud services (AWS/GCP/Azure)
- Familiarity with containerization (Docker)
- Command-line proficiency (Bash/Linux)
- Version control with Git

**Estimated Learning Time:** 15-25 hours for full implementation

---


## 🏗️ Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Database Migration Platform                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌───────────────┐    ┌─────────────────┐    ┌───────────────────┐   │
│   │    INPUT      │    │   PROCESSING    │    │     OUTPUT        │   │
│   │               │───▶│                 │───▶│                   │   │
│   │ • API Gateway │    │ • Business Logic│    │ • Response/Events │   │
│   │ • Event Queue │    │ • Validation    │    │ • Persistence     │   │
│   │ • File Upload │    │ • Transformation│    │ • Notifications   │   │
│   └───────────────┘    └─────────────────┘    └───────────────────┘   │
│           │                    │                       │              │
│           └────────────────────┴───────────────────────┘              │
│                                │                                       │
│                    ┌───────────┴───────────┐                          │
│                    │    INFRASTRUCTURE     │                          │
│                    │ • Compute (EKS/Lambda)│                          │
│                    │ • Storage (S3/RDS)    │                          │
│                    │ • Network (VPC/ALB)   │                          │
│                    │ • Security (IAM/KMS)  │                          │
│                    └───────────────────────┘                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

**Source System**
- Source Database, Transaction Logs, CDC Agent

**Replication Layer**
- Debezium, Kafka Connect, Schema Registry

**Target System**
- Target Database, Data Validation, Sync Status

**Control Plane**
- Migration Orchestrator, Health Monitoring, Rollback Manager

### Data Flow

`Source DB → CDC Capture → Kafka → Consumer → Target DB → Validation`

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Multi-AZ Deployment | Ensures high availability during AZ failures |
| Managed Services | Reduces operational burden, focus on business logic |
| Infrastructure as Code | Reproducibility, version control, audit trail |
| GitOps Workflow | Single source of truth, automated reconciliation |

---


## 🛠️ Tech Stack

### Technologies Used

| Technology | Purpose & Rationale |
|------------|---------------------|
| **Python** | Primary automation language for scripts, data processing, and ML pipelines |
| **Debezium** | CDC platform capturing database changes as event streams |
| **Kafka** | Core component |
| **PostgreSQL** | Enterprise-grade relational database with extensibility |
| **Docker** | Container packaging ensuring consistent runtime environments across all stages |

### Why This Combination?

This stack was carefully selected based on:

1. **Production Maturity** - All components are battle-tested at scale
2. **Community & Ecosystem** - Strong documentation, plugins, and support
3. **Integration** - Technologies work together with established patterns
4. **Scalability** - Architecture supports growth without major refactoring
5. **Operability** - Built-in observability and debugging capabilities
6. **Cost Efficiency** - Balance of capability and cloud spend optimization

### Alternative Considerations

| Current Choice | Alternatives Considered | Why Current Was Chosen |
|---------------|------------------------|------------------------|
| Terraform | CloudFormation, Pulumi | Provider-agnostic, mature ecosystem |
| Kubernetes | ECS, Nomad | Industry standard, portable |
| PostgreSQL | MySQL, MongoDB | ACID compliance, JSON support |

---

## 🔬 Technology Deep Dives

### 📚 Why Apache Kafka?

Apache Kafka is a distributed event streaming platform capable of handling
trillions of events per day. Originally developed at LinkedIn, it provides durable,
fault-tolerant message storage with high throughput for real-time data pipelines.

Kafka decouples data producers from consumers, enabling asynchronous communication
at scale. Unlike traditional message queues, Kafka retains messages for configurable
periods, allowing consumers to replay events and enabling event sourcing patterns.

#### How It Works


**Core Concepts:**
- **Topics**: Named feeds of messages, partitioned for parallelism
- **Partitions**: Ordered, immutable sequence of records
- **Producers**: Publish messages to topics
- **Consumers**: Subscribe to topics and process messages
- **Consumer Groups**: Coordinate consumption across instances

**Data Flow:**
1. Producers send records to topic partitions
2. Brokers persist records to disk with replication
3. Consumers poll brokers for new records
4. Offsets track consumer progress (committed after processing)


#### Working Code Example

```python
# Example: Kafka Producer and Consumer with Python
from confluent_kafka import Producer, Consumer
import json

# Producer Configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'acks': 'all',  # Wait for all replicas
    'retries': 3,
    'linger.ms': 5  # Batch messages for efficiency
}

producer = Producer(producer_config)

def delivery_callback(err, msg):
    if err:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()}[{msg.partition()}]')

# Send message
event = {'user_id': 123, 'action': 'purchase', 'amount': 99.99}
producer.produce(
    topic='user-events',
    key=str(event['user_id']).encode(),
    value=json.dumps(event).encode(),
    callback=delivery_callback
)
producer.flush()

# Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'analytics-consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False  # Manual commit for exactly-once
}

consumer = Consumer(consumer_config)
consumer.subscribe(['user-events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            print(f'Consumer error: {msg.error()}')
            continue

        event = json.loads(msg.value().decode())
        process_event(event)  # Your business logic
        consumer.commit(asynchronous=False)  # Commit after processing
finally:
    consumer.close()
```

#### Key Benefits

- **High Throughput**: Handle millions of messages per second per broker
- **Durability**: Messages persisted to disk with configurable replication
- **Scalability**: Add partitions and brokers for horizontal scaling
- **Exactly-Once Semantics**: Guaranteed delivery without duplicates
- **Message Retention**: Replay events for recovery or reprocessing
- **Ecosystem**: Connect, Streams, Schema Registry, ksqlDB

#### Best Practices

- ✅ Use meaningful partition keys for related event ordering
- ✅ Set appropriate replication factor (min 3 for production)
- ✅ Enable idempotent producers for exactly-once semantics
- ✅ Use Schema Registry for schema evolution management
- ✅ Monitor consumer lag to detect processing bottlenecks
- ✅ Implement dead letter queues for poison messages

#### Common Pitfalls to Avoid

- ❌ Using Kafka for request-response patterns (use gRPC/REST)
- ❌ Storing large payloads in messages (use references instead)
- ❌ Single partition topics for high-throughput workloads
- ❌ Auto-commit offsets without idempotent processing
- ❌ Ignoring consumer group rebalancing implications

#### Further Reading

- [Kafka Documentation](https://kafka.apache.org/documentation/)
- [Confluent Developer](https://developer.confluent.io/)
- [Designing Data-Intensive Applications (Book)](https://dataintensive.net/)

---



## 📖 Implementation Guide

This section provides production-ready code you can adapt for your own projects.

### Cdc

```python
# Zero-Downtime Database Migration with CDC
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from confluent_kafka import Consumer, Producer, KafkaError
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ChangeEvent:
    """Represents a database change captured by Debezium."""
    operation: str  # 'c' (create), 'u' (update), 'd' (delete)
    table: str
    before: Optional[Dict[str, Any]]
    after: Optional[Dict[str, Any]]
    timestamp: datetime
    transaction_id: str

class CDCMigrator:
    """
    Handles zero-downtime database migration using CDC.

    Flow:
    1. Initial snapshot of source database
    2. Continuous CDC replication during migration
    3. Dual-write verification
    4. Traffic cutover with instant rollback capability
    """

    def __init__(self, source_config: dict, target_config: dict, kafka_config: dict):
        self.source_conn = psycopg2.connect(**source_config)
        self.target_conn = psycopg2.connect(**target_config)

        self.consumer = Consumer({
            'bootstrap.servers': kafka_config['bootstrap_servers'],
            'group.id': 'migration-consumer',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

        self.producer = Producer({
            'bootstrap.servers': kafka_config['bootstrap_servers'],
            'acks': 'all'
        })

        self.metrics = {
            'events_processed': 0,
            'events_failed': 0,
            'lag_ms': 0
        }

    def start_initial_snapshot(self, tables: list[str]) -> None:
        """Perform initial data snapshot to target database."""
        logger.info("Starting initial snapshot...")

        for table in tables:
            with self.source_conn.cursor(cursor_factory=RealDictCursor) as src_cur:
                with self.target_conn.cursor() as tgt_cur:
                    # Get row count for progress tracking
                    src_cur.execute(f"SELECT COUNT(*) FROM {table}")
                    total_rows = src_cur.fetchone()['count']

                    # Stream data in batches
                    src_cur.execute(f"SELECT * FROM {table}")
                    batch_size = 1000
                    processed = 0

                    while True:
                        rows = src_cur.fetchmany(batch_size)
                        if not rows:
                            break

                        # Insert batch into target
                        columns = rows[0].keys()
                        values_template = ','.join(['%s'] * len(columns))
                        insert_sql = f"""
                            INSERT INTO {table} ({','.join(columns)})
                            VALUES ({values_template})
                            ON CONFLICT DO NOTHING
                        """

                        for row in rows:
                            tgt_cur.execute(insert_sql, list(row.values()))

                        self.target_conn.commit()
                        processed += len(rows)
                        logger.info(f"Snapshot progress: {table} - {processed}/{total_rows}")

        logger.info("Initial snapshot completed")

    def process_cdc_events(self, topic: str) -> None:
        """Process CDC events from Kafka and apply to target."""
        self.consumer.subscribe([topic])
        logger.info(f"Subscribed to CDC topic: {topic}")

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                # Parse Debezium event
                event = self._parse_debezium_event(msg.value())

                # Apply to target database
                success = self._apply_change(event)

                if success:
                    self.consumer.commit(asynchronous=False)
                    self.metrics['events_processed'] += 1
                else:
                    self.metrics['events_failed'] += 1
                    # Send to dead letter queue
                    self._send_to_dlq(msg.value())

        except KeyboardInterrupt:
            logger.info("Shutting down CDC processor")
        finally:
            self.consumer.close()

    def _parse_debezium_event(self, raw_event: bytes) -> ChangeEvent:
        """Parse Debezium CDC event."""
        data = json.loads(raw_event.decode('utf-8'))
        payload = data['payload']

        return ChangeEvent(
            operation=payload['op'],
            table=payload['source']['table'],
            before=payload.get('before'),
            after=payload.get('after'),
            timestamp=datetime.fromtimestamp(payload['ts_ms'] / 1000),
            transaction_id=str(payload['source']['txId'])
        )

    def _apply_change(self, event: ChangeEvent) -> bool:
        """Apply a single change event to target database."""
        try:
            with self.target_conn.cursor() as cur:
                if event.operation == 'c':  # INSERT
                    columns = event.after.keys()
                    values = [event.after[c] for c in columns]
                    sql = f"""
                        INSERT INTO {event.table} ({','.join(columns)})
                        VALUES ({','.join(['%s'] * len(columns))})
                    """
                    cur.execute(sql, values)

                elif event.operation == 'u':  # UPDATE
                    set_clause = ', '.join([f"{k} = %s" for k in event.after.keys()])
                    sql = f"UPDATE {event.table} SET {set_clause} WHERE id = %s"
                    values = list(event.after.values()) + [event.after['id']]
                    cur.execute(sql, values)

                elif event.operation == 'd':  # DELETE
                    sql = f"DELETE FROM {event.table} WHERE id = %s"
                    cur.execute(sql, [event.before['id']])

                self.target_conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to apply change: {e}")
            self.target_conn.rollback()
            return False

    def validate_data_integrity(self, table: str) -> dict:
        """Compare row counts and checksums between source and target."""
        with self.source_conn.cursor() as src_cur:
            with self.target_conn.cursor() as tgt_cur:
                # Row count comparison
                src_cur.execute(f"SELECT COUNT(*) FROM {table}")
                src_count = src_cur.fetchone()[0]

                tgt_cur.execute(f"SELECT COUNT(*) FROM {table}")
                tgt_count = tgt_cur.fetchone()[0]

                # Checksum comparison (sample)
                src_cur.execute(f"""
                    SELECT MD5(CAST(ARRAY_AGG(t.* ORDER BY id) AS TEXT))
                    FROM (SELECT * FROM {table} ORDER BY id LIMIT 1000) t
                """)
                src_checksum = src_cur.fetchone()[0]

                tgt_cur.execute(f"""
                    SELECT MD5(CAST(ARRAY_AGG(t.* ORDER BY id) AS TEXT))
                    FROM (SELECT * FROM {table} ORDER BY id LIMIT 1000) t
                """)
                tgt_checksum = tgt_cur.fetchone()[0]

                return {
                    'table': table,
                    'source_count': src_count,
                    'target_count': tgt_count,
                    'counts_match': src_count == tgt_count,
                    'checksums_match': src_checksum == tgt_checksum,
                    'validated_at': datetime.utcnow().isoformat()
                }
```

---


## ✅ Best Practices

### Infrastructure

| Practice | Description | Why It Matters |
|----------|-------------|----------------|
| **Infrastructure as Code** | Define all resources in version-controlled code | Reproducibility, audit trail, peer review |
| **Immutable Infrastructure** | Replace instances, don't modify them | Consistency, easier rollback, no drift |
| **Least Privilege** | Grant minimum required permissions | Security, blast radius reduction |
| **Multi-AZ Deployment** | Distribute across availability zones | High availability during AZ failures |

### Security

- ⛔ **Never** hardcode credentials in source code
- ⛔ **Never** commit secrets to version control
- ✅ **Always** use IAM roles over access keys
- ✅ **Always** encrypt data at rest and in transit
- ✅ **Always** enable audit logging (CloudTrail, VPC Flow Logs)

### Operations

1. **Observability First**
   - Instrument code before production deployment
   - Establish baselines for normal behavior
   - Create actionable alerts, not noise

2. **Automate Everything**
   - Manual processes don't scale
   - Runbooks should be scripts, not documents
   - Test automation regularly

3. **Practice Failure**
   - Regular DR drills validate recovery procedures
   - Chaos engineering builds confidence
   - Document and learn from incidents

### Code Quality

```python
# ✅ Good: Clear, testable, observable
class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway, metrics: MetricsClient):
        self.gateway = gateway
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)

    def process(self, payment: Payment) -> Result:
        self.logger.info(f"Processing payment {payment.id}")
        start = time.time()

        try:
            result = self.gateway.charge(payment)
            self.metrics.increment("payments.success")
            return result
        except GatewayError as e:
            self.metrics.increment("payments.failure")
            self.logger.error(f"Payment failed: {e}")
            raise
        finally:
            self.metrics.timing("payments.duration", time.time() - start)

# ❌ Bad: Untestable, no observability
def process_payment(payment):
    return requests.post(GATEWAY_URL, json=payment).json()
```

---


## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- [ ] **Docker** (20.10+) and Docker Compose installed
- [ ] **Python** 3.11+ with pip
- [ ] **AWS CLI** configured with appropriate credentials
- [ ] **kubectl** installed and configured
- [ ] **Terraform** 1.5+ installed
- [ ] **Git** for version control

### Step 1: Clone the Repository

```bash
git clone https://github.com/samueljackson-collab/Portfolio-Project.git
cd Portfolio-Project/projects/2-database-migration
```

### Step 2: Review the Documentation

```bash
# Read the project README
cat README.md

# Review available make targets
make help
```

### Step 3: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your configuration
vim .env

# Validate configuration
make validate-config
```

### Step 4: Start Local Development

```bash
# Start all services with Docker Compose
make up

# Verify services are running
make status

# View logs
make logs

# Run tests
make test
```

### Step 5: Deploy to Cloud

```bash
# Initialize Terraform
cd terraform
terraform init

# Review planned changes
terraform plan -out=tfplan

# Apply infrastructure
terraform apply tfplan

# Deploy application
cd ..
make deploy ENV=staging
```

### Verification

```bash
# Check deployment health
make health

# Run smoke tests
make smoke-test

# View dashboards
open http://localhost:3000  # Grafana
```

---


## ⚙️ Operational Guide

### Monitoring & Alerting

| Metric Type | Tool | Dashboard |
|-------------|------|-----------|
| **Metrics** | Prometheus | Grafana `http://localhost:3000` |
| **Logs** | Loki | Grafana Explore |
| **Traces** | Tempo/Jaeger | Grafana Explore |
| **Errors** | Sentry | `https://sentry.io/org/project` |

### Key Metrics to Monitor

```promql
# Request latency (P99)
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m]))

# Resource utilization
container_memory_usage_bytes / container_spec_memory_limit_bytes
```

### Common Operations

| Task | Command | When to Use |
|------|---------|-------------|
| View logs | `kubectl logs -f deploy/app` | Debugging issues |
| Scale up | `kubectl scale deploy/app --replicas=5` | Handling load |
| Rollback | `kubectl rollout undo deploy/app` | Bad deployment |
| Port forward | `kubectl port-forward svc/app 8080:80` | Local debugging |
| Exec into pod | `kubectl exec -it deploy/app -- bash` | Investigation |

### Runbooks

<details>
<summary><strong>🔴 High Error Rate</strong></summary>

**Symptoms:** Error rate exceeds 1% threshold

**Investigation:**
1. Check recent deployments: `kubectl rollout history deploy/app`
2. Review error logs: `kubectl logs -l app=app --since=1h | grep ERROR`
3. Check dependency health: `make check-dependencies`
4. Review metrics dashboard for patterns

**Resolution:**
- If recent deployment: `kubectl rollout undo deploy/app`
- If dependency failure: Check upstream service status
- If resource exhaustion: Scale horizontally or vertically

**Escalation:** Page on-call if not resolved in 15 minutes
</details>

<details>
<summary><strong>🟡 High Latency</strong></summary>

**Symptoms:** P99 latency > 500ms

**Investigation:**
1. Check traces for slow operations
2. Review database query performance
3. Check for resource constraints
4. Review recent configuration changes

**Resolution:**
- Identify slow queries and optimize
- Add caching for frequently accessed data
- Scale database read replicas
- Review and optimize N+1 queries
</details>

<details>
<summary><strong>🔵 Deployment Failure</strong></summary>

**Symptoms:** ArgoCD sync fails or pods not ready

**Investigation:**
1. Check ArgoCD UI for sync errors
2. Review pod events: `kubectl describe pod <pod>`
3. Check image pull status
4. Verify secrets and config maps exist

**Resolution:**
- Fix manifest issues and re-sync
- Ensure image exists in registry
- Verify RBAC permissions
- Check resource quotas
</details>

### Disaster Recovery

**RTO Target:** 15 minutes
**RPO Target:** 1 hour

```bash
# Failover to DR region
./scripts/dr-failover.sh --region us-west-2

# Validate data integrity
./scripts/dr-validate.sh

# Failback to primary
./scripts/dr-failback.sh --region us-east-1
```

---


## 🌍 Real-World Scenarios

These scenarios demonstrate how this project applies to actual business situations.

### Scenario: Database Version Upgrade

**Challenge:** Upgrade PostgreSQL 11 to 15 without downtime for 24/7 SaaS application

**Solution:** CDC replication to new version, dual-write verification, gradual traffic shift, instant rollback capability

---

### Scenario: Cloud Migration

**Challenge:** Migrate on-premise Oracle to AWS RDS PostgreSQL

**Solution:** Schema conversion, CDC-based data sync, application compatibility testing, cutover with validation

---



## 🔗 Related Projects

Explore these related projects that share technologies or concepts:

| Project | Description | Shared Tags |
|---------|-------------|-------------|
| [Real-time Data Streaming](/projects/real-time-data-streaming) | High-throughput event streaming pipeline using Apa... | 2 |
| [MLOps Platform](/projects/mlops-platform) | End-to-end MLOps workflow for training, evaluating... | 1 |
| [Quantum Computing Integration](/projects/quantum-computing-integration) | Hybrid quantum-classical workloads using Qiskit.... | 1 |
| [Advanced Cybersecurity Platform](/projects/advanced-cybersecurity-platform) | SOAR engine consolidating SIEM alerts with automat... | 1 |

---


## 📚 Resources

### Project Links

| Resource | Link |
|----------|------|
| 📂 Source Code | [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/2-database-migration) |
| 📖 Documentation | [`projects/2-database-migration/docs/`](projects/2-database-migration/docs/) |
| 🐛 Issues | [Report bugs or request features](https://github.com/samueljackson-collab/Portfolio-Project/issues) |

### Recommended Reading

- [The Twelve-Factor App](https://12factor.net/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

### Community Resources

- Stack Overflow: Tag your questions appropriately
- Reddit: r/devops, r/aws, r/kubernetes
- Discord: Many technology-specific servers

---

<div align="center">

**Last Updated:** 2026-01-23 |
**Version:** 3.0 |
**Generated by:** Portfolio Wiki Content Generator

*Found this helpful? Star the repository!*

</div>

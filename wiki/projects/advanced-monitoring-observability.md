---
title: "Advanced Monitoring & Observability"
description: "Unified observability stack with Prometheus, Tempo, Loki, and Grafana."
published: true
date: 2026-01-23T15:24:46.000Z
tags:
  - monitoring
  - observability
  - grafana
  - prometheus
editor: markdown
dateCreated: 2026-01-23T15:24:46.000Z
---


# Advanced Monitoring & Observability

> **Status**: Production Ready | **Completion**: [██████████] 100%
>
> `monitoring` `observability` `grafana` `prometheus`

Unified observability stack with Prometheus, Tempo, Loki, and Grafana.

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

### The Observability Challenge

Modern distributed systems generate signals across multiple dimensions, but siloed
tools create dangerous blind spots:

**The Correlation Problem**: A latency spike in the API could be caused by database
slowness, network issues, upstream dependencies, or application bugs. Without
correlation, engineers play detective across multiple dashboards.

**The Alert Fatigue Problem**: Each monitoring tool generates its own alerts. Teams
are overwhelmed by notifications, most of which are noise. Critical alerts get
lost in the flood.

**The Context Problem**: An alert fires at 3 AM. The on-call engineer has no context.
Which dashboard should they check? What runbook applies? What changed recently?

**The Cardinality Problem**: High-cardinality data (unique user IDs, request IDs)
is valuable for debugging but expensive to store. Teams compromise between cost
and visibility.


**Business Impact:**
- Extended MTTR from context switching between tools
- Alert fatigue leads to ignored critical alerts
- On-call burnout from poorly actionable alerts
- Hidden issues that only manifest in production
- Excessive monitoring costs from inefficient tooling


### How This Project Solves It


**Unified observability connects the three pillars:**

1. **Correlated Signals**: Trace IDs link metrics, logs, and traces. Jump from
   alert to relevant logs to distributed trace in one click.

2. **Intelligent Alerting**: ML-powered anomaly detection reduces noise. Alerts
   include context—recent deploys, related incidents, runbook links.

3. **SLO-Based Approach**: Define Service Level Objectives. Alert on error budget
   burn rate, not raw metrics. Focus on user impact.

4. **Cost-Efficient Storage**: Sampling and aggregation for high-volume data.
   Detailed retention for recent data, summarized for historical.


### Key Capabilities Delivered

- ✅ **Custom application exporter**
- ✅ **Multi-channel alerting**
- ✅ **Long-term storage**
- ✅ **SLO tracking**

---


## 🎓 Learning Objectives

By studying and implementing this project, you will:

   1. Design unified observability with metrics, logs, and traces
   2. Implement SLO-based alerting strategies
   3. Configure distributed tracing with OpenTelemetry
   4. Build custom Prometheus exporters
   5. Create actionable dashboards and runbooks

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
│                         Advanced Monitoring & Observability                  │
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
| **Prometheus** | Pull-based metrics collection with powerful PromQL query language |
| **Grafana** | Unified visualization platform connecting metrics, logs, and traces |
| **Loki** | Log aggregation designed for efficiency with label-based indexing |
| **Thanos** | Highly available Prometheus with long-term storage and global querying |
| **Python** | Primary automation language for scripts, data processing, and ML pipelines |

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

### 📚 Why Unified Observability?

Modern systems generate signals across three pillars: metrics, logs, and traces.
Siloed monitoring tools create blind spots—a spike in error rate (metric) needs
correlation with stack traces (logs) and request flow (traces) for effective debugging.

Unified observability platforms like Grafana combine these signals, enabling
engineers to understand system behavior holistically and reduce Mean Time to
Resolution (MTTR).

#### How It Works


**Three Pillars of Observability:**
- **Metrics**: Numeric measurements over time (Prometheus)
- **Logs**: Discrete events with context (Loki)
- **Traces**: Request flow across services (Tempo/Jaeger)

**Correlation:**
- Trace ID links logs and traces
- Exemplars connect metrics to traces
- Labels/tags enable cross-signal queries

**Alerting Flow:**
1. Metrics trigger alert conditions
2. Alertmanager routes and deduplicates
3. Notifications sent to PagerDuty/Slack
4. Dashboard links provide investigation context


#### Working Code Example

```python
# Example: Instrumented FastAPI Application
from fastapi import FastAPI, Request
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
import time

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="tempo:4317", insecure=True)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    start_time = time.time()

    # Get trace context
    span = trace.get_current_span()
    trace_id = format(span.get_span_context().trace_id, '032x')

    # Add trace ID to logs
    log = logger.bind(
        trace_id=trace_id,
        method=request.method,
        path=request.url.path
    )

    try:
        response = await call_next(request)
        status = response.status_code
        log.info("request_completed", status=status)
    except Exception as e:
        status = 500
        log.error("request_failed", error=str(e))
        raise
    finally:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=status
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

    return response

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    with tracer.start_as_current_span("fetch_user") as span:
        span.set_attribute("user.id", user_id)
        logger.info("fetching_user", user_id=user_id)

        # Simulate database call
        with tracer.start_as_current_span("db_query"):
            await asyncio.sleep(0.05)

        return {"user_id": user_id, "name": "Example User"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

#### Key Benefits

- **Unified View**: Correlate metrics, logs, and traces in one platform
- **Faster MTTR**: Quickly identify root cause with connected signals
- **Proactive Alerting**: Detect issues before users are impacted
- **Capacity Planning**: Historical data informs scaling decisions
- **SLO Tracking**: Measure and report on service level objectives
- **Cost Visibility**: Understand resource utilization
- **Team Collaboration**: Shared dashboards and runbooks

#### Best Practices

- ✅ Instrument applications with OpenTelemetry for vendor neutrality
- ✅ Use structured logging with trace IDs for correlation
- ✅ Define SLOs with error budgets for reliability targets
- ✅ Create actionable alerts with runbook links
- ✅ Implement log sampling for high-volume services
- ✅ Use recording rules for frequently-used Prometheus queries

#### Common Pitfalls to Avoid

- ❌ Alert fatigue from too many low-value alerts
- ❌ Separate tools without correlation capability
- ❌ High-cardinality labels in Prometheus
- ❌ Storing logs indefinitely without retention policy
- ❌ Missing context in alerts (no runbook, no dashboard)

#### Further Reading

- [Grafana Documentation](https://grafana.com/docs/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)

---

### 📚 Why Prometheus?

Prometheus is an open-source monitoring system with a dimensional data model
and powerful query language (PromQL). Originally built at SoundCloud and now a
CNCF graduated project, it's the de facto standard for Kubernetes monitoring.

Prometheus uses a pull-based model where it scrapes metrics from targets at
configured intervals. This approach simplifies service discovery and makes it
easy to monitor dynamic environments.

#### How It Works


**Architecture:**
- **Prometheus Server**: Scrapes and stores metrics
- **Exporters**: Expose metrics in Prometheus format
- **Alertmanager**: Handles alert routing and deduplication
- **Pushgateway**: For short-lived batch jobs

**Data Model:**
- Time series identified by metric name + labels
- Labels enable dimensional queries
- Samples: (timestamp, value) pairs

**Example Metrics:**
- `http_requests_total{method="GET", status="200"}` (counter)
- `http_request_duration_seconds` (histogram)
- `process_cpu_seconds_total` (gauge)


#### Working Code Example

```python
# Example: Custom Prometheus Exporter
from prometheus_client import (
    Counter, Histogram, Gauge, Info,
    start_http_server, CollectorRegistry
)
import time
import random

# Define metrics
REQUEST_COUNT = Counter(
    'app_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'app_request_duration_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

ACTIVE_CONNECTIONS = Gauge(
    'app_active_connections',
    'Number of active connections'
)

APP_INFO = Info(
    'app',
    'Application information'
)

# Set static info
APP_INFO.info({
    'version': '1.2.3',
    'environment': 'production'
})

# Instrument your application
def handle_request(method: str, endpoint: str):
    """Example request handler with metrics."""
    ACTIVE_CONNECTIONS.inc()

    start_time = time.time()
    try:
        # Simulate request processing
        time.sleep(random.uniform(0.01, 0.5))
        status = "200"
    except Exception:
        status = "500"
    finally:
        duration = time.time() - start_time

        # Record metrics
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

        ACTIVE_CONNECTIONS.dec()

if __name__ == '__main__':
    # Start metrics server on port 8000
    start_http_server(8000)
    print("Metrics available at http://localhost:8000/metrics")

    # Simulate traffic
    while True:
        handle_request("GET", "/api/users")
        time.sleep(0.1)
```

```yaml
# prometheus.yml - Scrape configuration
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts/*.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'application'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: (.+)
```

#### Key Benefits

- **Pull-Based Model**: Prometheus scrapes metrics, simplifying service discovery
- **PromQL**: Powerful query language for analysis and alerting
- **Service Discovery**: Auto-discover Kubernetes pods, EC2 instances, etc.
- **Alertmanager**: Flexible alerting with routing, grouping, silencing
- **CNCF Graduated**: Production-proven with strong community support
- **Dimensional Data**: Labels enable flexible querying and aggregation
- **Efficient Storage**: Custom TSDB optimized for time series

#### Best Practices

- ✅ Use recording rules for frequently-used complex queries
- ✅ Implement alerting rules with proper severity levels
- ✅ Set appropriate scrape intervals (15s default is usually fine)
- ✅ Use relabeling to add metadata and filter targets
- ✅ Configure retention based on storage capacity
- ✅ Use federation or remote write for long-term storage

#### Common Pitfalls to Avoid

- ❌ High-cardinality labels (user IDs, request IDs)
- ❌ Storing logs in Prometheus (use Loki instead)
- ❌ Missing `le` label in histogram queries
- ❌ Alerting on raw values without smoothing
- ❌ Too short scrape intervals causing load

#### Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/)
- [PromQL Tutorial](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Prometheus: Up & Running (Book)](https://www.oreilly.com/library/view/prometheus-up/9781492034131/)

---



## 📖 Implementation Guide

This section provides production-ready code you can adapt for your own projects.

### Step 1: Implementing Custom application exporter

**Objective:** Build custom application exporter with production-grade quality.

**Implementation Approach:**

1. **Define Requirements**
   - Functional: What it must do
   - Non-functional: Performance, security, reliability targets

2. **Design the Solution**
   - Consider failure modes and edge cases
   - Plan for observability from the start
   - Document architectural decisions

3. **Implement Iteratively**
   - Start with a minimal working version
   - Add tests before extending functionality
   - Refactor for clarity and maintainability

4. **Validate Thoroughly**
   - Unit tests for business logic
   - Integration tests for component interaction
   - Load tests for performance validation

### Step 2: Implementing Multi-channel alerting

**Objective:** Build multi-channel alerting with production-grade quality.

**Implementation Approach:**

1. **Define Requirements**
   - Functional: What it must do
   - Non-functional: Performance, security, reliability targets

2. **Design the Solution**
   - Consider failure modes and edge cases
   - Plan for observability from the start
   - Document architectural decisions

3. **Implement Iteratively**
   - Start with a minimal working version
   - Add tests before extending functionality
   - Refactor for clarity and maintainability

4. **Validate Thoroughly**
   - Unit tests for business logic
   - Integration tests for component interaction
   - Load tests for performance validation

### Step 3: Implementing Long-term storage

**Objective:** Build long-term storage with production-grade quality.

**Implementation Approach:**

1. **Define Requirements**
   - Functional: What it must do
   - Non-functional: Performance, security, reliability targets

2. **Design the Solution**
   - Consider failure modes and edge cases
   - Plan for observability from the start
   - Document architectural decisions

3. **Implement Iteratively**
   - Start with a minimal working version
   - Add tests before extending functionality
   - Refactor for clarity and maintainability

4. **Validate Thoroughly**
   - Unit tests for business logic
   - Integration tests for component interaction
   - Load tests for performance validation

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
cd Portfolio-Project/projects/23-advanced-monitoring
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

### Scenario: Production Traffic Surge

**Challenge:** Application needs to handle 5x normal traffic during peak events.

**Solution:** Auto-scaling policies trigger based on CPU and request metrics.
Load testing validates capacity before the event. Runbooks document
manual intervention procedures if automated scaling is insufficient.

---

### Scenario: Security Incident Response

**Challenge:** Vulnerability discovered in production dependency.

**Solution:** Automated scanning detected the CVE. Patch branch created
and tested within hours. Rolling deployment updated all instances with
zero downtime. Audit trail documented the entire response timeline.

---



## 📚 Resources

### Project Links

| Resource | Link |
|----------|------|
| 📂 Source Code | [GitHub Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/23-advanced-monitoring) |
| 📖 Documentation | [`projects/23-advanced-monitoring/docs/`](projects/23-advanced-monitoring/docs/) |
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

# Project 23: Advanced Monitoring & Observability

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


**Status**: ✅ **100% Complete** - Production-Ready

## Overview

Enterprise-grade monitoring and observability stack featuring Prometheus, Grafana, Alertmanager, Loki, Thanos, and custom application metrics. This project demonstrates production-ready monitoring patterns including SLO tracking, intelligent alerting, long-term storage, and comprehensive application metrics.

## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://23-advanced-monitoring.staging.portfolio.example.com` |
| DNS | `23-advanced-monitoring.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services; IaC in `terraform/`, `infra/`, or `deploy/` for this project) |

### Deployment automation
- **CI/CD:** GitHub Actions [`/.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`/.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.
- **Deployment status:** See [`DEPLOYMENT_STATUS.md`](DEPLOYMENT_STATUS.md) for live deployment tracking and verification steps.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
![Live deployment dashboard](../../assets/screenshots/live-deployment-placeholder.svg)

## 🎯 Features

### Core Components
- **Prometheus**: Metrics collection, aggregation, and querying
- **Grafana**: Visualization dashboards with SLO tracking
- **Alertmanager**: Multi-channel alerting (Slack, PagerDuty, Email)
- **Loki**: Log aggregation with Promtail
- **Thanos**: Long-term metric storage and global querying
- **Custom Exporters**: Application-specific business metrics

### Advanced Features
- ✅ **Custom Application Exporter** - Business and performance metrics
- ✅ **PagerDuty/Slack Integration** - Multi-channel alerting with routing
- ✅ **Long-term Storage** - Thanos for historical metric retention
- ✅ **SLO Tracking** - Error budgets and burn rate calculations
- ✅ **Multi-cluster Support** - Kubernetes service discovery
- ✅ **Alert Routing** - Intelligent alert distribution by severity

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 8GB+ RAM recommended
- Ports available: 3000, 9090, 9093, 8000, 10904

### Start the Stack

```bash
# Copy environment template and customize credentials/urls
cp .env.example .env

# Start all monitoring services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f prometheus grafana
```

### Access Dashboards

- **Grafana**: http://localhost:3000 (admin credentials set via `.env`)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093
- **Thanos Query**: http://localhost:10904
- **Custom Metrics**: http://localhost:8000/metrics

> **Security note:** All web UIs bind to `127.0.0.1` by default. Expose them externally only via a reverse proxy with TLS/authentication.

### Version Matrix & Health Expectations

| Service | Version | Health endpoint | Notes |
| --- | --- | --- | --- |
| Prometheus | `v2.52.0` | `/-/healthy` | 30s interval, 5s timeout, 5 retries |
| Grafana | `10.4.3` | `/api/health` | 30s interval, 5s timeout, 5 retries |
| Alertmanager | `v0.27.0` | `/-/healthy` | 30s interval, 5s timeout, 5 retries |
| Loki | `2.9.3` | `/ready` | 30s interval, 5s timeout, 5 retries |
| Promtail | `2.9.3` | `/ready` (port 9080) | 30s interval, 5s timeout, 5 retries |
| Node Exporter | `v1.8.1` | `/-/healthy` | 30s interval, 5s timeout, 5 retries |
| cAdvisor | `v0.47.2` | `/healthz` | 30s interval, 5s timeout, 5 retries |
| Thanos (sidecar/query/store/compactor) | `v0.34.1` | `/-/healthy` | Query binds 10904→9090 on localhost |

### Configuration via `.env`

The stack reads user-tunable values from `.env`:
- Retention: `PROMETHEUS_RETENTION_TIME`, `LOKI_RETENTION_PERIOD`
- Credentials & admin users: `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`
- Alert destinations: `ALERTMANAGER_SLACK_API_URL`, `ALERTMANAGER_PAGERDUTY_KEY`
- Promtail host tag: `PROMTAIL_HOSTNAME`
- App exporter metadata: `APP_EXPORTER_VERSION`, `APP_EXPORTER_ENVIRONMENT`, `APP_EXPORTER_AWS_REGION`

> Keep `.env` out of version control if it contains secrets.

## 📊 Components

### 1. Custom Application Exporter

Located in `exporters/app_exporter.py`, this custom Prometheus exporter collects:

**Business Metrics**:
- Active users by tier (free/premium/enterprise)
- Revenue tracking by product and region
- Transaction counts and types
- Feature usage by user tier

**Performance Metrics**:
- Request duration histograms
- Request/response sizes
- Error rates and types

**Infrastructure Metrics**:
- Database connection pools
- Query performance
- Cache hit/miss ratios
- Queue depths and processing times

**SLO Metrics**:
- Service availability percentages
- Error budget tracking
- Burn rate calculations

**Run Standalone**:
```bash
cd exporters
pip install -r requirements.txt
python app_exporter.py --port 8000 --interval 15
```

**View Metrics**:
```bash
curl http://localhost:8000/metrics
```

### 2. Alertmanager with Multi-Channel Integration

Located in `alertmanager/alertmanager.yml`

**Supported Channels**:
- **Slack**: Critical, warning, infrastructure, and application channels
- **PagerDuty**: Critical alerts with incident tracking
- **Email**: Optional team notifications
- **Webhook**: Custom integrations

**Alert Routing**:
```yaml
- Critical alerts → PagerDuty + Slack
- Warnings → Slack warnings channel
- Infrastructure → Dedicated Slack channel
- Application → Application team Slack channel
```

**Configuration**:
```bash
# Edit alertmanager.yml
vi alertmanager/alertmanager.yml

# Update Slack webhook URL
slack_api_url: '${ALERTMANAGER_SLACK_API_URL}'

# Update PagerDuty integration key
service_key: '${ALERTMANAGER_PAGERDUTY_KEY}'

# Restart Alertmanager
docker-compose restart alertmanager
```

### 3. Long-term Storage with Thanos

Thanos provides unlimited metric retention and global query capabilities.

**Components**:
- **Thanos Sidecar**: Uploads Prometheus data to object storage
- **Thanos Query**: Unified query interface across all Prometheus instances
- **Thanos Store**: Queries historical data from object storage
- **Thanos Compactor**: Downsamples and compacts old data

**Storage Backends Supported**:
- AWS S3
- Google Cloud Storage (GCS)
- Azure Blob Storage
- Local filesystem (testing only)

**Configuration**:
```bash
# Edit Thanos bucket config
vi thanos/bucket.yml

# Update S3 bucket name
bucket: "your-thanos-metrics-bucket"

# Set AWS credentials via environment or IAM role
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

**Query Historical Data**:
```bash
# Query via Thanos Query (unlimited retention)
curl 'http://localhost:10904/api/v1/query?query=up'

# View in Grafana
# Add Thanos Query as data source: http://thanos-query:9090
```

## 📈 Highlights

### SLO Dashboard
- `dashboards/portfolio.json` – Visualizes SLOs, burn rates, and release markers
- Error budget tracking across services
- Multi-window burn rate alerts (1h, 6h, 24h)

### Alert Rules
- `alerts/portfolio_rules.yml` – Production-ready alerting rules
- Time-windowed burn rate calculations
- Severity-based routing (critical, warning, info)

### Kubernetes Integration
- `manifests/` – Kustomize overlays for staging/production
- Service discovery for pods, nodes, services
- Automatic metric scraping via annotations


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Observability Setup

#### 1. Prometheus Rules
```
Create Prometheus alerting rules for application health, including error rate thresholds, latency percentiles, and service availability with appropriate severity levels
```

#### 2. Grafana Dashboard
```
Generate a Grafana dashboard JSON for microservices monitoring with panels for request rate, error rate, latency distribution, and resource utilization
```

#### 3. Log Aggregation
```
Write a Fluentd configuration that collects logs from multiple sources, parses JSON logs, enriches with Kubernetes metadata, and forwards to Elasticsearch
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

# Enterprise Portfolio - Tools & Automation

This directory contains automation tools, scripts, and configuration for the
Enterprise Portfolio infrastructure.

## 📂 Directory Structure

```text
tools/
├── grafana/              # Grafana provisioning
│   └── provisioning/
│       ├── datasources/  # Auto-configured data sources
│       └── dashboards/   # Dashboard providers
├── loki/                 # Loki log aggregation config
│   └── loki-config.yml
├── alertmanager/         # Alertmanager configuration
│   └── alertmanager.yml
├── wikijs_push.py        # Wiki.js documentation publisher
└── README.md             # This file
```

## 🛠️ Tools Overview

### Wiki.js Documentation Publisher

Automatically publishes Markdown documentation to Wiki.js via GraphQL API.

**Usage:**

```bash
# Set environment variables
export WIKI_URL="http://localhost:3000/graphql"
export WIKI_TOKEN="your-api-token-here"

# Publish single file
python tools/wikijs_push.py docs/project-overview.md

# Publish entire directory
python tools/wikijs_push.py docs/projects/ --pattern "*.md"

# Custom base path
python tools/wikijs_push.py docs/ --base-path "/portfolio"
```

**Features:**

- Automatic page creation and updates
- Support for directory batch publishing
- SHA-256 verification
- Error handling and retry logic

**Configuration:**

- `WIKI_URL`: Wiki.js GraphQL API endpoint
- `WIKI_TOKEN`: API authentication token
- `WIKI_BASE_PATH`: Base path for published pages (default: `/projects`)

### Grafana Provisioning

Automatically configures Grafana datasources and dashboards on startup.

**Datasources:**

- Prometheus (default): `http://prometheus:9090`
- Loki: `http://loki:3100`

**Dashboard Provisioning:**
Place dashboard JSON files in `grafana/provisioning/dashboards/` for automatic import.

### Loki Configuration

Log aggregation system with 7-day retention.

**Key Settings:**

- Retention: 168 hours (7 days)
- Storage: Filesystem-based
- Schema: v11 (BoltDB shipper)

**Querying Logs:**

```bash
# Via API
curl -G -s "http://localhost:3100/loki/api/v1/query" \
  --data-urlencode 'query={job="systemd-journal"}'

# Via LogQL in Grafana
{job="varlogs"} |= "error"
```

### Alertmanager Configuration

Routes and manages alerts from Prometheus.

**Alert Routing:**

- **Critical**: Routed to `critical` receiver
- **Warning**: Routed to `warning` receiver
- **Default**: All other alerts

**Customization:**

Edit `alertmanager/alertmanager.yml` to configure:

- Slack webhooks
- Email notifications
- PagerDuty integration
- Custom webhook receivers

## 🚀 Quick Start

### 1. Start Demo Stack

```bash
# From repository root
docker compose -f compose.demo.yml up -d

# Verify services
docker compose -f compose.demo.yml ps
```

### 2. Access Services

- **Prometheus**: <http://localhost:9090>
- **Grafana**: <http://localhost:3001> (admin/admin)
- **Alertmanager**: <http://localhost:9093>
- **Loki**: <http://localhost:3100>

### 3. Publish Documentation to Wiki.js

```bash
# Install dependencies
pip install requests

# Set credentials
export WIKI_TOKEN="your-token"

# Publish project documentation
python tools/wikijs_push.py projects/01-sde-devops/PRJ-SDE-001/README.md
```

## 📊 Monitoring & Observability

### Prometheus Metrics

Access metrics at:

- Node Exporter: <http://localhost:9100/metrics>
- cAdvisor: <http://localhost:8080/metrics>
- Prometheus: <http://localhost:9090/metrics>

### Grafana Dashboards

Import pre-built dashboards:

1. Navigate to <http://localhost:3001>
2. Login (admin/admin)
3. Go to Dashboards → Import
4. Use dashboard IDs from <https://grafana.com/grafana/dashboards/>

**Recommended Dashboards:**

- 1860: Node Exporter Full
- 893: Docker and System Monitoring
- 13639: Loki Dashboard

### Alert Testing

Trigger test alerts:

```bash
# High CPU alert
stress-ng --cpu 8 --timeout 10m

# Disk space alert
dd if=/dev/zero of=/tmp/testfile bs=1G count=10
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in repository root:

```bash
# Wiki.js
WIKI_URL=http://localhost:3000/graphql
WIKI_TOKEN=your-api-token
WIKI_BASE_PATH=/projects

# Monitoring
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=admin

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_SERVICE_KEY=your-service-key
```

### Docker Compose Overrides

Create `compose.override.yml` for local customization:

```yaml
version: '3.8'

services:
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=custom_password
    ports:
      - "3000:3000"  # Different port

  prometheus:
    volumes:
      - ./custom-prometheus.yml:/etc/prometheus/prometheus.yml:ro
```

## 📝 Development Workflow

### 1. Make Changes

Edit configuration files in `tools/` directory.

### 2. Test Locally

```bash
# Restart affected service
docker compose -f compose.demo.yml restart prometheus

# View logs
docker compose -f compose.demo.yml logs -f prometheus
```

### 3. Validate

```bash
# Validate Prometheus config
docker exec portfolio-prometheus promtool check config /etc/prometheus/prometheus.yml

# Validate Alertmanager config
docker exec portfolio-alertmanager amtool config show
```

### 4. Commit Changes

```bash
git add tools/
git commit -m "feat: update monitoring configuration"
git push
```

## 🐛 Troubleshooting

### Grafana Can't Connect to Prometheus

```bash
# Check Prometheus is accessible
curl http://localhost:9090/-/healthy

# Check datasource configuration
docker exec portfolio-grafana cat /etc/grafana/provisioning/datasources/datasources.yml

# Restart Grafana
docker compose -f compose.demo.yml restart grafana
```

### Wiki.js Push Fails

```bash
# Test API connectivity
curl -H "Authorization: Bearer $WIKI_TOKEN" \
  http://localhost:3000/graphql \
  -d '{"query": "{ pages { list { id } } }"}'

# Enable debug mode
python -u tools/wikijs_push.py docs/test.md --api-url http://localhost:3000/graphql
```

### Loki Not Receiving Logs

```bash
# Check Loki health
curl http://localhost:3100/ready

# Test log push
curl -X POST http://localhost:3100/loki/api/v1/push \
  -H 'Content-Type: application/json' \
  -d '{"streams":[{"stream":{"job":"test"},"values":[["'$(date +%s)000000000'","test log"]]}]}'
```

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Wiki.js Documentation](https://docs.requarks.io/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)

## 🤝 Contributing

1. Test changes in local Docker environment
2. Update documentation
3. Commit with conventional commit messages
4. Submit pull request with detailed description

---

**Last Updated**: 2025-11-10
**Maintainer**: Portfolio Project Team

---

## 📋 Technical Specifications

### Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Frontend | React / Next.js / Vue | 18.x / 14.x / 3.x | Component-based UI framework |
| Backend | Node.js / FastAPI / Django | 20.x / 0.109+ / 5.x | REST API and business logic |
| Database | PostgreSQL / MySQL | 15.x / 8.x | Relational data store |
| Cache | Redis / Memcached | 7.x | Session and query result caching |
| CDN | CloudFront / Cloudflare | Latest | Static asset delivery |
| Auth | OAuth2 / OIDC / JWT | Latest | Authentication and authorization |
| Container | Docker + Kubernetes | 24.x / 1.28+ | Containerization and orchestration |
| CI/CD | GitHub Actions | Latest | Automated testing and deployment |

### Runtime Requirements

| Requirement | Minimum | Recommended | Notes |
|---|---|---|---|
| CPU | 2 vCPU | 4 vCPU | Scale up for high-throughput workloads |
| Memory | 4 GB RAM | 8 GB RAM | Tune heap/runtime settings accordingly |
| Storage | 20 GB SSD | 50 GB NVMe SSD | Persistent volumes for stateful services |
| Network | 100 Mbps | 1 Gbps | Low-latency interconnect for clustering |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS | RHEL 8/9 also validated |

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | Runtime environment: `development`, `staging`, `production` |
| `LOG_LEVEL` | No | `INFO` | Log verbosity: `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `DB_HOST` | Yes | `localhost` | Primary database host address |
| `DB_PORT` | No | `5432` | Database port number |
| `DB_NAME` | Yes | — | Target database name |
| `DB_USER` | Yes | — | Database authentication username |
| `DB_PASSWORD` | Yes | — | Database password — use a secrets manager in production |
| `API_PORT` | No | `8080` | Application HTTP server listen port |
| `METRICS_PORT` | No | `9090` | Prometheus metrics endpoint port |
| `HEALTH_CHECK_PATH` | No | `/health` | Liveness and readiness probe path |
| `JWT_SECRET` | Yes (prod) | — | JWT signing secret — minimum 32 characters |
| `TLS_CERT_PATH` | No | — | Path to PEM-encoded TLS certificate |
| `TLS_KEY_PATH` | No | — | Path to PEM-encoded TLS private key |
| `TRACE_ENDPOINT` | No | — | OpenTelemetry collector gRPC/HTTP endpoint |
| `CACHE_TTL_SECONDS` | No | `300` | Default cache time-to-live in seconds |

### Configuration Files

| File | Location | Purpose | Managed By |
|---|---|---|---|
| Application config | `./config/app.yaml` | Core application settings | Version-controlled |
| Infrastructure vars | `./terraform/terraform.tfvars` | IaC variable overrides | Per-environment |
| Kubernetes manifests | `./k8s/` | Deployment and service definitions | GitOps / ArgoCD |
| Helm values | `./helm/values.yaml` | Helm chart value overrides | Per-environment |
| CI pipeline | `./.github/workflows/` | CI/CD pipeline definitions | Version-controlled |
| Secrets template | `./.env.example` | Environment variable template | Version-controlled |

---

## 🔌 API & Interface Reference

### Core Endpoints

| Method | Endpoint | Auth | Description | Response |
|---|---|---|---|---|
| `GET` | `/api/v1/users` | Bearer | List users with pagination | 200 OK |
| `POST` | `/api/v1/users` | Bearer | Create a new user | 201 Created |
| `GET` | `/api/v1/users/{id}` | Bearer | Get user by ID | 200 OK |
| `PUT` | `/api/v1/users/{id}` | Bearer | Update user attributes | 200 OK |
| `DELETE` | `/api/v1/users/{id}` | Bearer | Delete a user (soft delete) | 204 No Content |
| `POST` | `/api/v1/auth/login` | None | Authenticate and receive JWT | 200 OK |
| `GET` | `/health` | None | Health check endpoint | 200 OK |

### Authentication Flow

This project uses Bearer token authentication for secured endpoints:

1. **Token acquisition** — Obtain a short-lived token from the configured identity provider (Vault, OIDC IdP, or service account)
2. **Token format** — JWT with standard claims (`sub`, `iat`, `exp`, `aud`)
3. **Token TTL** — Default 1 hour; configurable per environment
4. **Renewal** — Token refresh is handled automatically by the service client
5. **Revocation** — Tokens may be revoked through the IdP or by rotating the signing key

> **Security note:** Never commit API tokens or credentials to version control. Use environment variables or a secrets manager.

---

## 📊 Data Flow & Integration Patterns

### Primary Data Flow

```mermaid
flowchart TD
  A[Input Source / Trigger] --> B[Ingestion / Validation Layer]
  B --> C{Valid?}
  C -->|Yes| D[Core Processing Engine]
  C -->|No| E[Error Queue / DLQ]
  D --> F[Transformation / Enrichment]
  F --> G[Output / Storage Layer]
  G --> H[Downstream Consumers]
  E --> I[Alert + Manual Review Queue]
  H --> J[Monitoring / Feedback Loop]
```

### Integration Touchpoints

| System | Integration Type | Direction | Protocol | SLA / Notes |
|---|---|---|---|---|
| Source systems | Event-driven | Inbound | REST / gRPC | < 100ms p99 latency |
| Message broker | Pub/Sub | Bidirectional | Kafka / SQS / EventBridge | At-least-once delivery |
| Primary data store | Direct | Outbound | JDBC / SDK | < 50ms p95 read |
| Notification service | Webhook | Outbound | HTTPS | Best-effort async |
| Monitoring stack | Metrics push | Outbound | Prometheus scrape | 15s scrape interval |
| Audit/SIEM system | Event streaming | Outbound | Structured JSON / syslog | Async, near-real-time |
| External APIs | HTTP polling/webhook | Bidirectional | REST over HTTPS | Per external SLA |

---

## 📈 Performance & Scalability

### Performance Targets

| Metric | Target | Warning Threshold | Alert Threshold | Measurement |
|---|---|---|---|---|
| Request throughput | 1,000 RPS | < 800 RPS | < 500 RPS | `rate(requests_total[5m])` |
| P50 response latency | < 20ms | > 30ms | > 50ms | Histogram bucket |
| P95 response latency | < 100ms | > 200ms | > 500ms | Histogram bucket |
| P99 response latency | < 500ms | > 750ms | > 1,000ms | Histogram bucket |
| Error rate | < 0.1% | > 0.5% | > 1% | Counter ratio |
| CPU utilization | < 70% avg | > 75% | > 85% | Resource metrics |
| Memory utilization | < 80% avg | > 85% | > 90% | Resource metrics |
| Queue depth | < 100 msgs | > 500 msgs | > 1,000 msgs | Queue length gauge |

### Scaling Strategy

| Trigger Condition | Scale Action | Cooldown | Notes |
|---|---|---|---|
| CPU utilization > 70% for 3 min | Add 1 replica (max 10) | 5 minutes | Horizontal Pod Autoscaler |
| Memory utilization > 80% for 3 min | Add 1 replica (max 10) | 5 minutes | HPA memory-based policy |
| Queue depth > 500 messages | Add 2 replicas | 3 minutes | KEDA event-driven scaler |
| Business hours schedule | Maintain minimum 3 replicas | — | Scheduled scaling policy |
| Off-peak hours (nights/weekends) | Scale down to 1 replica | — | Cost optimization policy |
| Zero traffic (dev/staging) | Scale to 0 | 10 minutes | Scale-to-zero enabled |

---

## 🔍 Monitoring & Alerting

### Key Metrics Emitted

| Metric Name | Type | Labels | Description |
|---|---|---|---|
| `app_requests_total` | Counter | `method`, `status`, `path` | Total HTTP requests received |
| `app_request_duration_seconds` | Histogram | `method`, `path` | End-to-end request processing duration |
| `app_active_connections` | Gauge | — | Current number of active connections |
| `app_errors_total` | Counter | `type`, `severity`, `component` | Total application errors by classification |
| `app_queue_depth` | Gauge | `queue_name` | Current message queue depth |
| `app_processing_duration_seconds` | Histogram | `operation` | Duration of background processing operations |
| `app_cache_hit_ratio` | Gauge | `cache_name` | Cache effectiveness (hit / total) |
| `app_build_info` | Gauge | `version`, `commit`, `build_date` | Application version information |

### Alert Definitions

| Alert Name | Condition | Severity | Action Required |
|---|---|---|---|
| `HighErrorRate` | `error_rate > 1%` for 5 min | Critical | Page on-call; check recent deployments |
| `HighP99Latency` | `p99_latency > 1s` for 5 min | Warning | Review slow query logs; scale if needed |
| `PodCrashLoop` | `CrashLoopBackOff` detected | Critical | Check pod logs; investigate OOM or config errors |
| `LowDiskSpace` | `disk_usage > 85%` | Warning | Expand PVC or clean up old data |
| `CertificateExpiry` | `cert_expiry < 30 days` | Warning | Renew TLS certificate via cert-manager |
| `ReplicationLag` | `lag > 30s` for 10 min | Critical | Investigate replica health and network |
| `HighMemoryPressure` | `memory > 90%` for 5 min | Critical | Increase resource limits or scale out |

### Dashboards

| Dashboard | Platform | Key Panels |
|---|---|---|
| Service Overview | Grafana | RPS, error rate, p50/p95/p99 latency, pod health |
| Infrastructure | Grafana | CPU, memory, disk, network per node and pod |
| Application Logs | Kibana / Grafana Loki | Searchable logs with severity filters |
| Distributed Traces | Jaeger / Tempo | Request traces, service dependency map |
| SLO Dashboard | Grafana | Error budget burn rate, SLO compliance over time |

---

## 🚨 Incident Response & Recovery

### Severity Classification

| Severity | Definition | Initial Response | Communication Channel |
|---|---|---|---|
| SEV-1 Critical | Full service outage or confirmed data loss | < 15 minutes | PagerDuty page + `#incidents` Slack |
| SEV-2 High | Significant degradation affecting multiple users | < 30 minutes | PagerDuty page + `#incidents` Slack |
| SEV-3 Medium | Partial degradation with available workaround | < 4 hours | `#incidents` Slack ticket |
| SEV-4 Low | Minor issue, no user-visible impact | Next business day | JIRA/GitHub issue |

### Recovery Runbook

**Step 1 — Initial Assessment**

```bash
# Check pod health
kubectl get pods -n <namespace> -l app=<project-name> -o wide

# Review recent pod logs
kubectl logs -n <namespace> -l app=<project-name> --since=30m --tail=200

# Check recent cluster events
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | tail -30

# Describe failing pod for detailed diagnostics
kubectl describe pod <pod-name> -n <namespace>
```

**Step 2 — Health Validation**

```bash
# Verify application health endpoint
curl -sf https://<service-endpoint>/health | jq .

# Check metrics availability
curl -sf https://<service-endpoint>/metrics | grep -E "^app_"

# Run automated smoke tests
./scripts/smoke-test.sh --env <environment> --timeout 120
```

**Step 3 — Rollback Procedure**

```bash
# Initiate deployment rollback
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# Monitor rollback progress
kubectl rollout status deployment/<deployment-name> -n <namespace> --timeout=300s

# Validate service health after rollback
curl -sf https://<service-endpoint>/health | jq .status
```

**Step 4 — Post-Incident**

- [ ] Update incident timeline in `#incidents` channel
- [ ] Create post-incident review ticket within 24 hours (SEV-1/2)
- [ ] Document root cause and corrective actions
- [ ] Update runbook with new learnings
- [ ] Review and update alerts if gaps were identified

---

## 🛡️ Compliance & Regulatory Controls

### Control Mappings

| Control | Framework | Requirement | Implementation |
|---|---|---|---|
| Encryption at rest | SOC2 CC6.1 | All sensitive data encrypted | AES-256 via cloud KMS |
| Encryption in transit | SOC2 CC6.7 | TLS 1.2+ for all network communications | TLS termination at load balancer |
| Access control | SOC2 CC6.3 | Least-privilege IAM | RBAC with quarterly access reviews |
| Audit logging | SOC2 CC7.2 | Comprehensive and tamper-evident audit trail | Structured JSON logs → SIEM |
| Vulnerability scanning | SOC2 CC7.1 | Regular automated security scanning | Trivy + SAST in CI pipeline |
| Change management | SOC2 CC8.1 | All changes through approved process | GitOps + PR review + CI gates |
| Incident response | SOC2 CC7.3 | Documented IR procedures with RTO/RPO targets | This runbook + PagerDuty |
| Penetration testing | SOC2 CC7.1 | Annual third-party penetration test | External pentest + remediation |

### Data Classification

| Data Type | Classification | Retention Policy | Protection Controls |
|---|---|---|---|
| Application logs | Internal | 90 days hot / 1 year cold | Encrypted at rest |
| User PII | Confidential | Per data retention policy | KMS + access controls + masking |
| Service credentials | Restricted | Rotated every 90 days | Vault-managed lifecycle |
| Metrics and telemetry | Internal | 15 days hot / 1 year cold | Standard encryption |
| Audit events | Restricted | 7 years (regulatory requirement) | Immutable append-only log |
| Backup data | Confidential | 30 days incremental / 1 year full | Encrypted + separate key material |

---

## 👥 Team & Collaboration

### Project Ownership

| Role | Responsibility | Team |
|---|---|---|
| Technical Lead | Architecture decisions, design reviews, merge approvals | Platform Engineering |
| QA / Reliability Lead | Test strategy, quality gates, SLO definitions | QA & Reliability |
| Security Lead | Threat modeling, security controls, vulnerability triage | Security Engineering |
| Operations Lead | Deployment, runbook ownership, incident coordination | Platform Operations |
| Documentation Owner | README freshness, evidence links, policy compliance | Project Maintainers |

### Development Workflow

```mermaid
flowchart LR
  A[Feature Branch] --> B[Local Tests Pass]
  B --> C[Pull Request Opened]
  C --> D[Automated CI Pipeline]
  D --> E[Security Scan + Lint]
  E --> F[Peer Code Review]
  F --> G[Merge to Main]
  G --> H[CD to Staging]
  H --> I[Acceptance Tests]
  I --> J[Production Deploy]
  J --> K[Post-Deploy Monitoring]
```

### Contribution Checklist

Before submitting a pull request to this project:

- [ ] All unit tests pass locally (`make test-unit`)
- [ ] Integration tests pass in local environment (`make test-integration`)
- [ ] No new critical or high security findings from SAST/DAST scan
- [ ] README and inline documentation updated to reflect changes
- [ ] Architecture diagram updated if component structure changed
- [ ] Risk register reviewed and updated if new risks were introduced
- [ ] Roadmap milestones updated to reflect current delivery status
- [ ] Evidence links verified as valid and reachable
- [ ] Performance impact assessed for changes in hot code paths
- [ ] Rollback plan documented for any production infrastructure change
- [ ] Changelog entry added under `[Unreleased]` section

---

## 📚 Extended References

### Internal Documentation

| Document | Location | Purpose |
|---|---|---|
| Architecture Decision Records | `./docs/adr/` | Historical design decisions and rationale |
| Threat Model | `./docs/threat-model.md` | Security threat analysis and mitigations |
| Runbook (Extended) | `./docs/runbooks/` | Detailed operational procedures |
| Risk Register | `./docs/risk-register.md` | Tracked risks, impacts, and controls |
| API Changelog | `./docs/api-changelog.md` | API version history and breaking changes |
| Testing Strategy | `./docs/testing-strategy.md` | Full test pyramid definition |

### External References

| Resource | Description |
|---|---|
| [12-Factor App](https://12factor.net) | Cloud-native application methodology |
| [OWASP Top 10](https://owasp.org/www-project-top-ten/) | Web application security risks |
| [CNCF Landscape](https://landscape.cncf.io) | Cloud-native technology landscape |
| [SRE Handbook](https://sre.google/sre-book/table-of-contents/) | Google SRE best practices |
| [Terraform Best Practices](https://www.terraform-best-practices.com) | IaC conventions and patterns |
| [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) | Security controls framework |

# Portfolio Master Index – Final Complete Edition

## 4.1.8 Observability – Monitoring, Logging, and Alerting

### Monitoring Stack Architecture
```
Tier 1 – Collection: node_exporter, cAdvisor, blackbox_exporter, custom exporters, Promtail, Syslog-ng, structured JSON logs.
Tier 2 – Storage: Prometheus (90d retention), Loki (30–90d by label), Alertmanager.
Tier 3 – Visualization: Grafana with Prometheus/Loki datasources, LDAP+MFA, 15+ dashboards.
```

### Prometheus Configuration
- Global scrape/evaluation interval: 60s (critical targets 30s/15s).
- Jobs for Prometheus self-monitoring, nodes, cAdvisor, blackbox probes, TrueNAS exporter, UniFi exporter.
- External labels annotate cluster/datacenter/environment.

### Grafana Dashboards
- **Homelab Infrastructure Overview:** CPU/memory/disk/network stat panels + time-series trends.
- **Service Health & SLO Tracking:** Service uptime table (30-day rolling), p95 latency, HTTP error rate, request volume.
- **Capacity Planning:** Storage growth, CPU utilization trends, bandwidth forecasting.

### Alerting (SLO-Focused)
- Burn-rate alerts: Critical when consuming 1% error budget/hour, warning at slower burn.
- ServiceDown fallback for absolute outages.
- Infrastructure alerts for host down, high CPU/memory, disk space.
- Security alerts (SSH brute force, CrowdSec threats).

### Alertmanager Routing
- Critical severity → PagerDuty + email.
- Warning → Email + Slack (#homelab-alerts).
- Info → Slack-only.
- Security alerts → dedicated #security-alerts.
- Inhibition suppresses downstream alerts (e.g., host down suppresses service alerts).

### Loki & Promtail
- Loki boltdb-shipper backend, filesystem storage, 90-day retention.
- Promtail scrapes system logs, Docker logs, app logs, nginx logs, auth logs with JSON parsing.
- LogQL queries for errors, HTTP 5xx, OOM detection, container restarts.

### Runbooks & MTTR
- Example Service OOM runbook includes detection, restart procedures, validation, and post-incident actions.
- Runbooks cut MTTR from 45 to 15 minutes (67% improvement) and standardize responses.

### Capacity Planning
- Predictive Grafana panels using `predict_linear` for disk growth, CPU trends, memory growth, bandwidth peaks.
- Alerts when predicted capacity breaches thresholds (e.g., <100GB free within 30 days).

### Interview Narrative
- Emphasize SLO/SLI/error budget approach, alert fatigue reduction, MTTR improvement proof.

---

## 4.2 Automation & DevOps

### 4.2.1 GitHub Actions Multi-Stage CI/CD Pipeline
- **Stages:** Build → Test → Package → Deploy (staging) → Deploy (production) with manual approval.
- Quality gates: linting, unit/integration tests (80% coverage min), npm audit, Trivy image scan, smoke tests.
- Packaging: Docker Buildx pushing to GHCR with semantic tags.
- Deployment: Kubernetes blue-green strategy with health checks, auto-rollback, Slack notifications.
- **Metrics:** Deployment time 2h → 12m (80% faster), 0% prod failures in 6 months, 240+ hours/month reclaimed.

### 4.2.2 Terraform Multi-Cloud IaC
- Modular structure (`modules/vpc`, `modules/compute`, etc.) with environment overlays (dev/staging/prod).
- Remote state via S3 + DynamoDB locking; drift detection with `terraform plan -detailed-exitcode`.
- Cost estimation using Infracost (NAT optimization, reserved instances suggestions).
- **Benefits:** Reproducible environments, audit trail, consistent tagging, ability to revert manual drift.

---

## 4.3 Observability & Reliability Projects

### 4.3.1 SLO-Based Alerting & On-Call Runbooks
- Defined SLIs/SLOs (e.g., Immich 99.5% availability, 216-minute error budget).
- Multi-window, multi-burn-rate alerts (fast burn critical, slow burn warning) plus absolute downtime backup.
- Comprehensive runbooks (Immich Service Down, Container OOM, NFS failures) with detection, diagnosis, resolution, validation, and post-incident actions.
- Runbook metrics: MTTR dropped 45m → 15m, consistent outcomes across engineers.

---

## 4.4 Innovation & Research Highlights
- AstraDup multi-modal AI deduplication (perceptual hash + CLIP embeddings + audio fingerprinting + metadata fusion).
- Emphasis on hybrid solutions, evaluation metrics, and interview narratives for learning new domains.

---

## 5. Project Cross-Reference Map
- Tables aligning Systems Development Engineer, Solutions Architect, SRE, and DevOps role requirements with portfolio projects, evidence links, and talking points.

---

## 6. Technical Implementation Evidence
- Tiered evidence strategy (screenshots, config files, metrics) with repository structure guidance.
- Sample Grafana JSON exports, fio benchmark logs, OpenSCAP security scan results.

---

## 7. Interview Question Mapping
- STAR responses for reliability improvements, trade-off decisions, automation wins.
- Technical deep-dives covering monitoring design and SSH hardening.

---

## 8. Evidence & Metrics Dashboard
- Portfolio-wide KPI tables for cost, reliability, security, automation, performance.
- Detailed cost savings (homelab vs AWS, backup automation, CI/CD), uptime and incident logs, security metrics, automation ROI.

---

## 9. Open Source Contributions
- Documented contributions/PRs (Prometheus node_exporter, Grafana docs, Loki retention, TrueNAS exporter, Fail2Ban docs) plus community engagement.

---

## 10. Knowledge Sharing & Mentorship
- Blog output (top posts, traffic), Wiki.js documentation volume, mentorship outcomes for three mentees, internal workshops.

---

## 11. Continuous Learning Roadmap
- Quarterly goals for AWS depth, Kubernetes, advanced observability/chaos, ML/MLOps.
- Certification plan (AWS SAA, CKAD, PCA, CKA), budget/time allocation, emerging tech radar, success metrics.

---

## Conclusion
- Summarizes infrastructure, automation, observability, learning, leadership accomplishments.
- Provides contact info and readiness statement (Version 3.0 Final Complete, Jan 11 2026, ~45k words).

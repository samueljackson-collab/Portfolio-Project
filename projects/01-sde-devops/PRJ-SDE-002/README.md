# PRJ-SDE-002: Observability & Backups Stack

**Status:** 🟢 Completed (Documentation Pending)
**Category:** System Development Engineering / DevOps
**Technologies:** Prometheus, Grafana, Loki, Alertmanager, Proxmox Backup Server

---

## Overview

Implemented a comprehensive monitoring, logging, and alerting stack to observe homelab infrastructure and ensure data resilience through automated backups.

## Architecture

### Monitoring (Prometheus)
- Metrics collection from multiple targets
- Node exporter for system metrics (CPU, memory, disk, network)
- Proxmox exporter for hypervisor metrics
- Service-specific exporters (PostgreSQL, Redis, etc.)
- Retention and storage configuration

### Visualization (Grafana)
- Pre-built and custom dashboards
- Golden signals: latency, traffic, errors, saturation
- System health overview
- Per-service detailed views
- Annotations for deployments and incidents

### Logging (Loki)
- Centralized log aggregation
- LogQL for querying and filtering logs
- Integration with Grafana for unified interface
- Log retention policies
- Promtail agents for log shipping

### Alerting (Alertmanager)
- Alert routing and grouping
- Notification channels (email, Slack, PagerDuty)
- Silencing and inhibition rules
- Alert templates and severity levels
- On-call rotation support (if applicable)

### Backup (Proxmox Backup Server)
- Incremental backup of VMs and containers
- Deduplication to save storage
- Encryption at rest
- Scheduled backup jobs
- Retention policies and pruning

## Key Dashboards

### Infrastructure Overview
- Cluster resource utilization
- Network throughput
- Storage capacity and IOPS
- Uptime tracking

### Service Health
- HTTP response times and error rates
- Database query performance
- Queue depths and processing rates
- Cache hit ratios

### Alerting Dashboard
- Active alerts summary
- Alert history and trends
- Mean time to acknowledge (MTTA)
- Mean time to resolve (MTTR)

## Alert Examples

### Critical Alerts
- Host down or unreachable
- Disk usage >90%
- Memory usage >95%
- Backup job failures
- SSL certificate expiration <7 days

### Warning Alerts
- Disk usage >80%
- High CPU sustained >80% for 15 minutes
- Backup job duration increasing
- Log error rate spike

## Backup Configuration

### Schedule
- **Daily:** All VMs and containers (incremental)
- **Weekly:** Full backup verification
- **Monthly:** Backup restore test

### Retention Policy
- **Daily backups:** Keep 7 days
- **Weekly backups:** Keep 4 weeks
- **Monthly backups:** Keep 3 months

### Verification
- Automated backup integrity checks
- Monthly restore drills
- Documentation of restore procedures

## Skills Demonstrated

- Metrics collection and time-series databases
- Dashboard design and visualization
- Log aggregation and analysis
- Alert design and tuning (reducing noise)
- Backup automation and verification
- Observability best practices (SLIs, SLOs, SLAs)

## Observability Philosophy

Following the **USE Method** (Utilization, Saturation, Errors):
- **Utilization:** How busy is the resource?
- **Saturation:** How much extra work is queued?
- **Errors:** What errors are occurring?

And the **RED Method** (Rate, Errors, Duration) for services:
- **Rate:** Requests per second
- **Errors:** Failed requests per second
- **Duration:** Response time distribution

## Documentation Status

📝 **Pending:** Dashboard exports, Prometheus configurations, alert rule examples, and backup logs are being prepared and will be added to the `assets/` directory.

## Future Enhancements

- Distributed tracing with Tempo or Jaeger
- Synthetic monitoring (uptime checks)
- Anomaly detection with machine learning
- Cost tracking dashboards
- SLO tracking and error budgets

---

**Last Updated:** October 28, 2025

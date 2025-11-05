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

## How It Works

1. **Provision Prometheus and exporters** on the Proxmox host, followed by Node Exporter installation on all VMs and containers.
2. **Deploy Grafana** once Prometheus is scraping data to verify dashboards render correctly.
3. **Configure Loki and Promtail** to begin ingesting logs alongside metrics.
4. **Set up Alertmanager** with notification channels and connect it to Prometheus.
5. **Integrate PBS** nightly jobs and mount TrueNAS NFS shares for resilient storage.

**Configuration Locations**
- Prometheus: `/etc/prometheus/prometheus.yml`, alert rules in `/etc/prometheus/alerts/`
- Grafana dashboards: `/etc/grafana/provisioning/dashboards/`
- Loki: `/etc/loki/loki-config.yml`
- Promtail: `/etc/promtail/promtail-config.yml`
- Alertmanager: `/etc/alertmanager/alertmanager.yml`

**Service Management**
- `sudo systemctl enable --now prometheus`
- `sudo systemctl enable --now grafana-server`
- `sudo systemctl enable --now loki`
- `sudo systemctl enable --now promtail`
- `sudo systemctl enable --now alertmanager`
- `sudo systemctl enable --now proxmox-backup`

**Data Flow Overview**
`Logs & Metrics → Promtail/Exporters → Prometheus & Loki → Alertmanager & Grafana`

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

## Alert Examples and Responses

| Alert Name | Trigger Condition | Severity | Response Time | Runbook |
|------------|-------------------|----------|---------------|---------|
| HostDown | `up == 0` for 2 minutes | Critical | 5 minutes | [HostDown](https://runbooks.homelab.local/HostDown) |
| HighCPUUsage | CPU >80% for 15 minutes | Warning | 30 minutes | [HighCPUUsage](https://runbooks.homelab.local/HighCPUUsage) |
| DiskSpaceLow | Free space <15% | Warning | 1 hour | [DiskSpaceLow](https://runbooks.homelab.local/DiskSpaceLow) |
| BackupJobFailed | `proxmox_backup_job_last_status != 0` | Critical | 15 minutes | [BackupJobFailed](https://runbooks.homelab.local/BackupJobFailed) |
| ServiceUnreachable | `probe_success == 0` for 5 minutes | Critical | 10 minutes | [ServiceUnreachable](https://runbooks.homelab.local/ServiceUnreachable) |

**Example Slack Payload**
```json
{
  "status": "firing",
  "receiver": "critical-all",
  "alerts": [
    {
      "labels": {
        "alertname": "HostDown",
        "instance": "192.168.1.21:9100",
        "severity": "critical"
      },
      "annotations": {
        "summary": "Host 192.168.1.21:9100 is unreachable",
        "description": "Prometheus has not scraped 192.168.1.21:9100 for over two minutes. Investigate network connectivity or system health.",
        "runbook": "https://runbooks.homelab.local/HostDown"
      }
    }
  ],
  "groupLabels": {
    "alertname": "HostDown"
  },
  "commonLabels": {
    "environment": "homelab",
    "cluster": "main"
  }
}
```

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

## Backup and Recovery Procedures

**Schedule**
- Nightly backups at 02:00 via Proxmox Backup Server job schedule.
- Weekly verification tasks run on Sundays to validate snapshot integrity.
- Monthly restore rehearsals verify end-to-end recovery steps.

**Scope of Backups**
- VMs: 192.168.1.20-24 (Wiki.js, Home Assistant, Immich, database, utility).
- Containers: 192.168.1.30-32 (supporting services).
- Configuration directories exported from `/etc/` for Prometheus, Grafana, Loki, and Alertmanager.

**Retention Policy**
- 7 daily restore points, 4 weekly rollups, 3 monthly archives retained on PBS.

**Recovery Steps**
1. Log in to PBS web UI at `https://192.168.1.15:8007`.
2. Select the desired snapshot for the VM or container.
3. Restore to the original ID or clone to a staging ID for validation.
4. Power on the restored workload and confirm service availability.
5. Re-run Prometheus `ServiceUnreachable` probes to ensure monitoring reflects the recovered service.

**Automation Support**
- Backup verification script: [`verify-pbs-backups.sh`](./assets/scripts/verify-pbs-backups.sh).

## Metrics Cheat Sheet

| Metric Goal | Prometheus Query | Expected Result |
|-------------|------------------|-----------------|
| CPU usage per host | `100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` | Percentage utilization |
| Memory available | `node_memory_MemAvailable_bytes` | Bytes available |
| Disk space used | `100 - ((node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100)` | Percentage used |
| Network traffic | `rate(node_network_receive_bytes_total[5m])` | Bytes per second |
| Backup job status | `proxmox_backup_job_last_status` | 0 = OK, 1 = error |

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

## Lessons Learned

- Started with InfluxDB but migrated to Prometheus for richer querying and community support.
- Initial 5-second scrape interval filled disk quickly; 15 seconds balanced granularity with retention.
- Alert fatigue required tuning thresholds, adding inhibition rules, and documenting runbooks.
- The backup verification script surfaced incomplete snapshots that PBS UI marked as successful.
- Standardizing dashboards accelerated onboarding for new homelab contributors.

## Future Enhancements

- Distributed tracing with Tempo or Jaeger
- Synthetic monitoring (uptime checks)
- Anomaly detection with machine learning
- Cost tracking dashboards
- SLO tracking and error budgets

## 📸 Evidence Gallery

![Infrastructure Overview Dashboard](./assets/screenshots/grafana-infrastructure-dashboard.png)
*Grafana dashboard showing CPU, memory, disk, and network metrics across all homelab hosts*

![Active Alerts Panel](./assets/screenshots/grafana-alerts-panel.png)
*Alerting panel showing current firing alerts with severity levels*

![Prometheus Targets](./assets/screenshots/prometheus-targets.png)
*Prometheus targets page showing all scrape endpoints with UP status*

---

**Last Updated:** October 28, 2025

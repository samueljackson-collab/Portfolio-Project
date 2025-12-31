# PRJ-SDE-002: Observability & Backups Stack

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../../DOCUMENTATION_INDEX.md).


**Status:** 🟢 Completed  
**Category:** System Development Engineering / DevOps  
**Technologies:** Prometheus, Grafana, Loki, Alertmanager, Proxmox Backup Server

Comprehensive monitoring, logging, alerting, and backup automation for the homelab portfolio. The stack is designed around the USE/RED philosophies, emphasizes alert hygiene with linked runbooks, and documents PBS backup posture with verification evidence.

## Quick Links
- [Assets Index](./assets/README.md)
- [Monitoring Philosophy (USE/RED)](./assets/docs/monitoring-philosophy.md)
- [Alert Runbooks](./assets/runbooks/ALERT_RESPONSES.md)
- [Operational Runbook](./assets/runbooks/OPERATIONAL_RUNBOOK.md)
- [Grafana Dashboards](./assets/grafana/dashboards)
- [Screenshots](./assets/screenshots)
- [Log Samples](./assets/logs)
- [Prometheus/Alertmanager/Loki/Promtail Configs](./assets/configs)
- [PBS Jobs & Retention Evidence](./assets/backups)
- [Parent Documentation](../../../README.md)

**Sanitization:** All artifacts use placeholder hosts/webhooks and demo data. Screenshots are scrubbed; configs omit credentials.

Monitoring, logging, alerting, and backup stack built with Prometheus, Grafana, Loki, Alertmanager, Promtail, and Proxmox Backup Server (PBS). All assets are sanitized for portfolio sharing.

## Overview
Implemented a comprehensive monitoring, logging, and alerting stack to observe homelab infrastructure and ensure data resilience through automated backups.

## Architecture

## Architecture Snapshot
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
5. **Integrate PBS** nightly jobs and mount NAS shares for resilient storage.

**Configuration Locations (portfolio mirrors)**:
- Prometheus: [`assets/configs/prometheus.yml`](./assets/configs/prometheus.yml), alert rules in [`assets/configs/alerts/`](./assets/configs/alerts/)
- Grafana dashboards: [`assets/grafana/dashboards/`](./assets/grafana/dashboards/)
- Loki: [`assets/loki/loki-config.yml`](./assets/loki/loki-config.yml)
- Promtail: [`assets/loki/promtail-config.yml`](./assets/loki/promtail-config.yml)
- Alertmanager: [`assets/alertmanager/alertmanager.yml`](./assets/alertmanager/alertmanager.yml)

**Service Management (example)**:
- `sudo systemctl enable --now prometheus`
- `sudo systemctl enable --now grafana-server`
- `sudo systemctl enable --now loki`
- `sudo systemctl enable --now promtail`
- `sudo systemctl enable --now alertmanager`
- `sudo systemctl enable --now proxmox-backup`

**Network Flow Architecture**:
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Targets   │────▶│  Exporters  │────▶│ Prometheus  │
│ (VMs/Hosts) │     │ (Port 9100+)│     │ (Port 9090) │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                              │
                   ┌──────────────────────────┼──────────────────────────┐
                   │                          │                          │
                   ▼                          ▼                          ▼
           ┌───────────────┐         ┌──────────────┐         ┌─────────────┐
           │ Alertmanager  │         │   Grafana    │         │    Loki     │
           │  (Port 9093)  │         │ (Port 3000)  │         │ (Port 3100) │
           └───────┬───────┘         └──────────────┘         └──────┬──────┘
                   │                                                  │
                   ▼                                                  ▼
           ┌───────────────┐                                  ┌─────────────┐
           │ Slack/Email   │                                  │  Promtail   │
           │ Notifications │                                  │  (Logs)     │
           └───────────────┘                                  └─────────────┘
```

**Data Flow Overview**
1. **Metrics Collection**: Node Exporters (9100), Proxmox Exporter (9221), and application-specific exporters expose metrics.
2. **Log Shipping**: Promtail agents tail log files and push to Loki (port 3100).
3. **Scraping**: Prometheus scrapes all exporters every 15 seconds, evaluates alert rules every 30 seconds.
4. **Storage**: Prometheus stores metrics locally with 30-day retention; Loki stores logs with 14-day retention.
5. **Alerting**: Alertmanager receives alerts from Prometheus, groups/routes them to Slack channel #homelab-alerts.
6. **Visualization**: Grafana queries Prometheus and Loki, renders dashboards on port 3000.
7. **Backup**: PBS runs nightly at 02:00, snapshots are stored on TrueNAS NFS share at <NFS_SERVER>:/mnt/<DATASTORE>/backups.

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

## Alert Examples and Responses (Sanitized)
| Alert Name | Trigger Condition | Severity | Response Time | Runbook |
|------------|-------------------|----------|---------------|---------|
| HostDown | `up == 0` for 2 minutes | Critical | 5 minutes | [HostDown](./assets/runbooks/OPERATIONAL_RUNBOOK.md#alert-hostdown) |
| HighCPUUsage | CPU >80% for 15 minutes | Warning | 30 minutes | [HighCPUUsage](./assets/runbooks/OPERATIONAL_RUNBOOK.md#alert-highcpuusage) |
| DiskSpaceLow | Free space <15% | Warning | 1 hour | [DiskSpaceLow](./assets/runbooks/OPERATIONAL_RUNBOOK.md#alert-diskspacelow) |
| BackupJobFailed | `proxmox_backup_job_last_status != 0` | Critical | 15 minutes | [BackupJobFailed](./assets/runbooks/OPERATIONAL_RUNBOOK.md#alert-backupjobfailed) |
| ServiceUnreachable | `probe_success == 0` for 5 minutes | Critical | 10 minutes | [Service Recovery](./assets/runbooks/OPERATIONAL_RUNBOOK.md#service-recovery) |

**Example Slack Payload (Sanitized)**
```json
{
  "status": "firing",
  "receiver": "critical-all",
  "alerts": [
    {
      "labels": {
        "alertname": "HostDown",
        "instance": "demo-vm-01:9100",
        "severity": "critical"
      },
      "annotations": {
        "summary": "Host demo-vm-01:9100 is unreachable",
        "description": "Prometheus has not scraped demo-vm-01:9100 for over two minutes. Investigate network connectivity or system health.",
        "runbook": "assets/runbooks/OPERATIONAL_RUNBOOK.md#alert-hostdown"
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

## Configurations
- **Prometheus:** [`assets/configs/prometheus.yml`](./assets/configs/prometheus.yml) plus [`configs/alerts/demo-alerts.yml`](./assets/configs/alerts/demo-alerts.yml) and recording rules.
- **Alertmanager:** [`assets/alertmanager/alertmanager.yml`](./assets/alertmanager/alertmanager.yml) uses environment variables for secrets and generic notification channels.
- **Loki & Promtail:** [`assets/loki/loki-config.yml`](./assets/loki/loki-config.yml) and [`assets/loki/promtail-config.yml`](./assets/loki/promtail-config.yml) with log scrubbing and tenant labels.

## Backups & PBS Evidence
- Job manifest, retention report, and restore checklist under [`assets/pbs/`](./assets/pbs) with supporting guidance in [`backups-and-lessons.md`](./assets/docs/backups-and-lessons.md).
- Metrics and alerts surface backup success ratios and retention drift (see `alerting-backup-overview.json`).

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
- VMs and containers in the homelab cluster (sanitized inventory in [`pbs-job-manifest.yml`](./assets/pbs/pbs-job-manifest.yml)).
- Configuration directories exported from `/etc/` for Prometheus, Grafana, Loki, and Alertmanager (represented in this repo as configs).

**Retention Policy**
- 7 daily restore points, 4 weekly rollups, 3 monthly archives retained on PBS.

**Recovery Steps**
1. Log in to PBS web UI (sanitized).
2. Select the desired snapshot for the VM or container.
3. Restore to the original ID or clone to a staging ID for validation.
4. Power on the restored workload and confirm service availability.
5. Re-run Prometheus `ServiceUnreachable` probes to ensure monitoring reflects the recovered service.

**Automation Support**
- Backup verification script: [`verify-pbs-backups.sh`](./assets/scripts/verify-pbs-backups.sh) (see notes in `backups-and-lessons.md`).

## Metrics Cheat Sheet
### Essential PromQL Queries
| Metric Goal | Prometheus Query | Expected Result |
|-------------|------------------|-----------------|
| CPU usage per host | `100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)` | Percentage utilization |
| Memory available | `node_memory_MemAvailable_bytes / 1024 / 1024 / 1024` | GB available |
| Memory utilization % | `100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))` | Percentage used |
| Disk space used | `100 - ((node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|fuse.lxcfs"}) * 100)` | Percentage used |
| Disk I/O rate | `rate(node_disk_read_bytes_total[5m]) + rate(node_disk_written_bytes_total[5m])` | Bytes per second |
| Network traffic inbound | `rate(node_network_receive_bytes_total{device!~"lo|veth.*"}[5m])` | Bytes per second |
| Network traffic outbound | `rate(node_network_transmit_bytes_total{device!~"lo|veth.*"}[5m])` | Bytes per second |
| System load average | `node_load1 / count(node_cpu_seconds_total{mode="idle"})` | Load per CPU core |
| Backup job status | `proxmox_backup_job_last_status` | 0 = OK, 1 = error |
| HTTP request rate | `sum(rate(http_requests_total[5m])) by (service)` | Requests per second |
| HTTP error rate | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))` | Error ratio (0-1) |
| Service uptime | `time() - process_start_time_seconds` | Seconds since start |

### Recording Rules (Pre-computed Metrics)
```yaml
# /etc/prometheus/recording_rules.yml
groups:
  - name: homelab_aggregations
    interval: 60s
    rules:
      - record: instance:node_cpu_utilization:rate5m
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

      - record: instance:node_memory_utilization:ratio
        expr: 1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)

      - record: instance:node_disk_utilization:ratio
        expr: 1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"} / node_filesystem_size_bytes{fstype!~"tmpfs|fuse.lxcfs"})

      - record: job:http_request_rate:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)

      - record: job:http_error_rate:rate5m
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) by (job) / sum(rate(http_requests_total[5m])) by (job)
```

**Usage Notes:**
- Recording rules reduce dashboard load time by pre-computing complex queries.
- Stored with 5-minute granularity for 90 days.
- Used in high-traffic dashboards and alerting rules.

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

📝 Dashboard exports, Prometheus configurations, alert rule examples, and backup evidence are provided in the `assets/` directory, including sanitized configs, screenshots, and PBS retention artifacts.

## Lessons Learned

### Technical Insights
1. **Metrics Backend Selection**: Started with InfluxDB but migrated to Prometheus for richer querying (PromQL), better alerting integration, and stronger community support. The migration took 3 days but improved query performance by ~40%.
2. **Scrape Interval Optimization**: Initial 5-second scrape interval filled disk quickly (80GB in 2 weeks). Settled on 15-second intervals which balanced granularity with 30-day retention, reducing storage to 12GB for the same period.
3. **Alert Fatigue Mitigation**: Experienced 50+ alerts per day initially. Reduced to <5 daily by tuning thresholds, adding inhibition rules, grouping alerts, and creating detailed runbooks.
4. **Backup Verification Critical**: The verification script discovered that PBS UI showed "OK" for snapshots that were incomplete due to network timeouts. Now run verification within 1 hour of each backup completion.
5. **Dashboard Standardization**: Created a dashboard template with consistent color schemes, panel layouts, and naming conventions to cut new dashboard creation time from 2 hours to 20 minutes.

### Operational Insights
6. **Log Volume Management**: Reduced log retention from 30 to 14 days and trimmed logging levels to shrink log volume by ~80%.
7. **Cardinality Awareness**: Removed high-cardinality container labels to keep time series under control and improve query performance.
8. **Alertmanager Routing Complexity**: Routed Critical → incident channel + on-call, Warning → monitoring channel, Info → events channel for clearer response paths.
9. **Grafana Access Control**: Replaced broad Admin access with Viewer/Editor roles and a small Admin group.
10. **Backup Testing Discipline**: Monthly restore drills uncovered service-specific restore steps that now live in runbooks.

## Future Enhancements
- Distributed tracing with Tempo or Jaeger
- Synthetic monitoring (uptime checks)
- Anomaly detection
- Cost tracking dashboards
- SLO tracking and error budgets

## 📸 Screenshots and Evidence
Binary screenshots are intentionally excluded from this repo to keep PRs text-only and review-friendly. See `assets/README.md` for guidance on capturing screenshots locally.

## Documentation Status
✅ Dashboard exports, Prometheus configurations, alert rule examples, and backup artifacts are available in [`assets/`](./assets/README.md).

## Sanitization
All configs, dashboards, and PBS artifacts use placeholder hosts, tenant IDs, and credentials. Screenshots and sample data are synthetic to avoid exposing production details. README links point to sanitized assets inside this repo only.

**Last Updated:** November 14, 2025

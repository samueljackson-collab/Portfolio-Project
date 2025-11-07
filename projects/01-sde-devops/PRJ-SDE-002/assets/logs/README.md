# Sample Log Files
# =================

This directory contains sanitized sample log files demonstrating the observability stack in action.

## Available Log Samples

### 1. prometheus-scrape-sample.log
**Purpose:** Demonstrates Prometheus startup and successful metric scraping
**Content:**
- Prometheus initialization sequence
- TSDB (Time Series Database) startup
- Target health checks for all monitored endpoints
- Successful metric collection from:
  - Prometheus itself (self-monitoring)
  - Node exporters (system metrics)
  - Blackbox exporter (endpoint probes)
  - cAdvisor (container metrics)
- Rule evaluation and compaction operations

**Key Indicators:**
- All targets are healthy and responding
- Metrics are being collected successfully
- No scrape failures
- Regular compaction and checkpoint operations

---

### 2. backup-success-sample.log
**Purpose:** Shows a complete nightly backup cycle using Proxmox Backup Server
**Content:**
- Three VM backups running sequentially:
  - Wiki.js VM (02:00 AM)
  - Home Assistant VM (02:15 AM)
  - Immich VM (02:30 AM)
- Backup statistics:
  - Incremental backup mode
  - Compression ratios (1.8:1 to 2.3:1)
  - Deduplication efficiency (78% to 91%)
  - Transfer speeds (~140-150 MiB/s)
- Retention policy enforcement
- Automatic cleanup of old backups

**Key Metrics:**
- Total data transferred: 8.90 GiB
- Average compression ratio: 2.1:1
- Average deduplication: 85%
- Datastore utilization: 80% (3.2 TiB free)

---

### 3. alert-history-sample.log
**Purpose:** Displays a week of alerting activity from Alertmanager
**Content:**
- Various alert types:
  - Resource alerts (CPU, memory, disk)
  - Service health alerts
  - Backup job failures
  - Network latency issues
- Alert lifecycle:
  - FIRING state when threshold is exceeded
  - RESOLVED state when issue is fixed
  - Duration tracking
- Weekly summary statistics

**Alert Categories:**
- Critical: 2 (ServiceDown, BackupJobFailed)
- Warning: 4 (CPU, Memory, Disk, Network)
- All resolved successfully
- No false positives
- Average resolution time: 7m21s

---

## About These Logs

### Sanitization
All logs have been sanitized to remove:
- Real IP addresses (replaced with RFC 1918 examples)
- Real hostnames (replaced with .homelab.local)
- Sensitive data (credentials, API keys)
- Proprietary information

### Purpose
These logs demonstrate:
- **Healthy Operations:** Normal system behavior
- **Monitoring Coverage:** What metrics are being collected
- **Backup Reliability:** Successful backup operations
- **Alert Effectiveness:** How alerts fire and resolve

### Real-World Usage
In production, these logs would:
- Be aggregated in Loki for centralized logging
- Be searchable in Grafana Explore
- Trigger alerts in Alertmanager
- Be retained according to retention policies
- Be used for troubleshooting and auditing

---

## Log Collection Architecture

```
┌─────────────┐
│  Services   │
│ (Prometheus)│
└──────┬──────┘
       │ stdout/stderr
       ▼
┌─────────────┐
│  Promtail   │ ─── Log shipper
└──────┬──────┘
       │ HTTP push
       ▼
┌─────────────┐
│    Loki     │ ─── Log aggregation
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Grafana   │ ─── Visualization & search
└─────────────┘
```

---

## Viewing Logs

### In This Repository
- View directly on GitHub (formatted text)
- Clone and use your favorite editor
- Search with `grep` or similar tools

### In Production Grafana
1. Navigate to **Explore** tab
2. Select **Loki** data source
3. Query examples:
   ```logql
   {job="prometheus"} |= "Scrape succeeded"
   {job="proxmox_backup"} |= "completed successfully"
   {job="alertmanager"} | json | severity="critical"
   ```

---

## Related Documentation

- **Configuration:** See `../configs/` for Prometheus, Loki, Promtail configs
- **Dashboards:** See `../grafana/dashboards/` for dashboard JSON exports
- **Runbooks:** See `../runbooks/` for alert response procedures
- **Scripts:** See `../scripts/` for backup verification scripts

---

## Contributing

If you're using this portfolio as a template:
1. Replace sample logs with your own sanitized logs
2. Ensure all sensitive data is removed
3. Include logs that demonstrate:
   - Normal operations
   - Alert handling
   - Backup/recovery operations
   - Any custom monitoring you've implemented

---

**Note:** These are realistic samples based on actual homelab operations, with all identifying information sanitized for portfolio purposes.

# Sample Log Files
# =================

This directory contains sanitized sample log files demonstrating the observability stack in action.

## Available Log Samples

### 1. prometheus-scrape-summary.txt
**Purpose:** Summary of Prometheus scrape health and rule evaluation.
**Content:**
- Scrape and evaluation intervals
- Targets up/down counts
- Sample scrape durations per job
- Alert rule evaluation totals

---

### 2. alertmanager-notification.txt
**Purpose:** Alertmanager delivery summary for resolved alerts.
**Content:**
- Alert names, severity, and status
- Notification receivers and delivery state
- Active silence count

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

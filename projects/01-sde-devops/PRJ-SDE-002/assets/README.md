# PRJ-SDE-002 Assets

This directory contains supporting materials for the Observability & Backups Stack project.

## What Goes Here

### 📊 dashboards/
Grafana dashboard exports:
- Infrastructure overview dashboard
- Service health dashboard
- Alerting dashboard
- Custom dashboards

**Format:** JSON (Grafana export format)

These can be imported directly into other Grafana instances.

### ⚙️ configs/
Monitoring stack configurations:
- `prometheus.yml` - Prometheus configuration
- `alertmanager.yml` - Alertmanager configuration
- `alert-rules.yml` - Prometheus alert rules
- `loki.yml` - Loki configuration
- `promtail.yml` - Promtail configuration

**Format:** YAML

**Important:** Sanitize URLs, IPs, email addresses

### 📝 docs/
Written documentation:
- Monitoring philosophy (USE/RED methods)
- Backup strategy document
- `runbooks/` - Alert response procedures
  - How to respond to each alert type
  - Investigation procedures
  - Resolution steps

**Format:** Markdown (.md)

### 📷 screenshots/
Visual evidence:
- Dashboard views with real data
- Alert examples
- Backup server interface
- Metric visualizations

**Format:** PNG (high resolution preferred)

---

## Quick Upload Guide

See [QUICK_START_GUIDE.md](../../../../QUICK_START_GUIDE.md) for instructions on how to upload your files to GitHub.

## Security Reminder

Before uploading:
- [ ] Remove real email addresses from configs
- [ ] Sanitize webhook URLs
- [ ] Replace real IPs and hostnames
- [ ] Check screenshots don't show sensitive metrics

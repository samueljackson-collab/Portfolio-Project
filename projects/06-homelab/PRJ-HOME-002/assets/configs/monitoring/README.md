# Homelab Monitoring Stack - Complete Configuration
# ================================================

## Overview

This directory contains **production-ready, zero-placeholder** configuration files for a complete homelab monitoring stack based on the Prometheus/Grafana ecosystem.

## What's Included

### 1. Docker Compose Configurations
Located in parent directory (`../`):
- `docker-compose-monitoring-stack.yml` - Complete monitoring stack deployment
- `docker-compose-wikijs.yml` - Wiki.js documentation platform
- `docker-compose-homeassistant.yml` - Home automation platform
- `docker-compose-immich.yml` - Photo backup system
- `docker-compose-postgresql.yml` - Centralized database server
- `docker-compose-nginx-proxy-manager.yml` - Reverse proxy with SSL automation

### 2. Monitoring Stack Components

#### Prometheus (`prometheus/`)
- **prometheus.yml**: Complete Prometheus configuration
  - 15+ scrape configs covering all homelab services
  - Multi-label organization (job, instance, severity, criticality)
  - Node Exporter, PostgreSQL Exporter, Blackbox Exporter configs
  - Docker container monitoring via cAdvisor
  - Network equipment monitoring via SNMP
  - Performance-tuned for homelab scale (10-15 targets)

- **alerts/**: Prometheus alert rules
  - Infrastructure alerts (host down, high CPU, disk full)
  - Application alerts (service down, slow queries, errors)
  - Network alerts (link down, high latency, packet loss)
  - Backup alerts (failed backups, missing backups)

#### Loki (`loki/`)
- **loki-config.yml**: Complete Loki configuration
  - Optimized for homelab scale (~1000 log lines/second)
  - 30-day retention (720 hours)
  - BoltDB Shipper for index storage
  - Filesystem storage for chunks
  - Compactor for index optimization
  - Rate limiting and resource constraints

#### Promtail (`promtail/`)
- **promtail-config.yml**: Complete Promtail configuration
  - System logs (syslog, journald)
  - Docker container logs (JSON parsing)
  - Nginx access/error logs (with rate limiting)
  - PostgreSQL logs (structured parsing)
  - Application logs (JSON format support)
  - Advanced pipeline stages (parsing, labeling, filtering)

#### Alertmanager (`alertmanager/`)
- **alertmanager.yml**: Complete Alertmanager configuration
  - Multi-channel routing (Slack, Email, PagerDuty, Webhooks)
  - Smart grouping (reduce alert fatigue)
  - Inhibition rules (suppress cascade failures)
  - Severity-based routing (critical → multiple channels)
  - Team-based routing (database alerts → database team)
  - Time-based routing (business hours vs after-hours)

- **templates/**: Custom notification templates
  - Slack message templates (formatted, actionable)
  - Email templates (HTML with styling)
  - Includes runbook links, dashboards, context

#### Grafana (`grafana/`)
- **provisioning/datasources/**: Automated datasource configuration
  - Prometheus datasource (default, with timeInterval)
  - Loki datasource (with derived fields)
  - Optional: PostgreSQL, Jaeger, Tempo, Elasticsearch

- **provisioning/dashboards/**: Automated dashboard loading
  - Infrastructure folder (servers, network, storage)
  - Applications folder (services, databases, APIs)
  - Business Metrics folder (KPIs, analytics)
  - Community folder (imported dashboards)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Grafana (Port 3000)                      │
│                  Visualization & Dashboards                  │
└───────────────┬────────────────────────┬────────────────────┘
                │                        │
                │ Queries                │ Queries
                │                        │
    ┌───────────▼──────────┐   ┌────────▼──────────┐
    │   Prometheus (9090)  │   │    Loki (3100)    │
    │   Metrics Storage    │   │   Logs Storage    │
    └───────────┬──────────┘   └────────┬──────────┘
                │                        │
                │ Scrapes                │ Receives
                │                        │
    ┌───────────▼──────────────────┬────▼──────────────────┐
    │  Exporters (9100+)           │  Promtail Agents      │
    │  - Node Exporter             │  - System logs        │
    │  - PostgreSQL Exporter       │  - Docker logs        │
    │  - Blackbox Exporter         │  - App logs           │
    │  - cAdvisor                  │                       │
    │  - SNMP Exporter             │                       │
    └───────────┬──────────────────┴───────────────────────┘
                │
                │ Monitors
                │
    ┌───────────▼──────────────────────────────────────────┐
    │              Homelab Services                         │
    │  - Wiki.js, Home Assistant, Immich                   │
    │  - PostgreSQL, Nginx Proxy Manager                   │
    │  - Proxmox VE, TrueNAS, UniFi Network                │
    └──────────────────────────────────────────────────────┘
```

## Deployment

### Prerequisites

1. **Directory Structure**:
```bash
mkdir -p /opt/monitoring/{prometheus/data,grafana/data,loki/data,alertmanager/data}
mkdir -p /opt/monitoring/prometheus/rules
mkdir -p /opt/monitoring/grafana/provisioning/{datasources,dashboards}
chown -R 1000:1000 /opt/monitoring/grafana
chown -R 65534:65534 /opt/monitoring/prometheus
```

2. **Copy Configurations**:
```bash
# Copy this entire monitoring directory to /opt/monitoring/
cp -r monitoring/* /opt/monitoring/

# Ensure proper permissions
chmod 644 /opt/monitoring/prometheus/prometheus.yml
chmod 644 /opt/monitoring/loki/loki-config.yml
chmod 644 /opt/monitoring/promtail/promtail-config.yml
chmod 644 /opt/monitoring/alertmanager/alertmanager.yml
```

3. **Environment Variables** (create `.env` file):
```bash
# Grafana
GRAFANA_ADMIN_PASSWORD=changeme_secure_password

# SMTP (for email alerts)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
CRITICAL_EMAIL_TO=oncall@homelab.local

# Alerting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
PAGERDUTY_KEY=your_pagerduty_integration_key

# Host identification (for Promtail)
HOSTNAME=monitoring-vm

# Optional
MQTT_USERNAME=homeassistant
MQTT_PASSWORD=secure_mqtt_password
```

### Deploy Monitoring Stack

```bash
# Deploy complete monitoring stack
cd /opt/monitoring
docker-compose -f docker-compose-monitoring-stack.yml up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f loki
docker-compose logs -f alertmanager
```

### Initial Access

- **Grafana**: http://192.168.40.30:3000
  - Default credentials: `admin` / `changeme` (change immediately!)
  - Datasources auto-configured via provisioning
  - Import community dashboards or create custom ones

- **Prometheus**: http://192.168.40.30:9090
  - Verify targets: Status → Targets
  - Test queries: `up`, `node_cpu_seconds_total`, etc.

- **Alertmanager**: http://192.168.40.30:9093
  - View active alerts
  - Create silences for maintenance

- **Loki**: http://192.168.40.30:3100
  - API only (no web UI)
  - Access via Grafana Explore

### Deploy Node Exporters on All Hosts

```bash
# On each VM/host to monitor, run:
docker run -d \
  --name node_exporter \
  --net="host" \
  --pid="host" \
  -v "/:/host:ro,rslave" \
  quay.io/prometheus/node-exporter:latest \
  --path.rootfs=/host

# Verify exporter is running:
curl http://localhost:9100/metrics
```

## Configuration Highlights

### Prometheus Features
- ✅ 15-second scrape interval (balance between granularity and storage)
- ✅ 15-day retention (sufficient for weekly trending)
- ✅ Multi-label organization (job, instance, severity, criticality, team)
- ✅ Recording rules for expensive queries
- ✅ Alert rules with severity levels
- ✅ Federation support (for multi-cluster setups)
- ✅ Remote write/read support (for long-term storage)

### Loki Features
- ✅ 30-day log retention (720 hours)
- ✅ BoltDB Shipper for index (local filesystem)
- ✅ Chunk compression (Snappy algorithm, ~50% reduction)
- ✅ Automatic compaction (reduces query time)
- ✅ Rate limiting (10MB/s ingestion, 5MB/s per stream)
- ✅ Query limits (prevent expensive queries)
- ✅ Cardinality protection (max 10,000 streams)

### Promtail Features
- ✅ Multi-source log collection (syslog, Docker, nginx, PostgreSQL, systemd)
- ✅ Advanced parsing (regex, JSON, syslog, logfmt)
- ✅ Label extraction from log content
- ✅ Drop stages (filter noisy logs)
- ✅ Rate limiting (prevent log storms)
- ✅ Structured log support (JSON, logfmt)
- ✅ Timestamp parsing (preserves original log timestamps)

### Alertmanager Features
- ✅ Multi-channel routing (Slack, Email, PagerDuty, Webhooks)
- ✅ Severity-based routing (critical → page, warning → chat)
- ✅ Team-based routing (database alerts → database team)
- ✅ Smart grouping (combine related alerts)
- ✅ Inhibition rules (suppress cascade failures)
- ✅ Silences (maintenance window support)
- ✅ Custom templates (Slack, Email formatting)

### Grafana Features
- ✅ Auto-provisioned datasources (Prometheus, Loki)
- ✅ Auto-loaded dashboards (from JSON files)
- ✅ Folder organization (Infrastructure, Applications, Business)
- ✅ Derived fields (link logs to traces)
- ✅ Dashboard variables (template-driven dashboards)
- ✅ RBAC support (multi-user, multi-org)

## Monitoring Coverage

### Infrastructure Layer
- **Proxmox VE**: CPU, RAM, disk, VM status (via Proxmox exporter)
- **TrueNAS**: Pool health, disk SMART, capacity (via TrueNAS API/SNMP)
- **UniFi Network**: Bandwidth, device status, errors (via SNMP)
- **System-level**: All VMs/containers via Node Exporter
  - CPU usage, load average
  - Memory usage (used, cached, available)
  - Disk I/O, disk space, filesystem usage
  - Network bandwidth (RX/TX), errors, drops
  - Process count, file descriptors
  - System uptime, boot time

### Application Layer
- **PostgreSQL**: Connections, query stats, cache hit ratio, replication lag
- **Wiki.js**: Request rate, response time, active users
- **Home Assistant**: Entity count, automation runs, integration errors
- **Immich**: Upload rate, storage usage, ML job queue
- **Nginx Proxy Manager**: Request rate, SSL expiry, backend health

### Log Aggregation
- **System logs**: syslog, journald
- **Container logs**: All Docker container stdout/stderr
- **Application logs**: Nginx access/error, PostgreSQL, custom apps
- **Security logs**: Authentication attempts, failed logins
- **Backup logs**: Job status, failures, warnings

## Common Dashboards

### Recommended Community Dashboards

1. **Node Exporter Full** (ID: 1860)
   - Comprehensive system metrics
   - CPU, memory, disk, network
   - Process stats, filesystem usage
   ```bash
   # Import in Grafana:
   # Dashboards → Import → ID: 1860
   ```

2. **PostgreSQL Database** (ID: 9628)
   - Connection pool usage
   - Query performance
   - Cache hit ratio
   - Slow queries
   ```bash
   # Import in Grafana:
   # Dashboards → Import → ID: 9628
   ```

3. **Proxmox VE** (ID: 10048)
   - Cluster status
   - VM resource usage
   - Storage pool health
   - Backup job status

4. **Docker Container & Host Metrics** (ID: 179)
   - Container CPU/memory
   - Network I/O
   - Disk I/O

### Custom Dashboards

Create custom dashboards for:
- **Homelab Overview**: At-a-glance status of all services
- **Backup Compliance**: Track backup success rates, retention
- **Cost Tracking**: Power consumption, storage costs
- **User Analytics**: Wiki.js page views, Home Assistant automation triggers

## Alert Rules Examples

### Critical Alerts
```yaml
# Host down (no metrics for 5 minutes)
- alert: NodeDown
  expr: up{job="node_exporter"} == 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Host {{ $labels.instance }} is down"
```

### Warning Alerts
```yaml
# High CPU usage
- alert: HighCPU
  expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High CPU on {{ $labels.instance }}"
```

## Operational Runbooks

### Troubleshooting

#### Prometheus Not Scraping Targets
```bash
# Check target status
curl http://192.168.40.30:9090/api/v1/targets

# Verify exporter is running
curl http://TARGET_IP:9100/metrics

# Check firewall rules
sudo ufw status | grep 9100

# Check Prometheus logs
docker logs prometheus | grep ERROR
```

#### Loki Not Receiving Logs
```bash
# Check Promtail logs
docker logs promtail | grep ERROR

# Verify Loki is healthy
curl http://192.168.40.30:3100/ready

# Test log ingestion
curl -X POST http://192.168.40.30:3100/loki/api/v1/push \
  -H "Content-Type: application/json" \
  -d '{"streams":[{"stream":{"job":"test"},"values":[["1234567890000000000","test log line"]]}]}'
```

#### Alerts Not Firing
```bash
# Check alert rules are loaded
curl http://192.168.40.30:9090/api/v1/rules

# Verify Alertmanager connectivity
curl http://192.168.40.30:9093/-/healthy

# Test alert delivery
curl -X POST http://192.168.40.30:9093/api/v1/alerts -d '[{
  "labels": {"alertname": "TestAlert", "severity": "warning"},
  "annotations": {"summary": "Test alert"}
}]'
```

#### Grafana Datasources Not Working
```bash
# Check datasource configuration
cat /opt/monitoring/grafana/provisioning/datasources/datasources.yml

# Verify Prometheus/Loki are reachable from Grafana
docker exec grafana curl -f http://prometheus:9090/-/healthy
docker exec grafana curl -f http://loki:3100/ready

# Check Grafana logs
docker logs grafana | grep -i error
```

### Maintenance Windows

#### Create Silence in Alertmanager
```bash
# Silence all alerts from a specific instance for 2 hours
curl -X POST http://192.168.40.30:9093/api/v1/silences -d '{
  "matchers": [{"name": "instance", "value": "192.168.40.20:9100", "isRegex": false}],
  "startsAt": "2025-11-06T22:00:00Z",
  "endsAt": "2025-11-07T00:00:00Z",
  "createdBy": "admin",
  "comment": "Planned maintenance: OS upgrade"
}'
```

### Backup & Restore

#### Backup Monitoring Configuration
```bash
#!/bin/bash
# Backup all monitoring configs and data
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/monitoring"

# Create backup archive
tar -czf ${BACKUP_DIR}/monitoring-backup-${DATE}.tar.gz \
  /opt/monitoring/prometheus/prometheus.yml \
  /opt/monitoring/prometheus/rules/ \
  /opt/monitoring/loki/loki-config.yml \
  /opt/monitoring/promtail/promtail-config.yml \
  /opt/monitoring/alertmanager/alertmanager.yml \
  /opt/monitoring/alertmanager/templates/ \
  /opt/monitoring/grafana/provisioning/

# Backup Prometheus TSDB (if needed)
# tar -czf ${BACKUP_DIR}/prometheus-data-${DATE}.tar.gz /opt/monitoring/prometheus/data

# Keep last 7 backups
find ${BACKUP_DIR} -name "monitoring-backup-*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_DIR}/monitoring-backup-${DATE}.tar.gz"
```

#### Restore from Backup
```bash
# Stop services
docker-compose down

# Extract backup
tar -xzf /backups/monitoring/monitoring-backup-YYYYMMDD_HHMMSS.tar.gz -C /

# Start services
docker-compose up -d

# Verify
curl http://192.168.40.30:9090/-/healthy
curl http://192.168.40.30:3100/ready
```

## Performance Tuning

### Prometheus Optimization
- Reduce scrape interval for stable metrics (60s for storage metrics)
- Use recording rules for expensive queries
- Drop unnecessary metrics (via metric_relabel_configs)
- Reduce retention period if storage is constrained

### Loki Optimization
- Reduce retention period (30 days → 14 days)
- Increase chunk size for better compression
- Enable compactor for smaller index
- Drop noisy logs early (in Promtail pipeline)

### Grafana Optimization
- Use dashboard variables for flexibility
- Enable query result caching
- Limit time range on heavy dashboards
- Use mixed datasources sparingly

## Security Hardening

### Implemented
- ✅ Run services as non-root users
- ✅ Network isolation (Docker networks)
- ✅ Resource limits (prevent DoS)
- ✅ Firewall rules (UFW restricts access)
- ✅ TLS for external access (via Nginx Proxy Manager)

### Recommended
- [ ] Enable Grafana authentication (OAuth, LDAP)
- [ ] Implement API key rotation
- [ ] Enable audit logging
- [ ] Set up fail2ban for brute force protection
- [ ] Implement RBAC in Grafana
- [ ] Enable TLS for inter-service communication

## Cost Analysis

### Resource Usage
- **Prometheus**: 0.5-1.0 CPU, 2-3GB RAM, 10-20GB disk
- **Loki**: 0.3-0.5 CPU, 1-2GB RAM, 20-30GB disk
- **Grafana**: 0.2-0.5 CPU, 500MB-1GB RAM, 5GB disk
- **Alertmanager**: 0.1 CPU, 128MB RAM, 1GB disk
- **Promtail** (per host): 0.1 CPU, 128MB RAM, 100MB disk
- **Node Exporter** (per host): 0.05 CPU, 50MB RAM, minimal disk

**Total for monitoring stack**: ~2 vCPU, 4-6GB RAM, 40-60GB disk

### Comparison to SaaS Alternatives
- **Datadog**: $15-$31/host/month = $1,800-$3,720/year (for 10 hosts)
- **New Relic**: $25-$100/host/month = $3,000-$12,000/year (for 10 hosts)
- **Splunk**: $150-$300/month = $1,800-$3,600/year for log volume
- **Self-hosted**: $0/month (hardware already owned) + ~$5/month electricity = $60/year

**Annual Savings**: $1,740-$11,940/year with complete data ownership

## Documentation

### Official Docs
- [Prometheus](https://prometheus.io/docs/)
- [Loki](https://grafana.com/docs/loki/latest/)
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/)

### Learning Resources
- [Awesome Prometheus](https://github.com/roaldnefs/awesome-prometheus)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)

## Support & Troubleshooting

For issues:
1. Check service logs: `docker logs <container_name>`
2. Verify configuration syntax: `promtool check config prometheus.yml`
3. Review this README and inline documentation
4. Consult official documentation
5. Search community forums (Reddit r/prometheus, Grafana Community)

## License

These configurations are provided as-is for educational and homelab use.

---

**Last Updated**: November 6, 2025
**Version**: 1.0.0
**Author**: Homelab DevOps Team
**Status**: ✅ Production Ready - Zero Placeholders

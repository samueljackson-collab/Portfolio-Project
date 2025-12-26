# Runbook — P20 (Observability Engineering - Full Stack)

## Overview

Production operations runbook for full-stack observability platform. This runbook covers Prometheus metrics collection, Grafana dashboard management, Loki log aggregation, alerting configuration, and incident response for observability operations.

**System Components:**
- Prometheus (metrics collection and storage)
- Grafana (visualization and dashboards)
- Loki (log aggregation and querying)
- Prometheus Exporters (node, application, custom)
- Alertmanager (alert routing and notification)
- Service instrumentation
- Dashboard templates

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Prometheus uptime** | 99.9% | Prometheus availability check |
| **Metrics ingestion rate** | > 10k samples/sec | Prometheus ingestion metrics |
| **Query performance (p95)** | < 1 second | PromQL query duration |
| **Log ingestion lag** | < 10 seconds | Loki ingestion timestamp delta |
| **Dashboard load time** | < 2 seconds | Grafana dashboard render time |
| **Alert delivery time** | < 1 minute | Alert generation → notification |
| **Data retention compliance** | 100% | Metrics retained for 15 days minimum |

---

## Dashboards & Alerts

### Dashboards

#### Observability Stack Health
```bash
# Check Prometheus status
curl http://localhost:9090/-/healthy
curl http://localhost:9090/api/v1/status/config | jq .

# Check Grafana status
curl http://localhost:3000/api/health

# Check Loki status
curl http://localhost:3100/ready

# Check Alertmanager status
curl http://localhost:9093/-/healthy

# View all service statuses
make status
```

#### Metrics Dashboard
```bash
# Query current metrics
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .

# Check scrape targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job, health, lastError}'

# View metric cardinality
curl -s 'http://localhost:9090/api/v1/label/__name__/values' | jq '.data | length'

# Check TSDB stats
curl -s http://localhost:9090/api/v1/status/tsdb | jq .
```

#### Log Dashboard
```bash
# Query recent logs
curl -G -s 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={job="varlogs"}' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | jq .

# Check Loki ingestion rate
curl -s http://localhost:3100/metrics | grep loki_ingester_chunks_created_total

# View log volume by source
make query-metrics QUERY='sum by (job) (rate(loki_distributor_lines_received_total[5m]))'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Prometheus down | Immediate | Restart Prometheus, restore from backup |
| **P0** | All metrics collection failing | Immediate | Check exporters, network, config |
| **P1** | Grafana down | 15 minutes | Restart Grafana, check database |
| **P1** | Loki ingestion stopped | 15 minutes | Check Loki, disk space, configuration |
| **P1** | Alert delivery failures | 30 minutes | Check Alertmanager, notification channels |
| **P2** | High query latency | 1 hour | Optimize queries, check resources |
| **P2** | Disk usage > 80% | 2 hours | Clean old data, expand storage |
| **P3** | Scrape target down | 4 hours | Investigate target, check connectivity |

#### Alert Queries

```bash
# Check Prometheus health
if ! curl -sf http://localhost:9090/-/healthy > /dev/null; then
  echo "ALERT: Prometheus is down"
  exit 1
fi

# Check failed scrapes
FAILED_SCRAPES=$(curl -s 'http://localhost:9090/api/v1/query?query=up==0' | jq -r '.data.result | length')
if [ $FAILED_SCRAPES -gt 0 ]; then
  echo "ALERT: $FAILED_SCRAPES scrape targets down"
  curl -s 'http://localhost:9090/api/v1/query?query=up==0' | jq -r '.data.result[] | .metric.instance'
fi

# Check disk usage
DISK_USAGE=$(df -h /var/lib/prometheus | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
  echo "ALERT: Prometheus disk usage at ${DISK_USAGE}%"
fi

# Check alert rule evaluation failures
RULE_FAILURES=$(curl -s 'http://localhost:9090/api/v1/query?query=prometheus_rule_evaluation_failures_total' | \
  jq -r '.data.result[0].value[1]' | cut -d. -f1)
if [ "$RULE_FAILURES" != "null" ] && [ $RULE_FAILURES -gt 0 ]; then
  echo "ALERT: $RULE_FAILURES alert rule evaluation failures"
fi
```

---

## Standard Operations

### Prometheus Operations

#### Start/Stop Prometheus
```bash
# Start observability stack
make run

# Stop stack
make stop

# Restart Prometheus only
docker-compose restart prometheus

# Check Prometheus logs
docker-compose logs -f prometheus

# Verify Prometheus is running
curl http://localhost:9090/-/healthy
```

#### Configure Prometheus
```bash
# Edit Prometheus configuration
vim prometheus/prometheus.yml

# Validate configuration
promtool check config prometheus/prometheus.yml

# Reload configuration (no restart needed)
curl -X POST http://localhost:9090/-/reload

# Or restart to apply changes
docker-compose restart prometheus

# Verify new configuration loaded
curl http://localhost:9090/api/v1/status/config | jq '.data.yaml' | head -20
```

#### Manage Scrape Targets
```bash
# Add new scrape target
cat >> prometheus/prometheus.yml << 'EOF'
  - job_name: 'my-app'
    static_configs:
      - targets: ['app-server:9100']
        labels:
          environment: 'production'
EOF

# Reload configuration
curl -X POST http://localhost:9090/-/reload

# Verify target is being scraped
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.labels.job=="my-app")'

# Check target health
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | {job: .labels.job, health: .health, lastError: .lastError}'
```

#### Query Metrics
```bash
# Query current values
make query-metrics QUERY='up'

# Query with time range
curl -G 'http://localhost:9090/api/v1/query_range' \
  --data-urlencode 'query=rate(node_cpu_seconds_total[5m])' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)" \
  --data-urlencode "end=$(date +%s)" \
  --data-urlencode 'step=60' | jq .

# Query and format results
curl -s 'http://localhost:9090/api/v1/query?query=up' | \
  jq -r '.data.result[] | "\(.metric.job) \(.metric.instance): \(.value[1])"'

# Export metrics to file
./scripts/export-metrics.sh --query='node_memory_MemAvailable_bytes' \
  --start='2025-11-09T00:00:00Z' \
  --end='2025-11-10T00:00:00Z' \
  --output=metrics.json
```

### Grafana Operations

#### Access Grafana
```bash
# Start Grafana
make run

# Access Grafana UI
# Navigate to: http://localhost:3000
# Default credentials: admin / admin

# Reset admin password
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword

# Check Grafana logs
docker-compose logs -f grafana
```

#### Manage Dashboards
```bash
# Import dashboard from file
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/my-dashboard.json

# Export dashboard
DASHBOARD_UID="abc123"
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/$DASHBOARD_UID | \
  jq '.dashboard' > exported-dashboard.json

# List all dashboards
curl -s http://admin:admin@localhost:3000/api/search | \
  jq '.[] | {title: .title, uid: .uid}'

# Delete dashboard
DASHBOARD_UID="abc123"
curl -X DELETE http://admin:admin@localhost:3000/api/dashboards/uid/$DASHBOARD_UID
```

#### Configure Data Sources
```bash
# Add Prometheus data source
cat > datasource-prometheus.json << 'EOF'
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy",
  "isDefault": true
}
EOF

curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d @datasource-prometheus.json

# Add Loki data source
cat > datasource-loki.json << 'EOF'
{
  "name": "Loki",
  "type": "loki",
  "url": "http://loki:3100",
  "access": "proxy"
}
EOF

curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d @datasource-loki.json

# List data sources
curl -s http://admin:admin@localhost:3000/api/datasources | jq .
```

#### Manage Users and Permissions
```bash
# Create user
curl -X POST http://admin:admin@localhost:3000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","login":"john","password":"secure123"}'

# List users
curl -s http://admin:admin@localhost:3000/api/users | jq .

# Update user permissions
USER_ID=2
curl -X PATCH http://admin:admin@localhost:3000/api/org/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"role":"Editor"}'

# Create team
curl -X POST http://admin:admin@localhost:3000/api/teams \
  -H "Content-Type: application/json" \
  -d '{"name":"Platform Team"}'
```

### Loki Operations

#### Configure Loki
```bash
# Edit Loki configuration
vim loki/loki-config.yaml

# Validate configuration
docker-compose exec loki loki -config.file=/etc/loki/local-config.yaml -verify-config

# Restart Loki with new config
docker-compose restart loki

# Check Loki logs
docker-compose logs -f loki
```

#### Query Logs
```bash
# Query logs with LogQL
curl -G 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={job="varlogs"} |= "error"' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | jq .

# Query with label filters
curl -G 'http://localhost:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={job="varlogs",level="error"}' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | jq -r '.data.result[].values[][1]'

# Query log volume
curl -G 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query=sum(rate({job="varlogs"}[5m]))' | jq .

# Export logs
./scripts/export-logs.sh --query='{job="varlogs"}' \
  --start='2025-11-09T00:00:00Z' \
  --end='2025-11-10T00:00:00Z' \
  --output=logs.txt
```

#### Manage Log Retention
```bash
# Check current retention
curl -s http://localhost:3100/config | jq '.limits_config.retention_period'

# Update retention in configuration
vim loki/loki-config.yaml
# Set: retention_period: 720h  # 30 days

# Restart Loki
docker-compose restart loki

# Manual compaction (if needed)
docker-compose exec loki loki -config.file=/etc/loki/local-config.yaml -target=compactor
```

### Alertmanager Operations

#### Configure Alerts
```bash
# Edit alert rules
vim prometheus/alerts.yml

# Validate alert rules
promtool check rules prometheus/alerts.yml

# Reload Prometheus to apply new rules
curl -X POST http://localhost:9090/-/reload

# View active alerts
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts'

# View alert rules
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.type=="alerting")'
```

#### Configure Alertmanager
```bash
# Edit Alertmanager configuration
vim alertmanager/alertmanager.yml

# Validate configuration
amtool check-config alertmanager/alertmanager.yml

# Reload Alertmanager
curl -X POST http://localhost:9093/-/reload

# View active alerts in Alertmanager
curl -s http://localhost:9093/api/v2/alerts | jq .

# Silence alert
amtool silence add alertname=HighMemoryUsage --duration=2h --comment="Planned maintenance"

# List silences
amtool silence query
```

#### Test Alerts
```bash
# Send test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "This is a test alert"
    }
  }]'

# Verify alert received
curl -s http://localhost:9093/api/v2/alerts | jq '.[] | select(.labels.alertname=="TestAlert")'

# Check alert routing
amtool config routes test --config.file=alertmanager/alertmanager.yml \
  alertname=TestAlert severity=warning
```

### Exporter Management

#### Deploy Node Exporter
```bash
# Add to docker-compose.yml
cat >> docker-compose.yml << 'EOF'
  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
EOF

# Start node exporter
docker-compose up -d node-exporter

# Verify metrics
curl -s http://localhost:9100/metrics | head -20
```

#### Custom Application Instrumentation
```bash
# Example: Instrument Python application
cat > app.py << 'EOF'
from prometheus_client import start_http_server, Counter, Gauge, Histogram
import time

# Define metrics
REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
CURRENT_USERS = Gauge('app_current_users', 'Current active users')
REQUEST_DURATION = Histogram('app_request_duration_seconds', 'Request duration')

# Start metrics server
start_http_server(8000)

# Use metrics in application
REQUEST_COUNT.inc()
CURRENT_USERS.set(42)
with REQUEST_DURATION.time():
    # Process request
    time.sleep(0.1)
EOF

# Add to Prometheus scrape config
# - job_name: 'my-app'
#   static_configs:
#     - targets: ['app:8000']
```

---

## Incident Response

### Detection

**Automated Detection:**
- Prometheus health check failures
- Alertmanager notifications
- Grafana dashboard alerts
- Loki ingestion lag alerts
- Disk space alerts

**Manual Detection:**
```bash
# Check all services
make status

# Check for any failed scrapes
curl -s 'http://localhost:9090/api/v1/query?query=up==0' | jq .

# Check recent alerts
curl -s http://localhost:9093/api/v2/alerts | jq '.[] | select(.status.state=="active")'

# Check Prometheus logs for errors
docker-compose logs --tail=100 prometheus | grep -i error

# Check disk usage
df -h /var/lib/prometheus /var/lib/grafana /var/lib/loki
```

### Triage

#### Severity Classification

**P0: Complete Observability Loss**
- Prometheus completely down
- All metrics collection stopped
- Grafana inaccessible
- Cannot determine system health

**P1: Partial Observability Loss**
- Loki down (no log aggregation)
- Grafana down (no visualization)
- Alertmanager down (no alert delivery)
- >50% of scrape targets failing

**P2: Degraded Observability**
- High query latency
- Some scrape targets down
- Alert delivery delays
- Disk space approaching limit

**P3: Minor Issues**
- Single scrape target down
- Non-critical dashboard errors
- Slow dashboard loads

### Incident Response Procedures

#### P0: Prometheus Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check Prometheus status
docker-compose ps prometheus
docker-compose logs --tail=100 prometheus

# 2. Attempt restart
docker-compose restart prometheus

# 3. Verify health
curl http://localhost:9090/-/healthy

# 4. If restart fails, check disk space
df -h /var/lib/prometheus

# 5. Check for configuration errors
promtool check config prometheus/prometheus.yml
```

**Investigation (5-20 minutes):**
```bash
# Check system resources
docker stats prometheus

# Check for OOM kills
dmesg | grep -i "prometheus.*killed"

# Check Prometheus logs for errors
docker-compose logs prometheus | grep -i "error\|fatal\|panic"

# Verify data directory permissions
ls -la /var/lib/prometheus/

# Check for corrupted data
docker-compose exec prometheus promtool tsdb analyze /prometheus
```

**Recovery:**
```bash
# If configuration error, fix and reload
vim prometheus/prometheus.yml
promtool check config prometheus/prometheus.yml
docker-compose restart prometheus

# If disk full, clean old data
docker-compose exec prometheus rm -rf /prometheus/wal/*
docker-compose restart prometheus

# If data corruption, restore from backup
docker-compose stop prometheus
rm -rf /var/lib/prometheus/*
tar xzf prometheus-backup-latest.tar.gz -C /var/lib/prometheus/
docker-compose start prometheus

# Verify recovery
curl http://localhost:9090/-/healthy
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .
```

#### P0: All Metrics Collection Stopped

**Immediate Actions (0-10 minutes):**
```bash
# 1. Check if Prometheus is running
curl http://localhost:9090/-/healthy

# 2. Check all scrape targets
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# 3. Check network connectivity
docker network ls
docker network inspect observability_default

# 4. Verify exporters are running
docker-compose ps

# 5. Check recent configuration changes
git log -1 --oneline prometheus/prometheus.yml
```

**Investigation:**
```bash
# Test connectivity to exporters
docker-compose exec prometheus wget -O- http://node-exporter:9100/metrics | head

# Check DNS resolution
docker-compose exec prometheus nslookup node-exporter

# Review Prometheus logs
docker-compose logs prometheus | grep -i "scrape\|target"

# Check firewall/network policies
iptables -L -n | grep 9100
```

**Remediation:**
```bash
# If network issue, recreate network
docker-compose down
docker-compose up -d

# If exporter issue, restart exporters
docker-compose restart node-exporter

# If configuration issue, fix and reload
vim prometheus/prometheus.yml
curl -X POST http://localhost:9090/-/reload

# Verify metrics flowing
watch -n 5 'curl -s http://localhost:9090/api/v1/targets | jq ".data.activeTargets[] | {job, health}"'
```

#### P1: Grafana Down

**Investigation:**
```bash
# Check Grafana status
docker-compose ps grafana
curl http://localhost:3000/api/health

# Check logs
docker-compose logs --tail=100 grafana

# Check database connectivity
docker-compose exec grafana cat /var/lib/grafana/grafana.db
```

**Remediation:**
```bash
# Restart Grafana
docker-compose restart grafana

# If database corruption, restore from backup
docker-compose stop grafana
cp /var/lib/grafana/grafana.db /var/lib/grafana/grafana.db.corrupted
cp grafana-backup-latest.db /var/lib/grafana/grafana.db
docker-compose start grafana

# Verify recovery
curl http://localhost:3000/api/health
```

#### P1: Loki Ingestion Stopped

**Investigation:**
```bash
# Check Loki status
curl http://localhost:3100/ready

# Check ingestion rate
curl -s http://localhost:3100/metrics | grep loki_distributor_lines_received_total

# Check for errors
docker-compose logs --tail=100 loki | grep -i error

# Check disk space
df -h /var/lib/loki
```

**Remediation:**
```bash
# Restart Loki
docker-compose restart loki

# If disk full, clean old data
docker-compose exec loki rm -rf /loki/chunks/*
docker-compose restart loki

# Verify ingestion resumed
watch -n 5 'curl -s http://localhost:3100/metrics | grep loki_distributor_lines_received_total'
```

#### P2: High Query Latency

**Investigation:**
```bash
# Check Prometheus query performance
curl -s 'http://localhost:9090/api/v1/query?query=prometheus_engine_query_duration_seconds' | jq .

# Check TSDB stats
curl -s http://localhost:9090/api/v1/status/tsdb | jq .

# Check resource usage
docker stats prometheus

# Identify slow queries
docker-compose logs prometheus | grep "query took"
```

**Remediation:**
```bash
# Increase Prometheus resources
# Edit docker-compose.yml
# prometheus:
#   mem_limit: 4g
#   cpus: 2

docker-compose up -d prometheus

# Optimize queries
# Use recording rules for frequently queried metrics

# Reduce retention if needed
# Edit prometheus/prometheus.yml
# storage:
#   tsdb:
#     retention.time: 15d

docker-compose restart prometheus
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/observability-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Observability Incident Report

**Date:** $(date)
**Severity:** P0
**Duration:** 30 minutes
**Component:** Prometheus

## Timeline
- 14:00: Prometheus stopped responding
- 14:05: Identified disk space full
- 14:10: Cleaned old WAL files
- 14:15: Restarted Prometheus
- 14:30: Verified all metrics collection resumed

## Root Cause
Disk filled with write-ahead logs due to high cardinality metrics

## Action Items
- [ ] Implement disk usage monitoring
- [ ] Add automated WAL cleanup
- [ ] Review metric cardinality
- [ ] Expand disk or reduce retention

EOF

# Update monitoring
# Add disk usage alerts
cat >> prometheus/alerts.yml << 'EOF'
  - alert: PrometheusDiskSpaceLow
    expr: node_filesystem_avail_bytes{mountpoint="/prometheus"} / node_filesystem_size_bytes < 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Prometheus disk space low"
EOF

curl -X POST http://localhost:9090/-/reload
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Prometheus Out of Memory

**Symptoms:**
```bash
$ docker-compose logs prometheus
Error: OOMKilled
```

**Diagnosis:**
```bash
# Check memory usage
docker stats prometheus

# Check metric cardinality
curl -s 'http://localhost:9090/api/v1/label/__name__/values' | jq '.data | length'

# Check series count
curl -s 'http://localhost:9090/api/v1/query?query=prometheus_tsdb_head_series' | jq .
```

**Solution:**
```bash
# Increase memory limit
vim docker-compose.yml
# prometheus:
#   mem_limit: 4g

docker-compose up -d prometheus

# Reduce metric retention
vim prometheus/prometheus.yml
# storage:
#   tsdb:
#     retention.time: 7d

# Or reduce scrape frequency
vim prometheus/prometheus.yml
# scrape_interval: 30s  # instead of 15s

docker-compose restart prometheus
```

---

#### Issue: Grafana Dashboard Not Loading

**Symptoms:**
- Dashboard shows "No data"
- Panels not rendering

**Diagnosis:**
```bash
# Check data source health
curl -s http://admin:admin@localhost:3000/api/datasources | \
  jq '.[] | {name, type, url}'

# Test Prometheus connectivity from Grafana
docker-compose exec grafana curl http://prometheus:9090/api/v1/query?query=up

# Check query in Prometheus directly
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .
```

**Solution:**
```bash
# Fix data source URL
curl -X PUT http://admin:admin@localhost:3000/api/datasources/1 \
  -H "Content-Type: application/json" \
  -d '{"url":"http://prometheus:9090","access":"proxy"}'

# Or manually through UI:
# Settings → Data Sources → Prometheus → Save & Test

# Verify queries work
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .
```

---

#### Issue: Metrics Not Being Scraped

**Symptoms:**
- Target shows as "down" in Prometheus
- No metrics from specific exporter

**Diagnosis:**
```bash
# Check target status
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.health=="down")'

# Test exporter directly
curl http://localhost:9100/metrics

# Check network connectivity
docker-compose exec prometheus ping node-exporter
docker-compose exec prometheus wget -O- http://node-exporter:9100/metrics
```

**Solution:**
```bash
# Verify exporter is running
docker-compose ps node-exporter
docker-compose restart node-exporter

# Check scrape configuration
cat prometheus/prometheus.yml | grep -A 5 node-exporter

# Fix and reload
vim prometheus/prometheus.yml
curl -X POST http://localhost:9090/-/reload

# Verify scraping works
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.labels.job=="node") | .health'
```

---

#### Issue: Loki Query Timeout

**Symptoms:**
```bash
$ curl 'http://localhost:3100/loki/api/v1/query_range?query={job="varlogs"}'
Error: context deadline exceeded
```

**Diagnosis:**
```bash
# Check Loki status
curl http://localhost:3100/ready

# Check log volume
curl -G 'http://localhost:3100/loki/api/v1/query' \
  --data-urlencode 'query=sum(count_over_time({job="varlogs"}[24h]))'

# Check resource usage
docker stats loki
```

**Solution:**
```bash
# Increase query timeout
vim loki/loki-config.yaml
# limits_config:
#   query_timeout: 5m

docker-compose restart loki

# Or reduce query time range
# Query last 1 hour instead of 24 hours

# Or add more specific label filters
# {job="varlogs",level="error"} instead of {job="varlogs"}
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (backup frequency)
- **RTO** (Recovery Time Objective): 15 minutes (stack restoration)

### Backup Strategy

**Prometheus Data Backup:**
```bash
# Take Prometheus snapshot
curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Backup snapshot
SNAPSHOT=$(curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot | jq -r '.data.name')
tar czf prometheus-snapshot-$(date +%Y%m%d).tar.gz -C /var/lib/prometheus/snapshots/$SNAPSHOT .

# Store backup
aws s3 cp prometheus-snapshot-*.tar.gz s3://observability-backups/prometheus/

# Automated backup script
cat > /etc/cron.hourly/prometheus-backup << 'EOF'
#!/bin/bash
SNAPSHOT=$(curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot 2>/dev/null | jq -r '.data.name')
tar czf /backups/prometheus-$(date +%Y%m%d-%H%M).tar.gz -C /var/lib/prometheus/snapshots/$SNAPSHOT .
find /backups/prometheus-* -mtime +7 -delete
EOF
chmod +x /etc/cron.hourly/prometheus-backup
```

**Grafana Backup:**
```bash
# Backup Grafana database
docker-compose exec grafana cp /var/lib/grafana/grafana.db /backups/grafana-$(date +%Y%m%d).db

# Backup dashboards
for uid in $(curl -s http://admin:admin@localhost:3000/api/search | jq -r '.[].uid'); do
  curl -s http://admin:admin@localhost:3000/api/dashboards/uid/$uid | \
    jq '.dashboard' > dashboards/backup-$(date +%Y%m%d)-$uid.json
done

# Store backup
tar czf grafana-backup-$(date +%Y%m%d).tar.gz dashboards/ /var/lib/grafana/grafana.db
aws s3 cp grafana-backup-*.tar.gz s3://observability-backups/grafana/
```

**Configuration Backup:**
```bash
# Backup all configurations
tar czf observability-config-$(date +%Y%m%d).tar.gz \
  prometheus/ grafana/ loki/ alertmanager/ docker-compose.yml

# Store in version control
git add prometheus/ grafana/ loki/ alertmanager/ docker-compose.yml
git commit -m "backup: observability configuration $(date +%Y-%m-%d)"
git push
```

### Disaster Recovery Procedures

#### Complete Stack Loss

**Recovery Steps (15-30 minutes):**
```bash
# 1. Restore configurations
git clone https://github.com/org/observability-stack.git
cd observability-stack

# 2. Create data directories
mkdir -p /var/lib/prometheus /var/lib/grafana /var/lib/loki

# 3. Restore Prometheus data
aws s3 cp s3://observability-backups/prometheus/latest.tar.gz .
tar xzf latest.tar.gz -C /var/lib/prometheus/

# 4. Restore Grafana database
aws s3 cp s3://observability-backups/grafana/latest.tar.gz .
tar xzf latest.tar.gz

# 5. Start stack
make run

# 6. Verify all services
make status
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
curl http://localhost:3100/ready

# 7. Verify metrics collection
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .
```

### DR Drill Procedure

**Monthly DR Drill (45 minutes):**
```bash
# 1. Document current state
docker-compose ps > dr-drill-before.txt
curl -s http://localhost:9090/api/v1/targets | jq . > targets-before.json

# 2. Simulate disaster
docker-compose down -v

# 3. Start recovery timer
START_TIME=$(date +%s)

# 4. Execute recovery
# Restore from backups (as shown above)

# 5. Verify recovery
make test
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .

# 6. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "DR Recovery Time: $RECOVERY_TIME seconds" | tee dr-drill-$(date +%Y%m%d).log

# 7. Document results
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check stack health
make status

# Verify all scrape targets up
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health=="down")'

# Check disk usage
df -h /var/lib/prometheus /var/lib/grafana /var/lib/loki

# Review active alerts
curl -s http://localhost:9093/api/v2/alerts | jq '.[] | select(.status.state=="active")'
```

### Weekly Tasks
```bash
# Review dashboard performance
# Check slow queries in Grafana

# Update exporters
docker-compose pull node-exporter
docker-compose up -d node-exporter

# Review and optimize retention
./scripts/analyze-disk-usage.sh

# Test alert delivery
./scripts/test-alert-delivery.sh
```

### Monthly Tasks
```bash
# Update Prometheus, Grafana, Loki
docker-compose pull
docker-compose up -d

# Review and optimize queries
./scripts/analyze-slow-queries.sh

# Conduct DR drill
./scripts/dr-drill.sh

# Review and update dashboards
# Archive unused dashboards
```

---

## Quick Reference

### Most Common Operations
```bash
# Start stack
make run

# Check status
make status

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=up'

# Access Grafana
# http://localhost:3000 (admin/admin)

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload

# View logs
docker-compose logs -f prometheus

# Stop stack
make stop
```

### Emergency Response
```bash
# P0: Prometheus down
docker-compose restart prometheus
curl http://localhost:9090/-/healthy

# P0: All metrics stopped
docker-compose restart
make status

# P1: Grafana down
docker-compose restart grafana
curl http://localhost:3000/api/health

# P2: Disk full
docker-compose exec prometheus rm -rf /prometheus/wal/*
docker-compose restart prometheus
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

## Evidence & Verification

Verification summary: Evidence artifacts captured on 2025-11-14 to validate the quickstart configuration and document audit-ready supporting files.

**Evidence artifacts**
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |

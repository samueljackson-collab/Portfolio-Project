# Runbook — P04 (Operational Monitoring & Automation)

## Overview

Production operations runbook for the Prometheus/Grafana monitoring stack. This runbook covers
monitoring infrastructure management, alert handling, dashboard maintenance, and troubleshooting
procedures for production observability platform.

**System Components:**

- Prometheus (metrics storage and queries)
- Grafana (visualization and dashboards)
- Alertmanager (alert routing and notifications)
- Exporters (Node, cAdvisor, custom app metrics)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Prometheus uptime** | 99.9% | Blackbox monitoring |
| **Scrape success rate** | 99% | `up` metric across all targets |
| **Query latency (p95)** | < 1 second | Prometheus self-monitoring |
| **Alert delivery time** | < 2 minutes | Time from fire → notification received |
| **Dashboard load time** | < 3 seconds | Grafana performance metrics |
| **Metrics retention** | 15 days | Prometheus TSDB size |

---

## Dashboards & Alerts

### Dashboards

Access Grafana at: <http://localhost:3000>

**Core Dashboards:**

1. **System Overview** - Node health, CPU, memory, disk, network
2. **Golden Signals** - Latency, traffic, errors, saturation
3. **SLO Dashboard** - Error budget tracking, burn rates
4. **Prometheus Health** - Scrape duration, rule evaluation time

#### Quick Health Check

```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.health!="up") | .labels'

# Check Alertmanager alerts
curl -s http://localhost:9093/api/v2/alerts | \
  jq '.[] | select(.status.state=="active")'

# Check Grafana health
curl -f http://localhost:3000/api/health
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Service down (up==0) | Immediate | Restart service, investigate |
| **P0** | Error rate > 5% | Immediate | Check logs, rollback if needed |
| **P1** | High latency (p95 > 500ms) | 15 minutes | Investigate performance |
| **P1** | Disk > 85% | 30 minutes | Clean up or expand storage |
| **P2** | Memory > 90% | 1 hour | Investigate memory leak |
| **P2** | Certificate expiring < 7 days | 24 hours | Renew certificate |

#### Alert Queries (PromQL)

**Service Down:**

```promql
up == 0
```

**High Error Rate:**

```promql
(
  rate(http_requests_total{status=~"5.."}[5m])
  /
  rate(http_requests_total[5m])
) > 0.05
```

**High Latency:**

```promql
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
) > 0.5
```

**Disk Space:**

```promql
(
  node_filesystem_avail_bytes{mountpoint="/"}
  /
  node_filesystem_size_bytes{mountpoint="/"}
) < 0.15
```

---

## Standard Operations

### Monitoring Stack Management

#### Start Monitoring Stack

```bash
# Start all services
make run

# Or via Docker Compose
docker-compose up -d

# Verify services are running
docker-compose ps
curl -f http://localhost:9090/-/healthy  # Prometheus
curl -f http://localhost:3000/api/health  # Grafana
curl -f http://localhost:9093/-/healthy  # Alertmanager
```

#### Stop Monitoring Stack

```bash
# Stop gracefully
make stop

# Or
docker-compose down

# Keep data volumes
docker-compose down --volumes  # ⚠️ This deletes all metrics!
```

#### Restart Services

```bash
# Restart specific service
docker-compose restart prometheus
docker-compose restart grafana

# Reload Prometheus config without restart
curl -X POST http://localhost:9090/-/reload

# Reload Alertmanager config
curl -X POST http://localhost:9093/-/reload
```

### Alert Management

#### View Active Alerts

```bash
# Via Alertmanager API
curl -s http://localhost:9093/api/v2/alerts | \
  jq '.[] | {labels: .labels, state: .status.state}'

# Via Prometheus
curl -s http://localhost:9090/api/v1/alerts | \
  jq '.data.alerts[] | {name: .labels.alertname, state: .state}'

# Via Grafana
# Navigate to: Alerting → Alert Rules
```

#### Silence Alert

```bash
# Create 2-hour silence
curl -X POST http://localhost:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [
      {"name": "alertname", "value": "HighMemoryUsage", "isRegex": false}
    ],
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'",
    "endsAt": "'$(date -u -d '+2 hours' +%Y-%m-%dT%H:%M:%S.000Z)'",
    "createdBy": "ops-engineer",
    "comment": "Planned maintenance"
  }'

# List silences
curl -s http://localhost:9093/api/v2/silences | jq '.'
```

### Dashboard Management

#### Export Dashboard

```bash
# Get dashboard JSON
DASHBOARD_UID="system-overview"
curl -s "http://admin:${GRAFANA_PASSWORD}@localhost:3000/api/dashboards/uid/${DASHBOARD_UID}" | \
  jq '.dashboard' > dashboards/system-overview.json
```

#### Import Dashboard

```bash
# Import from JSON
curl -X POST http://admin:${GRAFANA_PASSWORD}@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/new-dashboard.json

# Or import from Grafana.com
curl -X POST http://admin:${GRAFANA_PASSWORD}@localhost:3000/api/dashboards/import \
  -H "Content-Type: application/json" \
  -d '{"dashboard": {"id": 1860}, "overwrite": true}'
```

### Query and Analysis

#### Run PromQL Query

```bash
# Instant query
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up' | jq '.data.result'

# Range query (last hour)
curl -G http://localhost:9090/api/v1/query_range \
  --data-urlencode 'query=rate(http_requests_total[5m])' \
  --data-urlencode "start=$(date -u -d '1 hour ago' +%s)" \
  --data-urlencode "end=$(date -u +%s)" \
  --data-urlencode 'step=60' | jq '.data.result'
```

#### Analyze Cardinality

```bash
# Check metric cardinality (high cardinality = memory issues)
curl -s http://localhost:9090/api/v1/label/__name__/values | \
  jq -r '.data[]' | wc -l

# Top 10 metrics by series count
curl -s http://localhost:9090/api/v1/targets/metadata | \
  jq -r '.data[].metric' | sort | uniq -c | sort -rn | head -10
```

---

## Incident Response

### P0: Prometheus Down

**Immediate Actions (0-5 minutes):**

```bash
# 1. Check if Prometheus is running
docker-compose ps prometheus

# 2. Check logs
docker-compose logs --tail=100 prometheus

# 3. Restart Prometheus
docker-compose restart prometheus

# 4. Verify startup
curl -f http://localhost:9090/-/healthy

# 5. Check targets are being scraped
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[].health'
```

**If Still Down:**

```bash
# Check disk space
df -h

# Check memory
free -h

# Check for config errors
docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Check TSDB corruption
docker-compose exec prometheus promtool tsdb analyze /prometheus
```

**Recovery:**

```bash
# If config invalid, fix and reload
vi config/prometheus.yml
docker-compose restart prometheus

# If TSDB corrupt, restore from backup
docker-compose down
rm -rf prometheus-data/*
# Restore from backup or accept data loss
docker-compose up -d
```

### P0: High Error Rate Alert

**Investigation:**

```bash
# 1. Check which service has errors
curl -s http://localhost:9090/api/v1/query \
  --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[5m])' | \
  jq '.data.result[] | {job: .metric.job, value: .value[1]}'

# 2. Check error logs
docker-compose logs --tail=200 <service-name> | grep -i error

# 3. Check recent deployments
git log --oneline -5

# 4. Check resource usage
docker stats <service-name>
```

**Mitigation:**

```bash
# If recent deployment caused it
# Rollback deployment (see deployment runbook)

# If resource exhaustion
docker-compose up -d --scale <service-name>=3

# If external dependency down
# Check dependency status, enable circuit breaker if available
```

### P1: High Memory Usage

**Investigation:**

```bash
# Check memory usage by container
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# Check Prometheus memory
curl -s http://localhost:9090/api/v1/query \
  --data-urlencode 'query=process_resident_memory_bytes{job="prometheus"}' | \
  jq '.data.result[0].value[1]'

# Check for high cardinality metrics
curl -s http://localhost:9090/api/v1/status/tsdb | jq '.data.seriesCountByMetricName'
```

**Mitigation:**

```bash
# Drop high-cardinality metrics
# Edit prometheus.yml, add metric_relabel_configs:
# - source_labels: [__name__]
#   regex: 'high_cardinality_metric.*'
#   action: drop

docker-compose restart prometheus

# Reduce retention period (temporary)
docker-compose stop prometheus
# Edit docker-compose.yml: --storage.tsdb.retention.time=7d
docker-compose up -d prometheus
```

---

## Troubleshooting

### Common Issues

#### Issue: Targets showing as "DOWN"

**Diagnosis:**

```bash
# Check target details
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.health=="down")'

# Common causes:
# - Service not running
# - Firewall blocking scrape
# - Incorrect scrape config
```

**Solution:**

```bash
# Verify service is running and /metrics endpoint works
curl http://<target-host>:9100/metrics

# Check scrape config
cat config/prometheus.yml | grep -A 10 job_name

# Reload config if changed
curl -X POST http://localhost:9090/-/reload
```

---

#### Issue: Grafana dashboard shows "No Data"

**Diagnosis:**

```bash
# Check if Prometheus datasource is configured
curl -u admin:${GRAFANA_PASSWORD} \
  http://localhost:3000/api/datasources | jq '.'

# Test datasource
curl -u admin:${GRAFANA_PASSWORD} -X POST \
  http://localhost:3000/api/datasources/proxy/1/api/v1/query \
  -d 'query=up'

# Check if metrics exist
curl -s http://localhost:9090/api/v1/query --data-urlencode 'query=up'
```

**Solution:**

```bash
# Re-add Prometheus datasource
curl -X POST -u admin:${GRAFANA_PASSWORD} \
  http://localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Check alert status
make check-alerts

# Verify all targets are up
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health!="up")'

# Check disk usage
df -h prometheus-data/
```

### Weekly Tasks

```bash
# Review alert firing history
# Grafana → Alerting → Alert Rules → History

# Check for high cardinality metrics
curl -s http://localhost:9090/api/v1/status/tsdb | \
  jq '.data.seriesCountByMetricName | to_entries | sort_by(.value) | reverse | .[0:10]'

# Backup Grafana dashboards
./scripts/backup-dashboards.sh

# Test alert notifications
curl -X POST http://localhost:9093/api/v2/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"test"}}]'
```

### Monthly Tasks

```bash
# Review and optimize PromQL queries
# Check slow queries in Prometheus logs

# Clean up old metrics
# Review retention policy

# Update exporters and monitoring stack
docker-compose pull
docker-compose up -d

# Conduct monitoring drill
# Simulate service failure, verify alerts fire
```

---

## Quick Reference

### Common Commands

```bash
# Start stack
make run

# Check health
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health

# View alerts
curl http://localhost:9093/api/v2/alerts | jq '.'

# Query metrics
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=up'
```

### Emergency Response

```bash
# P0: Restart Prometheus
docker-compose restart prometheus

# P0: Silence noisy alert
curl -X POST http://localhost:9093/api/v2/silences -d '{"matchers":[{"name":"alertname","value":"NoisyAlert"}]}'

# P1: Clear disk space
docker exec prometheus rm -rf /prometheus/wal/*
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** SRE Team
- **Review Schedule:** Quarterly
- **Feedback:** Submit PR with updates

# Troubleshooting Guide

Comprehensive troubleshooting guide for the monitoring stack, organized by symptom.

## Table of Contents
- [Service Won't Start](#service-wont-start)
- [High Memory Usage](#high-memory-usage)
- [Prometheus Scrape Failures](#prometheus-scrape-failures)
- [Alert Not Firing](#alert-not-firing)
- [Dashboard Not Loading](#dashboard-not-loading)
- [Logs Not Appearing](#logs-not-appearing)
- [Container Restart Loops](#container-restart-loops)

---

## Service Won't Start

### Symptoms
- Container exits immediately after `docker compose up`
- Container status shows "Restarting" continuously
- Service never becomes "healthy"

### Diagnosis Steps

```bash
# 1. Check container status
docker compose ps

# 2. View container logs
docker compose logs <service-name>

# 3. Check exit code
docker inspect <container-name> | grep "ExitCode"

# 4. Verify configuration
./scripts/deploy.sh validate
```

### Common Causes and Solutions

#### Configuration Error

**Symptoms**: Logs show "configuration error", "invalid config", "parse error"

**Example**:
```
level=error msg="Error loading config" err="yaml: line 10: could not find expected ':'"
```

**Solution**:
```bash
# Validate configuration
# Prometheus
docker run --rm -v ./prometheus:/prometheus prom/prometheus:v2.48.0 promtool check config /prometheus/prometheus.yml

# Alertmanager
docker run --rm -v ./alertmanager:/alertmanager prom/alertmanager:v0.26.0 amtool check-config /alertmanager/alertmanager.yml

# Fix syntax errors in YAML files
# Common issues:
# - Incorrect indentation (use spaces, not tabs)
# - Missing colons
# - Unquoted special characters
```

#### Port Already in Use

**Symptoms**: Logs show "bind: address already in use"

**Example**:
```
level=error msg="Failed to bind" addr=:9090 err="listen tcp :9090: bind: address already in use"
```

**Solution**:
```bash
# Identify what's using the port
ss -tuln | grep :9090
# Or
lsof -i :9090

# Option 1: Stop conflicting service
sudo systemctl stop <conflicting-service>

# Option 2: Change port binding in docker-compose.yml
# Change: "127.0.0.1:9090:9090"
# To:     "127.0.0.1:9091:9090"
```

#### Permission Denied

**Symptoms**: Logs show "permission denied", "cannot write to directory"

**Example**:
```
level=error msg="opening storage failed" err="permission denied: /prometheus"
```

**Solution**:
```bash
# Check data directory ownership
ls -la data/

# Set proper permissions
# Prometheus, Grafana, etc. run as UID 65534 (nobody) or specific UIDs
chmod -R 777 data/  # Permissive (development)

# Or more restrictive (production)
chown -R 65534:65534 data/prometheus
chown -R 472:472 data/grafana  # Grafana UID
```

#### Out of Memory (OOM)

**Symptoms**: Container disappears, dmesg shows OOM killer

**Example**:
```bash
dmesg | grep -i "out of memory"
# Output: Out of memory: Killed process 12345 (prometheus)
```

**Solution**:
```bash
# Check memory limits
docker inspect prometheus | grep -A 5 "Memory"

# Option 1: Increase limit in docker-compose.yml
# Change: memory: 2G → memory: 4G

# Option 2: Reduce memory usage
# - Decrease retention: PROMETHEUS_RETENTION=7d
# - Drop unused metrics (add metric_relabel_configs)
# - Reduce scrape interval: scrape_interval: 30s

# Option 3: Add swap (temporary)
# Create swap file on Docker host
```

---

## High Memory Usage

### Symptoms
- Container using >90% of memory limit
- Docker host memory exhausted
- Services slow or crashing

### Diagnosis

```bash
# Check container memory usage
docker stats

# Check Prometheus memory breakdown
curl http://localhost:9090/api/v1/status/tsdb | jq .data.headStats

# Check Loki stream count (main memory driver)
curl http://localhost:3100/loki/api/v1/labels | jq '. | length'
```

### Solutions

#### Prometheus High Memory

**Cause 1: High Cardinality**

```bash
# Identify high-cardinality metrics
# In Prometheus, query:
topk(20, count by (__name__)({__name__!=""}))

# Check for metrics with >10K series
# Common culprits:
# - Labels with unique values (user_id, request_id, container_id)
# - High churn (containers created/destroyed frequently)
```

**Fix: Drop high-cardinality metrics**

```yaml
# Add to prometheus.yml
metric_relabel_configs:
  # Drop all container label metrics (high cardinality)
  - source_labels: [__name__]
    regex: 'container_label_.*'
    action: drop

  # Drop specific high-cardinality metric
  - source_labels: [__name__]
    regex: 'http_requests_total'
    action: drop
```

**Cause 2: Long Retention**

```bash
# Check current retention
docker inspect prometheus | grep retention

# Check TSDB size
du -sh data/prometheus
```

**Fix: Reduce retention**

```env
# In .env file
PROMETHEUS_RETENTION=7d  # Was 15d
```

#### Loki High Memory

**Cause: Too many streams (cardinality)**

```bash
# Check stream count
curl http://localhost:3100/loki/api/v1/labels | jq '. | length'

# High stream count (>10K) = memory issues
```

**Fix: Reduce stream cardinality**

```yaml
# In promtail-config.yml
pipeline_stages:
  # Drop high-cardinality labels
  - labeldrop:
      - container_id  # Don't use container ID as label
      - path          # Don't use file path as label
```

---

## Prometheus Scrape Failures

### Symptoms
- Targets show "DOWN" in Prometheus UI (http://localhost:9090/targets)
- `up{instance="..."}` metric = 0
- Gaps in metric graphs

### Diagnosis

```bash
# Check target status
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'

# Test connectivity from Prometheus container
docker exec prometheus wget -O- http://node-exporter:9100/metrics

# Check Prometheus logs
docker logs prometheus | grep -i "scrape"
```

### Common Causes

#### Target Not Accessible

**Solution**:
```bash
# Verify target is running
docker ps | grep node-exporter

# Verify network connectivity
docker exec prometheus ping node-exporter

# Check if target on correct network
docker network inspect monitoring-stack_monitoring_backend
```

#### Scrape Timeout

**Symptoms**: Logs show "context deadline exceeded"

**Causes**:
- Target slow to generate metrics
- Network latency
- Target overloaded

**Solution**:
```yaml
# Increase timeout in prometheus.yml
scrape_configs:
  - job_name: 'slow-target'
    scrape_timeout: 30s  # Was 10s
```

#### Authentication Required

**Symptoms**: HTTP 401 Unauthorized

**Solution**:
```yaml
# Add authentication to scrape config
scrape_configs:
  - job_name: 'protected-target'
    basic_auth:
      username: monitoring
      password: secret
```

---

## Alert Not Firing

### Symptoms
- Expected alert doesn't fire despite condition being met
- Alert shows "Inactive" in Prometheus UI

### Diagnosis

```bash
# Check alert rules loaded
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.type == "alerting")'

# Check rule evaluation
# In Prometheus UI: Status → Rules
# Shows: Alert state, last evaluation time, evaluation duration

# Test alert expression
# In Prometheus UI: Graph tab
# Enter alert expression, check if returns results
```

### Common Causes

#### Alert Expression Never True

**Solution**:
```bash
# Test expression in Prometheus
# Graph: http://localhost:9090/graph
# Query: Your alert expression
# Check if returns results

# Common issues:
# - Label mismatch (check exact label names)
# - Threshold never reached (check actual values)
# - Metric doesn't exist (typo in metric name)
```

#### 'for' Duration Not Met

**Example**:
```yaml
- alert: HighCPU
  expr: cpu_usage > 80
  for: 10m  # Must be true for 10 minutes
```

**Solution**:
- Alert only fires after condition true for full duration
- Check Prometheus UI: Alert shows "Pending" before "Firing"
- Reduce `for` duration if too long

#### Alertmanager Not Receiving

**Solution**:
```bash
# Check Prometheus → Alertmanager connectivity
curl http://localhost:9090/api/v1/alertmanagers

# Should show Alertmanager as "UP"

# Check Alertmanager logs
docker logs alertmanager | grep -i "alert"

# Test by firing alert manually
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"TestAlert"}}]'
```

---

## Dashboard Not Loading

### Symptoms
- Dashboard shows "Dashboard not found"
- Panels show "No data"
- Panels show "Error loading data"

### Diagnosis

```bash
# Check Grafana logs
docker logs grafana | grep -i error

# Check datasource status
curl -u admin:password http://localhost:3000/api/datasources

# Test datasource connectivity
# In Grafana: Configuration → Data Sources → Prometheus → Test
```

### Solutions

#### Dashboard Not Found

**Cause**: Dashboard not provisioned or UID mismatch

**Solution**:
```bash
# Check dashboard files exist
ls grafana/dashboards/

# Check provisioning config
cat grafana/provisioning/dashboards/dashboards.yml

# Verify path is correct
docker exec grafana ls /var/lib/grafana/dashboards

# Restart Grafana to re-provision
docker compose restart grafana

# Check dashboard provisioning logs
docker logs grafana | grep -i dashboard
```

#### Panels Show "No Data"

**Cause**: Datasource not configured or no metrics available

**Solution**:
```bash
# Test Prometheus datasource
curl -u admin:password http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up

# Should return JSON with metrics

# If fails:
# 1. Check Prometheus accessible from Grafana
docker exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up

# 2. Check datasource URL in provisioning
cat grafana/provisioning/datasources/datasources.yml

# 3. Recreate datasource
docker compose restart grafana
```

#### Panels Show "Error Loading Data"

**Cause**: Query timeout, invalid PromQL, datasource unavailable

**Solution**:
```bash
# Check Grafana logs for query errors
docker logs grafana | grep -i "query"

# Test query directly in Prometheus
# Copy panel query, test in Prometheus UI

# Common fixes:
# - Simplify complex queries
# - Add recording rules for expensive queries
# - Increase query timeout in datasource config
```

---

## Logs Not Appearing

### Symptoms
- Loki shows no logs
- Logs Explorer dashboard empty
- Log volume graph shows 0

### Diagnosis

```bash
# Check Promtail status
docker ps | grep promtail
docker logs promtail

# Check Loki status
docker logs loki

# Test Loki API
curl http://localhost:3100/loki/api/v1/labels

# Check if Promtail pushing to Loki
docker logs promtail | grep -i "post"
```

### Solutions

#### Promtail Not Finding Logs

**Cause**: Log path incorrect or permissions

**Solution**:
```bash
# Check log paths in promtail-config.yml
cat promtail/promtail-config.yml

# Verify Docker log directory exists
ls /var/lib/docker/containers/

# Check Promtail can access logs
docker exec promtail ls /var/lib/docker/containers/

# If permission denied:
# Check volume mount in docker-compose.yml
# Should be: /var/lib/docker/containers:/var/lib/docker/containers:ro
```

#### Promtail Not Pushing to Loki

**Cause**: Loki unreachable, network issue

**Solution**:
```bash
# Test connectivity from Promtail to Loki
docker exec promtail wget -O- http://loki:3100/ready

# If fails:
# 1. Verify both on monitoring_backend network
docker network inspect monitoring-stack_monitoring_backend

# 2. Check Loki is healthy
curl http://localhost:3100/ready

# 3. Restart Promtail
docker compose restart promtail
```

#### Loki Rejecting Logs

**Cause**: Rate limit exceeded, old timestamps

**Solution**:
```bash
# Check Loki logs for rejection reasons
docker logs loki | grep -i "reject"

# Common rejections:
# 1. "too many outstanding requests" → Increase ingestion_rate_mb
# 2. "sample too old" → Check timestamp parsing in Promtail
# 3. "per stream rate limit exceeded" → Reduce log volume or increase limit

# Adjust limits in loki-config.yml:
limits_config:
  ingestion_rate_mb: 8  # Was 4
  per_stream_rate_limit: 5MB  # Was 3MB
```

---

## Container Restart Loops

### Symptoms
- Container continuously restarting
- `docker ps` shows status "Restarting (1) X seconds ago"
- Service never becomes healthy

### Diagnosis

```bash
# Check restart count
docker inspect <container> | grep -A 10 "RestartCount"

# Check exit code
docker inspect <container> | grep "ExitCode"

# View logs (may be brief if restarting quickly)
docker logs <container> --tail 100
```

### Common Exit Codes

| Exit Code | Meaning | Common Cause | Solution |
|-----------|---------|--------------|----------|
| 0 | Normal exit | Shouldn't restart | Check restart policy |
| 1 | Application error | Config error, missing file | Check logs, fix config |
| 137 | SIGKILL (OOM) | Out of memory | Increase memory limit |
| 139 | SIGSEGV | Segmentation fault | Application bug, corrupt data |
| 143 | SIGTERM | Graceful shutdown | Normal, shouldn't restart |
| 255 | Exit code out of range | Various | Check application logs |

### Solutions by Exit Code

#### Exit Code 137 (OOM Killed)

```bash
# Increase memory limit
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G

# Or reduce memory usage
# For Prometheus:
# - Reduce retention
# - Drop high-cardinality metrics
```

#### Exit Code 1 (Application Error)

```bash
# Check logs for specific error
docker logs <container> 2>&1 | grep -i error

# Common errors:
# 1. "config file not found" → Check volume mount
# 2. "permission denied" → Check file permissions
# 3. "connection refused" → Check dependency availability
```

#### Health Check Failing

**Symptoms**: Container running but marked unhealthy

```bash
# Check health check status
docker inspect <container> | grep -A 20 "Health"

# Test health check manually
docker exec <container> wget --no-verbose --tries=1 --spider http://localhost:9090/-/healthy

# If fails:
# 1. Service not fully started (increase start_period)
# 2. Health check URL wrong
# 3. Actual service issue (check logs)
```

**Solution**:
```yaml
# Adjust health check in docker-compose.yml
healthcheck:
  start_period: 60s  # Increase from 40s
  interval: 60s      # Check less frequently
  retries: 5         # More retries before marking unhealthy
```

---

## Alert Fatigue (Too Many Alerts)

### Symptoms
- Receiving >10 alerts per day
- Many alerts resolve within minutes (flapping)
- Notifications ignored due to volume

### Solutions

#### Increase Alert Thresholds

```yaml
# If HighCPUUsage firing too often:
# Change threshold from 80% to 85%
- alert: HighCPUUsage
  expr: cpu_usage > 85  # Was 80
  for: 10m  # Was 5m (also increase duration)
```

#### Add Inhibition Rules

```yaml
# In alertmanager.yml
# Suppress warning if critical already firing
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal:
      - 'instance'
```

#### Increase Grouping Windows

```yaml
# In alertmanager.yml
route:
  group_wait: 30s        # Was 10s
  group_interval: 5m     # Was 1m
  repeat_interval: 24h   # Was 12h
```

#### Use Time-Based Routing

```yaml
# Only page during business hours
routes:
  - match:
      severity: critical
    receiver: pagerduty
    active_time_intervals:
      - business_hours

time_intervals:
  - name: business_hours
    time_intervals:
      - times:
          - start_time: '09:00'
            end_time: '17:00'
        weekdays: ['monday:friday']
```

---

## Performance Issues

### Slow Queries

**Symptoms**: Grafana dashboards slow to load, queries timeout

**Diagnosis**:
```bash
# Check slow queries in Prometheus
# Metrics → prometheus_http_request_duration_seconds
# Filter for: handler="/api/v1/query"

# Or check logs
docker logs prometheus | grep "query"
```

**Solutions**:

1. **Use Recording Rules** (pre-compute expensive queries):
```yaml
# In prometheus/alerts/rules.yml
groups:
  - name: recording_rules
    interval: 30s
    rules:
      - record: instance:cpu_usage:rate5m
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

2. **Optimize Queries**:
```promql
# Bad (slow): Nested aggregations
sum(rate(container_cpu_usage_seconds_total[5m])) by (name)

# Good (fast): Use recording rule
instance:cpu_usage:rate5m
```

3. **Reduce Time Range**: Query shorter time ranges
4. **Add Query Timeout**: In Grafana datasource settings

### Disk Space Issues

**Symptoms**: Prometheus/Loki stops ingesting, disk >95% full

**Diagnosis**:
```bash
# Check disk usage
df -h

# Check Prometheus data size
du -sh data/prometheus

# Check Loki data size
du -sh data/loki
```

**Immediate Actions**:
```bash
# Stop ingestion temporarily
docker compose stop promtail

# Clean up Docker resources
docker system prune -af --volumes

# Remove old Prometheus data
# In Prometheus UI: /-/admin → Delete Series
# Query: {__name__=~".+"}  # Delete all (CAUTION!)

# Or reduce retention
# Stop Prometheus
docker compose stop prometheus
# Edit .env: PROMETHEUS_RETENTION=7d
# Start Prometheus
docker compose up -d prometheus
```

---

## Network Connectivity Issues

### Symptoms
- Services can't communicate
- "connection refused" in logs
- "no such host" errors

### Diagnosis

```bash
# Check networks exist
docker network ls | grep monitoring

# Inspect network
docker network inspect monitoring-stack_monitoring_backend

# Check which containers on network
docker network inspect monitoring-stack_monitoring_backend | jq '.[].Containers'

# Test connectivity between containers
docker exec prometheus ping grafana
docker exec grafana wget -O- http://prometheus:9090/api/v1/query?query=up
```

### Solutions

#### Service Not on Correct Network

```yaml
# In docker-compose.yml, ensure service on correct network
prometheus:
  networks:
    - monitoring_frontend
    - monitoring_backend  # Must be on backend to scrape exporters
```

#### DNS Resolution Failing

```bash
# Test DNS inside container
docker exec prometheus nslookup grafana

# If fails:
# 1. Verify service name matches docker-compose.yml
# 2. Restart Docker daemon (DNS cache)
# 3. Recreate networks: docker compose down && docker compose up -d
```

---

## Emergency Procedures

### Complete Stack Reset

**When to use**: After catastrophic failure, data corruption

**WARNING**: This deletes all data. Backup first!

```bash
# 1. Backup (if possible)
./scripts/deploy.sh backup

# 2. Stop and remove everything
docker compose down -v  # -v removes volumes (DATA LOSS!)

# 3. Remove data directories
rm -rf data/*

# 4. Redeploy from scratch
./scripts/deploy.sh start

# 5. Restore from backup (if available)
# Untar backup and move data/ directories
```

**Recovery Time**: 10-15 minutes
**Data Loss**: Back to last backup

### Force Container Restart

**When to use**: Container stuck, health checks failing, investigating issue

```bash
# Graceful restart (sends SIGTERM, waits 10s, then SIGKILL)
docker compose restart <service>

# Forceful restart (immediate SIGKILL)
docker compose kill <service>
docker compose up -d <service>

# Restart all services
docker compose restart
```

---

## Getting Help

### Self-Service Resources

1. **Check logs first**: `docker compose logs <service>`
2. **Search this guide**: Common issues documented here
3. **Check upstream docs**:
   - Prometheus: https://prometheus.io/docs/
   - Grafana: https://grafana.com/docs/
   - Loki: https://grafana.com/docs/loki/

### Debugging Tools

```bash
# Interactive shell in container
docker exec -it prometheus sh

# Inside container, useful commands:
# - wget http://other-service:port (test connectivity)
# - cat /etc/prometheus/prometheus.yml (verify config)
# - ps aux (check running processes)
# - df -h (check disk space)

# Container resource usage
docker stats

# Network troubleshooting
docker network inspect monitoring-stack_monitoring_backend
```

### Log Collection for Support

```bash
# Collect all logs for troubleshooting
docker compose logs > debug-logs.txt

# Service status
docker compose ps > service-status.txt

# Configuration
docker compose config > resolved-config.yml

# Combine into archive
tar -czf debug-info.tar.gz debug-logs.txt service-status.txt resolved-config.yml
```

---

**Last Updated**: November 24, 2024

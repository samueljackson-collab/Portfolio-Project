# Operations Runbook

## Table of Contents
- [Day 1 Operations (Initial Deployment)](#day-1-operations)
- [Day 2 Operations (Ongoing Maintenance)](#day-2-operations)
- [Incident Response](#incident-response)
- [Scaling Guidelines](#scaling-guidelines)
- [Disaster Recovery](#disaster-recovery)
- [Upgrade Procedures](#upgrade-procedures)

## Day 1 Operations

### Initial Deployment

**Timeline**: 30-45 minutes for complete setup

#### Step 1: Environment Preparation (5 min)

```bash
# Navigate to project directory
cd /path/to/PRJ-SDE-002

# Verify prerequisites
./scripts/deploy.sh validate

# Create .env from template
cp .env.example .env

# Edit configuration
nano .env  # Or vim, code, etc.
```

**Required .env changes:**
- [ ] Set `GF_SECURITY_ADMIN_PASSWORD` (strong password, 20+ chars)
- [ ] Set `ALERTMANAGER_SMTP_*` if using email notifications
- [ ] Set `HOSTNAME` to meaningful identifier

#### Step 2: Configuration Review (10 min)

Review and customize configurations based on your environment:

**Prometheus** (`prometheus/prometheus.yml`):
- [ ] Review scrape_interval (15s default, adjust based on need)
- [ ] Add external targets (Proxmox hosts, additional VMs)
- [ ] Review retention period (15d default, adjust for disk space)

**Alert Rules** (`prometheus/alerts/rules.yml`):
- [ ] Review thresholds (80% CPU, 85% memory, etc.)
- [ ] Adjust `for` durations based on tolerance
- [ ] Add custom alerts for your applications

**Alertmanager** (`alertmanager/alertmanager.yml`):
- [ ] Configure notification receivers (email, Slack, PagerDuty)
- [ ] Review routing rules (critical vs warning)
- [ ] Test webhook URLs if using Slack/PagerDuty

#### Step 3: Deploy Stack (5 min)

```bash
# Deploy monitoring stack
./scripts/deploy.sh start
```

**Expected output:**
```
[STEP] Deploying monitoring stack...
[INFO] Pulling Docker images...
[SUCCESS] Images pulled successfully
[INFO] Creating data directories...
[INFO] Setting directory permissions...
[INFO] Starting services...
[SUCCESS] Services started
[INFO] Waiting for services to become healthy...
[INFO] Health check: 7/7 services healthy
[SUCCESS] Deployment complete
```

**Troubleshooting**:
- If services don't become healthy within 2 minutes:
  - Check logs: `./scripts/deploy.sh logs`
  - Verify ports not in use: `ss -tuln | grep -E '3000|9090|9093'`
  - Check disk space: `df -h`

#### Step 4: Verification (10 min)

```bash
# Run health checks
./scripts/health-check.sh

# Expected: All checks PASS
```

**Manual verification checklist:**

1. **Prometheus** (http://localhost:9090):
   - [ ] Navigate to Status → Targets
   - [ ] Verify all targets show "UP" (green)
   - [ ] Check Graph tab, query: `up`
   - [ ] Should see result=1 for all instances

2. **Grafana** (http://localhost:3000):
   - [ ] Login with credentials from .env
   - [ ] Change password immediately (user icon → Change Password)
   - [ ] Navigate to Dashboards → Browse
   - [ ] Open "Infrastructure Overview"
   - [ ] Verify panels show data (not "No data")

3. **Alertmanager** (http://localhost:9093):
   - [ ] Navigate to Status
   - [ ] Verify config loaded successfully
   - [ ] Check "Silences" (should be empty initially)

4. **Loki** (via Grafana):
   - [ ] Open "Logs Explorer" dashboard
   - [ ] Select container in dropdown
   - [ ] Verify logs appear

#### Step 5: Configure Alerts (5 min)

**Test alert pipeline:**

```bash
# Send test alert
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {"alertname": "TestAlert", "severity": "warning"},
    "annotations": {"summary": "Test alert", "description": "Testing notification pipeline"}
  }]'

# Check Slack/Email for notification
# Check Alertmanager UI for alert
```

If notification not received:
- [ ] Check Alertmanager logs: `docker logs alertmanager`
- [ ] Verify SMTP settings in .env
- [ ] Test SMTP connectivity: `telnet smtp.gmail.com 587`
- [ ] Check Slack webhook URL validity

#### Step 6: Documentation (5 min)

Document your deployment:

**Create deployment log:**
```bash
# Log deployment details
cat > deployment-log.md <<EOF
# Deployment Log

**Date**: $(date)
**Operator**: $USER
**Environment**: Production

## Deployment Details
- Prometheus retention: 15d
- Grafana admin user: admin
- Monitored hosts: 1 (node-exporter)
- Alert receivers configured: Email

## Post-Deployment Checks
- [x] All services healthy
- [x] Grafana accessible
- [x] Prometheus scraping targets
- [x] Test alert delivered

## Notes
- Initial deployment successful
- All targets showing UP status
- No firing alerts (expected for new deployment)
EOF
```

**Update monitoring inventory:**
- Document all monitored hosts with IPs
- Record alert notification channels
- Note any customizations made

---

## Day 2 Operations

### Daily Operations (10-15 minutes)

#### Morning Health Check

```bash
# Quick health check
./scripts/health-check.sh

# Check for alerts
curl -s http://localhost:9093/api/v2/alerts | jq '.[] | select(.status.state == "active")'

# Or visit Alertmanager UI
open http://localhost:9093
```

**Review Infrastructure Overview Dashboard:**
1. Open http://localhost:3000/d/infrastructure-overview
2. Check for anomalies:
   - Unexpected CPU/memory spikes
   - Hosts down
   - Disk space trends
3. Investigate any active alerts

#### Log Review

**Check for errors:**

```bash
# Search for errors in last 24 hours (via API)
curl -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={job="docker"} |= "ERROR"' \
  --data-urlencode 'start='$(date -d '24 hours ago' +%s)000000000 \
  --data-urlencode 'end='$(date +%s)000000000
```

**Or use Grafana Logs Explorer:**
1. Open http://localhost:3000/d/logs-explorer
2. Set time range: Last 24 hours
3. Search: `ERROR` or `FATAL`
4. Investigate any unexpected errors

#### Disk Space Monitoring

```bash
# Check data volume sizes
du -sh data/*

# Typical growth rates:
# - prometheus: 1-2GB/day
# - loki: 5-10GB/day (depends on log volume)
# - grafana: <100MB (minimal growth)
# - alertmanager: <10MB

# Check total disk usage
df -h

# Alert if monitoring data volumes >80% of allocated space
```

### Weekly Operations (30-60 minutes)

#### Performance Review

**Check query performance:**

1. Open Prometheus: http://localhost:9090
2. Navigate to Status → TSDB Status
3. Review metrics:
   - **Number of Series**: Should be <100K for single-host (increase = cardinality issue)
   - **Number of Chunks**: Indicates TSDB health
   - **Memory in Chunks**: Should be <50% of memory limit

**Identify slow queries:**

```promql
# Top 10 slowest queries (last 7 days)
topk(10, prometheus_engine_query_duration_seconds{quantile="0.99"})
```

If queries >5s:
- Review query complexity
- Add recording rules for expensive queries
- Increase Prometheus CPU allocation

#### Alert Rule Review

**Check alert effectiveness:**

```bash
# View alert firing history
# In Grafana, create query:
# ALERTS{alertstate="firing"}
# Review over last 7 days

# Questions to ask:
# - Are alerts actionable?
# - Any false positives? (tune thresholds)
# - Any missed incidents? (add new alerts)
# - Response time acceptable?
```

**Alert tuning:**
- If >5 false positives/week for an alert: Increase threshold or `for` duration
- If incident occurred without alert: Add new alert rule
- Document all alert rule changes in Git commit messages

#### Backup

```bash
# Weekly full backup
./scripts/deploy.sh backup

# Verify backup created
ls -lh backups/ | tail -1

# Keep last 4 weekly backups
cd backups
ls -t backup_*.tar.gz | tail -n +5 | xargs rm -f
```

### Monthly Operations (1-2 hours)

#### Update Check and Deployment

**Check for updates:**

```bash
# Check current versions
docker compose images

# Check for newer versions
# Prometheus: https://github.com/prometheus/prometheus/releases
# Grafana: https://github.com/grafana/grafana/releases
# Loki: https://github.com/grafana/loki/releases
```

**Update procedure:**

```bash
# 1. Backup first!
./scripts/deploy.sh backup

# 2. Update image versions in docker-compose.yml
nano docker-compose.yml
# Change: prom/prometheus:v2.48.0 → prom/prometheus:v2.49.0

# 3. Pull new images
docker compose pull

# 4. Review release notes for breaking changes

# 5. Deploy updates
docker compose up -d

# 6. Verify health
./scripts/health-check.sh

# 7. Check for errors in logs
docker compose logs | grep -i error
```

**Rollback if issues:**

```bash
# Revert image version in docker-compose.yml
# Redeploy
docker compose up -d
```

#### Capacity Review

**Analyze storage trends:**

```promql
# Prometheus TSDB size growth
prometheus_tsdb_storage_blocks_bytes

# Predict disk full date
predict_linear(node_filesystem_avail_bytes[7d], 30*24*3600) < 0
```

**Analyze metric cardinality:**

```promql
# Top 10 metrics by cardinality
topk(10, count by (__name__) (up))
```

**Actions if capacity issues:**
- Decrease retention period
- Drop unused metrics
- Archive old data
- Expand disk space

#### Security Review

**Review access logs:**

```logql
# Grafana login attempts
{job="docker", container_name="grafana"} |= "login"

# Failed logins
{job="docker", container_name="grafana"} |= "login" |= "failed"
```

**Update credentials:**
- [ ] Rotate Grafana admin password (quarterly)
- [ ] Rotate SMTP passwords (if applicable)
- [ ] Review and remove unused Grafana users

## Incident Response

### Alert Severity and Response Times

| Severity | Response Time | Escalation Path |
|----------|---------------|-----------------|
| Critical | 5 minutes | Immediate notification → On-call engineer → Team lead (if not resolved in 15 min) |
| Warning | 30 minutes | Email/Slack → Engineer review during business hours |
| Info | Best effort | Email notification → Weekly review |

### Incident Response Workflow

**For Critical Alerts:**

1. **Acknowledge** (1 minute):
   ```bash
   # Silence alert in Alertmanager (if investigating)
   # Prevents alert spam during troubleshooting
   open http://localhost:9093
   # Click alert → Silence → Set duration (1h typical)
   ```

2. **Assess** (2 minutes):
   - What is affected? (host, service, user impact)
   - Is this impacting users? (check application metrics)
   - What changed recently? (deployments, config changes)

3. **Mitigate** (5-10 minutes):
   - Follow alert runbook steps
   - Apply quick fixes (restart service, clear disk, etc.)
   - Redirect traffic if needed

4. **Resolve** (15-30 minutes):
   - Implement permanent fix
   - Verify metrics return to normal
   - Remove silence from Alertmanager

5. **Document** (15 minutes):
   - Create incident report
   - Update runbooks if gaps found
   - Schedule follow-up if needed

### Common Incident Scenarios

#### Scenario 1: Prometheus Down

**Symptoms**:
- Grafana dashboards show "No data"
- Alertmanager not receiving alerts
- Prometheus UI inaccessible

**Immediate Actions**:
```bash
# Check container status
docker ps | grep prometheus

# If not running, check why
docker logs prometheus --tail 50

# Common causes:
# 1. Configuration error
docker run --rm -v ./prometheus:/prometheus prom/prometheus:v2.48.0 promtool check config /prometheus/prometheus.yml

# 2. Disk full
df -h

# 3. OOM killed
docker logs prometheus | grep -i "out of memory"

# Restart
docker compose restart prometheus
```

**Recovery Time**: 2-5 minutes

#### Scenario 2: High Alert Volume (Alert Storm)

**Symptoms**:
- 50+ alerts firing simultaneously
- Alertmanager UI slow
- Notification channels overloaded

**Immediate Actions**:
```bash
# Silence all alerts temporarily (1 hour)
# Via Alertmanager UI: Create silence with matcher: alertname=~".*"

# Or via API:
curl -X POST http://localhost:9093/api/v2/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name": "alertname", "value": ".*", "isRegex": true}],
    "startsAt": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'",
    "endsAt": "'$(date -u -d '+1 hour' +%Y-%m-%dT%H:%M:%S.000Z)'",
    "createdBy": "operator",
    "comment": "Alert storm - investigating root cause"
  }'

# Identify root cause
# Usually: Single host down causing cascade alerts

# Check Prometheus targets
open http://localhost:9090/targets

# Find root cause alert (often InstanceDown)
# Fix root cause
# Remove silence
```

**Recovery Time**: 10-30 minutes

## Day 2 Operations

### Regular Maintenance Tasks

#### Daily (10 minutes)

**Morning Health Check:**
```bash
# Run automated health checks
./scripts/health-check.sh

# Check alert status
open http://localhost:9093

# Review Infrastructure Overview dashboard
open http://localhost:3000/d/infrastructure-overview
```

**Expected State:**
- All health checks PASS
- 0 firing alerts (normal operation)
- CPU usage <70% average
- Memory usage <70% average
- Disk space >15% free on all mounts

**If anything abnormal:**
- Investigate immediately if critical
- Create ticket if warning level
- Document for weekly review if informational

#### Weekly (30 minutes)

**Performance Review:**
```bash
# Check resource usage trends
# In Grafana, Infrastructure Overview:
# - Review CPU/memory trends over last 7 days
# - Identify any capacity concerns
# - Plan scaling if approaching limits
```

**Alert Review:**
```bash
# Count alerts by name (last 7 days)
# In Prometheus, query:
count_over_time(ALERTS{alertstate="firing"}[7d])

# Identify noisy alerts (firing frequently)
# Tune thresholds or add inhibition rules
```

**Log Review:**
```bash
# Check error rate trends
# In Loki, query:
rate({job="docker"} |= "ERROR" [7d])

# If error rate increasing:
# - Investigate source
# - Fix underlying issues
# - Consider new alerts
```

**Cleanup:**
```bash
# Clean up Docker resources
docker system prune -f

# Check volume usage
docker system df -v

# Clean up old backups (keep last 7)
cd backups
ls -t backup_*.tar.gz | tail -n +8 | xargs rm -f
```

#### Monthly (1-2 hours)

**Version Updates:**

Follow [Upgrade Procedures](#upgrade-procedures) section.

**Capacity Planning:**
```bash
# Export capacity metrics for analysis
# Prometheus query (last 30 days):
avg_over_time(instance:cpu_usage:rate5m[30d])

# Disk growth rate
# Predict when disk will fill:
predict_linear(node_filesystem_avail_bytes[30d], 90*24*3600)
```

**Disaster Recovery Drill:**
```bash
# Test restore from backup
# 1. Deploy to test environment
# 2. Restore backup
# 3. Verify functionality
# 4. Document any issues
# 5. Update DR procedures
```

## Scaling Guidelines

### Horizontal Scaling

**When to scale:**
- Prometheus query latency >5s consistently
- CPU usage >70% sustained
- Memory usage >80% sustained

**Scaling Prometheus:**

```yaml
# Option 1: Prometheus Federation
# Deploy additional Prometheus instances
# Configure parent Prometheus to scrape children

# Parent prometheus.yml
scrape_configs:
  - job_name: 'federate'
    honor_labels: true
    metrics_path: '/federate'
    params:
      'match[]':
        - '{job="node-exporter"}'
    static_configs:
      - targets:
          - 'prometheus-child-01:9090'
          - 'prometheus-child-02:9090'
```

**Scaling Loki:**

```yaml
# Split into microservices mode
# Deploy separate: distributor, ingester, querier
# Use object storage (S3, GCS) instead of filesystem
# Add memcached for query caching
```

### Vertical Scaling

**Increase resources:**

```yaml
# In docker-compose.yml, increase limits
prometheus:
  deploy:
    resources:
      limits:
        memory: 4G    # Was 2G
        cpus: '2.0'   # Was 1.0
```

**Reload:**
```bash
docker compose up -d
```

## Disaster Recovery

### Backup Strategy

**What is backed up:**
- Prometheus data (time-series database)
- Grafana data (dashboards, users, settings)
- Loki data (logs)
- Alertmanager data (silences, notification history)
- Configuration files (all YAML configs)

**Backup frequency:**
- **Automated**: Daily at 02:00 via cron
- **Manual**: Before any major changes
- **On-demand**: `./scripts/deploy.sh backup`

**Backup retention:**
- Daily: 7 days
- Weekly: 4 weeks
- Monthly: 3 months

**Backup location:**
- Local: `./backups/backup_YYYYMMDD_HHMMSS.tar.gz`
- Remote: Copy to NAS/S3 for offsite backup

### Recovery Procedures

#### Full Stack Recovery

**Scenario**: Complete monitoring stack failure

**Steps**:

```bash
# 1. Stop failed stack (if running)
docker compose down

# 2. List available backups
ls -lh backups/

# 3. Extract backup
tar -xzf backups/backup_20241124_020000.tar.gz

# 4. Restore data directories
rm -rf data/
mv backup_20241124_020000/data ./

# 5. Restore configurations (if modified)
cp -r backup_20241124_020000/prometheus ./
cp -r backup_20241124_020000/grafana ./
# etc.

# 6. Deploy stack
./scripts/deploy.sh start

# 7. Verify health
./scripts/health-check.sh

# 8. Check data continuity
# In Grafana, verify historical data exists
# Query Prometheus for old metrics
```

**Expected RTO**: 15 minutes
**Expected RPO**: 24 hours (last backup point)

#### Partial Recovery (Single Service)

**Example: Grafana data corruption**

```bash
# Stop Grafana
docker compose stop grafana

# Backup current (corrupted) state
mv data/grafana data/grafana.corrupted

# Extract Grafana data from backup
tar -xzf backups/backup_LATEST.tar.gz backup_TIMESTAMP/data/grafana
mv backup_TIMESTAMP/data/grafana ./data/

# Restart Grafana
docker compose up -d grafana

# Verify
docker logs grafana
open http://localhost:3000
```

## Upgrade Procedures

### Minor Version Updates

**Example**: Prometheus v2.48.0 → v2.48.1

**Risk**: Low (patch releases)
**Downtime**: ~2 minutes

```bash
# 1. Backup
./scripts/deploy.sh backup

# 2. Update docker-compose.yml
sed -i 's/prometheus:v2.48.0/prometheus:v2.48.1/' docker-compose.yml

# 3. Pull new image
docker compose pull prometheus

# 4. Rolling update
docker compose up -d prometheus

# 5. Verify health
docker logs prometheus
curl http://localhost:9090/-/healthy
```

### Major Version Updates

**Example**: Prometheus v2.x → v3.x

**Risk**: Medium-High (potential breaking changes)
**Downtime**: 5-15 minutes

```bash
# 1. Review release notes
# https://github.com/prometheus/prometheus/releases

# 2. Test in non-production environment first!

# 3. Backup production
./scripts/deploy.sh backup

# 4. Schedule maintenance window

# 5. Update docker-compose.yml
nano docker-compose.yml  # Update version

# 6. Update configurations if required
# Check release notes for config changes

# 7. Deploy update
docker compose down
docker compose pull
docker compose up -d

# 8. Verify functionality
./scripts/health-check.sh

# 9. Check for deprecation warnings
docker logs prometheus | grep -i deprecat

# 10. Monitor for issues (24-48 hours)
```

**Rollback if issues:**
```bash
# Restore previous version
sed -i 's/prometheus:v3.0.0/prometheus:v2.48.0/' docker-compose.yml
docker compose up -d prometheus
```

### Configuration Updates

**Safe configuration updates:**

```bash
# 1. Validate configuration locally
docker run --rm -v ./prometheus:/prometheus prom/prometheus:v2.48.0 promtool check config /prometheus/prometheus.yml

# 2. Commit to version control
git add prometheus/prometheus.yml
git commit -m "Update Prometheus config: Add new scrape target"

# 3. Apply to running Prometheus (hot reload)
curl -X POST http://localhost:9090/-/reload

# 4. Verify in UI
open http://localhost:9090/targets

# 5. Monitor for errors
docker logs prometheus -f
```

**If hot reload fails:**
```bash
# Check logs for error
docker logs prometheus

# Fix configuration
nano prometheus/prometheus.yml

# Validate again
# Restart container
docker compose restart prometheus
```

---

**Maintenance Schedule Summary:**

| Frequency | Tasks | Duration |
|-----------|-------|----------|
| **Daily** | Health check, alert review | 10-15 min |
| **Weekly** | Performance review, backups, log analysis | 30-60 min |
| **Monthly** | Updates, capacity planning, DR drill | 1-2 hours |
| **Quarterly** | Security review, credential rotation | 2-3 hours |
| **Annually** | Major version upgrades, architecture review | 1 day |

---

**Last Updated**: November 24, 2024

# Runbook — Project 22 (Autonomous DevOps Platform)

## Overview

Production operations runbook for the Autonomous DevOps Platform. This runbook covers event-driven automation, remediation workflows, runbook execution, incident coordination, and telemetry processing for autonomous operations.

**System Components:**
- Event processing engine
- Telemetry aggregation layer
- Remediation workflow orchestrator
- Runbooks-as-Code execution engine
- Incident coordination system
- Python-based autonomous engine
- Integration adapters (monitoring, alerting, ITSM)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Platform availability** | 99.9% | Autonomous engine uptime |
| **Event processing latency (p95)** | < 5 seconds | Event ingestion → workflow trigger |
| **Workflow success rate** | 95% | Successful remediation completions |
| **Runbook execution time (p95)** | < 2 minutes | Runbook start → completion |
| **False positive rate** | < 5% | Incorrect workflow triggers |
| **Incident detection accuracy** | > 98% | Correctly identified incidents |
| **Auto-remediation success rate** | 80% | Issues resolved without human intervention |

---

## Dashboards & Alerts

### Dashboards

#### Platform Health Dashboard
```bash
# Check autonomous engine status
systemctl status autonomous-devops.service

# Check event processing queue
curl -s http://localhost:9000/api/metrics | jq '.event_queue_depth'

# Check workflow execution status
curl -s http://localhost:9000/api/workflows | jq '.active_workflows'

# View recent events
curl -s http://localhost:9000/api/events/recent | jq '.events[] | {timestamp, type, status}'
```

#### Event Processing Dashboard
```bash
# Event ingestion rate
curl -s http://localhost:9000/api/metrics | jq '.events_per_minute'

# Event types distribution
curl -s http://localhost:9000/api/metrics | jq '.event_types'

# Processing errors
curl -s http://localhost:9000/api/metrics | jq '.processing_errors_last_hour'

# Queue health
python -c "from src.autonomous_engine import get_queue_health; print(get_queue_health())"
```

#### Workflow Execution Dashboard
```bash
# Active workflows
curl -s http://localhost:9000/api/workflows?status=running | jq '.workflows[] | {id, runbook, started_at}'

# Workflow success rate (last 24h)
curl -s http://localhost:9000/api/metrics | jq '.workflow_success_rate_24h'

# Failed workflows
curl -s http://localhost:9000/api/workflows?status=failed | jq '.workflows[] | {id, runbook, error}'

# Average execution time
curl -s http://localhost:9000/api/metrics | jq '.avg_workflow_duration_seconds'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Autonomous engine down | Immediate | Restart engine, check dependencies |
| **P0** | Event processing stopped | Immediate | Clear queue, restart processor |
| **P0** | All workflows failing | Immediate | Check runbook repo, verify credentials |
| **P1** | Workflow success rate < 80% | 15 minutes | Review failures, adjust thresholds |
| **P1** | Event queue depth > 1000 | 15 minutes | Scale processors, investigate backlog |
| **P1** | High false positive rate (>10%) | 30 minutes | Tune detection rules |
| **P2** | Slow workflow execution (>5 min) | 1 hour | Optimize runbooks, check resources |
| **P2** | Integration connectivity issues | 1 hour | Check API credentials, network |
| **P3** | Individual workflow failure | 4 hours | Review logs, update runbook |

#### Alert Queries

```bash
# Check engine health
if ! systemctl is-active --quiet autonomous-devops.service; then
  echo "ALERT: Autonomous DevOps engine is down"
  exit 1
fi

# Check event processing
QUEUE_DEPTH=$(curl -s http://localhost:9000/api/metrics | jq '.event_queue_depth')
if [ $QUEUE_DEPTH -gt 1000 ]; then
  echo "ALERT: Event queue depth is $QUEUE_DEPTH (threshold: 1000)"
fi

# Check workflow success rate
SUCCESS_RATE=$(curl -s http://localhost:9000/api/metrics | jq '.workflow_success_rate_1h')
if (( $(echo "$SUCCESS_RATE < 0.8" | bc -l) )); then
  echo "ALERT: Workflow success rate is ${SUCCESS_RATE}% (threshold: 80%)"
fi

# Check for stuck workflows
STUCK_COUNT=$(curl -s 'http://localhost:9000/api/workflows?status=running' | \
  jq '[.workflows[] | select(.started_at < (now - 3600))] | length')
if [ $STUCK_COUNT -gt 0 ]; then
  echo "ALERT: $STUCK_COUNT workflows stuck for >1 hour"
fi
```

---

## Standard Operations

### Service Management

#### Start/Stop Service
```bash
# Start autonomous engine
sudo systemctl start autonomous-devops.service

# Stop service
sudo systemctl stop autonomous-devops.service

# Restart service
sudo systemctl restart autonomous-devops.service

# Check status
sudo systemctl status autonomous-devops.service

# Enable auto-start
sudo systemctl enable autonomous-devops.service

# View logs
sudo journalctl -u autonomous-devops.service -f
```

#### Manual Service Startup
```bash
# Activate Python environment
cd /opt/autonomous-devops
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run autonomous engine
python src/autonomous_engine.py

# Run with debug logging
LOGLEVEL=DEBUG python src/autonomous_engine.py

# Run in background
nohup python src/autonomous_engine.py > /var/log/autonomous-devops/engine.log 2>&1 &
```

#### Configure Service
```bash
# Edit configuration
vim /etc/autonomous-devops/config.yaml

# Example configuration:
cat > /etc/autonomous-devops/config.yaml << 'EOF'
engine:
  event_processing:
    workers: 4
    queue_size: 10000
    batch_size: 100
  workflow_execution:
    max_concurrent: 20
    timeout: 600
    retry_attempts: 3

integrations:
  prometheus:
    url: http://localhost:9090
    scrape_interval: 15
  alertmanager:
    url: http://localhost:9093
  pagerduty:
    api_key: ${PAGERDUTY_API_KEY}

runbooks:
  repository: /var/lib/autonomous-devops/runbooks
  auto_reload: true
  validation: strict
EOF

# Validate configuration
python -c "from src.autonomous_engine import validate_config; validate_config('/etc/autonomous-devops/config.yaml')"

# Reload service
sudo systemctl restart autonomous-devops.service
```

### Event Processing

#### Monitor Event Queue
```bash
# View queue depth
curl -s http://localhost:9000/api/metrics | jq '.event_queue_depth'

# View event processing rate
curl -s http://localhost:9000/api/metrics | jq '.events_processed_per_second'

# List recent events
curl -s http://localhost:9000/api/events/recent?limit=20 | jq '.events'

# Filter events by type
curl -s 'http://localhost:9000/api/events?type=alert' | jq '.events'

# Event statistics
python -c "from src.autonomous_engine import get_event_stats; print(get_event_stats())"
```

#### Inject Test Event
```bash
# Inject alert event
curl -X POST http://localhost:9000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "type": "alert",
    "severity": "warning",
    "source": "prometheus",
    "labels": {
      "alertname": "HighMemoryUsage",
      "instance": "server-01",
      "severity": "warning"
    },
    "annotations": {
      "summary": "High memory usage detected"
    }
  }'

# Inject metric event
curl -X POST http://localhost:9000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "type": "metric",
    "source": "prometheus",
    "metric_name": "cpu_usage_percent",
    "value": 95,
    "labels": {"instance": "server-01"}
  }'

# Verify event processed
curl -s http://localhost:9000/api/events/recent | jq '.events[0]'
```

#### Clear Event Queue
```bash
# Drain event queue (emergency)
curl -X POST http://localhost:9000/api/admin/drain-queue

# Verify queue is empty
curl -s http://localhost:9000/api/metrics | jq '.event_queue_depth'

# Resume event processing
curl -X POST http://localhost:9000/api/admin/resume-processing
```

### Workflow Management

#### List Workflows
```bash
# List all workflows
curl -s http://localhost:9000/api/workflows | jq '.workflows'

# List running workflows
curl -s 'http://localhost:9000/api/workflows?status=running' | jq '.workflows'

# List failed workflows
curl -s 'http://localhost:9000/api/workflows?status=failed' | jq '.workflows'

# Get workflow details
WORKFLOW_ID="wf-12345"
curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID | jq .
```

#### Execute Runbook Manually
```bash
# Execute runbook
curl -X POST http://localhost:9000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "runbook": "remediation/high-memory-usage.yaml",
    "parameters": {
      "instance": "server-01",
      "threshold": 90
    },
    "dry_run": false
  }'

# Dry-run mode (no actual changes)
curl -X POST http://localhost:9000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{
    "runbook": "remediation/restart-service.yaml",
    "parameters": {"service": "nginx"},
    "dry_run": true
  }' | jq .

# Monitor execution
WORKFLOW_ID=$(curl -s -X POST http://localhost:9000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{"runbook": "test.yaml"}' | jq -r '.workflow_id')

watch -n 2 "curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID | jq '.status'"
```

#### Cancel Workflow
```bash
# Cancel running workflow
WORKFLOW_ID="wf-12345"
curl -X POST http://localhost:9000/api/workflows/$WORKFLOW_ID/cancel

# Verify cancellation
curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID | jq '.status'

# Force kill stuck workflow
curl -X POST http://localhost:9000/api/workflows/$WORKFLOW_ID/kill
```

### Runbook Management

#### List Available Runbooks
```bash
# List all runbooks
curl -s http://localhost:9000/api/runbooks | jq '.runbooks[] | {name, category, description}'

# List by category
curl -s 'http://localhost:9000/api/runbooks?category=remediation' | jq .

# Search runbooks
curl -s 'http://localhost:9000/api/runbooks/search?q=memory' | jq .
```

#### Validate Runbook
```bash
# Validate runbook syntax
curl -X POST http://localhost:9000/api/runbooks/validate \
  -H "Content-Type: application/json" \
  -d '{
    "runbook_path": "remediation/high-cpu-usage.yaml"
  }' | jq .

# Or validate locally
python -c "
from src.autonomous_engine import validate_runbook
validate_runbook('/var/lib/autonomous-devops/runbooks/remediation/high-cpu-usage.yaml')"

# Validate all runbooks
python scripts/validate-all-runbooks.py
```

#### Add/Update Runbook
```bash
# Create new runbook
cat > /var/lib/autonomous-devops/runbooks/remediation/custom-fix.yaml << 'EOF'
name: Custom Fix
description: Custom remediation workflow
category: remediation

triggers:
  - type: alert
    labels:
      alertname: CustomAlert

steps:
  - name: Check system
    action: exec
    command: "systemctl status myservice"

  - name: Restart if needed
    action: exec
    command: "systemctl restart myservice"

  - name: Verify
    action: exec
    command: "curl -f http://localhost:8080/health"
EOF

# Validate new runbook
python -c "from src.autonomous_engine import validate_runbook; validate_runbook('/var/lib/autonomous-devops/runbooks/remediation/custom-fix.yaml')"

# Reload runbooks
curl -X POST http://localhost:9000/api/admin/reload-runbooks

# Verify runbook available
curl -s http://localhost:9000/api/runbooks | jq '.runbooks[] | select(.name=="Custom Fix")'
```

#### Version Control Runbooks
```bash
# Runbooks are stored in Git
cd /var/lib/autonomous-devops/runbooks

# View changes
git status
git diff

# Commit changes
git add remediation/
git commit -m "feat: add custom remediation runbook"
git push

# Pull latest runbooks
git pull
curl -X POST http://localhost:9000/api/admin/reload-runbooks
```

### Integration Management

#### Check Integration Health
```bash
# Check all integrations
curl -s http://localhost:9000/api/integrations/health | jq .

# Check specific integration
curl -s http://localhost:9000/api/integrations/prometheus/health | jq .

# Test Prometheus connection
python -c "
from src.autonomous_engine import test_integration
test_integration('prometheus')"

# Test Alertmanager connection
python -c "
from src.autonomous_engine import test_integration
test_integration('alertmanager')"
```

#### Configure Integrations
```bash
# Update Prometheus integration
curl -X PUT http://localhost:9000/api/integrations/prometheus \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://prometheus:9090",
    "scrape_interval": 15,
    "timeout": 10
  }'

# Update PagerDuty integration
curl -X PUT http://localhost:9000/api/integrations/pagerduty \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "your-api-key",
    "routing_key": "your-routing-key"
  }'

# Test integration after update
curl -s http://localhost:9000/api/integrations/prometheus/test | jq .
```

#### Disable/Enable Integration
```bash
# Disable integration
curl -X POST http://localhost:9000/api/integrations/slack/disable

# Enable integration
curl -X POST http://localhost:9000/api/integrations/slack/enable

# Check integration status
curl -s http://localhost:9000/api/integrations | jq '.[] | {name, enabled, health}'
```

---

## Incident Response

### Detection

**Automated Detection:**
- Service health check failures
- Event processing backlog alerts
- Workflow failure rate alerts
- Integration connectivity failures
- Queue depth threshold breaches

**Manual Detection:**
```bash
# Check service health
systemctl status autonomous-devops.service

# Check for errors
journalctl -u autonomous-devops.service --since "1 hour ago" | grep -i "error\|critical"

# Check event processing
curl -s http://localhost:9000/api/metrics | jq '{queue_depth, processing_errors, events_per_minute}'

# Check workflow failures
curl -s 'http://localhost:9000/api/workflows?status=failed&since=1h' | jq '.workflows | length'

# Check integrations
curl -s http://localhost:9000/api/integrations/health | jq '.[] | select(.healthy==false)'
```

### Triage

#### Severity Classification

**P0: Platform Failure**
- Autonomous engine completely down
- Event processing stopped
- All workflows failing
- Critical integration failures (monitoring)

**P1: Degraded Operations**
- High workflow failure rate (>20%)
- Event processing backlog
- Multiple integration failures
- Stuck workflows causing backpressure

**P2: Performance Issues**
- Slow workflow execution
- Elevated error rates (5-20%)
- Individual integration failures
- Queue depth approaching limits

**P3: Minor Issues**
- Individual workflow failures
- Non-critical integration warnings
- Transient errors
- Performance variations

### Incident Response Procedures

#### P0: Autonomous Engine Down

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check service status
systemctl status autonomous-devops.service

# 2. Attempt restart
sudo systemctl restart autonomous-devops.service

# 3. Check if restart successful
sleep 5
systemctl is-active autonomous-devops.service

# 4. Check logs for errors
journalctl -u autonomous-devops.service -n 100 --no-pager
```

**Investigation (2-10 minutes):**
```bash
# Check Python errors
journalctl -u autonomous-devops.service | grep -i "traceback\|exception" | tail -50

# Check dependencies
cd /opt/autonomous-devops
source venv/bin/activate
pip check

# Check configuration
python -c "from src.autonomous_engine import validate_config; validate_config('/etc/autonomous-devops/config.yaml')"

# Check disk space
df -h /var/lib/autonomous-devops

# Check port conflicts
netstat -tlnp | grep 9000

# Check system resources
free -h
top -b -n 1 | head -20
```

**Recovery:**
```bash
# Fix configuration issues
vim /etc/autonomous-devops/config.yaml
python -c "from src.autonomous_engine import validate_config; validate_config('/etc/autonomous-devops/config.yaml')"

# Reinstall dependencies if needed
cd /opt/autonomous-devops
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Clear corrupted state
rm -rf /var/lib/autonomous-devops/state/*

# Restart service
sudo systemctl restart autonomous-devops.service

# Verify recovery
curl http://localhost:9000/api/health
curl -s http://localhost:9000/api/metrics | jq .
```

#### P0: Event Processing Stopped

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check queue status
curl -s http://localhost:9000/api/metrics | jq '.event_queue_depth'

# 2. Check processing errors
curl -s http://localhost:9000/api/metrics | jq '.processing_errors_last_hour'

# 3. Check worker status
curl -s http://localhost:9000/api/admin/workers | jq .

# 4. Check event sources
curl -s http://localhost:9000/api/integrations/health | jq .
```

**Investigation:**
```bash
# Check for stuck workers
curl -s http://localhost:9000/api/admin/workers | jq '.workers[] | select(.status=="stuck")'

# Check recent processing errors
curl -s http://localhost:9000/api/events?status=error&limit=50 | jq '.events[] | {timestamp, type, error}'

# Check event queue health
python -c "from src.autonomous_engine import diagnose_queue; diagnose_queue()"

# Check for poison messages
curl -s http://localhost:9000/api/admin/poison-messages | jq .
```

**Recovery:**
```bash
# Restart workers
curl -X POST http://localhost:9000/api/admin/restart-workers

# Clear poison messages if found
curl -X POST http://localhost:9000/api/admin/clear-poison-messages

# If queue is corrupt, drain and restart
curl -X POST http://localhost:9000/api/admin/drain-queue
sudo systemctl restart autonomous-devops.service

# Resume processing
curl -X POST http://localhost:9000/api/admin/resume-processing

# Verify recovery
watch -n 5 'curl -s http://localhost:9000/api/metrics | jq ".events_processed_per_second"'
```

#### P0: All Workflows Failing

**Investigation:**
```bash
# Check recent failures
curl -s 'http://localhost:9000/api/workflows?status=failed&limit=20' | \
  jq '.workflows[] | {runbook, error, started_at}'

# Check runbook repository
ls -la /var/lib/autonomous-devops/runbooks/

# Validate runbooks
python scripts/validate-all-runbooks.py

# Check execution environment
python -c "
from src.autonomous_engine import check_execution_environment
check_execution_environment()"

# Check credentials/permissions
python -c "from src.autonomous_engine import verify_credentials; verify_credentials()"
```

**Recovery:**
```bash
# Pull latest runbooks if repository issue
cd /var/lib/autonomous-devops/runbooks
git status
git pull

# Reload runbooks
curl -X POST http://localhost:9000/api/admin/reload-runbooks

# Fix permissions if needed
sudo chown -R autonomous-devops:autonomous-devops /var/lib/autonomous-devops/runbooks

# Test execution environment
curl -X POST http://localhost:9000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{"runbook": "test/noop.yaml", "dry_run": true}' | jq .

# Verify workflows working
# Re-trigger a test workflow
```

#### P1: High Workflow Failure Rate

**Investigation:**
```bash
# Analyze failure patterns
curl -s 'http://localhost:9000/api/workflows?status=failed&since=1h' | \
  jq '.workflows | group_by(.runbook) | map({runbook: .[0].runbook, failures: length}) | sort_by(.failures) | reverse'

# Check specific failing runbook
FAILING_RUNBOOK="remediation/restart-service.yaml"
curl -s "http://localhost:9000/api/workflows?runbook=$FAILING_RUNBOOK&status=failed" | \
  jq '.workflows[] | {error, parameters}'

# Validate problematic runbook
python -c "from src.autonomous_engine import validate_runbook; validate_runbook('/var/lib/autonomous-devops/runbooks/$FAILING_RUNBOOK')"
```

**Remediation:**
```bash
# Disable problematic runbook temporarily
curl -X POST http://localhost:9000/api/runbooks/disable \
  -H "Content-Type: application/json" \
  -d '{"runbook": "remediation/restart-service.yaml"}'

# Fix runbook
vim /var/lib/autonomous-devops/runbooks/remediation/restart-service.yaml

# Validate fix
python -c "from src.autonomous_engine import validate_runbook; validate_runbook('/var/lib/autonomous-devops/runbooks/remediation/restart-service.yaml')"

# Test in dry-run mode
curl -X POST http://localhost:9000/api/runbooks/execute \
  -H "Content-Type: application/json" \
  -d '{"runbook": "remediation/restart-service.yaml", "dry_run": true}' | jq .

# Re-enable runbook
curl -X POST http://localhost:9000/api/runbooks/enable \
  -H "Content-Type: application/json" \
  -d '{"runbook": "remediation/restart-service.yaml"}'
```

#### P1: Event Queue Backlog

**Investigation:**
```bash
# Check queue depth trend
curl -s http://localhost:9000/api/metrics/history?metric=event_queue_depth | jq .

# Check processing rate
curl -s http://localhost:9000/api/metrics | jq '{ingestion_rate, processing_rate, queue_depth}'

# Identify event types causing backlog
curl -s http://localhost:9000/api/admin/queue-analysis | jq '.event_type_distribution'

# Check worker utilization
curl -s http://localhost:9000/api/admin/workers | jq '.workers[] | {id, status, current_task, utilization}'
```

**Mitigation:**
```bash
# Scale up workers temporarily
curl -X POST http://localhost:9000/api/admin/scale-workers \
  -H "Content-Type: application/json" \
  -d '{"workers": 8}'  # from 4 to 8

# Prioritize critical events
curl -X POST http://localhost:9000/api/admin/set-event-priority \
  -H "Content-Type: application/json" \
  -d '{"type": "alert", "severity": "critical", "priority": 1}'

# Temporarily disable low-priority event sources
curl -X POST http://localhost:9000/api/integrations/metrics-scraper/pause

# Monitor queue drainage
watch -n 10 'curl -s http://localhost:9000/api/metrics | jq ".event_queue_depth"'

# Once recovered, re-enable integrations
curl -X POST http://localhost:9000/api/integrations/metrics-scraper/resume

# Scale workers back to normal
curl -X POST http://localhost:9000/api/admin/scale-workers \
  -H "Content-Type: application/json" \
  -d '{"workers": 4}'
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > /var/log/autonomous-devops/incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Autonomous DevOps Platform Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 45 minutes
**Component:** Event Processing

## Timeline
- 14:00: Event queue backlog alert triggered
- 14:05: Investigation started
- 14:10: Identified metrics scraper flooding queue
- 14:15: Scaled workers from 4 to 8
- 14:20: Paused metrics scraper
- 14:30: Queue drained
- 14:45: Restored normal operations

## Root Cause
Metrics scraper integration misconfigured with 1s interval instead of 15s

## Mitigation
- Scaled event workers to handle backlog
- Temporarily paused metrics scraper
- Fixed scraper interval configuration
- Drained queue and resumed normal operations

## Action Items
- [ ] Add queue depth rate-of-change alerting
- [ ] Implement automatic worker scaling
- [ ] Add integration health checks
- [ ] Review all scrape intervals
- [ ] Add integration rate limiting

EOF

# Update monitoring
# Add new alerts based on incident

# Review runbooks
# Update runbooks if needed
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Runbook validation failed"

**Symptoms:**
```bash
$ curl -X POST http://localhost:9000/api/runbooks/execute -d '{"runbook":"test.yaml"}'
{"error": "Runbook validation failed: Invalid YAML syntax"}
```

**Diagnosis:**
```bash
# Validate YAML syntax
python -c "
import yaml
with open('/var/lib/autonomous-devops/runbooks/test.yaml') as f:
    yaml.safe_load(f)"

# Validate runbook schema
python -c "from src.autonomous_engine import validate_runbook; validate_runbook('/var/lib/autonomous-devops/runbooks/test.yaml')"
```

**Solution:**
```bash
# Fix YAML syntax
vim /var/lib/autonomous-devops/runbooks/test.yaml

# Validate fix
python scripts/validate-runbook.py test.yaml

# Reload runbooks
curl -X POST http://localhost:9000/api/admin/reload-runbooks
```

---

#### Issue: Workflow stuck in "running" state

**Symptoms:**
- Workflow shows running for >1 hour
- No progress in logs
- Resource usage normal

**Diagnosis:**
```bash
# Get workflow details
WORKFLOW_ID="wf-12345"
curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID | jq .

# Check workflow logs
curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID/logs | jq .

# Check current step
curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID | jq '.current_step'
```

**Solution:**
```bash
# Cancel stuck workflow
curl -X POST http://localhost:9000/api/workflows/$WORKFLOW_ID/cancel

# If cancel doesn't work, force kill
curl -X POST http://localhost:9000/api/workflows/$WORKFLOW_ID/kill

# Review runbook for hanging commands
vim /var/lib/autonomous-devops/runbooks/$(curl -s http://localhost:9000/api/workflows/$WORKFLOW_ID | jq -r '.runbook')

# Add timeout to runbook steps
# timeout: 300  # 5 minutes
```

---

#### Issue: Integration authentication failure

**Symptoms:**
```bash
{"error": "Prometheus integration: 401 Unauthorized"}
```

**Diagnosis:**
```bash
# Check integration config
curl -s http://localhost:9000/api/integrations/prometheus | jq .

# Test credentials manually
curl -H "Authorization: Bearer $TOKEN" http://prometheus:9090/api/v1/query?query=up

# Check environment variables
sudo systemctl show autonomous-devops.service | grep Environment
```

**Solution:**
```bash
# Update credentials in config
vim /etc/autonomous-devops/config.yaml

# Or update via API
curl -X PUT http://localhost:9000/api/integrations/prometheus \
  -H "Content-Type: application/json" \
  -d '{"url": "http://prometheus:9090", "bearer_token": "new-token"}'

# Restart service to reload credentials
sudo systemctl restart autonomous-devops.service

# Verify integration health
curl -s http://localhost:9000/api/integrations/prometheus/health | jq .
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 15 minutes (configuration and state backups)
- **RTO** (Recovery Time Objective): 10 minutes (service restoration)

### Backup Strategy

**Configuration Backup:**
```bash
# Backup configuration and runbooks
tar czf /backup/autonomous-devops/config-$(date +%Y%m%d).tar.gz \
  /etc/autonomous-devops/config.yaml \
  /var/lib/autonomous-devops/runbooks/

# Automated backup cron
cat > /etc/cron.hourly/autonomous-devops-backup << 'EOF'
#!/bin/bash
tar czf /backup/autonomous-devops/config-$(date +%Y%m%d-%H00).tar.gz \
  /etc/autonomous-devops/ \
  /var/lib/autonomous-devops/runbooks/
find /backup/autonomous-devops/ -name "config-*.tar.gz" -mtime +7 -delete
EOF
chmod +x /etc/cron.hourly/autonomous-devops-backup
```

**State Backup:**
```bash
# Export workflow history
curl -s http://localhost:9000/api/workflows?limit=10000 > \
  /backup/autonomous-devops/workflows-$(date +%Y%m%d).json

# Export event history
curl -s 'http://localhost:9000/api/events?since=30d' > \
  /backup/autonomous-devops/events-$(date +%Y%m%d).json

# Backup database (if using)
pg_dump autonomous_devops > /backup/autonomous-devops/db-$(date +%Y%m%d).sql
```

### Disaster Recovery Procedures

**Complete Platform Loss:**
```bash
# 1. Restore code from Git
cd /opt
git clone https://github.com/org/autonomous-devops.git
cd autonomous-devops

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Restore configuration
LATEST_BACKUP=$(ls -t /backup/autonomous-devops/config-*.tar.gz | head -1)
tar xzf $LATEST_BACKUP -C /

# 4. Restore runbooks from Git
cd /var/lib/autonomous-devops
git clone https://github.com/org/devops-runbooks.git runbooks

# 5. Start service
sudo systemctl daemon-reload
sudo systemctl start autonomous-devops.service

# 6. Verify
curl http://localhost:9000/api/health
curl -s http://localhost:9000/api/runbooks | jq '.runbooks | length'
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check service health
systemctl status autonomous-devops.service

# Check event processing
curl -s http://localhost:9000/api/metrics | jq '{queue_depth, events_per_minute, processing_errors}'

# Check workflow success rate
curl -s http://localhost:9000/api/metrics | jq '.workflow_success_rate_24h'

# Check integration health
curl -s http://localhost:9000/api/integrations/health | jq .
```

### Weekly Tasks
```bash
# Review failed workflows
curl -s 'http://localhost:9000/api/workflows?status=failed&since=7d' | \
  jq '.workflows | group_by(.runbook) | map({runbook: .[0].runbook, failures: length})'

# Validate all runbooks
python scripts/validate-all-runbooks.py

# Check for stuck workflows
curl -s 'http://localhost:9000/api/workflows?status=running' | \
  jq '.workflows[] | select(.started_at < (now - 3600))'

# Review logs for errors
journalctl -u autonomous-devops.service --since "7 days ago" | grep ERROR | less
```

### Monthly Tasks
```bash
# Update dependencies
cd /opt/autonomous-devops
source venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt
sudo systemctl restart autonomous-devops.service

# Review and optimize runbooks
# Analyze execution times
curl -s http://localhost:9000/api/metrics/runbook-performance | jq .

# Backup and archive old workflow data
curl -s 'http://localhost:9000/api/workflows?since=90d' > \
  /archive/workflows-$(date +%Y%m%d).json
curl -X POST http://localhost:9000/api/admin/archive-workflows?before=90d

# Update documentation
git pull
# Review and update this runbook
```

---

## Quick Reference

### Most Common Operations
```bash
# Check service status
systemctl status autonomous-devops.service

# Restart service
sudo systemctl restart autonomous-devops.service

# View logs
journalctl -u autonomous-devops.service -f

# Check metrics
curl -s http://localhost:9000/api/metrics | jq .

# Execute runbook
curl -X POST http://localhost:9000/api/runbooks/execute \
  -d '{"runbook":"remediation/restart-service.yaml","parameters":{"service":"nginx"}}'

# List running workflows
curl -s 'http://localhost:9000/api/workflows?status=running' | jq .

# Check integrations
curl -s http://localhost:9000/api/integrations/health | jq .
```

### Emergency Response
```bash
# P0: Engine down
sudo systemctl restart autonomous-devops.service
journalctl -u autonomous-devops.service -n 100

# P0: Event processing stopped
curl -X POST http://localhost:9000/api/admin/restart-workers
curl -s http://localhost:9000/api/metrics | jq .

# P1: Queue backlog
curl -X POST http://localhost:9000/api/admin/scale-workers -d '{"workers":8}'
curl -s http://localhost:9000/api/metrics | jq '.event_queue_depth'

# P1: Workflow failures
curl -s 'http://localhost:9000/api/workflows?status=failed' | jq .
python scripts/validate-all-runbooks.py
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

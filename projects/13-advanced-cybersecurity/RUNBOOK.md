# Runbook — Project 13 (Advanced Cybersecurity Platform)

## Overview

Production operations runbook for Security Orchestration and Automated Response (SOAR) platform. This runbook covers SIEM alert consolidation, threat intelligence enrichment, risk scoring, automated response playbooks, and incident management for enterprise security operations.

**System Components:**
- SOAR engine (alert orchestration and automation)
- SIEM integration (Splunk, ELK, QRadar connectors)
- Threat intelligence adapters (VirusTotal, AbuseIPDB, MISP)
- CMDB integration (asset context and criticality)
- Risk scoring engine
- Automated response backends (isolation, credential rotation, ticketing)
- Playbook execution engine
- Security metrics and dashboards

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Alert processing time** | < 30 seconds | Time from SIEM alert → SOAR enrichment |
| **Enrichment success rate** | > 95% | Successfully enriched alerts / total alerts |
| **Playbook execution time** | < 5 minutes | Time from trigger → completion |
| **False positive rate** | < 10% | False positives / total alerts |
| **Response action success** | > 99% | Successful automations / total actions |
| **Mean time to respond (MTTR)** | < 15 minutes | Alert time → remediation complete |
| **Threat intel freshness** | < 5 minutes | Age of threat intelligence data |

---

## Dashboards & Alerts

### Dashboards

#### Security Operations Dashboard
```bash
# Check SOAR engine status
systemctl status soar-engine
curl -f http://localhost:8080/health

# Check alert ingestion rate
curl -s http://localhost:8080/api/metrics | \
  jq '.alerts_ingested_last_hour'

# View active incidents
curl -s http://localhost:8080/api/incidents?status=active | \
  jq '.incidents[] | {id, severity, asset, status}'

# Check playbook execution stats
curl -s http://localhost:8080/api/playbooks/stats | \
  jq '.executions_last_24h'
```

#### Threat Intelligence Dashboard
```bash
# Check enrichment adapter status
for adapter in virustotal abuseipdb misp cmdb; do
  curl -sf http://localhost:8080/api/adapters/$adapter/status && \
    echo "$adapter: OK" || echo "$adapter: FAILED"
done

# Check threat intel cache status
redis-cli INFO | grep -E "used_memory_human|keyspace"

# View recent threat indicators
curl -s http://localhost:8080/api/threats/recent | \
  jq '.threats[] | {indicator, type, severity, source}'

# Check API quota status
python src/check_api_quotas.py
```

#### Risk Scoring Dashboard
```bash
# View high-risk assets
curl -s http://localhost:8080/api/assets/high-risk | \
  jq '.assets[] | {hostname, risk_score, reasons}'

# Check risk score distribution
curl -s http://localhost:8080/api/analytics/risk-distribution

# Historical incident patterns
curl -s http://localhost:8080/api/analytics/incident-trends?days=30 | \
  jq '.trends'

# Asset criticality matrix
curl -s http://localhost:8080/api/assets/criticality-matrix
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | SOAR engine down | Immediate | Restart engine, check dependencies |
| **P0** | Critical asset compromised | Immediate | Execute containment playbook |
| **P0** | Mass credential compromise | Immediate | Force password reset, revoke tokens |
| **P1** | High-severity alert unprocessed > 5 min | 5 minutes | Check enrichment, escalate |
| **P1** | Response automation failed | 15 minutes | Manual intervention, investigate failure |
| **P1** | Threat intel feed unavailable | 30 minutes | Use cached data, contact vendor |
| **P2** | Elevated false positive rate | 1 hour | Tune detection rules, review playbooks |
| **P2** | Enrichment adapter degraded | 2 hours | Check API limits, rotate keys |
| **P3** | Individual playbook timeout | 4 hours | Review playbook logic, optimize |

#### Alert Queries

```bash
# Check for unprocessed high-severity alerts
UNPROCESSED=$(curl -s http://localhost:8080/api/alerts?status=new\&severity=high | jq '.alerts | length')
if [ $UNPROCESSED -gt 5 ]; then
  echo "ALERT: $UNPROCESSED high-severity alerts unprocessed"
fi

# Check SOAR engine health
if ! curl -sf http://localhost:8080/health > /dev/null; then
  echo "ALERT: SOAR engine is down"
  exit 1
fi

# Check enrichment failure rate
ENRICHMENT_FAILURES=$(curl -s http://localhost:8080/api/metrics | \
  jq '.enrichment_failures_last_hour')
TOTAL_ALERTS=$(curl -s http://localhost:8080/api/metrics | \
  jq '.alerts_processed_last_hour')

if [ $TOTAL_ALERTS -gt 0 ]; then
  FAILURE_RATE=$(echo "scale=2; $ENRICHMENT_FAILURES / $TOTAL_ALERTS * 100" | bc)
  if [ $(echo "$FAILURE_RATE > 10" | bc) -eq 1 ]; then
    echo "ALERT: Enrichment failure rate is ${FAILURE_RATE}%"
  fi
fi

# Check for failed response actions
FAILED_ACTIONS=$(curl -s http://localhost:8080/api/actions?status=failed\&since=1h | \
  jq '.actions | length')
if [ $FAILED_ACTIONS -gt 5 ]; then
  echo "ALERT: $FAILED_ACTIONS response actions failed in last hour"
fi

# Check threat intel cache age
CACHE_AGE=$(redis-cli GET threat_intel_last_update)
CURRENT_TIME=$(date +%s)
AGE_SECONDS=$((CURRENT_TIME - CACHE_AGE))
if [ $AGE_SECONDS -gt 600 ]; then
  echo "ALERT: Threat intelligence cache is stale (${AGE_SECONDS}s old)"
fi
```

---

## Standard Operations

### SOAR Engine Operations

#### Start/Stop SOAR Engine
```bash
# Start SOAR engine
sudo systemctl start soar-engine

# Check status
sudo systemctl status soar-engine

# View logs
sudo journalctl -u soar-engine -f

# Stop engine (gracefully)
sudo systemctl stop soar-engine

# Restart engine
sudo systemctl restart soar-engine

# Manual start for debugging
cd /home/user/Portfolio-Project/projects/13-advanced-cybersecurity
source venv/bin/activate
python src/soar_engine.py --config config/soar_config.yaml --debug
```

#### Configure SOAR Engine
```bash
# Edit main configuration
vim config/soar_config.yaml

# Example configuration:
cat > config/soar_config.yaml << 'EOF'
soar:
  listen_address: "0.0.0.0"
  port: 8080
  workers: 4

siem_integrations:
  - name: splunk
    type: splunk
    url: https://splunk.example.com:8089
    api_token: ${SPLUNK_TOKEN}
    index: security

  - name: elastic
    type: elasticsearch
    url: https://elastic.example.com:9200
    api_key: ${ELASTIC_KEY}
    index: security-*

enrichment:
  adapters:
    - virustotal
    - abuseipdb
    - misp
    - cmdb

  cache:
    enabled: true
    ttl_seconds: 3600
    backend: redis

risk_scoring:
  enabled: true
  model: weighted
  weights:
    asset_criticality: 0.3
    threat_severity: 0.4
    historical_incidents: 0.3

response:
  automation_enabled: true
  require_approval: false  # For high-risk actions
  timeout_seconds: 300

playbooks:
  directory: /opt/soar/playbooks
  max_concurrent: 10
EOF

# Validate configuration
python src/validate_config.py config/soar_config.yaml

# Reload configuration (no restart)
curl -X POST http://localhost:8080/api/admin/reload-config

# Or restart to apply changes
sudo systemctl restart soar-engine
```

### Alert Management

#### Process Incoming Alerts
```bash
# Submit alert manually (for testing)
curl -X POST http://localhost:8080/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "source": "splunk",
    "alert_id": "alert-12345",
    "severity": "high",
    "type": "suspicious_login",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "asset": {
      "hostname": "web-server-01",
      "ip": "192.168.1.100"
    },
    "indicators": {
      "source_ip": "203.0.113.45",
      "username": "admin"
    }
  }'

# Process alerts from file
python src/soar_engine.py --alerts data/alerts.json

# Check alert processing queue
curl -s http://localhost:8080/api/alerts/queue | \
  jq '{queued: .count, oldest: .oldest_timestamp}'

# View alert details
ALERT_ID="alert-12345"
curl -s http://localhost:8080/api/alerts/$ALERT_ID | jq .

# Update alert status
curl -X PATCH http://localhost:8080/api/alerts/$ALERT_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "investigating", "assignee": "analyst@example.com"}'
```

#### Bulk Alert Operations
```bash
# List all active alerts
curl -s http://localhost:8080/api/alerts?status=active | \
  jq '.alerts[] | {id, severity, asset, created_at}'

# Close false positive alerts
curl -X POST http://localhost:8080/api/alerts/bulk-update \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {"status": "new", "type": "false_positive"},
    "action": "close",
    "reason": "Confirmed false positive"
  }'

# Export alerts to CSV
curl -s "http://localhost:8080/api/alerts/export?format=csv&start=$(date -d '24 hours ago' +%Y-%m-%d)" \
  > alerts_$(date +%Y%m%d).csv

# Delete old resolved alerts
curl -X DELETE "http://localhost:8080/api/alerts/cleanup?status=resolved&older_than=90days"
```

### Threat Intelligence Operations

#### Configure Enrichment Adapters
```bash
# Configure VirusTotal adapter
cat > config/adapters/virustotal.yaml << 'EOF'
name: virustotal
type: threat_intel
enabled: true
api_key: ${VIRUSTOTAL_API_KEY}
rate_limit: 4  # requests per minute
timeout: 10
cache_ttl: 3600

enrichment_fields:
  - ip_address
  - file_hash
  - domain
  - url
EOF

# Configure AbuseIPDB adapter
cat > config/adapters/abuseipdb.yaml << 'EOF'
name: abuseipdb
type: threat_intel
enabled: true
api_key: ${ABUSEIPDB_API_KEY}
rate_limit: 1000  # requests per day
timeout: 5

enrichment_fields:
  - ip_address

confidence_threshold: 75
EOF

# Configure CMDB adapter
cat > config/adapters/cmdb.yaml << 'EOF'
name: cmdb
type: asset_context
enabled: true
url: https://cmdb.example.com/api
api_token: ${CMDB_TOKEN}

fields:
  - hostname
  - ip_address
  - asset_criticality
  - owner
  - business_unit
EOF

# Reload adapter configurations
curl -X POST http://localhost:8080/api/adapters/reload
```

#### Manage Threat Intelligence
```bash
# Query threat intelligence
curl -s "http://localhost:8080/api/threats/lookup?type=ip&value=203.0.113.45" | jq .

# Add custom threat indicator
curl -X POST http://localhost:8080/api/threats/indicators \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ip",
    "value": "198.51.100.123",
    "severity": "high",
    "source": "manual",
    "tags": ["c2_server", "malware"],
    "expires_at": "'$(date -u -d '+30 days' +%Y-%m-%dT%H:%M:%SZ)'"
  }'

# Import threat feed
curl -X POST http://localhost:8080/api/threats/import \
  -H "Content-Type: application/json" \
  -d @threat_feeds/malicious_ips.json

# Check enrichment adapter health
curl -s http://localhost:8080/api/adapters/health | \
  jq '.adapters[] | {name, status, last_success, errors}'

# Clear threat intelligence cache
redis-cli FLUSHDB

# Or selective cache clear
redis-cli DEL "threat:ip:203.0.113.45"
```

#### Monitor API Quotas
```bash
# Check all API quotas
python src/check_api_quotas.py

# VirusTotal quota
curl -s https://www.virustotal.com/api/v3/users/$(cat config/vt_user_id) \
  -H "x-apikey: $VIRUSTOTAL_API_KEY" | \
  jq '.data.attributes.quotas'

# AbuseIPDB quota
curl -s https://api.abuseipdb.com/api/v2/check-block \
  -H "Key: $ABUSEIPDB_API_KEY" \
  -H "Accept: application/json" | \
  jq .
```

### Playbook Operations

#### List and Manage Playbooks
```bash
# List available playbooks
curl -s http://localhost:8080/api/playbooks | \
  jq '.playbooks[] | {name, description, trigger_types}'

# View playbook details
curl -s http://localhost:8080/api/playbooks/isolate_host | jq .

# Execute playbook manually
curl -X POST http://localhost:8080/api/playbooks/isolate_host/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "hostname": "web-server-01",
      "reason": "Suspected compromise",
      "ticket_id": "INC-12345"
    }
  }'

# Check playbook execution status
EXECUTION_ID="exec-67890"
curl -s http://localhost:8080/api/playbooks/executions/$EXECUTION_ID | \
  jq '{status, progress, steps_completed, current_step}'

# Cancel running playbook
curl -X POST http://localhost:8080/api/playbooks/executions/$EXECUTION_ID/cancel
```

#### Create Custom Playbook
```bash
# Create new playbook
cat > playbooks/credential_rotation.yaml << 'EOF'
name: credential_rotation
description: Rotate compromised credentials and notify user
version: "1.0"

triggers:
  - alert_type: credential_compromise
  - alert_severity: [high, critical]

parameters:
  required:
    - username
    - ticket_id
  optional:
    - notification_email

steps:
  - name: disable_account
    action: ad.disable_user
    parameters:
      username: "{{ username }}"
    on_failure: abort

  - name: revoke_sessions
    action: okta.revoke_user_sessions
    parameters:
      username: "{{ username }}"

  - name: reset_password
    action: ad.force_password_reset
    parameters:
      username: "{{ username }}"

  - name: create_ticket_update
    action: jira.add_comment
    parameters:
      ticket_id: "{{ ticket_id }}"
      comment: "Credentials rotated for user {{ username }}"

  - name: notify_user
    action: email.send
    parameters:
      to: "{{ notification_email | default(username + '@example.com') }}"
      subject: "Security Alert: Your credentials have been reset"
      template: credential_reset_notification

rollback:
  - name: re_enable_account
    action: ad.enable_user
    parameters:
      username: "{{ username }}"
    condition: "steps.disable_account.success"
EOF

# Validate playbook
python src/validate_playbook.py playbooks/credential_rotation.yaml

# Load playbook
curl -X POST http://localhost:8080/api/playbooks/load \
  -H "Content-Type: application/json" \
  -d '{"playbook_file": "playbooks/credential_rotation.yaml"}'

# Test playbook (dry-run)
curl -X POST http://localhost:8080/api/playbooks/credential_rotation/test \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "username": "jdoe",
      "ticket_id": "INC-12345"
    },
    "dry_run": true
  }'
```

### Risk Scoring Operations

#### Configure Risk Model
```bash
# Edit risk scoring configuration
vim config/risk_scoring.yaml

# Example configuration:
cat > config/risk_scoring.yaml << 'EOF'
risk_model:
  type: weighted
  version: "2.0"

weights:
  asset_criticality: 0.3
  threat_severity: 0.4
  historical_incidents: 0.2
  vulnerability_score: 0.1

asset_criticality:
  critical: 10
  high: 7
  medium: 5
  low: 2
  unknown: 1

threat_severity:
  critical: 10
  high: 7
  medium: 5
  low: 2
  info: 1

decay:
  enabled: true
  half_life_days: 90

thresholds:
  critical: 9.0
  high: 7.0
  medium: 5.0
  low: 3.0
EOF

# Recalculate all risk scores
curl -X POST http://localhost:8080/api/risk/recalculate

# Get risk score for specific asset
curl -s "http://localhost:8080/api/risk/score?asset=web-server-01" | \
  jq '{asset, score, factors, last_calculated}'
```

#### Monitor High-Risk Assets
```bash
# List top high-risk assets
curl -s http://localhost:8080/api/risk/top-assets?limit=20 | \
  jq '.assets[] | {hostname, score, recent_incidents}'

# Assets with increasing risk
curl -s http://localhost:8080/api/risk/trending?direction=up | \
  jq '.assets[] | {hostname, current_score, previous_score, delta}'

# Generate risk report
curl -s "http://localhost:8080/api/reports/risk?format=pdf&period=30days" \
  > risk_report_$(date +%Y%m%d).pdf

# Export risk data
curl -s "http://localhost:8080/api/risk/export?format=csv" \
  > risk_scores_$(date +%Y%m%d).csv
```

### Response Automation Operations

#### Configure Response Backends
```bash
# Configure isolation backend (firewall)
cat > config/response/firewall.yaml << 'EOF'
name: firewall_isolation
type: network_isolation
enabled: true

palo_alto:
  host: firewall.example.com
  api_key: ${PALOALTO_API_KEY}

actions:
  isolate_host:
    security_policy: quarantine
    address_group: isolated_hosts

  restore_host:
    security_policy: production
    address_group: production_hosts
EOF

# Configure credential rotation backend
cat > config/response/ad.yaml << 'EOF'
name: active_directory
type: identity_management
enabled: true

connection:
  host: ad.example.com
  port: 636
  use_ssl: true
  bind_dn: ${AD_BIND_DN}
  bind_password: ${AD_BIND_PASSWORD}

actions:
  disable_user:
    ou: "OU=Users,DC=example,DC=com"

  force_password_reset:
    password_policy: strong
    require_change_at_next_logon: true
EOF

# Configure ticketing backend
cat > config/response/jira.yaml << 'EOF'
name: jira
type: ticketing
enabled: true

connection:
  url: https://jira.example.com
  api_token: ${JIRA_API_TOKEN}
  project_key: SEC

actions:
  create_incident:
    issue_type: Incident
    labels: [security, automated]

  add_comment:
    visibility: internal
EOF

# Reload response configurations
curl -X POST http://localhost:8080/api/response/reload
```

#### Test Response Actions
```bash
# Test host isolation (dry-run)
curl -X POST http://localhost:8080/api/response/test \
  -H "Content-Type: application/json" \
  -d '{
    "action": "isolate_host",
    "parameters": {"hostname": "web-server-01"},
    "dry_run": true
  }'

# Execute isolation
curl -X POST http://localhost:8080/api/response/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "isolate_host",
    "parameters": {
      "hostname": "web-server-01",
      "reason": "Suspected malware infection",
      "ticket_id": "INC-12345"
    }
  }'

# Restore host from isolation
curl -X POST http://localhost:8080/api/response/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "restore_host",
    "parameters": {
      "hostname": "web-server-01",
      "approved_by": "security-team@example.com"
    }
  }'

# Check action history
curl -s "http://localhost:8080/api/response/history?asset=web-server-01" | \
  jq '.actions[] | {timestamp, action, status, executed_by}'
```

---

## Incident Response

### Detection

**Automated Detection:**
- SIEM alert ingestion
- Threat intelligence matches
- Automated playbook triggers
- Anomaly detection

**Manual Detection:**
```bash
# Check SOAR engine health
curl http://localhost:8080/health

# Review unprocessed alerts
curl -s "http://localhost:8080/api/alerts?status=new&severity=high,critical" | jq .

# Check recent playbook failures
curl -s "http://localhost:8080/api/playbooks/executions?status=failed&since=1h" | \
  jq '.executions[] | {id, playbook, error, timestamp}'

# Review system logs
sudo journalctl -u soar-engine --since "10 minutes ago" | grep -i error

# Check enrichment failures
curl -s http://localhost:8080/api/metrics | \
  jq '{enrichment_failures, total_alerts, failure_rate}'
```

### Triage

#### Severity Classification

**P0: Security Incident in Progress**
- SOAR engine completely down during active incident
- Critical asset compromise confirmed
- Mass credential breach
- Automated containment failing

**P1: Operational Degradation**
- SOAR engine degraded performance
- High-severity alerts not processing
- Response automation failures
- Threat intelligence feeds unavailable

**P2: Reduced Capability**
- Single enrichment adapter failing
- Playbook execution slow
- Elevated false positive rate
- Non-critical automation issues

**P3: Minor Issues**
- Individual playbook timeout
- Single alert processing error
- Non-critical configuration warnings

### Incident Response Procedures

#### P0: SOAR Engine Down During Active Incident

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check engine status
sudo systemctl status soar-engine

# 2. Check logs
sudo journalctl -u soar-engine -n 100 --no-pager

# 3. Attempt restart
sudo systemctl restart soar-engine

# 4. Verify restart
curl -f http://localhost:8080/health

# 5. If restart fails, start manually for diagnostics
cd /home/user/Portfolio-Project/projects/13-advanced-cybersecurity
source venv/bin/activate
python src/soar_engine.py --debug 2>&1 | tee /tmp/soar-debug.log
```

**Investigation (5-20 minutes):**
```bash
# Check dependencies
systemctl status redis
systemctl status postgresql

# Check database connectivity
psql -h localhost -U soar -d soar_db -c "SELECT 1;"

# Check disk space
df -h /var/lib/soar /var/log/soar

# Check memory
free -h
ps aux | grep soar | awk '{print $6}' | paste -sd+ | bc

# Check for Python errors
grep -i "traceback\|exception\|error" /var/log/soar/soar-engine.log | tail -50

# Check configuration
python src/validate_config.py config/soar_config.yaml
```

**Recovery:**
```bash
# If dependency issue, restart dependencies
sudo systemctl restart redis postgresql
sleep 10
sudo systemctl restart soar-engine

# If database connection issue
psql -h localhost -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='soar_db';"
sudo systemctl restart soar-engine

# If disk full
# Clean old logs
find /var/log/soar -name "*.log.*" -mtime +7 -delete
# Clean Redis cache if needed
redis-cli FLUSHDB

# If configuration error
cp config/soar_config.yaml.backup config/soar_config.yaml
sudo systemctl restart soar-engine

# Manual failover to backup instance (if available)
./scripts/failover_to_backup.sh

# Verify recovery
curl http://localhost:8080/health
curl -s http://localhost:8080/api/alerts?status=new | jq '.alerts | length'
```

#### P0: Critical Asset Compromised

**Immediate Actions (0-2 minutes):**
```bash
# 1. Trigger isolation playbook immediately
curl -X POST http://localhost:8080/api/playbooks/isolate_host/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "hostname": "critical-db-01",
      "reason": "Confirmed compromise",
      "emergency": true
    }
  }'

# 2. Create incident ticket
curl -X POST http://localhost:8080/api/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "severity": "critical",
    "title": "Critical asset compromised: critical-db-01",
    "description": "Confirmed malicious activity on critical database server",
    "affected_assets": ["critical-db-01"],
    "response_team": "security-incident-response@example.com"
  }'

# 3. Notify security team
curl -X POST http://localhost:8080/api/notifications/emergency \
  -H "Content-Type: application/json" \
  -d '{
    "message": "P0: Critical asset compromised - critical-db-01",
    "channels": ["pagerduty", "slack", "email"]
  }'
```

**Containment (2-15 minutes):**
```bash
# Isolate affected asset
# (Already triggered above, verify completion)
curl -s http://localhost:8080/api/response/status?asset=critical-db-01 | \
  jq '{isolated, isolation_time, status}'

# Disable compromised accounts
curl -X POST http://localhost:8080/api/playbooks/disable_accounts/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "usernames": ["compromised_user1", "compromised_user2"],
      "reason": "Account compromise - incident INC-12345"
    }
  }'

# Revoke access tokens/sessions
curl -X POST http://localhost:8080/api/playbooks/revoke_sessions/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "users": ["compromised_user1"],
      "services": ["all"]
    }
  }'

# Block malicious IPs at firewall
curl -X POST http://localhost:8080/api/response/block_ips \
  -H "Content-Type: application/json" \
  -d '{
    "ips": ["203.0.113.45", "198.51.100.123"],
    "duration": "permanent",
    "reason": "C2 communication - INC-12345"
  }'

# Collect forensic data
./scripts/collect_forensics.sh critical-db-01
```

**Eradication & Recovery (15+ minutes):**
```bash
# Once forensics collected and threat removed:

# Restore from clean backup
./scripts/restore_from_backup.sh critical-db-01 --snapshot clean-snapshot-20251109

# Rotate all credentials
curl -X POST http://localhost:8080/api/playbooks/rotate_all_credentials/execute \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "scope": "asset",
      "asset": "critical-db-01"
    }
  }'

# Remove from isolation (when safe)
curl -X POST http://localhost:8080/api/response/restore_host \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "critical-db-01",
    "approved_by": "security-manager@example.com",
    "ticket_id": "INC-12345"
  }'

# Enhanced monitoring
curl -X POST http://localhost:8080/api/monitoring/enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "asset": "critical-db-01",
    "duration_days": 30,
    "alert_threshold": "low"
  }'
```

#### P1: High-Severity Alerts Not Processing

**Investigation:**
```bash
# Check alert queue
curl -s http://localhost:8080/api/alerts/queue | \
  jq '{queue_depth, oldest_alert, processing_rate}'

# Check enrichment adapter status
curl -s http://localhost:8080/api/adapters/health | \
  jq '.adapters[] | select(.status != "healthy")'

# Check worker threads
curl -s http://localhost:8080/api/metrics/workers | \
  jq '{active, idle, busy}'

# Check for stuck alerts
curl -s 'http://localhost:8080/api/alerts?status=processing&age_minutes=>30' | \
  jq '.alerts[] | {id, age, current_step}'
```

**Mitigation:**
```bash
# Increase worker threads temporarily
curl -X POST http://localhost:8080/api/admin/scale-workers \
  -H "Content-Type: application/json" \
  -d '{"workers": 8}'

# Skip enrichment for critical alerts (temporary)
curl -X POST http://localhost:8080/api/admin/bypass-enrichment \
  -H "Content-Type: application/json" \
  -d '{"severity": ["critical"], "duration_minutes": 60}'

# Reset stuck alerts
curl -X POST http://localhost:8080/api/alerts/reset-stuck

# Process critical alerts manually
curl -s 'http://localhost:8080/api/alerts?status=new&severity=critical' | \
  jq -r '.alerts[].id' | \
  while read alert_id; do
    python src/manual_alert_processor.py --alert-id $alert_id
  done
```

#### P1: Response Automation Failures

**Investigation:**
```bash
# List recent failures
curl -s 'http://localhost:8080/api/response/history?status=failed&since=1h' | \
  jq '.actions[] | {action, error, parameters, timestamp}'

# Check response backend connectivity
for backend in firewall ad okta jira; do
  curl -sf http://localhost:8080/api/response/backends/$backend/test || \
    echo "$backend: FAILED"
done

# Review automation logs
tail -100 /var/log/soar/automation.log | grep -i error

# Check permissions
python src/check_automation_permissions.py
```

**Recovery:**
```bash
# Retry failed actions
curl -X POST http://localhost:8080/api/response/retry-failed \
  -H "Content-Type: application/json" \
  -d '{"since": "1h", "max_attempts": 3}'

# Manual execution of critical actions
# Example: Manual host isolation
ssh firewall.example.com "configure; set address-group isolated_hosts static 192.168.1.100; commit"

# Disable failing backend temporarily
curl -X POST http://localhost:8080/api/response/backends/ad/disable

# Use alternative automation method
./scripts/manual_credential_rotation.sh user@example.com

# Re-enable backend when fixed
curl -X POST http://localhost:8080/api/response/backends/ad/enable
```

### Post-Incident

**After Resolution:**
```bash
# Generate incident report
curl -s http://localhost:8080/api/incidents/INC-12345/report | \
  jq . > incidents/INC-12345-report.json

# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Security Incident Report

**Incident ID:** INC-12345
**Date:** $(date)
**Severity:** P0
**Duration:** 3 hours
**Affected Assets:** critical-db-01

## Timeline
- 14:00: SIEM alert - suspicious activity on critical-db-01
- 14:02: SOAR engine enriched alert, confirmed malicious
- 14:03: Automated isolation triggered
- 14:15: Security team engaged
- 14:30: Forensics collected
- 15:00: Threat eradicated
- 16:30: System restored and monitoring enhanced
- 17:00: Incident closed

## Root Cause
Compromised service account credentials used for lateral movement

## Actions Taken
- Isolated affected host
- Disabled compromised accounts
- Blocked malicious IPs
- Rotated all credentials
- Restored from clean backup

## Action Items
- [ ] Implement service account monitoring
- [ ] Review lateral movement detection rules
- [ ] Update incident response playbooks
- [ ] Conduct security awareness training

EOF

# Update threat intelligence
curl -X POST http://localhost:8080/api/threats/indicators \
  -H "Content-Type: application/json" \
  -d '{
    "indicators": [
      {"type": "ip", "value": "203.0.113.45", "tags": ["c2", "malware", "INC-12345"]},
      {"type": "file_hash", "value": "abc123...", "tags": ["malware", "INC-12345"]}
    ],
    "source": "incident_response",
    "severity": "critical"
  }'

# Update playbooks if gaps identified
# Document lessons learned
echo "Lesson: Need faster credential rotation playbook" >> playbooks/improvements.txt
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Enrichment Timeouts

**Symptoms:**
- Alerts stuck in enrichment phase
- High enrichment failure rate
- Timeout errors in logs

**Diagnosis:**
```bash
# Check adapter response times
curl -s http://localhost:8080/api/adapters/metrics | \
  jq '.adapters[] | {name, avg_response_time_ms, timeout_count}'

# Test each adapter
for adapter in virustotal abuseipdb misp; do
  time curl -s http://localhost:8080/api/adapters/$adapter/test
done

# Check API rate limits
python src/check_api_quotas.py
```

**Solution:**
```bash
# Increase timeout values
vim config/soar_config.yaml
# enrichment:
#   adapters:
#     timeout_seconds: 30  # Increase from 10

# Reduce concurrent enrichment requests
vim config/soar_config.yaml
# enrichment:
#   max_concurrent: 5  # Reduce from 10

# Use cached data more aggressively
vim config/soar_config.yaml
# enrichment:
#   cache:
#     ttl_seconds: 7200  # Increase from 3600

# Skip non-critical enrichment
curl -X POST http://localhost:8080/api/admin/enrichment-priority \
  -d '{"required": ["cmdb"], "optional": ["virustotal", "abuseipdb"]}'

sudo systemctl restart soar-engine
```

---

#### Issue: Playbook Execution Hanging

**Symptoms:**
- Playbook status stuck at specific step
- No progress for extended period
- No error messages

**Diagnosis:**
```bash
# Check playbook execution
EXEC_ID="exec-12345"
curl -s http://localhost:8080/api/playbooks/executions/$EXEC_ID | \
  jq '{status, current_step, started_at, last_update}'

# Check playbook logs
tail -f /var/log/soar/playbooks/$EXEC_ID.log

# Check response backend connectivity
BACKEND=$(jq -r '.current_step.action' <(curl -s http://localhost:8080/api/playbooks/executions/$EXEC_ID))
curl -sf http://localhost:8080/api/response/backends/$BACKEND/test || echo "Backend unreachable"
```

**Solution:**
```bash
# Cancel hung execution
curl -X POST http://localhost:8080/api/playbooks/executions/$EXEC_ID/cancel

# Increase step timeout
vim playbooks/playbook_name.yaml
# steps:
#   - name: slow_step
#     timeout: 600  # Increase timeout

# Add health checks to playbook
vim playbooks/playbook_name.yaml
# steps:
#   - name: action_step
#     health_check:
#       enabled: true
#       interval: 30
#       max_failures: 3

# Implement retry logic
vim playbooks/playbook_name.yaml
# steps:
#   - name: action_step
#     retry:
#       max_attempts: 3
#       backoff_seconds: 10

# Reload playbook
curl -X POST http://localhost:8080/api/playbooks/reload \
  -d '{"playbook": "playbook_name"}'
```

---

#### Issue: False Positive Rate High

**Symptoms:**
- Many alerts marked as false positives
- Unnecessary playbook executions
- Alert fatigue

**Diagnosis:**
```bash
# Analyze false positive rate
curl -s "http://localhost:8080/api/analytics/false-positives?days=30" | \
  jq '{total_alerts, false_positives, rate_percent}'

# Identify patterns
curl -s "http://localhost:8080/api/analytics/false-positives/patterns" | \
  jq '.patterns[] | {alert_type, count, common_attributes}'

# Review detection rules
curl -s http://localhost:8080/api/rules | \
  jq '.rules[] | select(.false_positive_rate > 0.2) | {name, fp_rate}'
```

**Solution:**
```bash
# Tune detection thresholds
curl -X PATCH http://localhost:8080/api/rules/suspicious_login \
  -H "Content-Type: application/json" \
  -d '{
    "threshold": {
      "failed_attempts": 10,  # Increase from 5
      "time_window_minutes": 15
    }
  }'

# Add whitelist exclusions
curl -X POST http://localhost:8080/api/whitelist \
  -H "Content-Type: application/json" \
  -d '{
    "type": "ip_range",
    "value": "10.0.0.0/8",
    "reason": "Internal corporate network",
    "rule": "suspicious_login"
  }'

# Implement ml-based filtering (if available)
vim config/soar_config.yaml
# filtering:
#   ml_enabled: true
#   confidence_threshold: 0.7

# Review and update risk scoring
vim config/risk_scoring.yaml
# Adjust weights to reduce false positives

sudo systemctl restart soar-engine
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 15 minutes (database replication interval)
- **RTO** (Recovery Time Objective): 30 minutes (failover to standby)

### Backup Strategy

**Database Backup:**
```bash
# Backup SOAR database
pg_dump -h localhost -U soar soar_db | \
  gzip > /backups/soar_db_$(date +%Y%m%d-%H%M).sql.gz

# Upload to S3
aws s3 cp /backups/soar_db_$(date +%Y%m%d-%H%M).sql.gz \
  s3://soar-backups/database/

# Automated backup script
cat > /etc/cron.hourly/soar-backup << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d-%H%M)
pg_dump -h localhost -U soar soar_db | gzip > /backups/soar_db_$TIMESTAMP.sql.gz
aws s3 cp /backups/soar_db_$TIMESTAMP.sql.gz s3://soar-backups/database/
find /backups -name "soar_db_*.sql.gz" -mtime +7 -delete
EOF
chmod +x /etc/cron.hourly/soar-backup
```

**Configuration Backup:**
```bash
# Backup all configurations
tar czf soar-config-backup-$(date +%Y%m%d).tar.gz \
  config/ \
  playbooks/ \
  src/

aws s3 cp soar-config-backup-$(date +%Y%m%d).tar.gz \
  s3://soar-backups/config/

# Git commit
git add config/ playbooks/
git commit -m "backup: SOAR configurations $(date +%Y-%m-%d)"
git push
```

**Threat Intelligence Backup:**
```bash
# Backup Redis threat intel cache
redis-cli --rdb /backups/threat_intel_$(date +%Y%m%d).rdb
aws s3 cp /backups/threat_intel_$(date +%Y%m%d).rdb s3://soar-backups/redis/
```

### Disaster Recovery Procedures

#### Complete System Loss

**Recovery Steps (30-60 minutes):**
```bash
# 1. Provision new infrastructure
terraform apply -auto-approve

# 2. Restore configurations
aws s3 cp s3://soar-backups/config/latest.tar.gz .
tar xzf latest.tar.gz

# 3. Restore database
aws s3 cp s3://soar-backups/database/latest.sql.gz .
gunzip < latest.sql.gz | psql -h localhost -U soar soar_db

# 4. Restore Redis cache
aws s3 cp s3://soar-backups/redis/latest.rdb /var/lib/redis/dump.rdb
systemctl restart redis

# 5. Start SOAR engine
systemctl start soar-engine

# 6. Verify system
./scripts/test_soar_health.sh

# 7. Resume alert processing
curl -X POST http://localhost:8080/api/admin/resume-processing
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Morning health check
./scripts/daily_health_check.sh

# Review overnight alerts
curl -s "http://localhost:8080/api/alerts?since=24h&severity=high,critical" | \
  jq '.alerts | length'

# Check playbook execution success rate
curl -s http://localhost:8080/api/metrics/playbooks/success-rate

# Review false positives
curl -s "http://localhost:8080/api/alerts?status=closed&reason=false_positive&since=24h" | \
  jq '.alerts | length'
```

### Weekly Tasks
```bash
# Review and tune detection rules
python src/analyze_detection_rules.py --output reports/rules_analysis.html

# Update threat intelligence
python src/update_threat_feeds.py

# Review high-risk assets
curl -s http://localhost:8080/api/risk/weekly-report | \
  jq . > reports/risk_report_$(date +%Y%m%d).json

# Audit response actions
curl -s "http://localhost:8080/api/response/history?since=7d" | \
  jq '.actions[] | {timestamp, action, asset, status}'

# Database maintenance
psql -h localhost -U soar soar_db -c "VACUUM ANALYZE;"
```

### Monthly Tasks
```bash
# Security review
./scripts/security_audit.sh

# Update playbooks
git pull origin main
curl -X POST http://localhost:8080/api/playbooks/reload-all

# Review API quotas and costs
python src/monthly_cost_analysis.py

# Update enrichment adapters
pip install --upgrade virustotal-api abuseipdb-wrapper

# Conduct tabletop exercise
./scripts/incident_simulation.sh --scenario ransomware
```

---

## Quick Reference

### Most Common Operations
```bash
# Check SOAR status
curl http://localhost:8080/health

# View active alerts
curl -s 'http://localhost:8080/api/alerts?status=active' | jq .

# Execute playbook
curl -X POST http://localhost:8080/api/playbooks/isolate_host/execute \
  -d '{"parameters":{"hostname":"web-01"}}'

# Check enrichment status
curl -s http://localhost:8080/api/adapters/health | jq .

# View high-risk assets
curl -s http://localhost:8080/api/risk/top-assets?limit=10 | jq .

# Manual alert submission
curl -X POST http://localhost:8080/api/alerts -d @alert.json
```

### Emergency Response
```bash
# P0: SOAR engine down
sudo systemctl restart soar-engine
curl http://localhost:8080/health

# P0: Isolate compromised host
curl -X POST http://localhost:8080/api/playbooks/isolate_host/execute \
  -d '{"parameters":{"hostname":"HOST","emergency":true}}'

# P1: Disable enrichment temporarily
curl -X POST http://localhost:8080/api/admin/bypass-enrichment \
  -d '{"duration_minutes":60}'

# P1: Scale workers
curl -X POST http://localhost:8080/api/admin/scale-workers -d '{"workers":8}'
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Operations Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

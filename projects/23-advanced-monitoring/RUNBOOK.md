# Runbook — Project 23 (Advanced Monitoring & Observability)

## Overview

Production operations runbook for the Advanced Monitoring & Observability stack. This runbook covers unified observability with Prometheus metrics, Tempo distributed tracing, Loki log aggregation, Grafana dashboards, SLO tracking, burn rate calculations, and release markers for portfolio workloads.

**System Components:**
- Prometheus (metrics collection and alerting)
- Tempo (distributed tracing backend)
- Loki (log aggregation)
- Grafana (unified visualization platform)
- Portfolio dashboard with SLO tracking
- Alert rules with burn rate calculations
- Kustomize overlays for staging/production
- Release marker annotations

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Observability stack uptime** | 99.95% | All components available |
| **Metrics ingestion lag** | < 30 seconds | Prometheus scrape delay |
| **Log ingestion lag** | < 10 seconds | Loki ingestion timestamp delta |
| **Trace ingestion lag** | < 5 seconds | Tempo trace arrival time |
| **Dashboard load time (p95)** | < 3 seconds | Portfolio dashboard render |
| **Query performance (p95)** | < 2 seconds | PromQL/LogQL query duration |
| **Alert delivery time** | < 60 seconds | Alert generation → notification |
| **Data retention compliance** | 100% | Metrics: 30d, Logs: 30d, Traces: 7d |

---

## Dashboards & Alerts

### Dashboards

#### Observability Stack Health
```bash
# Check all components
kubectl get pods -n monitoring

# Check Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl http://localhost:9090/-/healthy

# Check Loki
kubectl port-forward -n monitoring svc/loki 3100:3100 &
curl http://localhost:3100/ready

# Check Tempo
kubectl port-forward -n monitoring svc/tempo 3200:3200 &
curl http://localhost:3200/ready

# Check Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
curl http://localhost:3000/api/health
```

#### Portfolio Dashboard Access
```bash
# Access Grafana dashboard
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Navigate to: http://localhost:3000
# Dashboard: "Portfolio Overview" (from dashboards/portfolio.json)

# Export dashboard via API
DASHBOARD_UID="portfolio-overview"
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/$DASHBOARD_UID | \
  jq '.dashboard' > portfolio-dashboard-backup.json
```

#### SLO Tracking Dashboard
```bash
# View current SLO compliance
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# Query SLO metrics
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_compliance_ratio{service="portfolio"}' | jq .

# Check error budget
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=error_budget_remaining{service="portfolio"}' | jq .

# View burn rate
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_burn_rate_1h{service="portfolio"}' | jq .
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All observability components down | Immediate | Emergency recovery, restore from backup |
| **P0** | SLO burn rate critical (>14.4x) | Immediate | Incident response, investigate service |
| **P1** | Prometheus/Loki/Tempo down | 15 minutes | Restart component, check resources |
| **P1** | SLO burn rate high (>6x) | 30 minutes | Investigate error spike, check deployments |
| **P1** | Alert delivery failing | 30 minutes | Check Alertmanager, notification channels |
| **P2** | Metrics/logs ingestion lag | 1 hour | Check scrape targets, disk space |
| **P2** | Dashboard load time high | 1 hour | Optimize queries, check Grafana resources |
| **P3** | Individual scrape target down | 4 hours | Investigate target, check connectivity |

#### Alert Queries

```bash
# Check Prometheus alert rules
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl -s http://localhost:9090/api/v1/rules | \
  jq '.data.groups[] | select(.name=="portfolio_rules")'

# Check active alerts
curl -s http://localhost:9090/api/v1/alerts | \
  jq '.data.alerts[] | {alertname: .labels.alertname, state: .state, severity: .labels.severity}'

# Check SLO burn rate alerts
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=ALERTS{alertname=~".*BurnRate.*"}' | jq .

# Check for critical SLO violations
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_compliance_ratio < 0.99' | jq .
```

---

## Standard Operations

### Stack Deployment

#### Deploy to Staging
```bash
# Apply Kustomize overlay for staging
kubectl apply -k manifests/overlays/staging

# Verify deployment
kubectl get pods -n monitoring-staging

# Check services
kubectl get svc -n monitoring-staging

# Port forward to access
kubectl port-forward -n monitoring-staging svc/grafana 3000:3000
```

#### Deploy to Production
```bash
# Review production overlay
cat manifests/overlays/production/kustomization.yaml

# Apply production configuration
kubectl apply -k manifests/overlays/production

# Verify deployment
kubectl get pods -n monitoring
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s

# Check all components
kubectl get pods,svc,pvc -n monitoring

# Verify Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[0:5]'
```

#### Update Stack Components
```bash
# Update Prometheus
kubectl set image deployment/prometheus prometheus=prom/prometheus:v2.48.0 -n monitoring
kubectl rollout status deployment/prometheus -n monitoring

# Update Grafana
kubectl set image deployment/grafana grafana=grafana/grafana:10.2.0 -n monitoring
kubectl rollout status deployment/grafana -n monitoring

# Update Loki
kubectl set image deployment/loki loki=grafana/loki:2.9.0 -n monitoring
kubectl rollout status deployment/loki -n monitoring

# Update Tempo
kubectl set image deployment/tempo tempo=grafana/tempo:2.3.0 -n monitoring
kubectl rollout status deployment/tempo -n monitoring
```

### Prometheus Operations

#### Manage Prometheus Configuration
```bash
# View current Prometheus config
kubectl get configmap -n monitoring prometheus-config -o yaml

# Edit Prometheus configuration
kubectl edit configmap -n monitoring prometheus-config

# Or update from file
kubectl create configmap prometheus-config \
  --from-file=prometheus.yml=prometheus/prometheus.yml \
  --dry-run=client -o yaml | kubectl apply -n monitoring -f -

# Reload Prometheus configuration
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/-/reload

# Verify new configuration loaded
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl -s http://localhost:9090/api/v1/status/config | jq '.data.yaml' | head -30
```

#### Manage Alert Rules
```bash
# View current alert rules
kubectl get configmap -n monitoring prometheus-alerts -o yaml

# Update alert rules from file
kubectl create configmap prometheus-alerts \
  --from-file=alerts.yml=alerts/portfolio_rules.yml \
  --dry-run=client -o yaml | kubectl apply -n monitoring -f -

# Validate alert rules locally
promtool check rules alerts/portfolio_rules.yml

# Reload Prometheus to apply new rules
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/-/reload

# Verify rules loaded
curl -s http://localhost:9090/api/v1/rules | \
  jq '.data.groups[] | {name, file, rules: (.rules | length)}'

# Check for rule evaluation errors
curl -s http://localhost:9090/api/v1/rules | \
  jq '.data.groups[].rules[] | select(.health=="err")'
```

#### Query Metrics
```bash
# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &

# Query current metric values
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up{job="portfolio-services"}' | jq .

# Query with time range
curl -G http://localhost:9090/api/v1/query_range \
  --data-urlencode 'query=rate(http_requests_total[5m])' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)" \
  --data-urlencode "end=$(date +%s)" \
  --data-urlencode 'step=60' | jq .

# Query SLO metrics
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_compliance_ratio{service=~".*"}' | \
  jq -r '.data.result[] | "\(.metric.service): \(.value[1])"'

# Check burn rates
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_burn_rate_1h{service="portfolio"}' | jq .
```

### Loki Operations

#### Configure Loki
```bash
# View Loki configuration
kubectl get configmap -n monitoring loki-config -o yaml

# Update Loki configuration
kubectl edit configmap -n monitoring loki-config

# Restart Loki to apply changes
kubectl rollout restart deployment/loki -n monitoring
kubectl rollout status deployment/loki -n monitoring
```

#### Query Logs
```bash
# Port forward to Loki
kubectl port-forward -n monitoring svc/loki 3100:3100 &

# Query recent logs
curl -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={namespace="default"}' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | jq .

# Query with filters
curl -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode 'query={namespace="default"} |= "error" | json' \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | \
  jq -r '.data.result[].values[][1]'

# Query log volume
curl -G http://localhost:3100/loki/api/v1/query \
  --data-urlencode 'query=sum(rate({namespace="default"}[5m])) by (pod)' | jq .

# List available labels
curl -s http://localhost:3100/loki/api/v1/labels | jq .
```

### Tempo Operations

#### Configure Tempo
```bash
# View Tempo configuration
kubectl get configmap -n monitoring tempo-config -o yaml

# Update configuration
kubectl edit configmap -n monitoring tempo-config

# Restart Tempo
kubectl rollout restart deployment/tempo -n monitoring
```

#### Query Traces
```bash
# Port forward to Tempo
kubectl port-forward -n monitoring svc/tempo 3200:3200 &

# Search for traces
curl -s "http://localhost:3200/api/search?tags=service.name%3Dportfolio-api" | jq .

# Get specific trace
TRACE_ID="abc123def456"
curl -s "http://localhost:3200/api/traces/$TRACE_ID" | jq .

# Query traces via Grafana
# Navigate to Explore → Tempo data source → Search
```

### Grafana Operations

#### Manage Dashboards
```bash
# Port forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# Import portfolio dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/portfolio.json

# Export dashboard
DASHBOARD_UID="portfolio-overview"
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/$DASHBOARD_UID | \
  jq '.dashboard' > portfolio-dashboard-export.json

# List all dashboards
curl -s http://admin:admin@localhost:3000/api/search?type=dash-db | \
  jq '.[] | {title, uid, url}'

# Update dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @dashboards/portfolio-updated.json
```

#### Configure Data Sources
```bash
# List data sources
curl -s http://admin:admin@localhost:3000/api/datasources | jq .

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

# Add Tempo data source
cat > datasource-tempo.json << 'EOF'
{
  "name": "Tempo",
  "type": "tempo",
  "url": "http://tempo:3200",
  "access": "proxy"
}
EOF

curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d @datasource-tempo.json
```

#### Manage Grafana Users
```bash
# Create user
curl -X POST http://admin:admin@localhost:3000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","login":"john","password":"changeme"}'

# List users
curl -s http://admin:admin@localhost:3000/api/users | jq .

# Update user role
USER_ID=2
curl -X PATCH http://admin:admin@localhost:3000/api/org/users/$USER_ID \
  -H "Content-Type: application/json" \
  -d '{"role":"Editor"}'

# Reset admin password
kubectl exec -n monitoring deployment/grafana -- \
  grafana-cli admin reset-admin-password newpassword
```

### Release Marker Operations

#### Add Release Marker
```bash
# Add release annotation to Grafana
RELEASE_VERSION="v1.2.3"
RELEASE_TIME=$(date +%s)000

curl -X POST http://admin:admin@localhost:3000/api/annotations \
  -H "Content-Type: application/json" \
  -d "{
    \"dashboardUID\": \"portfolio-overview\",
    \"time\": $RELEASE_TIME,
    \"tags\": [\"release\", \"deployment\"],
    \"text\": \"Release $RELEASE_VERSION deployed\"
  }"

# Or add via script
./scripts/add-release-marker.sh --version=v1.2.3 --environment=production

# Verify marker added
curl -s http://admin:admin@localhost:3000/api/annotations | \
  jq '.[] | select(.tags | contains(["release"]))'
```

#### Query Release Impact
```bash
# Query error rate around release time
RELEASE_TIME="2025-11-10T14:00:00Z"
START_TIME=$(date -d "$RELEASE_TIME - 1 hour" +%s)
END_TIME=$(date -d "$RELEASE_TIME + 1 hour" +%s)

curl -G http://localhost:9090/api/v1/query_range \
  --data-urlencode 'query=rate(http_requests_total{status=~"5.."}[5m])' \
  --data-urlencode "start=$START_TIME" \
  --data-urlencode "end=$END_TIME" \
  --data-urlencode 'step=60' | jq .

# Compare SLO before/after release
./scripts/compare-slo-impact.sh --release-time="$RELEASE_TIME"
```

### SLO Management

#### Calculate SLO Compliance
```bash
# Query current SLO compliance
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_compliance_ratio{service="portfolio"}' | \
  jq -r '.data.result[] | "\(.metric.service): \(.value[1] * 100)%"'

# Calculate error budget remaining
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=error_budget_remaining{service="portfolio"}' | \
  jq -r '.data.result[] | "\(.metric.service): \(.value[1])"'

# Check burn rate
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_burn_rate_1h{service="portfolio"}' | jq .

# Generate SLO report
./scripts/generate-slo-report.sh --service=portfolio --period=30d
```

#### Update SLO Targets
```bash
# Edit SLO alert rules
vim alerts/portfolio_rules.yml

# Update SLO target (example: 99.9% → 99.95%)
# slo_target: 0.9995

# Validate rules
promtool check rules alerts/portfolio_rules.yml

# Apply updated rules
kubectl create configmap prometheus-alerts \
  --from-file=alerts.yml=alerts/portfolio_rules.yml \
  --dry-run=client -o yaml | kubectl apply -n monitoring -f -

# Reload Prometheus
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/-/reload
```

---

## Incident Response

### Detection

**Automated Detection:**
- Prometheus/Loki/Tempo health check failures
- SLO burn rate alerts
- Alert delivery failures
- High query latency alerts
- Data ingestion lag alerts

**Manual Detection:**
```bash
# Check all components
kubectl get pods -n monitoring

# Check for failing pods
kubectl get pods -n monitoring | grep -v Running

# Check recent events
kubectl get events -n monitoring --sort-by='.lastTimestamp' | tail -20

# Check Prometheus health
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl http://localhost:9090/-/healthy

# Check active alerts
curl -s http://localhost:9090/api/v1/alerts | \
  jq '.data.alerts[] | select(.state=="firing")'
```

### Triage

#### Severity Classification

### P0: Complete Observability Loss
- All monitoring components down
- Cannot determine system health
- SLO tracking unavailable
- Critical alerts not firing

### P1: Partial Observability Loss
- Single component down (Prometheus/Loki/Tempo)
- SLO burn rate critical (>14.4x)
- Alert delivery completely failing
- Dashboard unavailable

### P2: Degraded Observability
- High query latency
- Ingestion lag significant
- SLO burn rate elevated (>6x)
- Some scrape targets down

### P3: Minor Issues
- Individual scrape target down
- Dashboard performance degraded
- Non-critical component warnings

### Incident Response Procedures

#### P0: All Monitoring Components Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check namespace status
kubectl get pods -n monitoring

# 2. Check node resources
kubectl top nodes
kubectl describe nodes | grep -A 5 "Allocated resources"

# 3. Check events for errors
kubectl get events -n monitoring --sort-by='.lastTimestamp' | tail -30

# 4. Attempt pod restart
kubectl rollout restart deployment/prometheus -n monitoring
kubectl rollout restart deployment/loki -n monitoring
kubectl rollout restart deployment/tempo -n monitoring
kubectl rollout restart deployment/grafana -n monitoring
```

**Investigation (5-20 minutes):**
```bash
# Check pod logs
kubectl logs -n monitoring deployment/prometheus --tail=100
kubectl logs -n monitoring deployment/loki --tail=100
kubectl logs -n monitoring deployment/tempo --tail=100

# Check PVC status
kubectl get pvc -n monitoring

# Check disk space
kubectl exec -n monitoring deployment/prometheus -- df -h

# Check configuration
kubectl get configmap -n monitoring
```

**Recovery:**
```bash
# If disk full, clean old data
kubectl exec -n monitoring deployment/prometheus -- \
  rm -rf /prometheus/wal/*

# If configuration error, restore from backup
kubectl apply -f backup/monitoring-configmaps.yaml

# Redeploy stack if necessary
kubectl delete namespace monitoring
kubectl create namespace monitoring
kubectl apply -k manifests/overlays/production

# Wait for recovery
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s

# Verify all components
kubectl get pods -n monitoring
curl http://localhost:9090/-/healthy
curl http://localhost:3100/ready
curl http://localhost:3200/ready
```

#### P0: Critical SLO Burn Rate

**Immediate Actions (0-5 minutes):**
```bash
# 1. Identify affected service
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=ALERTS{alertname="SLOBurnRateCritical"}' | \
  jq -r '.data.result[] | .labels.service'

# 2. Check current error rate
SERVICE="portfolio"
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode "query=rate(http_requests_total{status=~\"5..\",service=\"$SERVICE\"}[5m])" | jq .

# 3. Check recent deployments
curl -s http://admin:admin@localhost:3000/api/annotations | \
  jq '.[] | select(.tags | contains(["release"])) | select(.time > (now - 3600) * 1000)'

# 4. Trigger incident response
# Follow service-specific incident response procedures
```

**Investigation:**
```bash
# Check error patterns
curl -G http://localhost:9090/api/v1/query_range \
  --data-urlencode "query=rate(http_requests_total{status=~\"5..\",service=\"$SERVICE\"}[5m])" \
  --data-urlencode "start=$(date -d '2 hours ago' +%s)" \
  --data-urlencode "end=$(date +%s)" \
  --data-urlencode 'step=60' | jq .

# Check logs for errors
curl -G http://localhost:3100/loki/api/v1/query_range \
  --data-urlencode "query={service=\"$SERVICE\"} |= \"error\" | json" \
  --data-urlencode "start=$(date -d '1 hour ago' +%s)000000000" \
  --data-urlencode "end=$(date +%s)000000000" | \
  jq -r '.data.result[].values[][1]' | head -50

# Correlate with traces
# Use Grafana Explore to find slow traces
```

#### P1: Prometheus Down

**Investigation:**
```bash
# Check Prometheus pod
kubectl get pods -n monitoring -l app=prometheus

# Check logs
kubectl logs -n monitoring deployment/prometheus --tail=100

# Check events
kubectl describe pod -n monitoring -l app=prometheus

# Check PVC
kubectl get pvc -n monitoring prometheus-storage
```

**Recovery:**
```bash
# Restart Prometheus
kubectl rollout restart deployment/prometheus -n monitoring

# If PVC issue, check storage
kubectl describe pvc -n monitoring prometheus-storage

# If configuration issue, validate and fix
kubectl get configmap -n monitoring prometheus-config -o yaml
promtool check config /tmp/prometheus.yml

# If data corruption, restore from snapshot
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/api/v1/admin/tsdb/delete_series \
    --data 'match[]={__name__=~".+"}'

# Verify recovery
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
curl http://localhost:9090/-/healthy
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[0:3]'
```

#### P1: Loki Down

**Investigation & Recovery:**
```bash
# Check Loki status
kubectl get pods -n monitoring -l app=loki
kubectl logs -n monitoring deployment/loki --tail=100

# Check disk space
kubectl exec -n monitoring deployment/loki -- df -h

# Restart Loki
kubectl rollout restart deployment/loki -n monitoring

# Verify recovery
kubectl port-forward -n monitoring svc/loki 3100:3100 &
curl http://localhost:3100/ready

# Test log query
curl -G http://localhost:3100/loki/api/v1/query \
  --data-urlencode 'query={namespace="default"}' | jq .
```

#### P2: High Query Latency

**Investigation:**
```bash
# Check Prometheus query performance
curl -s http://localhost:9090/api/v1/query \
  --data-urlencode 'query=prometheus_engine_query_duration_seconds{quantile="0.95"}' | jq .

# Check resource usage
kubectl top pods -n monitoring

# Identify slow queries
kubectl logs -n monitoring deployment/prometheus | grep "query took"

# Check TSDB stats
curl -s http://localhost:9090/api/v1/status/tsdb | jq .
```

**Optimization:**
```bash
# Increase Prometheus resources
kubectl patch deployment prometheus -n monitoring -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "prometheus",
          "resources": {
            "requests": {"memory": "4Gi", "cpu": "2"},
            "limits": {"memory": "8Gi", "cpu": "4"}
          }
        }]
      }
    }
  }
}'

# Add recording rules for frequently queried metrics
# Update alerts/portfolio_rules.yml with recording rules

# Reload configuration
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/-/reload
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/monitoring-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Monitoring Stack Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 30 minutes
**Component:** Prometheus

## Timeline
- 14:00: Prometheus pod CrashLoopBackOff
- 14:05: Investigation started
- 14:10: Identified disk space issue
- 14:15: Cleaned WAL files
- 14:20: Restarted Prometheus
- 14:30: Full recovery confirmed

## Root Cause
Prometheus disk filled with write-ahead logs

## Mitigation
- Cleaned old WAL files
- Restarted Prometheus pod
- Verified all scrape targets operational

## Action Items
- [ ] Add disk usage monitoring
- [ ] Increase PVC size
- [ ] Implement automatic WAL cleanup
- [ ] Review retention settings
- [ ] Add resource quotas

EOF

# Update monitoring
# Add new alert rules based on learnings
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Dashboard shows "No data"

**Diagnosis:**
```bash
# Check data source health
curl -s http://admin:admin@localhost:3000/api/datasources | \
  jq '.[] | {name, type, url}'

# Test Prometheus connectivity
kubectl exec -n monitoring deployment/grafana -- \
  curl http://prometheus:9090/api/v1/query?query=up

# Check if metrics exist
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=up' | jq '.data.result | length'
```

**Solution:**
```bash
# Fix data source configuration in Grafana
# Navigate to: Configuration → Data Sources → Prometheus
# Update URL to: http://prometheus:9090

# Or via API
curl -X PUT http://admin:admin@localhost:3000/api/datasources/1 \
  -H "Content-Type: application/json" \
  -d '{"url":"http://prometheus:9090","access":"proxy"}'

# Verify
curl http://admin:admin@localhost:3000/api/datasources/proxy/1/api/v1/query?query=up
```

---

#### Issue: Metrics not being scraped

**Diagnosis:**
```bash
# Check Prometheus targets
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.health=="down")'

# Check scrape configuration
kubectl get configmap -n monitoring prometheus-config -o yaml

# Test target connectivity
TARGET_URL="http://portfolio-service:8080/metrics"
kubectl exec -n monitoring deployment/prometheus -- wget -O- $TARGET_URL
```

**Solution:**
```bash
# Update Prometheus configuration
kubectl edit configmap -n monitoring prometheus-config

# Add missing scrape target
# - job_name: 'portfolio-service'
#   static_configs:
#     - targets: ['portfolio-service:8080']

# Reload Prometheus
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/-/reload

# Verify scraping works
curl -s http://localhost:9090/api/v1/targets | \
  jq '.data.activeTargets[] | select(.labels.job=="portfolio-service")'
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (snapshot frequency)
- **RTO** (Recovery Time Objective): 20 minutes (stack restoration)

### Backup Strategy

**Configuration Backup:**
```bash
# Backup all manifests and configurations
tar czf monitoring-config-$(date +%Y%m%d).tar.gz \
  manifests/ dashboards/ alerts/

# Backup Kubernetes resources
kubectl get all,configmap,secret,pvc -n monitoring -o yaml > \
  backup/monitoring-resources-$(date +%Y%m%d).yaml

# Store in Git
git add manifests/ dashboards/ alerts/
git commit -m "backup: monitoring configuration $(date +%Y-%m-%d)"
git push
```

**Data Backup:**
```bash
# Prometheus snapshot
kubectl exec -n monitoring deployment/prometheus -- \
  curl -X POST http://localhost:9090/api/v1/admin/tsdb/snapshot

# Copy snapshot to backup location
POD=$(kubectl get pod -n monitoring -l app=prometheus -o jsonpath='{.items[0].metadata.name}')
SNAPSHOT=$(kubectl exec -n monitoring $POD -- ls /prometheus/snapshots | tail -1)
kubectl cp monitoring/$POD:/prometheus/snapshots/$SNAPSHOT ./backup/prometheus-$(date +%Y%m%d)

# Grafana backup
kubectl exec -n monitoring deployment/grafana -- \
  tar czf /tmp/grafana-backup.tar.gz /var/lib/grafana
kubectl cp monitoring/$(kubectl get pod -n monitoring -l app=grafana -o jsonpath='{.items[0].metadata.name}'):/tmp/grafana-backup.tar.gz \
  ./backup/grafana-$(date +%Y%m%d).tar.gz
```

### Disaster Recovery Procedures

**Complete Stack Loss:**
```bash
# 1. Restore manifests from Git
git clone https://github.com/org/portfolio-monitoring.git
cd portfolio-monitoring

# 2. Create namespace
kubectl create namespace monitoring

# 3. Deploy stack
kubectl apply -k manifests/overlays/production

# 4. Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n monitoring --timeout=600s

# 5. Restore Prometheus data (if available)
BACKUP_DIR="backup/prometheus-20251110"
POD=$(kubectl get pod -n monitoring -l app=prometheus -o jsonpath='{.items[0].metadata.name}')
kubectl cp $BACKUP_DIR monitoring/$POD:/prometheus/

# 6. Restart Prometheus
kubectl rollout restart deployment/prometheus -n monitoring

# 7. Restore Grafana dashboards
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
for dashboard in dashboards/*.json; do
  curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -d @$dashboard
done

# 8. Verify recovery
kubectl get pods -n monitoring
curl http://localhost:9090/-/healthy
curl http://localhost:3000/api/health
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check stack health
kubectl get pods -n monitoring

# Check for alerts
curl -s http://localhost:9090/api/v1/alerts | \
  jq '.data.alerts[] | select(.state=="firing")'

# Check SLO compliance
curl -G http://localhost:9090/api/v1/query \
  --data-urlencode 'query=slo_compliance_ratio' | \
  jq -r '.data.result[] | "\(.metric.service): \(.value[1] * 100)%"'

# Check disk usage
kubectl exec -n monitoring deployment/prometheus -- df -h
```

### Weekly Tasks
```bash
# Review dashboard performance
# Check slow queries in Grafana

# Validate alert rules
promtool check rules alerts/portfolio_rules.yml

# Review SLO burn rate trends
./scripts/slo-weekly-report.sh

# Check for outdated images
kubectl get pods -n monitoring -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
```

### Monthly Tasks
```bash
# Update components
kubectl set image deployment/prometheus prometheus=prom/prometheus:latest -n monitoring
kubectl set image deployment/grafana grafana=grafana/grafana:latest -n monitoring
kubectl set image deployment/loki loki=grafana/loki:latest -n monitoring
kubectl set image deployment/tempo tempo=grafana/tempo:latest -n monitoring

# Review and optimize retention
# Update retention periods in configurations

# Conduct DR drill
./scripts/dr-drill.sh

# Review and update dashboards
# Archive unused dashboards
```

---

## Quick Reference

### Most Common Operations
```bash
# Check stack status
kubectl get pods -n monitoring

# Port forward to Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Check active alerts
curl -s http://localhost:9090/api/v1/alerts | jq '.data.alerts'

# Reload Prometheus config
kubectl exec -n monitoring deployment/prometheus -- curl -X POST http://localhost:9090/-/reload

# View pod logs
kubectl logs -n monitoring deployment/prometheus -f

# Restart component
kubectl rollout restart deployment/prometheus -n monitoring
```

### Emergency Response
```bash
# P0: All components down
kubectl get pods -n monitoring
kubectl rollout restart deployment --all -n monitoring

# P1: Prometheus down
kubectl rollout restart deployment/prometheus -n monitoring
kubectl logs -n monitoring deployment/prometheus --tail=100

# P1: Critical burn rate
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=ALERTS{alertname="SLOBurnRateCritical"}'
# Follow service incident response

# P2: Disk full
kubectl exec -n monitoring deployment/prometheus -- df -h
kubectl exec -n monitoring deployment/prometheus -- rm -rf /prometheus/wal/*
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

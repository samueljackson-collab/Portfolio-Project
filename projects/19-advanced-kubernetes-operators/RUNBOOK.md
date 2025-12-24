# Runbook — Project 19 (Advanced Kubernetes Operators)

## Overview

Production operations runbook for the Advanced Kubernetes Operators built with Kopf (Kubernetes Operator Pythonic Framework), managing custom resources for portfolio deployments and orchestrating database migrations.

**System Components:**
- Kopf operator framework (Python-based)
- Custom Resource Definitions (CRDs)
- Operator controller with reconciliation loops
- Database migration orchestrator
- Portfolio deployment manager
- Event-driven automation handlers
- Webhook validation and mutation
- Operator metrics and health endpoints

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Operator availability** | 99.9% | Operator pod uptime |
| **Reconciliation latency** | < 30 seconds (p95) | Time from CR change → reconciliation complete |
| **CRD operation success rate** | 99.5% | Successful create/update/delete operations |
| **Migration success rate** | 99% | Successful database migrations |
| **Webhook response time** | < 100ms (p95) | Validation/mutation webhook latency |
| **Event processing backlog** | < 50 events | Unprocessed Kubernetes events in queue |
| **Resource drift detection** | < 5 minutes | Time to detect and remediate drift |

---

## Dashboards & Alerts

### Dashboards

#### Operator Health Dashboard
```bash
# Check operator pod status
kubectl get pods -n operator-system -l app=portfolio-operator

# Check operator logs
kubectl logs -n operator-system -l app=portfolio-operator --tail=100

# Check operator metrics
kubectl port-forward -n operator-system svc/portfolio-operator-metrics 8080:8080 &
curl -s http://localhost:8080/metrics | grep -E "(kopf|operator)"

# Check operator resource usage
kubectl top pods -n operator-system -l app=portfolio-operator
```

#### Custom Resource Dashboard
```bash
# List all custom resources
kubectl get portfoliodeployments --all-namespaces
kubectl get databasemigrations --all-namespaces

# Check CR status
kubectl get portfoliodeployments -o json | \
  jq '.items[] | {name: .metadata.name, status: .status.phase, conditions: .status.conditions}'

# Check CR events
kubectl get events --all-namespaces --field-selector involvedObject.kind=PortfolioDeployment --sort-by='.lastTimestamp'
```

#### Reconciliation Performance Dashboard
```bash
# Check reconciliation metrics
kubectl port-forward -n operator-system svc/portfolio-operator-metrics 8080:8080 &
curl -s http://localhost:8080/metrics | grep kopf_reconciliation

# Check handler execution times
curl -s http://localhost:8080/metrics | grep kopf_handler_duration_seconds

# Check event queue depth
curl -s http://localhost:8080/metrics | grep kopf_events_pending
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Operator pod down | Immediate | Restart operator, check dependencies |
| **P0** | Reconciliation loop stuck | Immediate | Review stuck resources, restart operator |
| **P1** | CRD operation failure rate > 5% | 15 minutes | Check validation, review errors |
| **P1** | Migration failure | 15 minutes | Review migration logs, rollback if needed |
| **P2** | High reconciliation latency | 30 minutes | Review operator performance, scale if needed |
| **P2** | Webhook timeout | 30 minutes | Check webhook service, adjust timeout |
| **P3** | Resource drift detected | 1 hour | Investigate and remediate drift |

#### Alert Queries (Prometheus)

```promql
# Operator down
up{job="portfolio-operator"} == 0

# High reconciliation latency
histogram_quantile(0.95,
  rate(kopf_reconciliation_duration_seconds_bucket[5m])
) > 30

# High failure rate
(
  rate(kopf_reconciliation_errors_total[5m])
  /
  rate(kopf_reconciliation_total[5m])
) > 0.05

# Stuck reconciliation loop
kopf_reconciliation_duration_seconds{quantile="0.99"} > 300

# Webhook errors
rate(kopf_webhook_errors_total[5m]) > 0.01

# Event queue backlog
kopf_events_pending > 50
```

---

## Standard Operations

### Operator Management

#### Deploy Operator
```bash
# Install CRDs
kubectl apply -f manifests/crds/

# Create operator namespace
kubectl create namespace operator-system

# Deploy operator
kubectl apply -f manifests/operator.yaml

# Verify operator is running
kubectl wait --for=condition=Ready pods -l app=portfolio-operator -n operator-system --timeout=120s

# Check operator logs
kubectl logs -n operator-system -l app=portfolio-operator -f

# Verify CRDs are registered
kubectl get crds | grep portfolio
```

#### Update Operator
```bash
# Update operator image
kubectl set image deployment/portfolio-operator \
  portfolio-operator=portfolio-operator:v2.0.0 \
  -n operator-system

# Monitor rollout
kubectl rollout status deployment/portfolio-operator -n operator-system

# Verify new version
kubectl get deployment portfolio-operator -n operator-system \
  -o jsonpath='{.spec.template.spec.containers[0].image}'

# Check for errors after update
kubectl logs -n operator-system -l app=portfolio-operator --tail=100
```

#### Restart Operator
```bash
# Restart operator pods
kubectl rollout restart deployment/portfolio-operator -n operator-system

# Wait for restart to complete
kubectl rollout status deployment/portfolio-operator -n operator-system

# Verify operator health
kubectl get pods -n operator-system -l app=portfolio-operator
kubectl logs -n operator-system -l app=portfolio-operator --tail=50
```

### Custom Resource Operations

#### Create Portfolio Deployment
```yaml
# portfolio-deployment.yaml
apiVersion: portfolio.example.com/v1alpha1
kind: PortfolioDeployment
metadata:
  name: my-portfolio
  namespace: production
spec:
  version: "1.0.0"
  replicas: 3
  database:
    host: postgres.database.svc.cluster.local
    port: 5432
    name: portfolio_db
    migrationVersion: "v1.2.0"
  resources:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  features:
    - analytics
    - reporting
  config:
    logLevel: "info"
    cacheEnabled: true
```

```bash
# Apply portfolio deployment
kubectl apply -f portfolio-deployment.yaml

# Watch reconciliation
kubectl get portfoliodeployment my-portfolio -n production --watch

# Check deployment status
kubectl get portfoliodeployment my-portfolio -n production -o jsonpath='{.status}'

# View events
kubectl describe portfoliodeployment my-portfolio -n production
```

#### Update Portfolio Deployment
```bash
# Update version
kubectl patch portfoliodeployment my-portfolio -n production \
  --type merge -p '{"spec":{"version":"1.1.0"}}'

# Update replicas
kubectl patch portfoliodeployment my-portfolio -n production \
  --type merge -p '{"spec":{"replicas":5}}'

# Monitor reconciliation
kubectl logs -n operator-system -l app=portfolio-operator -f | grep my-portfolio
```

#### Delete Portfolio Deployment
```bash
# Delete CR (operator will clean up resources)
kubectl delete portfoliodeployment my-portfolio -n production

# Verify cleanup
kubectl get all -n production -l portfolio=my-portfolio

# Check finalizer removal
kubectl get portfoliodeployment my-portfolio -n production -o jsonpath='{.metadata.finalizers}'
```

### Database Migration Operations

#### Create Database Migration
```yaml
# database-migration.yaml
apiVersion: portfolio.example.com/v1alpha1
kind: DatabaseMigration
metadata:
  name: migration-v1.2.0
  namespace: production
spec:
  targetDatabase:
    host: postgres.database.svc.cluster.local
    port: 5432
    database: portfolio_db
    credentialsSecret: db-credentials
  version: "v1.2.0"
  migrations:
    - name: "001_create_users_table"
      sql: |
        CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY,
          username VARCHAR(255) NOT NULL,
          email VARCHAR(255) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    - name: "002_add_users_index"
      sql: |
        CREATE INDEX idx_users_email ON users(email);
  rollback:
    enabled: true
    migrations:
      - name: "002_drop_users_index"
        sql: "DROP INDEX IF EXISTS idx_users_email;"
      - name: "001_drop_users_table"
        sql: "DROP TABLE IF EXISTS users;"
```

```bash
# Apply migration
kubectl apply -f database-migration.yaml

# Monitor migration progress
kubectl get databasemigration migration-v1.2.0 -n production --watch

# Check migration status
kubectl get databasemigration migration-v1.2.0 -n production \
  -o jsonpath='{.status.phase}'

# View migration logs
kubectl logs -n operator-system -l app=portfolio-operator | grep migration-v1.2.0
```

#### Rollback Migration
```bash
# Trigger rollback
kubectl patch databasemigration migration-v1.2.0 -n production \
  --type merge -p '{"spec":{"rollback":{"trigger":true}}}'

# Monitor rollback
kubectl logs -n operator-system -l app=portfolio-operator -f | grep migration-v1.2.0

# Verify rollback completion
kubectl get databasemigration migration-v1.2.0 -n production -o jsonpath='{.status}'
```

### Webhook Management

#### Verify Webhook Configuration
```bash
# Check validating webhooks
kubectl get validatingwebhookconfiguration portfolio-operator-webhook

# Check mutating webhooks
kubectl get mutatingwebhookconfiguration portfolio-operator-webhook

# Test webhook endpoint
kubectl port-forward -n operator-system svc/portfolio-operator-webhook 9443:9443 &
curl -k https://localhost:9443/health
```

#### Update Webhook Certificates
```bash
# Generate new certificates (using cert-manager)
kubectl annotate certificate portfolio-operator-webhook-cert \
  -n operator-system cert-manager.io/issue-temporary-certificate="true" --overwrite

# Wait for certificate renewal
kubectl wait --for=condition=Ready certificate/portfolio-operator-webhook-cert \
  -n operator-system --timeout=120s

# Restart operator to pick up new certs
kubectl rollout restart deployment/portfolio-operator -n operator-system

# Verify webhook is working
kubectl create -f test-portfolio-deployment.yaml --dry-run=server
```

---

## Incident Response

### P0: Operator Pod Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check operator pod status
kubectl get pods -n operator-system -l app=portfolio-operator

# 2. Check recent events
kubectl get events -n operator-system --sort-by='.lastTimestamp' | grep portfolio-operator

# 3. Check operator logs
kubectl logs -n operator-system -l app=portfolio-operator --tail=100 --previous

# 4. Restart operator
kubectl rollout restart deployment/portfolio-operator -n operator-system

# 5. Verify recovery
kubectl wait --for=condition=Ready pods -l app=portfolio-operator -n operator-system --timeout=120s
```

**Investigation (5-20 minutes):**
```bash
# Check operator resource usage
kubectl top pods -n operator-system -l app=portfolio-operator

# Check for OOMKilled
kubectl describe pod -n operator-system -l app=portfolio-operator | grep -A 10 "State:"

# Check operator metrics
kubectl port-forward -n operator-system svc/portfolio-operator-metrics 8080:8080 &
curl -s http://localhost:8080/metrics | grep -E "(memory|goroutines|handlers)"

# Review operator configuration
kubectl get deployment portfolio-operator -n operator-system -o yaml
```

**Recovery:**
```bash
# If resource exhaustion, increase limits
kubectl patch deployment portfolio-operator -n operator-system --type json -p='[
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/resources/limits/memory",
    "value": "1Gi"
  }
]'

# If configuration issue, restore from backup
kubectl apply -f backup/operator-deployment.yaml

# Verify operator health
kubectl get pods -n operator-system -l app=portfolio-operator
kubectl logs -n operator-system -l app=portfolio-operator --tail=50
```

### P0: Reconciliation Loop Stuck

**Investigation:**
```bash
# 1. Identify stuck resources
kubectl get portfoliodeployments --all-namespaces -o json | \
  jq '.items[] | select(.status.conditions[] | select(.type=="Reconciling" and .status=="True")) | {name: .metadata.name, namespace: .metadata.namespace}'

# 2. Check operator logs for errors
kubectl logs -n operator-system -l app=portfolio-operator --tail=500 | grep -A 10 "ERROR\|Exception"

# 3. Check resource status
kubectl describe portfoliodeployment <stuck-resource> -n <namespace>

# 4. Check operator metrics
curl -s http://localhost:8080/metrics | grep kopf_reconciliation_duration_seconds | grep <stuck-resource>
```

**Mitigation:**
```bash
# Option 1: Remove finalizers to force deletion
kubectl patch portfoliodeployment <stuck-resource> -n <namespace> \
  --type json -p='[{"op": "remove", "path": "/metadata/finalizers"}]'

# Option 2: Restart operator to reset state
kubectl rollout restart deployment/portfolio-operator -n operator-system

# Option 3: Manually fix resource state
kubectl patch portfoliodeployment <stuck-resource> -n <namespace> \
  --type merge -p '{"status":{"phase":"Ready","conditions":[]}}'

# Verify reconciliation resumes
kubectl logs -n operator-system -l app=portfolio-operator -f | grep <stuck-resource>
```

### P1: Migration Failure

**Investigation:**
```bash
# 1. Check migration status
kubectl get databasemigration <migration-name> -n <namespace> -o yaml

# 2. Check migration logs
kubectl logs -n operator-system -l app=portfolio-operator --tail=500 | grep <migration-name>

# 3. Check database connectivity
kubectl run db-test --rm -it --image=postgres:14 -- \
  psql -h postgres.database.svc.cluster.local -U portfolio -d portfolio_db -c "\dt"

# 4. Check migration SQL
kubectl get databasemigration <migration-name> -n <namespace> \
  -o jsonpath='{.spec.migrations[*].sql}'
```

**Common Causes & Fixes:**

**Database Connection Error:**
```bash
# Verify database is accessible
kubectl get svc -n database postgres

# Check credentials
kubectl get secret db-credentials -n <namespace> -o jsonpath='{.data.password}' | base64 -d

# Test connection
kubectl run psql --rm -it --image=postgres:14 -- \
  psql postgresql://user:pass@postgres.database.svc.cluster.local/portfolio_db
```

**SQL Syntax Error:**
```bash
# Review SQL in migration
kubectl get databasemigration <migration-name> -n <namespace> -o yaml

# Fix SQL and update CR
kubectl edit databasemigration <migration-name> -n <namespace>

# Or delete and recreate
kubectl delete databasemigration <migration-name> -n <namespace>
kubectl apply -f corrected-migration.yaml
```

**Migration Already Applied:**
```bash
# Check migration history in database
kubectl run psql --rm -it --image=postgres:14 -- \
  psql postgresql://user:pass@postgres.database.svc.cluster.local/portfolio_db \
  -c "SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 10;"

# Mark migration as complete
kubectl patch databasemigration <migration-name> -n <namespace> \
  --type merge -p '{"status":{"phase":"Completed"}}'
```

### P1: High CRD Operation Failure Rate

**Investigation:**
```bash
# 1. Check validation webhook logs
kubectl logs -n operator-system -l app=portfolio-operator --tail=200 | grep -i "validation\|webhook"

# 2. Identify failing operations
kubectl get events --all-namespaces --field-selector reason=FailedCreate,reason=FailedUpdate \
  --sort-by='.lastTimestamp' | grep PortfolioDeployment

# 3. Check operator metrics
curl -s http://localhost:8080/metrics | grep kopf_reconciliation_errors

# 4. Test CR creation
kubectl create -f test-portfolio-deployment.yaml --dry-run=server
```

**Common Issues:**

**Webhook Timeout:**
```bash
# Check webhook service
kubectl get svc portfolio-operator-webhook -n operator-system

# Test webhook endpoint
kubectl port-forward -n operator-system svc/portfolio-operator-webhook 9443:9443 &
time curl -k https://localhost:9443/validate

# Increase webhook timeout
kubectl patch validatingwebhookconfiguration portfolio-operator-webhook \
  --type json -p='[{"op": "replace", "path": "/webhooks/0/timeoutSeconds", "value": 30}]'
```

**Invalid Resource Spec:**
```bash
# Check validation errors
kubectl describe portfoliodeployment <name> -n <namespace> | grep -A 10 Events

# Review CRD schema
kubectl get crd portfoliodeployments.portfolio.example.com -o yaml | grep -A 50 "openAPIV3Schema:"

# Fix resource spec
kubectl edit portfoliodeployment <name> -n <namespace>
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "CRD not found"

**Symptoms:**
```
Error: the server could not find the requested resource (get portfoliodeployments.portfolio.example.com)
```

**Diagnosis:**
```bash
# Check if CRD exists
kubectl get crds | grep portfolio

# Check CRD details
kubectl get crd portfoliodeployments.portfolio.example.com
```

**Solution:**
```bash
# Install CRDs
kubectl apply -f manifests/crds/

# Verify CRD is registered
kubectl get crd portfoliodeployments.portfolio.example.com -o yaml

# Wait for CRD to be established
kubectl wait --for condition=established crd/portfoliodeployments.portfolio.example.com --timeout=60s
```

---

#### Issue: "Operator not reconciling changes"

**Symptoms:**
- CR status not updating
- Changes to CR spec not taking effect
- No logs from operator

**Diagnosis:**
```bash
# Check operator is running
kubectl get pods -n operator-system -l app=portfolio-operator

# Check operator logs
kubectl logs -n operator-system -l app=portfolio-operator --tail=100

# Check if operator is watching resources
curl -s http://localhost:8080/metrics | grep kopf_events_watched
```

**Solution:**
```bash
# Restart operator
kubectl rollout restart deployment/portfolio-operator -n operator-system

# Check operator has RBAC permissions
kubectl auth can-i get portfoliodeployments --as=system:serviceaccount:operator-system:portfolio-operator -n production
kubectl auth can-i update portfoliodeployments --as=system:serviceaccount:operator-system:portfolio-operator -n production

# Grant missing permissions if needed
kubectl apply -f manifests/rbac.yaml
```

---

#### Issue: "Finalizer preventing resource deletion"

**Symptoms:**
```bash
$ kubectl delete portfoliodeployment my-portfolio -n production
# Resource stuck in "Terminating" state
```

**Diagnosis:**
```bash
# Check finalizers
kubectl get portfoliodeployment my-portfolio -n production -o jsonpath='{.metadata.finalizers}'

# Check operator logs for cleanup errors
kubectl logs -n operator-system -l app=portfolio-operator --tail=100 | grep finalizer
```

**Solution:**
```bash
# Option 1: Wait for operator to complete cleanup
# Check operator logs for progress

# Option 2: Remove finalizers manually (use with caution)
kubectl patch portfoliodeployment my-portfolio -n production \
  --type json -p='[{"op": "remove", "path": "/metadata/finalizers"}]'

# Verify deletion
kubectl get portfoliodeployment my-portfolio -n production
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
# 1. Check operator status
kubectl get pods -n operator-system -l app=portfolio-operator

# 2. Check custom resources
kubectl get portfoliodeployments --all-namespaces
kubectl get databasemigrations --all-namespaces

# 3. Review operator logs for errors
kubectl logs -n operator-system -l app=portfolio-operator --tail=100 --since=24h | grep -i error

# 4. Check reconciliation metrics
kubectl port-forward -n operator-system svc/portfolio-operator-metrics 8080:8080 &
curl -s http://localhost:8080/metrics | grep kopf_reconciliation

# 5. Verify webhook health
kubectl get validatingwebhookconfiguration portfolio-operator-webhook
kubectl get mutatingwebhookconfiguration portfolio-operator-webhook
```

### Weekly Tasks

```bash
# 1. Review operator resource usage trends
kubectl top pods -n operator-system -l app=portfolio-operator

# 2. Check for stuck resources
kubectl get portfoliodeployments --all-namespaces -o json | \
  jq '.items[] | select(.status.phase != "Ready") | {name: .metadata.name, phase: .status.phase}'

# 3. Review and clean up completed migrations
kubectl get databasemigrations --all-namespaces -o json | \
  jq '.items[] | select(.status.phase == "Completed") | {name: .metadata.name, completedAt: .status.completionTime}'

# 4. Backup CRD configurations
kubectl get portfoliodeployments,databasemigrations --all-namespaces -o yaml > backup/crs-$(date +%Y%m%d).yaml

# 5. Review operator performance
# Check reconciliation latency trends
# Identify slow handlers
# Optimize if needed

# 6. Update operator documentation
# Document new CRs created
# Update troubleshooting guide
```

### Monthly Tasks

```bash
# 1. Update operator version (if available)
kubectl set image deployment/portfolio-operator \
  portfolio-operator=portfolio-operator:v2.1.0 \
  -n operator-system

# 2. Review and update CRD schemas
# Check for deprecated fields
# Plan schema migrations

# 3. Conduct disaster recovery drill
# Simulate operator failure
# Test recovery procedures

# 4. Review and optimize RBAC permissions
kubectl get clusterrole,role -n operator-system | grep portfolio-operator
# Remove unnecessary permissions

# 5. Capacity planning
# Review resource usage trends
# Plan for scaling
# Adjust resource limits

# 6. Security review
# Review webhook certificates
# Check for CVEs in operator dependencies
# Update base images if needed
```

### Disaster Recovery

**Backup Strategy:**
```bash
# 1. Backup CRDs
kubectl get crds -o yaml | grep -A 1000 portfolio.example.com > backup/crds.yaml

# 2. Backup custom resources
kubectl get portfoliodeployments,databasemigrations --all-namespaces -o yaml > backup/crs.yaml

# 3. Backup operator configuration
kubectl get deployment,service,configmap,secret -n operator-system -o yaml > backup/operator-config.yaml

# 4. Backup RBAC
kubectl get clusterrole,clusterrolebinding,role,rolebinding -n operator-system -o yaml > backup/rbac.yaml

# 5. Document operator state
kubectl get events -n operator-system > backup/events.txt
kubectl logs -n operator-system -l app=portfolio-operator > backup/operator-logs.txt
```

**Recovery Procedures:**
```bash
# 1. Reinstall CRDs
kubectl apply -f backup/crds.yaml

# 2. Wait for CRDs to be established
kubectl wait --for condition=established crd/portfoliodeployments.portfolio.example.com --timeout=60s
kubectl wait --for condition=established crd/databasemigrations.portfolio.example.com --timeout=60s

# 3. Restore RBAC
kubectl apply -f backup/rbac.yaml

# 4. Restore operator
kubectl apply -f backup/operator-config.yaml

# 5. Wait for operator to be ready
kubectl wait --for=condition=Ready pods -l app=portfolio-operator -n operator-system --timeout=120s

# 6. Restore custom resources
kubectl apply -f backup/crs.yaml

# 7. Verify operator functionality
kubectl logs -n operator-system -l app=portfolio-operator -f

# 8. Test with sample CR
kubectl apply -f test-portfolio-deployment.yaml
kubectl get portfoliodeployment test -o jsonpath='{.status.phase}'
```

---

## Quick Reference

### Common Commands

```bash
# Check operator status
kubectl get pods -n operator-system -l app=portfolio-operator

# View operator logs
kubectl logs -n operator-system -l app=portfolio-operator -f

# List custom resources
kubectl get portfoliodeployments --all-namespaces
kubectl get databasemigrations --all-namespaces

# Check CR status
kubectl get portfoliodeployment <name> -n <namespace> -o jsonpath='{.status}'

# Restart operator
kubectl rollout restart deployment/portfolio-operator -n operator-system
```

### Emergency Response

```bash
# P0: Operator down
kubectl rollout restart deployment/portfolio-operator -n operator-system

# P0: Reconciliation stuck
kubectl patch portfoliodeployment <name> -n <namespace> --type json -p='[{"op": "remove", "path": "/metadata/finalizers"}]'

# P1: Migration failed
kubectl logs -n operator-system -l app=portfolio-operator | grep <migration-name>
kubectl patch databasemigration <name> -n <namespace> --type merge -p '{"spec":{"rollback":{"trigger":true}}}'

# P1: High failure rate
kubectl logs -n operator-system -l app=portfolio-operator --tail=200 | grep ERROR
```

### Useful Queries

```bash
# Find all resources managed by operator
kubectl get all --all-namespaces -l managed-by=portfolio-operator

# Check operator metrics
curl -s http://localhost:8080/metrics | grep -E "(kopf|operator)"

# List resources by status
kubectl get portfoliodeployments --all-namespaces -o json | \
  jq -r '.items[] | "\(.metadata.namespace)/\(.metadata.name): \(.status.phase)"'
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Submit PR with updates

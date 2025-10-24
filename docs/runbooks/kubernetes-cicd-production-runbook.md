# Production Runbook - Kubernetes CI/CD Platform

**Version:** 1.0  
**Last Updated:** October 2025  
**Owner:** Platform Engineering Team  
**Status:** Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Quick Reference](#quick-reference)
3. [Initial Setup](#initial-setup)
4. [Daily Operations](#daily-operations)
5. [Deployment Procedures](#deployment-procedures)
6. [Incident Response](#incident-response)
7. [Monitoring & Alerting](#monitoring--alerting)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance Procedures](#maintenance-procedures)
10. [Emergency Contacts](#emergency-contacts)

---

## System Overview

### Architecture Components

```
Production System Architecture:
├── AWS EKS Cluster (Production)
│   ├── Application Pods (3+ replicas)
│   ├── Monitoring Stack (Prometheus, Grafana)
│   └── Service Mesh (Istio)
├── GitLab CI/CD Pipeline
├── ArgoCD (GitOps Controller)
├── Docker Registry (ECR)
├── Portfolio Website (S3 + CloudFront)
└── Database (RDS with automated backups)
```

### Key Services

| Service | URL | Purpose |
|---------|-----|---------|
| Production App | https://app.myapp.com | Main application |
| Portfolio | https://samueljackson.dev | Portfolio website |
| Grafana | https://grafana.mycompany.com | Metrics & dashboards |
| ArgoCD | https://argocd.mycompany.com | GitOps deployments |
| Prometheus | Internal | Metrics collection |

### Critical Metrics

- **SLA Target:** 99.9% uptime (43 minutes downtime/month)
- **Error Budget:** 0.1% (1000 errors per million requests)
- **Response Time:** p95 < 200ms, p99 < 500ms
- **Deployment Frequency:** Multiple times per day

---

## Quick Reference

### Essential Commands

```bash
# Check cluster health
kubectl get nodes
kubectl get pods -A | grep -v Running

# Check application status
kubectl get pods -n prod -l app=myapp-backend

# View recent deployments
argocd app history myapp-backend-prod | head -5

# Check error rate
./scripts/check-error-rate.sh prod 1h

# Rollback deployment
./scripts/rollback-deployment.sh prod myapp-backend

# View logs
kubectl logs -n prod -l app=myapp-backend --tail=100 -f

# Scale application
kubectl scale deployment myapp-backend -n prod --replicas=5

# Check resource usage
kubectl top nodes
kubectl top pods -n prod
```

### Common Alerts & Responses

| Alert | Severity | Action |
|-------|----------|--------|
| HighErrorRate | Critical | Run `./scripts/rollback-deployment.sh` |
| PodCrashLooping | High | Check logs, investigate restart cause |
| HighMemoryUsage | Medium | Scale up or optimize application |
| DiskSpaceLow | Medium | Clean up old logs, expand volume |
| CertificateExpiring | Low | Renew certificate via cert-manager |

---

## Initial Setup

### Prerequisites Checklist

- [ ] AWS CLI configured with appropriate credentials
- [ ] kubectl installed (v1.28+)
- [ ] Terraform installed (v1.5+)
- [ ] Helm installed (v3.12+)
- [ ] argocd CLI installed
- [ ] jq installed for JSON parsing
- [ ] Access to GitLab repository
- [ ] Access to AWS console with admin permissions

### One-Time Setup Procedure

**Duration:** ~45 minutes  
**Risk Level:** Low (new environment)  
**Rollback:** Destroy Terraform resources

```bash
# 1. Clone repository
git clone https://gitlab.com/mycompany/kubernetes-cicd-complete.git
cd kubernetes-cicd-complete

# 2. Run prerequisites check
./scripts/check-prerequisites.sh

# 3. Set up AWS infrastructure
cd infrastructure/kubernetes/terraform/environments/prod
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 4. Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name eks-prod

# 5. Verify cluster access
kubectl cluster-info
kubectl get nodes

# 6. Install Kubernetes add-ons
cd ../../../../
./infrastructure/kubernetes/scripts/install-addons.sh

# 7. Install monitoring stack
./monitoring/scripts/install-monitoring.sh

# Wait for monitoring pods
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s
kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=300s

# 8. Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Get initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 9. Configure ArgoCD applications
kubectl apply -f argocd/projects/
kubectl apply -f argocd/applications/

# 10. Deploy portfolio website infrastructure
cd infrastructure/portfolio-website/terraform
terraform init
terraform apply -auto-approve

# 11. Build and deploy portfolio website
cd ../../../applications/frontend
npm ci
npm run build
npm run export
aws s3 sync out/ s3://portfolio-production-website/ --delete

# 12. Run production readiness check
cd ../../
./scripts/production-readiness-check.sh

# 13. Run smoke tests
./scripts/smoke-tests.sh prod
```

### Post-Setup Verification

```bash
# Verify all components
echo "Checking cluster health..."
kubectl get nodes
kubectl get pods -A

echo "Checking ArgoCD applications..."
argocd app list

echo "Checking monitoring..."
curl -sf https://grafana.mycompany.com/api/health

echo "Checking portfolio website..."
curl -sf https://samueljackson.dev

echo "Setup complete! Access details:"
echo "- Grafana: https://grafana.mycompany.com"
echo "- ArgoCD: https://argocd.mycompany.com"
echo "- Portfolio: https://samueljackson.dev"
```

---

## Daily Operations

### Daily Health Check

**Schedule:** Run every morning at 9:00 AM  
**Duration:** 5-10 minutes  
**Owner:** On-call engineer

```bash
# Run automated daily operations check
./scripts/daily-operations.sh

# Manual verification steps:
# 1. Check Grafana dashboards
open https://grafana.mycompany.com/d/overview

# 2. Review active alerts
open https://grafana.mycompany.com/alerting/list

# 3. Check ArgoCD sync status
argocd app list

# 4. Verify recent deployments
argocd app history myapp-backend-prod | head -5

# 5. Review error budget
./scripts/check-error-budget.sh
```

### Weekly Tasks

**Schedule:** Every Monday at 10:00 AM

- [ ] Review capacity planning metrics
- [ ] Check certificate expiration dates
- [ ] Review and update documentation
- [ ] Analyze cost trends in AWS Cost Explorer
- [ ] Review security scan results
- [ ] Audit access logs
- [ ] Team sync on operational issues

```bash
# Run weekly maintenance script
./scripts/weekly-maintenance.sh
```

### Monthly Tasks

**Schedule:** First Monday of each month

- [ ] Update Kubernetes cluster (if patch available)
- [ ] Review and rotate secrets
- [ ] Conduct disaster recovery drill
- [ ] Review and update runbooks
- [ ] Security audit
- [ ] Capacity planning review
- [ ] Cost optimization review

```bash
# Run monthly maintenance script
./scripts/monthly-maintenance.sh
```

---

## Deployment Procedures

### Standard Deployment Process

**Duration:** 15-30 minutes  
**Risk Level:** Medium  
**Rollback Time:** 5 minutes

#### Pre-Deployment Checklist

- [ ] Code reviewed and approved
- [ ] All tests passing in CI pipeline
- [ ] Security scan passed
- [ ] Staging deployment successful
- [ ] Change ticket created
- [ ] Stakeholders notified
- [ ] Rollback plan ready

#### Deployment Steps

```bash
# 1. Verify current state
kubectl get deployment myapp-backend -n prod

# 2. Check error rate baseline
./scripts/check-error-rate.sh prod 1h

# 3. Deploy to development (automatic)
git checkout develop
git push origin develop

# GitLab CI/CD will automatically:
# - Build Docker image
# - Run tests
# - Scan for vulnerabilities
# - Deploy to dev namespace
# - Run smoke tests

# 4. Deploy to staging (manual approval required)
# Go to: GitLab > Pipelines > Latest > deploy:staging
# Click: Play button
# Wait: ~5 minutes

# 5. Verify staging deployment
./scripts/smoke-tests.sh staging
./scripts/verify-deployment.sh staging v1.2.3

# 6. Run production readiness check
./scripts/production-readiness-check.sh

# 7. Deploy to production with canary
# Go to: GitLab > Pipelines > Latest > deploy:prod
# Click: Play button
# Canary deployment will:
# - Deploy 10% traffic to new version
# - Monitor for 10 minutes
# - Auto-rollback if error rate increases
# - Gradually increase to 100%

# 8. Monitor deployment
./scripts/monitor-deployment.sh prod 3600

# Watch Grafana dashboard
open https://grafana.mycompany.com/d/deployment

# 9. Verify deployment
./scripts/smoke-tests.sh prod
./scripts/verify-deployment.sh prod v1.2.3

# 10. Update documentation
echo "v1.2.3 deployed at $(date)" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: update changelog for v1.2.3"
git push
```

#### Post-Deployment Verification

```bash
# Check application health
kubectl get pods -n prod -l app=myapp-backend
kubectl logs -n prod -l app=myapp-backend --tail=50

# Verify metrics
curl -s https://app.myapp.com/metrics | grep -E "http_requests_total|error_rate"

# Check error rate
./scripts/check-error-rate.sh prod 15m

# Test critical endpoints
./scripts/smoke-tests.sh prod

# Monitor for 15 minutes
watch -n 30 './scripts/check-error-rate.sh prod 5m'
```

### Emergency Hotfix Deployment

**Duration:** 10-15 minutes  
**Risk Level:** High  
**Authorization Required:** Engineering Lead

```bash
# 1. Create hotfix branch
git checkout -b hotfix/critical-bug-fix production

# 2. Make fix and commit
git add .
git commit -m "fix: critical bug fix"
git push origin hotfix/critical-bug-fix

# 3. Fast-track through pipeline
# Skip staging, deploy directly to prod with approval

# 4. Monitor closely
./scripts/monitor-deployment.sh prod 1800

# 5. Document incident
# Create post-mortem document
```

### Rollback Procedure

**Duration:** 3-5 minutes  
**Risk Level:** Low

```bash
# Automatic rollback (if monitoring detects issues)
# ArgoCD will auto-rollback if error rate exceeds threshold

# Manual rollback
./scripts/rollback-deployment.sh prod myapp-backend

# Or via ArgoCD UI
argocd app rollback myapp-backend-prod

# Verify rollback
kubectl get pods -n prod -l app=myapp-backend
./scripts/verify-deployment.sh prod v1.2.2  # previous version

# Check error rate normalized
./scripts/check-error-rate.sh prod 5m
```

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|---------------|------------|
| P0 | Complete outage | Immediate | CTO, CEO |
| P1 | Critical feature down | 15 minutes | VP Engineering |
| P2 | Degraded performance | 1 hour | Engineering Lead |
| P3 | Minor issue | 4 hours | Team Lead |
| P4 | Cosmetic issue | Best effort | None |

### P0: Complete Outage Response

**Immediate Actions (0-5 minutes)**

```bash
# 1. Acknowledge incident
echo "P0 INCIDENT: $(date)" >> /tmp/incident.log

# 2. Check cluster status
kubectl get nodes
kubectl get pods -A | grep -v Running

# 3. Check recent changes
argocd app history myapp-backend-prod | head -3

# 4. Check error rate
./scripts/check-error-rate.sh prod 5m

# 5. Rollback if recent deployment
if [[ $(argocd app history myapp-backend-prod | head -2 | tail -1 | awk '{print $1}') == "$(date +%Y-%m-%d)" ]]; then
    ./scripts/rollback-deployment.sh prod myapp-backend
fi

# 6. Notify stakeholders
# Send alert to #incidents Slack channel
```

**Investigation (5-15 minutes)**

```bash
# Check application logs
kubectl logs -n prod -l app=myapp-backend --tail=200 > /tmp/app-logs.txt
grep -i "error\|exception\|fatal" /tmp/app-logs.txt

# Check infrastructure
kubectl describe nodes
kubectl top nodes
kubectl top pods -n prod

# Check database connectivity
kubectl exec -n prod deployment/myapp-backend -- curl -sf http://database:5432/health

# Check external dependencies
curl -sf https://api.external-service.com/health
```

**Resolution Actions**

```bash
# Scale up if resource exhaustion
kubectl scale deployment myapp-backend -n prod --replicas=10

# Restart pods if needed
kubectl rollout restart deployment/myapp-backend -n prod

# Apply emergency configuration
kubectl apply -f config/emergency-config.yaml

# Verify resolution
./scripts/smoke-tests.sh prod
watch -n 10 './scripts/check-error-rate.sh prod 1m'
```

### P1: Critical Feature Down

**Response Procedure:**

1. Investigate affected feature
2. Check feature flags
3. Review recent changes to feature
4. Isolate issue
5. Deploy fix or rollback
6. Monitor for 30 minutes

### Common Incident Scenarios

#### High Error Rate

```bash
# Check error rate trend
./scripts/check-error-rate.sh prod 1h

# Identify error types
kubectl logs -n prod -l app=myapp-backend | grep "ERROR" | awk '{print $NF}' | sort | uniq -c | sort -rn

# Check if specific endpoint
kubectl logs -n prod -l app=myapp-backend | grep "ERROR" | grep -o "path=[^ ]*" | sort | uniq -c

# Rollback if recent deployment
./scripts/rollback-deployment.sh prod myapp-backend
```

#### Pods Crash Looping

```bash
# Identify crashing pods
kubectl get pods -n prod | grep -E "CrashLoopBackOff|Error"

# Get pod logs
POD=$(kubectl get pods -n prod -l app=myapp-backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n prod $POD --previous

# Describe pod for events
kubectl describe pod -n prod $POD

# Common causes:
# - OOMKilled: Increase memory limits
# - Config error: Check configmaps and secrets
# - Failed healthcheck: Review /health endpoint
```

#### High Memory Usage

```bash
# Check current usage
kubectl top pods -n prod -l app=myapp-backend

# Check memory limits
kubectl get pods -n prod -l app=myapp-backend -o jsonpath='{.items[0].spec.containers[0].resources}'

# Temporary fix: Scale up
kubectl scale deployment myapp-backend -n prod --replicas=5

# Permanent fix: Increase memory limits in Helm values
# Edit: helm/values-prod.yaml
# Apply: argocd app sync myapp-backend-prod
```

---

## Monitoring & Alerting

### Key Dashboards

1. **System Overview** - https://grafana.mycompany.com/d/overview
   - Cluster health
   - Application status
   - Error rates
   - Response times

2. **Application Metrics** - https://grafana.mycompany.com/d/application
   - Request rate
   - Error rate
   - Response time percentiles
   - Saturation metrics

3. **Kubernetes Metrics** - https://grafana.mycompany.com/d/kubernetes
   - Node resources
   - Pod resources
   - Network traffic
   - Storage usage

### Critical Alerts

#### Error Rate Alert

```yaml
Trigger: Error rate > 1% for 5 minutes
Action: Investigate and rollback if needed
Query: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
```

#### High Response Time

```yaml
Trigger: p99 latency > 500ms for 5 minutes
Action: Check database, scale up, or optimize
Query: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 0.5
```

#### Pod Availability

```yaml
Trigger: < 3 pods running for 2 minutes
Action: Check cluster health, scale up
Query: count(kube_pod_status_phase{namespace="prod", phase="Running"} == 1) < 3
```

### Checking Error Budget

```bash
# View current error budget status
./scripts/check-error-budget.sh

# Output example:
# Error Budget Status:
# SLO Target: 99.9%
# Current Availability: 99.95%
# Error Budget Remaining: 60%
# Errors This Month: 423 / 1000 allowed
# Status: HEALTHY
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Pods Not Starting

**Symptoms:** Pods stuck in Pending or ContainerCreating state

**Diagnosis:**
```bash
kubectl describe pod -n prod <pod-name>
kubectl get events -n prod --sort-by='.lastTimestamp'
```

**Common Causes:**
- Insufficient resources: Scale down or add nodes
- Image pull errors: Check ECR permissions
- PVC not bound: Check storage class and PV availability

**Solution:**
```bash
# Add nodes if resource constrained
eksctl scale nodegroup --cluster=eks-prod --name=ng-prod --nodes=5

# Check image accessibility
kubectl get pods -n prod <pod-name> -o jsonpath='{.spec.containers[0].image}'
docker pull <image>

# Check PVC status
kubectl get pvc -n prod
```

#### Issue: Service Unavailable

**Symptoms:** 503 errors, service unreachable

**Diagnosis:**
```bash
kubectl get svc -n prod
kubectl get endpoints -n prod myapp-backend
curl -v http://<service-ip>:<port>/health
```

**Solution:**
```bash
# Check if pods are ready
kubectl get pods -n prod -l app=myapp-backend

# Restart service
kubectl delete svc -n prod myapp-backend
kubectl apply -f helm/templates/service.yaml

# Check ingress
kubectl get ingress -n prod
kubectl describe ingress -n prod myapp-ingress
```

#### Issue: Database Connection Failures

**Symptoms:** Logs showing database connection errors

**Diagnosis:**
```bash
# Test from pod
kubectl exec -n prod deployment/myapp-backend -- nc -zv database-host 5432

# Check secrets
kubectl get secrets -n prod database-credentials -o yaml
```

**Solution:**
```bash
# Update database credentials
kubectl create secret generic database-credentials \
  --from-literal=username=<user> \
  --from-literal=password=<pass> \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new credentials
kubectl rollout restart deployment/myapp-backend -n prod
```

### Log Investigation

```bash
# Application logs
kubectl logs -n prod -l app=myapp-backend --tail=500

# Follow logs in real-time
kubectl logs -n prod -l app=myapp-backend -f

# Logs from all pods
kubectl logs -n prod -l app=myapp-backend --all-containers=true

# Previous pod logs (if crashed)
kubectl logs -n prod <pod-name> --previous

# Filter errors
kubectl logs -n prod -l app=myapp-backend | grep -i "error\|exception\|fatal"

# Export to file for analysis
kubectl logs -n prod -l app=myapp-backend --since=1h > /tmp/app-logs.txt
```

---

## Maintenance Procedures

### Kubernetes Cluster Update

**Frequency:** Every 3 months or when security patches available  
**Duration:** 2-4 hours  
**Downtime:** None (rolling update)

```bash
# 1. Check current version
kubectl version --short

# 2. Check available updates
aws eks describe-cluster --name eks-prod --query 'cluster.version'

# 3. Update control plane
aws eks update-cluster-version --name eks-prod --kubernetes-version 1.28

# 4. Wait for update (15-30 minutes)
aws eks wait cluster-active --name eks-prod

# 5. Update node groups (rolling)
eksctl upgrade nodegroup \
  --cluster=eks-prod \
  --name=ng-prod \
  --kubernetes-version=1.28

# 6. Update add-ons
./infrastructure/kubernetes/scripts/upgrade-addons.sh

# 7. Verify cluster health
kubectl get nodes
kubectl get pods -A
./scripts/smoke-tests.sh prod
```

### Certificate Renewal

**Frequency:** 90 days (automatic via cert-manager)  
**Manual Renewal:** Only if automation fails

```bash
# Check certificate status
kubectl get certificates -n prod

# Force renewal if needed
kubectl delete certificate -n prod myapp-tls
kubectl apply -f helm/templates/certificate.yaml

# Verify new certificate
kubectl describe certificate -n prod myapp-tls
```

### Database Backup & Restore

**Backup Schedule:** Daily at 2:00 AM UTC  
**Retention:** 30 days

```bash
# Manual backup
./scripts/backup-database.sh

# Verify backup
aws s3 ls s3://myapp-database-backups/prod/ --recursive | tail -5

# Restore from backup (CAUTION)
./scripts/restore-database.sh prod 2025-10-04

# Test restore in staging first
./scripts/restore-database.sh staging 2025-10-04
```

### Security Audit

**Frequency:** Monthly  
**Duration:** 1-2 hours

```bash
# Run security audit script
./scripts/security-audit.sh

# Manual checks:
# 1. Review IAM policies
# 2. Check for exposed secrets
# 3. Review network policies
# 4. Audit access logs
# 5. Check for vulnerabilities
# 6. Review security groups

# Run vulnerability scan
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/trivy-operator/main/deploy/static/trivy-operator.yaml

# Check results
kubectl get vulnerabilityreports -A
```

---

## Emergency Contacts

### On-Call Rotation

| Week | Primary | Secondary | Manager |
|------|---------|-----------|---------|
| Current | John Smith | Jane Doe | Bob Manager |
| Next | Jane Doe | Mike Tech | Bob Manager |

### Escalation Path

1. **L1:** On-call engineer (respond within 15 minutes)
2. **L2:** Team lead (respond within 30 minutes)
3. **L3:** Engineering manager (respond within 1 hour)
4. **L4:** VP Engineering (critical incidents only)

### Contact Information

```yaml
# Stored in: config/emergency-contacts.yaml
contacts:
  oncall:
    primary:
      name: "John Smith"
      phone: "+1-555-0101"
      slack: "@jsmith"
    secondary:
      name: "Jane Doe"
      phone: "+1-555-0102"
      slack: "@jdoe"
  
  management:
    team_lead:
      name: "Bob Manager"
      phone: "+1-555-0200"
      slack: "@bmanager"
    
  vendors:
    aws_support:
      account: "Enterprise"
      phone: "1-800-AWS-SUPPORT"
      case_portal: "https://console.aws.amazon.com/support"
```

### Communication Channels

- **#incidents:** For active incidents
- **#platform-alerts:** For automated alerts
- **#platform-team:** For general platform discussions
- **#on-call:** For on-call coordination

---

## Additional Resources

### Documentation

- [Architecture Overview](../architecture/system-overview.md)
- [Disaster Recovery Plan](../runbooks/disaster-recovery.md)
- [Security Policies](../architecture/security-model.md)
- [Onboarding Guide](../training/onboarding.md)

### External Resources

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Prometheus Query Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)

### Useful Links

- [GitLab Repository](https://gitlab.com/mycompany/kubernetes-cicd-complete)
- [Grafana Dashboards](https://grafana.mycompany.com)
- [ArgoCD Console](https://argocd.mycompany.com)
- [AWS Console](https://console.aws.amazon.com)

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-04 | Platform Team | Initial production release |

**Review Schedule:** This runbook should be reviewed and updated quarterly or after any major system changes.

**Feedback:** Submit updates via pull request or contact the Platform Engineering team.

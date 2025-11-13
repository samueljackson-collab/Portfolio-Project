# Runbook — Project 3 (Kubernetes CI/CD Pipeline)

## Overview

Production operations runbook for Project 3 Kubernetes CI/CD Pipeline. This runbook covers GitOps delivery using GitHub Actions, ArgoCD, progressive deployment strategies, incident response, and troubleshooting for declarative continuous delivery.

**System Components:**
- GitHub Actions for CI (build, test, containerize)
- ArgoCD for CD (GitOps continuous delivery)
- Kubernetes cluster (EKS, GKE, or on-premises)
- Docker container registry (ECR, GCR, or DockerHub)
- Helm charts for application packaging
- Progressive delivery (Canary, Blue-Green deployments)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deployment success rate** | 99% | ArgoCD sync status success |
| **Deployment time** | < 10 minutes | Git commit → application running |
| **ArgoCD sync time** | < 3 minutes | Time to detect and sync changes |
| **CI pipeline success rate** | 95% | GitHub Actions workflow completion |
| **Rollback time (RTO)** | < 2 minutes | Time to revert to previous version |
| **Application availability during deploy** | 99.9% | Zero-downtime deployments |

---

## Dashboards & Alerts

### Dashboards

#### ArgoCD Dashboard
- [ArgoCD Web UI](https://argocd.example.com)
- Application sync status
- Deployment history
- Resource health
- Git repository sync status

#### GitHub Actions Dashboard
- [GitHub Actions](https://github.com/your-org/Portfolio-Project/actions)
- Workflow runs status
- Build duration trends
- Test success rates
- Deployment history

#### Application Health Dashboard
```bash
# Check ArgoCD applications
argocd app list

# Check application status
argocd app get production-app

# Check Kubernetes resources
kubectl get all -n production -l app=myapp

# Check pod health
kubectl get pods -n production -o wide
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | ArgoCD sync failed in production | Immediate | Investigate and rollback |
| **P0** | All pods failing in production | Immediate | Emergency rollback |
| **P0** | GitHub Actions pipeline broken | Immediate | Fix CI or deploy manually |
| **P1** | Canary deployment health check failing | 5 minutes | Abort canary, rollback |
| **P1** | ArgoCD out of sync >10 minutes | 15 minutes | Investigate drift |
| **P2** | GitHub Actions job failing | 30 minutes | Fix tests or pipeline |
| **P2** | ArgoCD degraded (some resources unhealthy) | 30 minutes | Investigate resource issues |
| **P3** | Slow CI/CD pipeline (>15 min) | 1 hour | Optimize pipeline |

---

## Standard Operations

### CI Pipeline Operations

#### Trigger CI Pipeline
```bash
# CI pipelines automatically trigger on git push
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd

# Make changes to code
echo "new feature" >> app/feature.py

# Commit and push
git add .
git commit -m "feat: add new feature"
git push origin main

# Monitor pipeline
# Navigate to: https://github.com/your-org/Portfolio-Project/actions
```

#### Monitor CI Pipeline
```bash
# Using GitHub CLI
gh workflow list
gh run list --workflow=ci-cd.yaml
gh run view <run-id>

# Watch pipeline logs
gh run watch <run-id>

# Download pipeline artifacts
gh run download <run-id>
```

#### Manual Pipeline Trigger
```bash
# Trigger workflow manually
gh workflow run ci-cd.yaml

# Trigger with specific branch
gh workflow run ci-cd.yaml --ref feature-branch

# Trigger with inputs
gh workflow run ci-cd.yaml -f environment=production
```

### ArgoCD Operations

#### Deploy Application with ArgoCD
```bash
# Create ArgoCD application
argocd app create production-app \
  --repo https://github.com/your-org/Portfolio-Project.git \
  --path projects/3-kubernetes-cicd/manifests \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --sync-policy automated \
  --auto-prune \
  --self-heal

# Sync application
argocd app sync production-app

# Wait for sync to complete
argocd app wait production-app --health
```

#### Check Application Status
```bash
# List all applications
argocd app list

# Get application details
argocd app get production-app

# Check application health
argocd app get production-app --show-operation

# Check application resources
argocd app resources production-app

# View application logs
argocd app logs production-app
```

#### Sync Application
```bash
# Manual sync
argocd app sync production-app

# Sync specific resource
argocd app sync production-app --resource deployment:production-app

# Sync with prune (delete resources not in git)
argocd app sync production-app --prune

# Force sync (ignore differences)
argocd app sync production-app --force
```

#### Rollback Application
```bash
# View deployment history
argocd app history production-app

# Rollback to previous version
argocd app rollback production-app <history-id>

# Or rollback via git
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
git revert HEAD
git push origin main
# ArgoCD will automatically sync the rollback
```

### Progressive Delivery

#### Canary Deployment
```bash
# Update canary deployment manifest
cat > manifests/canary-rollout.yaml << 'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: production-app
  namespace: production
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 10
      - pause: {duration: 5m}
      - setWeight: 25
      - pause: {duration: 5m}
      - setWeight: 50
      - pause: {duration: 5m}
      - setWeight: 100
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:v2.0.0
EOF

# Apply canary rollout
kubectl apply -f manifests/canary-rollout.yaml

# Monitor canary progress
kubectl argo rollouts get rollout production-app -n production -w

# Promote canary to full deployment
kubectl argo rollouts promote production-app -n production

# Or abort canary if issues detected
kubectl argo rollouts abort production-app -n production
```

#### Blue-Green Deployment
```bash
# Update blue-green deployment manifest
cat > manifests/blue-green-rollout.yaml << 'EOF'
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: production-app
  namespace: production
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: production-app-active
      previewService: production-app-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 300
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: app
        image: myapp:v2.0.0
EOF

# Apply blue-green rollout
kubectl apply -f manifests/blue-green-rollout.yaml

# Test preview (green) environment
kubectl port-forward svc/production-app-preview 8080:80 -n production

# Promote green to blue (make it active)
kubectl argo rollouts promote production-app -n production

# Or abort if issues detected
kubectl argo rollouts abort production-app -n production
```

### Application Management

#### Scale Application
```bash
# Scale via kubectl
kubectl scale deployment production-app --replicas=10 -n production

# Scale via ArgoCD (update git manifest)
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
sed -i 's/replicas: 5/replicas: 10/' manifests/deployment.yaml
git add manifests/deployment.yaml
git commit -m "scale: increase replicas to 10"
git push origin main
# ArgoCD will automatically sync
```

#### Update Application Image
```bash
# Update image via git (GitOps approach)
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
sed -i 's/image: myapp:v1.0.0/image: myapp:v2.0.0/' manifests/deployment.yaml
git add manifests/deployment.yaml
git commit -m "feat: update to v2.0.0"
git push origin main

# Monitor ArgoCD sync
argocd app sync production-app
argocd app wait production-app --health

# Verify new image
kubectl get pods -n production -o jsonpath='{.items[0].spec.containers[0].image}'
```

#### Restart Application
```bash
# Restart via kubectl
kubectl rollout restart deployment production-app -n production

# Or via ArgoCD (update manifest with annotation)
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
kubectl patch deployment production-app -n production \
  -p "{\"spec\":{\"template\":{\"metadata\":{\"annotations\":{\"kubectl.kubernetes.io/restartedAt\":\"$(date +%s)\"}}}}}"
```

---

## Incident Response

### Detection

**Automated Detection:**
- ArgoCD sync status webhooks to Slack
- GitHub Actions failure notifications
- Kubernetes pod health checks
- Prometheus alerts on deployment failures

**Manual Detection:**
```bash
# Check ArgoCD applications
argocd app list | grep -E "OutOfSync|Degraded|Failed"

# Check GitHub Actions
gh run list --workflow=ci-cd.yaml --limit 10

# Check Kubernetes pods
kubectl get pods -n production | grep -v "Running"

# Check recent events
kubectl get events -n production --sort-by='.lastTimestamp' | head -20
```

### Triage

#### Severity Classification

**P0: Complete Outage**
- All pods failing in production
- ArgoCD cannot sync production applications
- GitHub Actions completely broken (no deployments possible)
- Kubernetes API server unreachable

**P1: Degraded Service**
- Some pods failing (reduced capacity)
- ArgoCD out of sync for >10 minutes
- Canary deployment failing health checks
- CI pipeline failing all builds

**P2: Warning State**
- Individual pod restarts
- ArgoCD application degraded
- Slow CI/CD pipeline
- Non-critical test failures

**P3: Informational**
- Successful deployments with warnings
- Minor sync delays
- Flaky tests

### Incident Response Procedures

#### P0: All Pods Failing in Production

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check pod status
kubectl get pods -n production -l app=myapp

# 2. Check recent ArgoCD sync
argocd app get production-app

# 3. Emergency rollback via git
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
git log --oneline -n 5
git revert HEAD --no-edit
git push origin main

# 4. Force ArgoCD sync
argocd app sync production-app --force

# 5. Verify rollback
kubectl rollout status deployment/production-app -n production
```

**Investigation (2-10 minutes):**
```bash
# Check pod logs
kubectl logs -l app=myapp -n production --tail=100 --all-containers

# Check previous pod logs (if crashed)
POD=$(kubectl get pods -n production -l app=myapp -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD --previous -n production

# Check events
kubectl describe pods -l app=myapp -n production | grep -A 10 "Events:"

# Check ArgoCD application events
argocd app events production-app
```

**Mitigation:**
```bash
# If rollback didn't work, manually apply previous manifest
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
git checkout HEAD~1 manifests/
kubectl apply -f manifests/ -n production

# Or delete and recreate
kubectl delete deployment production-app -n production
kubectl apply -f manifests/deployment.yaml -n production

# Verify mitigation
kubectl get pods -n production -l app=myapp
```

#### P0: ArgoCD Cannot Sync Production

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check ArgoCD status
argocd app get production-app

# 2. Check ArgoCD server health
kubectl get pods -n argocd
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server --tail=100

# 3. Check git repository connectivity
git ls-remote https://github.com/your-org/Portfolio-Project.git

# 4. Bypass ArgoCD and deploy manually
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
kubectl apply -f manifests/ -n production
```

**Investigation (5-15 minutes):**
```bash
# Check ArgoCD application controller logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-application-controller --tail=200

# Check ArgoCD repo server logs
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-repo-server --tail=200

# Check if git repository credentials are valid
argocd repo list

# Test git connectivity from ArgoCD pod
kubectl exec -n argocd <argocd-repo-server-pod> -- git ls-remote https://github.com/your-org/Portfolio-Project.git
```

**Resolution:**
```bash
# Restart ArgoCD components
kubectl rollout restart deployment argocd-server -n argocd
kubectl rollout restart deployment argocd-repo-server -n argocd
kubectl rollout restart deployment argocd-application-controller -n argocd

# Update git credentials if expired
argocd repo add https://github.com/your-org/Portfolio-Project.git \
  --username <username> \
  --password <token>

# Refresh application
argocd app get production-app --refresh
argocd app sync production-app
```

#### P1: Canary Deployment Failing

**Investigation:**
```bash
# Check rollout status
kubectl argo rollouts get rollout production-app -n production

# Check canary pod health
kubectl get pods -n production -l app=myapp,rollouts-pod-template-hash=<canary-hash>

# Check canary pod logs
kubectl logs -l app=myapp,rollouts-pod-template-hash=<canary-hash> -n production

# Check metrics for canary
kubectl describe analysisrun <analysis-run-name> -n production
```

**Mitigation:**
```bash
# Abort canary rollout
kubectl argo rollouts abort production-app -n production

# Verify stable version is still serving
kubectl get pods -n production -l app=myapp

# Fix issue and retry
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
# Fix the issue in code
git add .
git commit -m "fix: resolve canary issue"
git push origin main
```

#### P1: GitHub Actions Pipeline Broken

**Investigation:**
```bash
# Check recent workflow runs
gh run list --workflow=ci-cd.yaml --limit 10

# View failed run details
gh run view <run-id>

# Check workflow logs
gh run view <run-id> --log

# Common issues:
# - Credentials expired
# - Test failures
# - Image registry issues
# - Resource limits exceeded
```

**Mitigation:**
```bash
# Update GitHub secrets if credentials expired
gh secret set DOCKER_USERNAME
gh secret set DOCKER_PASSWORD
gh secret set KUBECONFIG

# Retry failed workflow
gh run rerun <run-id>

# Or bypass CI and deploy manually
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
docker build -t myapp:v2.0.0 .
docker push myapp:v2.0.0
kubectl set image deployment/production-app app=myapp:v2.0.0 -n production
```

#### P2: ArgoCD Application Out of Sync

**Investigation:**
```bash
# Check sync status
argocd app get production-app

# Check drift details
argocd app diff production-app

# Check manual changes to Kubernetes
kubectl get deployment production-app -n production -o yaml
```

**Resolution:**
```bash
# Option 1: Sync from git (revert manual changes)
argocd app sync production-app --prune

# Option 2: Update git to match cluster
cd /home/user/Portfolio-Project/projects/3-kubernetes-cicd
kubectl get deployment production-app -n production -o yaml > manifests/deployment.yaml
git add manifests/deployment.yaml
git commit -m "fix: sync manifest with cluster state"
git push origin main

# Option 3: Hard refresh
argocd app sync production-app --force --prune --replace
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# CI/CD Pipeline Incident Report

**Date:** $(date)
**Severity:** P0/P1/P2
**Duration:** XX minutes
**Affected Component:** ArgoCD/GitHub Actions/Application

## Timeline
- HH:MM: Incident detected
- HH:MM: Investigation started
- HH:MM: Root cause identified
- HH:MM: Mitigation applied
- HH:MM: Service restored

## Root Cause
[Description of root cause]

## Action Items
- [ ] Update pipeline configuration
- [ ] Add monitoring for similar issues
- [ ] Update deployment procedures
- [ ] Add automated rollback triggers

EOF

# Update runbook with lessons learned
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### ArgoCD Issues
```bash
# Check application status
argocd app get production-app

# Check application health
argocd app get production-app --show-operation

# View application events
argocd app events production-app

# View sync history
argocd app history production-app

# Check application resources
argocd app resources production-app

# View application diff
argocd app diff production-app

# Check ArgoCD server health
kubectl get pods -n argocd
kubectl logs -n argocd -l app.kubernetes.io/name=argocd-server
```

#### GitHub Actions Issues
```bash
# List recent runs
gh run list --workflow=ci-cd.yaml --limit 20

# View specific run
gh run view <run-id>

# View run logs
gh run view <run-id> --log

# Download run artifacts
gh run download <run-id>

# Rerun failed job
gh run rerun <run-id>

# Cancel running workflow
gh run cancel <run-id>
```

#### Kubernetes Deployment Issues
```bash
# Check deployment status
kubectl get deployment production-app -n production

# Check rollout status
kubectl rollout status deployment/production-app -n production

# View rollout history
kubectl rollout history deployment/production-app -n production

# Check replica sets
kubectl get rs -n production -l app=myapp

# Check pods
kubectl get pods -n production -l app=myapp -o wide

# View pod logs
kubectl logs -l app=myapp -n production --tail=100

# Describe pod
kubectl describe pod <pod-name> -n production
```

### Common Issues & Solutions

#### Issue: ArgoCD Application OutOfSync

**Symptoms:**
```bash
$ argocd app get production-app
Sync Status:     OutOfSync
```

**Diagnosis:**
```bash
# Check what's different
argocd app diff production-app

# Check if manual changes were made
kubectl get deployment production-app -n production -o yaml
```

**Solution:**
```bash
# Sync from git
argocd app sync production-app

# Or update git to match cluster
kubectl get deployment production-app -n production -o yaml > manifests/deployment.yaml
git add manifests/deployment.yaml
git commit -m "fix: sync manifest"
git push origin main
```

---

#### Issue: GitHub Actions Workflow Failing

**Symptoms:**
- Red X on commits in GitHub
- Workflow status shows failed

**Diagnosis:**
```bash
# Check recent runs
gh run list --workflow=ci-cd.yaml --status failure

# View failed run logs
gh run view <run-id> --log
```

**Common Causes:**
- **Test failures** → Fix tests or code
- **Image build failures** → Check Dockerfile
- **Registry push failures** → Update credentials
- **Deployment failures** → Check kubeconfig or permissions

**Solution:**
```bash
# Update secrets if credentials expired
gh secret set DOCKER_USERNAME
gh secret set DOCKER_PASSWORD

# Rerun workflow
gh run rerun <run-id>

# Or fix and push new commit
git add .
git commit -m "fix: resolve CI issue"
git push origin main
```

---

#### Issue: Rollout Stuck

**Symptoms:**
```bash
$ kubectl rollout status deployment/production-app -n production
Waiting for deployment "production-app" rollout to finish: 1 old replicas are pending termination...
```

**Diagnosis:**
```bash
# Check deployment
kubectl describe deployment production-app -n production

# Check pods
kubectl get pods -n production -l app=myapp

# Check events
kubectl get events -n production --sort-by='.lastTimestamp'
```

**Solution:**
```bash
# Force delete stuck pods
kubectl delete pod <stuck-pod> -n production --grace-period=0 --force

# Or rollback deployment
argocd app rollback production-app <history-id>

# Or revert via git
git revert HEAD
git push origin main
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 0 seconds (Git is source of truth)
- **RTO** (Recovery Time Objective): 5 minutes (redeploy from Git)

### Backup Strategy

#### Git Repository Backups
```bash
# Git is the single source of truth
# Ensure git repository is backed up regularly

# Clone backup
git clone --mirror https://github.com/your-org/Portfolio-Project.git backup-repo.git

# Push to backup remote
cd backup-repo.git
git push --mirror https://backup-location/Portfolio-Project.git
```

#### ArgoCD Configuration Backup
```bash
# Export ArgoCD applications
argocd app list -o json > backups/argocd-apps-$(date +%Y%m%d).json

# Export ArgoCD projects
argocd proj list -o json > backups/argocd-projects-$(date +%Y%m%d).json

# Backup ArgoCD settings
kubectl get configmap argocd-cm -n argocd -o yaml > backups/argocd-config-$(date +%Y%m%d).yaml
kubectl get secret argocd-secret -n argocd -o yaml > backups/argocd-secret-$(date +%Y%m%d).yaml
```

### Recovery Procedures

#### Recover from Complete Loss
```bash
# 1. Clone repository
git clone https://github.com/your-org/Portfolio-Project.git
cd Portfolio-Project/projects/3-kubernetes-cicd

# 2. Deploy directly to Kubernetes
kubectl create namespace production
kubectl apply -f manifests/ -n production

# 3. Reinstall ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 4. Recreate ArgoCD application
argocd app create production-app \
  --repo https://github.com/your-org/Portfolio-Project.git \
  --path projects/3-kubernetes-cicd/manifests \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace production \
  --sync-policy automated

# 5. Verify deployment
kubectl get pods -n production
argocd app get production-app
```

#### Recover from Bad Deployment
```bash
# Option 1: Rollback via ArgoCD
argocd app history production-app
argocd app rollback production-app <history-id>

# Option 2: Rollback via git
git revert HEAD
git push origin main
# ArgoCD will auto-sync

# Option 3: Rollback via kubectl
kubectl rollout undo deployment/production-app -n production
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check ArgoCD application health
argocd app list

# Check recent deployments
argocd app history production-app

# Check GitHub Actions
gh run list --workflow=ci-cd.yaml --limit 10

# Check pod health
kubectl get pods -n production
```

#### Weekly Tasks
```bash
# Review failed workflows
gh run list --workflow=ci-cd.yaml --status failure --limit 20

# Review ArgoCD sync history
argocd app history production-app

# Check for drift
argocd app diff production-app

# Review resource usage
kubectl top nodes
kubectl top pods -n production
```

#### Monthly Tasks
```bash
# Update ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Review and update GitHub Actions workflows
cd /home/user/Portfolio-Project
# Review .github/workflows/ci-cd.yaml

# Archive old deployment logs
mkdir -p archives/$(date +%Y-%m)
mv logs/*.log archives/$(date +%Y-%m)/ 2>/dev/null || true

# Test disaster recovery procedures
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Check ArgoCD application
argocd app get production-app

# Sync application
argocd app sync production-app

# Rollback deployment
argocd app rollback production-app <history-id>

# Check GitHub Actions
gh run list --workflow=ci-cd.yaml

# Trigger workflow
gh workflow run ci-cd.yaml

# Check pods
kubectl get pods -n production -l app=myapp

# Check deployment
kubectl get deployment production-app -n production

# View logs
kubectl logs -l app=myapp -n production --tail=100
```

### Emergency Response

```bash
# P0: Emergency rollback
git revert HEAD && git push origin main
argocd app sync production-app --force

# P0: Manual deployment
kubectl apply -f manifests/ -n production

# P1: Abort canary
kubectl argo rollouts abort production-app -n production

# P1: Restart ArgoCD
kubectl rollout restart deployment -n argocd

# Check application health
argocd app get production-app
kubectl get pods -n production
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

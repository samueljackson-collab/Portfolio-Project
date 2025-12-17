# Runbook — P18 (Kubernetes CI/CD Pipeline)

## Overview

Production operations runbook for the P18 Kubernetes CI/CD platform. This runbook covers cluster operations, deployment procedures, incident response, and troubleshooting for the kind-based Kubernetes environment with GitHub Actions CI/CD.

**System Components:**
- kind (Kubernetes in Docker) cluster
- GitHub Actions CI/CD pipeline
- Kubernetes deployment with rolling updates
- LoadBalancer service with health checks
- Automated testing and validation

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Deployment success rate** | 99% | kubectl rollout status success responses |
| **Pod availability** | 99.5% | ≥3 pods in Ready state |
| **Deployment time** | < 5 minutes | Time from git push → all pods Running |
| **Rollback time (RTO)** | < 2 minutes | Time from rollback initiate → pods stable |
| **Health check success rate** | 99.9% | /health and /ready endpoint responses |
| **CI pipeline success rate** | 95% | GitHub Actions workflow completion rate |

---

## Dashboards & Alerts

### Dashboards

#### Cluster Overview Dashboard
```bash
# Quick cluster health check
make test-cluster

# Expected output:
# Kubernetes control plane is running at https://127.0.0.1:xxxxx
# NAME                 STATUS   ROLES           AGE   VERSION
# dev-control-plane   Ready    control-plane   1d    v1.27.0
```

#### Application Health Dashboard
```bash
# Check deployment status
kubectl get deployment app -n default -o wide

# Check pod status
kubectl get pods -l app=myapp -n default

# Check service endpoints
kubectl get svc app-service -n default
kubectl get endpoints app-service -n default
```

#### Resource Usage Dashboard
```bash
# Node resource usage
kubectl top nodes

# Pod resource usage
kubectl top pods -n default -l app=myapp

# Check resource requests vs limits
kubectl describe deployment app -n default | grep -A 5 "Limits\|Requests"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | < 1 pods running | Immediate | Emergency rollback |
| **P1** | < 2 pods running | 5 minutes | Investigate and scale |
| **P1** | GitHub Actions failing | 15 minutes | Check pipeline logs |
| **P2** | Pod restart rate > 3/hour | 30 minutes | Check logs, investigate crash |
| **P2** | Health check failing | 30 minutes | Investigate application health |
| **P3** | High memory usage (>80%) | 1 hour | Consider resource adjustment |

#### Alert Queries

```bash
# Check pod availability
RUNNING_PODS=$(kubectl get pods -l app=myapp -n default --field-selector=status.phase=Running --no-headers | wc -l)
if [ $RUNNING_PODS -lt 2 ]; then
  echo "ALERT: Only $RUNNING_PODS pods running (expected ≥3)"
fi

# Check recent pod restarts
kubectl get pods -l app=myapp -n default -o json | \
  jq '.items[] | select(.status.containerStatuses[0].restartCount > 3) | .metadata.name'

# Check failed deployments
kubectl get events -n default --field-selector type=Warning,involvedObject.kind=Deployment
```

---

## Standard Operations

### Cluster Management

#### Create Cluster
```bash
# Create new kind cluster
make cluster-create CLUSTER_NAME=dev

# Verify cluster is ready
make test-cluster

# Check cluster info
kubectl cluster-info --context kind-dev
kubectl get nodes
kubectl get namespaces
```

#### Delete Cluster
```bash
# ⚠️ CAUTION: This destroys the cluster and all data
make cluster-delete CLUSTER_NAME=dev

# Verify deletion
kind get clusters
```

#### Cluster Health Check
```bash
# Quick health check (run daily)
kubectl get nodes
kubectl get pods -A
kubectl top nodes

# Detailed health check
kubectl get componentstatuses
kubectl get events --sort-by='.lastTimestamp' | head -20

# Check cluster capacity
kubectl describe nodes | grep -A 5 "Allocated resources"
```

### Application Deployment

#### Standard Deployment Process
```bash
# 1. Verify current state
kubectl get deployment app -n default
kubectl get pods -l app=myapp -n default

# 2. Deploy application
make deploy NAMESPACE=default

# 3. Watch rollout progress
kubectl rollout status deployment/app -n default

# 4. Verify deployment success
kubectl get deployment app -n default
kubectl get pods -l app=myapp -n default
make logs

# 5. Test application endpoint (if service is accessible)
kubectl port-forward svc/app-service 8080:80 -n default &
curl -f http://localhost:8080/health || echo "Health check failed"
pkill -f "port-forward"
```

#### Update Deployment (Image Change)
```bash
# Update deployment image
kubectl set image deployment/app app=nginx:1.24 -n default

# Watch rollout (RollingUpdate strategy)
kubectl rollout status deployment/app -n default

# Verify new image is running
kubectl get pods -l app=myapp -n default -o jsonpath='{.items[0].spec.containers[0].image}'
```

#### Scale Deployment
```bash
# Scale up
kubectl scale deployment app --replicas=5 -n default

# Scale down
kubectl scale deployment app --replicas=2 -n default

# Verify scaling
kubectl get deployment app -n default
watch kubectl get pods -l app=myapp -n default
```

#### Rollback Deployment
```bash
# Quick rollback (last known good)
make rollout-undo NAMESPACE=default

# Verify rollback
kubectl rollout status deployment/app -n default

# Rollback to specific revision
kubectl rollout history deployment/app -n default
kubectl rollout undo deployment/app --to-revision=2 -n default

# Verify
kubectl get pods -l app=myapp -n default
```

#### Restart Deployment (Zero-Downtime)
```bash
# Restart all pods with rolling update
make rollout-restart NAMESPACE=default

# Monitor restart
kubectl rollout status deployment/app -n default
kubectl get pods -l app=myapp -n default -w
```

### CI/CD Pipeline Operations

#### Trigger CI/CD Pipeline
```bash
# Pipelines trigger automatically on git push
git add .
git commit -m "feat: update application"
git push origin main

# Monitor pipeline
# Go to: https://github.com/your-org/Portfolio-Project/actions
```

#### Manual Deployment (Bypass CI/CD)
```bash
# ⚠️ Use only for emergencies
# Deploy directly from local manifests
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml
make deploy NAMESPACE=default
```

---

## Incident Response

### Detection

**Automated Detection:**
- GitHub Actions failure notifications
- Pod restart alerts
- Health check monitoring

**Manual Detection:**
```bash
# Check recent events
kubectl get events -n default --sort-by='.lastTimestamp' | head -20

# Check pod status
kubectl get pods -l app=myapp -n default

# Check deployment status
kubectl get deployment app -n default

# Check service health
kubectl describe svc app-service -n default
```

### Triage

#### Severity Classification

### P0: Complete Outage
- Zero pods running
- Deployment rollout failed completely
- Cluster unreachable

### P1: Degraded Service
- < 2 pods running (reduced capacity)
- Repeated pod crashes
- Service endpoints unavailable
- CI/CD pipeline completely broken

### P2: Warning State
- Pods restarting frequently
- Health checks intermittently failing
- High resource usage
- Individual CI/CD job failures

### P3: Informational
- Single pod restart
- Temporary health check blip
- Resource usage approaching limits

### Incident Response Procedures

#### P0: Zero Pods Running

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check pod status
kubectl get pods -l app=myapp -n default

# 2. Check recent events
kubectl get events -n default --field-selector involvedObject.name=app --sort-by='.lastTimestamp'

# 3. Check deployment
kubectl describe deployment app -n default

# 4. Emergency rollback if recent deployment
make rollout-undo NAMESPACE=default
```

**Investigation (2-10 minutes):**
```bash
# Check pod logs (if pods exist but failing)
kubectl logs -l app=myapp -n default --tail=100 --all-containers=true

# Check previous pod logs (if crashed)
FAILED_POD=$(kubectl get pods -l app=myapp -n default -o jsonpath='{.items[0].metadata.name}')
kubectl logs $FAILED_POD --previous -n default

# Check deployment configuration
kubectl get deployment app -n default -o yaml

# Check image pull status
kubectl describe pods -l app=myapp -n default | grep -A 5 "Image"
```

**Mitigation:**
```bash
# Option 1: Rollback to last known good
make rollout-undo NAMESPACE=default

# Option 2: Scale up to force new pods
kubectl scale deployment app --replicas=0 -n default
sleep 5
kubectl scale deployment app --replicas=3 -n default

# Option 3: Delete and recreate
kubectl delete deployment app -n default
make deploy NAMESPACE=default

# Verify mitigation
kubectl rollout status deployment/app -n default
kubectl get pods -l app=myapp -n default
```

#### P1: Pods Crash Looping

**Investigation:**
```bash
# Identify crashing pods
kubectl get pods -l app=myapp -n default | grep -E "CrashLoopBackOff|Error"

# Get crash logs
POD=$(kubectl get pods -l app=myapp -n default -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD --previous -n default

# Check events
kubectl describe pod $POD -n default | grep -A 10 "Events:"

# Check resource constraints
kubectl describe pod $POD -n default | grep -A 5 "Limits\|Requests\|State"
```

**Common Causes & Fixes:**

**Image Pull Error:**
```bash
# Verify image exists
IMAGE=$(kubectl get deployment app -n default -o jsonpath='{.spec.template.spec.containers[0].image}')
echo "Image: $IMAGE"

# Fix: Update to correct image
kubectl set image deployment/app app=nginx:1.24 -n default
```

**OOMKilled (Out of Memory):**
```bash
# Check memory usage
kubectl top pods -l app=myapp -n default

# Fix: Increase memory limits
kubectl patch deployment app -n default -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","resources":{"limits":{"memory":"256Mi"}}}]}}}}'
```

**Failed Health Checks:**
```bash
# Test health endpoints manually
kubectl port-forward svc/app-service 8080:80 -n default &
curl -v http://localhost:8080/health
curl -v http://localhost:8080/ready
pkill -f "port-forward"

# Fix: Adjust probe timings or fix application
kubectl patch deployment app -n default -p '{"spec":{"template":{"spec":{"containers":[{"name":"app","livenessProbe":{"initialDelaySeconds":60}}]}}}}'
```

#### P1: GitHub Actions Pipeline Failure

**Investigation:**
```bash
# View workflow run details
# Navigate to: https://github.com/your-org/Portfolio-Project/actions

# Check workflow logs for errors
# Common issues:
# - kubectl authentication failure
# - Image registry authentication
# - Test failures
# - Resource limits in CI environment
```

**Manual Deployment Bypass:**
```bash
# If CI/CD is broken, deploy manually
git pull origin main
make deploy NAMESPACE=default

# Document incident and fix pipeline
echo "Manual deployment at $(date)" >> INCIDENT.md
```

#### P2: High Resource Usage

**Investigation:**
```bash
# Check resource usage
kubectl top pods -l app=myapp -n default
kubectl top nodes

# Check resource requests vs actual usage
kubectl describe deployment app -n default | grep -A 10 "Requests\|Limits"

# Check node capacity
kubectl describe nodes | grep -A 10 "Allocated resources"
```

**Mitigation:**
```bash
# Temporary: Scale down if overloaded
kubectl scale deployment app --replicas=2 -n default

# Permanent: Adjust resource limits
kubectl patch deployment app -n default -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "app",
          "resources": {
            "requests": {"memory": "128Mi", "cpu": "200m"},
            "limits": {"memory": "256Mi", "cpu": "400m"}
          }
        }]
      }
    }
  }
}'
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 15 minutes
**Affected Component:** Application deployment

## Timeline
- 14:00: Deployment triggered
- 14:05: Pods failed to start (ImagePullBackOff)
- 14:10: Identified incorrect image tag
- 14:12: Rolled back to previous version
- 14:15: Service restored

## Root Cause
Incorrect image tag pushed to deployment manifest

## Action Items
- [ ] Add image validation to CI pipeline
- [ ] Implement pre-deployment smoke tests
- [ ] Update deployment checklist

EOF

# Update runbook if needed
# Document any new procedures discovered during incident
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Pod Issues
```bash
# Get pod status
kubectl get pods -l app=myapp -n default -o wide

# Describe pod (shows events)
kubectl describe pod <pod-name> -n default

# Get logs from running pod
kubectl logs <pod-name> -n default

# Get logs from crashed pod
kubectl logs <pod-name> --previous -n default

# Get logs from all pods
kubectl logs -l app=myapp -n default --all-containers=true --tail=100

# Follow logs
kubectl logs -l app=myapp -n default -f

# Execute command in pod
kubectl exec -it <pod-name> -n default -- /bin/sh
```

#### Deployment Issues
```bash
# Get deployment status
kubectl get deployment app -n default -o wide

# Describe deployment
kubectl describe deployment app -n default

# Check rollout status
kubectl rollout status deployment/app -n default

# View rollout history
kubectl rollout history deployment/app -n default

# Check replica set
kubectl get rs -l app=myapp -n default
kubectl describe rs <replicaset-name> -n default
```

#### Service & Networking Issues
```bash
# Check service
kubectl get svc app-service -n default
kubectl describe svc app-service -n default

# Check endpoints (should match pod IPs)
kubectl get endpoints app-service -n default

# Test service from within cluster
kubectl run debug --rm -it --image=busybox --restart=Never -- sh
# Inside debug pod:
wget -O- http://app-service.default.svc.cluster.local

# Port forward for local testing
kubectl port-forward svc/app-service 8080:80 -n default
# Then: curl http://localhost:8080
```

#### Cluster Issues
```bash
# Check cluster health
kubectl cluster-info
kubectl get nodes -o wide

# Check cluster events
kubectl get events -A --sort-by='.lastTimestamp' | head -30

# Check system pods
kubectl get pods -n kube-system

# Check resource usage across cluster
kubectl top nodes
kubectl top pods -A --sort-by=memory
```

### Common Issues & Solutions

#### Issue: "ImagePullBackOff"

**Symptoms:**
```bash
$ kubectl get pods -l app=myapp -n default
NAME                   READY   STATUS             RESTARTS   AGE
app-5d4b8c7f4f-abc12   0/1     ImagePullBackOff   0          2m
```

**Diagnosis:**
```bash
kubectl describe pod app-5d4b8c7f4f-abc12 -n default | grep -A 5 "Events:"
# Look for: Failed to pull image "nginx:nonexistent": image not found
```

**Solution:**
```bash
# Update to correct image
kubectl set image deployment/app app=nginx:1.24 -n default
```

---

#### Issue: "CrashLoopBackOff"

**Symptoms:**
```bash
$ kubectl get pods -l app=myapp -n default
NAME                   READY   STATUS             RESTARTS   AGE
app-5d4b8c7f4f-abc12   0/1     CrashLoopBackOff   5          5m
```

**Diagnosis:**
```bash
# Check crash logs
kubectl logs app-5d4b8c7f4f-abc12 --previous -n default

# Check events
kubectl describe pod app-5d4b8c7f4f-abc12 -n default
```

**Common Causes:**
- Application configuration error → Check logs
- Missing environment variables → Check deployment manifest
- Failed health checks → Adjust probe timings
- OOMKilled → Increase memory limits

---

#### Issue: Pods not receiving traffic

**Symptoms:**
- Pods are Running
- Service endpoints empty
- Application unreachable

**Diagnosis:**
```bash
# Check service and endpoints
kubectl get svc app-service -n default
kubectl get endpoints app-service -n default

# Check pod labels match service selector
kubectl get pods -l app=myapp -n default --show-labels
kubectl get svc app-service -n default -o jsonpath='{.spec.selector}'
```

**Solution:**
```bash
# If labels don't match, update deployment
kubectl patch deployment app -n default -p '{"spec":{"template":{"metadata":{"labels":{"app":"myapp"}}}}}'
```

---

#### Issue: Deployment stuck in rollout

**Symptoms:**
```bash
$ kubectl rollout status deployment/app -n default
Waiting for deployment "app" rollout to finish: 1 old replicas are pending termination...
```

**Diagnosis:**
```bash
# Check deployment status
kubectl describe deployment app -n default

# Check pods
kubectl get pods -l app=myapp -n default

# Check events
kubectl get events -n default --field-selector involvedObject.name=app
```

**Solution:**
```bash
# Force delete stuck pods
kubectl delete pod <stuck-pod-name> -n default --grace-period=0 --force

# Or rollback deployment
make rollout-undo NAMESPACE=default
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 15 minutes (Git commit history)
- **RTO** (Recovery Time Objective): 5 minutes (Cluster recreation + deployment)

### Backup Strategy

**Configuration Backups:**
```bash
# Backup all manifests to Git
git add manifests/
git commit -m "backup: kubernetes manifests $(date +%Y-%m-%d)"
git push

# Export running configuration
kubectl get deployment app -n default -o yaml > backup/deployment-$(date +%Y%m%d).yaml
kubectl get svc app-service -n default -o yaml > backup/service-$(date +%Y%m%d).yaml

# Backup entire namespace
kubectl get all -n default -o yaml > backup/namespace-backup-$(date +%Y%m%d).yaml
```

**Cluster State Backup:**
```bash
# Export cluster configuration
kind export kubeconfig --name dev --kubeconfig backup/kubeconfig-$(date +%Y%m%d).yaml

# Document cluster setup
kind get nodes --name dev > backup/cluster-nodes-$(date +%Y%m%d).txt
kubectl version > backup/cluster-version-$(date +%Y%m%d).txt
```

### Disaster Recovery Procedures

#### Complete Cluster Loss

**Recovery Steps (5-10 minutes):**
```bash
# 1. Recreate cluster
make cluster-create CLUSTER_NAME=dev

# 2. Verify cluster is ready
make test-cluster

# 3. Redeploy application
make deploy NAMESPACE=default

# 4. Verify deployment
kubectl rollout status deployment/app -n default
kubectl get pods -l app=myapp -n default

# 5. Test application
make logs
```

#### Application Recovery (No Cluster Loss)

**Recovery Steps (2-3 minutes):**
```bash
# 1. Delete failed deployment
kubectl delete deployment app -n default

# 2. Redeploy from manifests
make deploy NAMESPACE=default

# 3. Verify
kubectl rollout status deployment/app -n default
```

#### Rollback to Known Good State

```bash
# Option 1: Rollback deployment
make rollout-undo NAMESPACE=default

# Option 2: Deploy from Git tag
git checkout v1.0.0
make deploy NAMESPACE=default
git checkout main

# Option 3: Apply saved backup
kubectl apply -f backup/deployment-20250101.yaml
kubectl apply -f backup/service-20250101.yaml
```

### DR Drill Procedure

**Monthly DR Drill (30 minutes):**
```bash
# 1. Document current state
kubectl get all -n default > dr-drill-before.txt

# 2. Announce drill
echo "DR drill starting at $(date)" | tee dr-drill-log.txt

# 3. Simulate disaster: Delete cluster
make cluster-delete CLUSTER_NAME=dev

# 4. Start recovery timer
START_TIME=$(date +%s)

# 5. Execute recovery
make cluster-create CLUSTER_NAME=dev
make test-cluster
make deploy NAMESPACE=default

# 6. Verify recovery
kubectl rollout status deployment/app -n default
kubectl get pods -l app=myapp -n default

# 7. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "Recovery completed in $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt

# 8. Document results
echo "DR drill completed at $(date)" | tee -a dr-drill-log.txt
echo "Target RTO: 300 seconds (5 minutes)" | tee -a dr-drill-log.txt
echo "Actual recovery time: $RECOVERY_TIME seconds" | tee -a dr-drill-log.txt

# 9. Update runbook with lessons learned
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Morning health check
make test-cluster
kubectl get pods -l app=myapp -n default
kubectl top pods -n default

# Check for failed jobs or pods
kubectl get pods -A | grep -v "Running\|Completed"

# Check recent events
kubectl get events -n default --sort-by='.lastTimestamp' | head -10
```

#### Weekly Tasks
```bash
# Review pod restarts
kubectl get pods -l app=myapp -n default -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'

# Review resource usage trends
kubectl top pods -n default -l app=myapp
kubectl top nodes

# Update documentation
git pull
# Review and update this runbook if procedures changed
```

#### Monthly Tasks
```bash
# Update cluster (if new kind version available)
# Backup current state first!
kind delete cluster --name dev
kind create cluster --name dev
make deploy

# Review and test disaster recovery procedures
# Follow DR Drill Procedure above

# Archive old incident reports
mkdir -p incidents/archive/$(date +%Y-%m)
mv incidents/*.md incidents/archive/$(date +%Y-%m)/ 2>/dev/null || true
```

### Upgrade Procedures

#### Update Application Image
```bash
# 1. Test new image locally first
docker pull nginx:1.25
docker run -d -p 8080:80 nginx:1.25
curl http://localhost:8080

# 2. Update deployment
kubectl set image deployment/app app=nginx:1.25 -n default

# 3. Monitor rollout
kubectl rollout status deployment/app -n default

# 4. Verify new version
kubectl get pods -l app=myapp -n default -o jsonpath='{.items[0].spec.containers[0].image}'

# 5. Test application
make logs

# 6. Rollback if issues
make rollout-undo NAMESPACE=default
```

#### Update Kubernetes Manifests
```bash
# 1. Make changes in Git
git checkout -b update-manifests
# Edit manifests/deployment.yaml or manifests/service.yaml
git add manifests/
git commit -m "feat: update kubernetes manifests"

# 2. Test in local cluster
make deploy NAMESPACE=default

# 3. Verify changes
kubectl get deployment app -n default -o yaml
kubectl get svc app-service -n default -o yaml

# 4. If successful, merge to main
git push origin update-manifests
# Create PR and merge

# 5. CI/CD will auto-deploy (or manual deploy)
git checkout main
git pull
make deploy NAMESPACE=default
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] Code reviewed and approved
- [ ] All tests passing locally (`make test`)
- [ ] Manifests validated (`kubectl apply --dry-run=client -f manifests/`)
- [ ] Deployment tested in local kind cluster
- [ ] Rollback plan ready
- [ ] Incident channel (#incidents) notified

### Post-Deployment Checklist
- [ ] Deployment completed successfully
- [ ] All pods in Running state
- [ ] Health checks passing
- [ ] Logs show no errors
- [ ] Resource usage normal
- [ ] Monitor for 15 minutes

### Standard Change Window
- **Time:** Tuesday/Thursday, 2:00 PM - 4:00 PM ET
- **Approval:** Required for production changes
- **Blackout:** Avoid Friday deployments, holidays, end of quarter

### Escalation Path

| Level | Role | Response Time | Contact |
|-------|------|---------------|---------|
| L1 | On-call engineer | 15 minutes | Slack #incidents |
| L2 | Team lead | 30 minutes | Direct message |
| L3 | Engineering manager | 1 hour | Phone call |

---

## References

### Internal Documentation
- [P18 Project README](./README.md)
- [Kubernetes Manifests](./manifests/)
- [Test Suite](./tests/)
- [Makefile](./Makefile)

### External Resources
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kind Documentation](https://kind.sigs.k8s.io/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Emergency Contacts
- **On-call rotation:** See internal wiki
- **Slack channels:** #incidents, #platform-engineering
- **Escalation:** Follow escalation path above

---

## Quick Reference Card

### Most Common Operations
```bash
# Check cluster health
make test-cluster

# Deploy application
make deploy

# Check pod status
kubectl get pods -l app=myapp -n default

# View logs
make logs

# Rollback deployment
make rollout-undo

# Restart pods
make rollout-restart

# Scale deployment
kubectl scale deployment app --replicas=5 -n default

# Emergency: Delete and redeploy
kubectl delete deployment app -n default && make deploy
```

### Emergency Response
```bash
# P0: Zero pods running
make rollout-undo NAMESPACE=default
kubectl get pods -l app=myapp -n default

# P1: Pods crashing
kubectl logs -l app=myapp -n default --previous
make rollout-undo NAMESPACE=default

# P2: Cluster issues
make cluster-delete CLUSTER_NAME=dev
make cluster-create CLUSTER_NAME=dev
make deploy NAMESPACE=default
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

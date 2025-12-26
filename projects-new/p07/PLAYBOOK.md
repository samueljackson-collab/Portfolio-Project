# Playbook: Promoting a Model to Production

## Purpose & Scope
Safely promote a trained ML model from MLflow staging to production deployment on KFServing with canary testing and monitoring.

## Preconditions
- [ ] Model registered in MLflow registry with "Staging" tag
- [ ] All pipeline tests passed (data quality, training, evaluation gates)
- [ ] Approval from data science lead and compliance officer
- [ ] Monitoring dashboards and alerts configured for new model
- [ ] Rollback plan documented with previous model version
- [ ] KFServing namespace and service account ready

## Execution Steps

### 1. Verify MLflow Registry Entry
- [ ] Log into MLflow UI (http://mlflow-server:5000)
- [ ] Navigate to Models → demand-forecast
- [ ] Confirm model version in Staging with required tags (git_sha, dataset_version, approver)
- [ ] Download model artifact and verify signature/checksum

### 2. Deploy to Staging Environment
- [ ] Update `serving/inferenceservice.yaml` with model version from MLflow
- [ ] Apply to staging namespace:
  ```bash
  kubectl apply -f serving/inferenceservice.yaml -n mlops-staging
  ```
- [ ] Wait for Ready status:
  ```bash
  kubectl wait --for=condition=Ready inferenceservice/demand-forecast -n mlops-staging --timeout=5m
  ```

### 3. Run Smoke Tests
- [ ] Send test requests to staging endpoint:
  ```bash
  curl -X POST http://demand-forecast.mlops-staging/v1/models/demand-forecast:predict \
    -H "Content-Type: application/json" \
    -d '{"instances": [{"store_id": 42, "date": "2025-01-15", "promo": 1}]}'
  ```
- [ ] Verify response structure and latency < 200ms
- [ ] Run evaluation harness against known ground truth dataset
- [ ] Confirm accuracy metrics match or exceed MLflow logged values

### 4. Enable Canary Deployment (10% Traffic)
- [ ] Update `canaryTrafficPercent: 10` in production InferenceService
- [ ] Apply to production namespace:
  ```bash
  kubectl apply -f serving/inferenceservice-prod.yaml -n mlops
  ```
- [ ] Verify Istio VirtualService routes 10% traffic to new version:
  ```bash
  kubectl get virtualservice demand-forecast -n mlops -o yaml
  ```

### 5. Monitor Canary Window (30 minutes)
- [ ] Open Grafana dashboard for model serving metrics
- [ ] Compare canary vs production metrics:
  - Latency (p50/p95/p99)
  - Error rate
  - Prediction distribution
  - Feature drift scores
- [ ] Check logs for errors or warnings:
  ```bash
  kubectl logs -l serving.kserve.io/inferenceservice=demand-forecast -n mlops --tail=100
  ```
- [ ] Validate business metrics (if available in near-real-time)

### 6. Decision Point
- **If canary metrics are acceptable (within 5% of baseline):**
  - [ ] Proceed to full rollout (step 7)
- **If canary shows degradation:**
  - [ ] Execute rollback (section below)
  - [ ] Capture logs and metrics for post-mortem
  - [ ] Create incident ticket and notify team

### 7. Full Rollout to Production
- [ ] Update `canaryTrafficPercent: 0` to send 100% traffic to new version
- [ ] Apply configuration:
  ```bash
  kubectl apply -f serving/inferenceservice-prod.yaml -n mlops
  ```
- [ ] Promote model in MLflow from Staging to Production:
  ```bash
  mlflow models transition --name demand-forecast --version <VERSION> --stage Production
  ```
- [ ] Update model version in documentation and release notes

### 8. Post-Deployment Monitoring (24 hours)
- [ ] Monitor dashboards continuously for first hour
- [ ] Set alerts for:
  - Error rate > 1%
  - Latency p95 > 300ms
  - Drift score > threshold
- [ ] Daily review for first week
- [ ] Capture baseline metrics for next release comparison

## Verification Checklist
- [ ] Canary error rate ≤ production baseline + 0.5%
- [ ] Canary latency p95 ≤ production p95 + 50ms
- [ ] No increase in drift alerts during canary window
- [ ] Business KPIs (forecast accuracy) stable or improved
- [ ] MLflow registry shows "Production" tag on correct version

## Rollback Procedure
- [ ] Revert `canaryTrafficPercent` to 0 (full traffic to old version)
- [ ] Apply previous InferenceService configuration:
  ```bash
  kubectl apply -f serving/inferenceservice-prod-v<PREVIOUS>.yaml -n mlops
  ```
- [ ] Verify old version serving 100% traffic
- [ ] Demote failed model in MLflow registry:
  ```bash
  mlflow models transition --name demand-forecast --version <FAILED_VERSION> --stage Archived
  ```
- [ ] Announce rollback in Slack/email with incident link
- [ ] Schedule post-mortem within 24 hours

## Documentation & Communication
- **Links:**
  - Pipeline run: [Kubeflow UI link]
  - MLflow experiment: [MLflow link]
  - Grafana dashboard: [Dashboard link]
  - GitHub PR: [PR link]
  - Approval ticket: [Jira/Linear link]
- **Notifications:**
  - [ ] Slack #ml-ops channel: deployment start/complete/rollback
  - [ ] Email stakeholders: release summary with metrics
- **Records:**
  - [ ] Update CHANGELOG.md with version, date, changes
  - [ ] Log deployment in audit trail (compliance requirement)

## Outcome
- [ ] Deployment successful / rolled back
- [ ] Metrics captured and compared to baseline
- [ ] Lessons learned documented (if rollback occurred)
- [ ] Next model promotion date scheduled (if applicable)

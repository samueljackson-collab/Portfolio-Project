# Incident Runbooks (MLOps)

## 1) Pipeline Component Failure
**Symptoms:** Kubeflow pipeline stuck or failed; one or more components show error status.

**Immediate Containment:**
- [ ] Check if failure is isolated to one pipeline run or affecting all runs
- [ ] Pause scheduled pipeline triggers to prevent cascade failures
- [ ] Capture failed pod logs before they're garbage collected

**Diagnostics:**
```bash
# Get pipeline run details
kubectl get pipelineruns -n kubeflow
kubectl describe pipelinerun <run-id> -n kubeflow

# Check component pod logs
kubectl logs -n kubeflow <component-pod-name>

# Verify artifacts and secrets
kubectl get secrets -n kubeflow | grep mlflow
aws s3 ls s3://mlflow-artifacts/ # or equivalent
```

**Common causes:**
- Missing/expired secrets (AWS credentials, DB password)
- Artifact storage unreachable (S3/GCS permissions)
- Resource limits (OOM, GPU unavailable)
- Incompatible component versions or missing dependencies

**Permanent Fixes:**
- Rotate/update secrets; verify IAM/service account permissions
- Increase component resource requests/limits
- Pin component image versions; add dependency checks to CI
- Add retry logic with exponential backoff for transient failures

**Validation/Closure:**
- [ ] Rerun pipeline with same inputs; verify success
- [ ] Check next scheduled run completes without issues
- [ ] Update runbook if new failure mode discovered

---

## 2) Serving Latency or Error Spike
**Symptoms:** KFServing inference latency p95 > SLA (200ms) or error rate > 1%; alerts firing.

**Immediate Containment:**
- [ ] Check if spike correlates with recent deployment; rollback if yes
- [ ] Scale replicas manually if autoscaler lagging:
  ```bash
  kubectl scale deploy <predictor-deployment> -n mlops --replicas=5
  ```
- [ ] Enable rate limiting if traffic spike detected

**Diagnostics:**
```bash
# Check predictor pod status and logs
kubectl get pods -n mlops -l serving.kserve.io/inferenceservice=demand-forecast
kubectl logs -n mlops <predictor-pod> --tail=200

# Check HPA status
kubectl get hpa -n mlops
kubectl describe hpa demand-forecast-predictor -n mlops

# Verify Feast feature store latency
kubectl logs -n mlops <feast-online-pod>

# Check Istio metrics for traffic distribution
kubectl exec -n istio-system <istio-pilot-pod> -- pilot-discovery request GET /debug/endpointz
```

**Common causes:**
- Cold start after scale-to-zero (first request slow)
- Feature store (Feast online) latency spike
- Model load time increased (larger model, insufficient resources)
- Downstream dependency (DB, external API) timeout
- Traffic burst exceeding replica capacity

**Permanent Fixes:**
- Set `minReplicas: 1` to avoid cold starts for critical models
- Optimize feature retrieval (caching, batch fetching)
- Increase predictor resources or switch to GPU instances
- Add circuit breakers for downstream dependencies
- Tune HPA metrics and thresholds

**Validation/Closure:**
- [ ] p95 latency < 200ms for 30 consecutive minutes
- [ ] Error rate < 0.5% sustained
- [ ] Autoscaler scaling behavior observed and stable
- [ ] Load test to validate capacity headroom

---

## 3) Drift Detector False Positives/Negatives
**Symptoms:** Drift alerts firing frequently for non-drifted data, or failing to detect known drift.

**Immediate Containment:**
- [ ] Review recent alerts and compare feature distributions manually
- [ ] Temporarily adjust thresholds to reduce noise (document change)
- [ ] Disable automatic retraining trigger if false positives causing churn

**Diagnostics:**
```bash
# Check drift detector logs
kubectl logs -n mlops <drift-detector-pod> --tail=100

# Query prediction logs for feature distribution stats
aws s3 sync s3://prediction-logs/$(date +%Y-%m-%d) ./logs/
python scripts/analyze_drift.py --reference-data ./reference.parquet --current-data ./logs/
```

**Common causes:**
- Reference dataset not representative of production distribution
- Threshold too sensitive (e.g., KS test p-value < 0.05 too strict)
- Seasonal/time-based patterns misinterpreted as drift
- Feature encoding changes (categorical mapping, scaling)

**Permanent Fixes:**
- Update reference dataset with recent production data (sliding window)
- Tune drift thresholds based on historical false positive rate
- Add seasonal decomposition or segmented drift detection
- Version feature transformations and validate consistency
- Implement human-in-the-loop review for drift alerts before retraining

**Validation/Closure:**
- [ ] Run drift detector on historical data with known drift/non-drift periods
- [ ] Validate alert precision/recall meet targets (e.g., >80% precision)
- [ ] Document threshold tuning and add to ADR

---

## 4) Feature Store Outage or Staleness
**Symptoms:** Serving errors due to missing features; feature freshness lags behind SLA.

**Immediate Containment:**
- [ ] Switch to fallback/cached features if available
- [ ] Scale Feast online store (Redis/DynamoDB) if capacity issue
- [ ] Pause feature materialization jobs if causing load

**Diagnostics:**
```bash
# Check Feast online store health
kubectl get pods -n mlops -l app=feast-online
kubectl logs -n mlops <feast-online-pod>

# Verify materialization job status
kubectl get jobs -n mlops | grep materialize
kubectl logs -n mlops <materialize-job-pod>

# Check feature freshness
feast feature-views list
feast feature-views describe <feature-view>
```

**Common causes:**
- Materialization job failed (resource limits, data source unavailable)
- Online store (Redis/DynamoDB) throttled or out of capacity
- Network partition between online store and serving pods
- Schema mismatch between offline and online stores

**Permanent Fixes:**
- Add retries and alerting to materialization jobs
- Scale online store capacity; enable auto-scaling
- Implement feature caching in predictor for resilience
- Validate schema compatibility in CI before deployment

**Validation/Closure:**
- [ ] Feature freshness within SLA (e.g., < 15 minutes lag)
- [ ] Serving requests succeed with correct feature values
- [ ] Materialization job runs successfully for 24 hours

---

## 5) Model Regression After Deployment
**Symptoms:** Business metrics (forecast accuracy, conversion rate) degrade after new model deployed; user complaints increase.

**Immediate Containment:**
- [ ] Execute rollback playbook to revert to previous model version
- [ ] Capture prediction samples from degraded period for analysis

**Diagnostics:**
```bash
# Compare predictions before/after deployment
aws s3 cp s3://prediction-logs/<date-before>/ ./before/
aws s3 cp s3://prediction-logs/<date-after>/ ./after/
python scripts/compare_predictions.py --before ./before/ --after ./after/

# Re-evaluate model on recent ground truth data
python scripts/evaluate.py --model-uri models:/demand-forecast/<version> --data ./recent_actuals.csv

# Check for data quality issues or distribution shift
python scripts/validate_data.py --data ./recent_actuals.csv
```

**Common causes:**
- Training/serving skew (feature encoding differs)
- Overfitting to recent training data; poor generalization
- Concept drift not detected during evaluation
- Data quality issue in training set (mislabeled, biased sample)

**Permanent Fixes:**
- Add training/serving parity tests to CI
- Expand validation set to cover diverse scenarios
- Implement shadow mode testing before full rollout
- Enhance drift detection to catch subtle concept drift
- Require longer canary period with business metric validation

**Validation/Closure:**
- [ ] Previous model version restored and metrics recovered
- [ ] Root cause identified and documented in post-mortem
- [ ] New model re-trained with fixes; passes expanded evaluation
- [ ] Rollout playbook updated with additional gates

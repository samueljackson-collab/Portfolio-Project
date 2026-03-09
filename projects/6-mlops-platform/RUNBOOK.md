# Runbook — Project 6 (MLOps Platform)

## Overview

Production operations runbook for the MLOps Platform. This runbook covers MLflow operations, model
training workflows, hyperparameter optimization, model deployment procedures, monitoring, and
troubleshooting for ML pipelines.

**System Components:**

- MLflow Tracking Server (experiment logging & model registry)
- Optuna Study (hyperparameter optimization)
- Model Training Jobs (scikit-learn, XGBoost)
- Deployment Orchestrator (Kubernetes/Lambda/SageMaker)
- Feature Store (data preprocessing service)
- Drift Detection & Monitoring Service

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Model training success rate** | 95% | Successful experiment completion without errors |
| **MLflow server availability** | 99.5% | Tracking server uptime and API responsiveness |
| **Model inference latency (p95)** | < 100ms | Time from request to prediction response |
| **Deployment success rate** | 98% | Model registration → deployment completion |
| **Drift detection accuracy** | > 90% | True positive rate for data/model drift |
| **Hyperparameter tuning completion** | < 4 hours | Time for Optuna study convergence |

---

## Dashboards & Alerts

### Dashboards

#### MLflow Tracking Dashboard

```bash
# Access MLflow UI
mlflow ui --backend-store-uri sqlite:///mlruns.db --port 5000

# Expected output:
# [INFO] Starting MLflow server at http://127.0.0.1:5000
# Navigate to http://localhost:5000 to view experiments

# Check tracking server health
curl -f http://localhost:5000/health || echo "MLflow server down"
```

#### Model Registry Dashboard

```bash
# List registered models
mlflow models list --max-results 10

# Get model details
mlflow models describe --name "churn-classifier"

# Check model serving endpoints
kubectl get svc -n ml-serving -l app=model-server
```

#### Training Jobs Dashboard

```bash
# Check active experiments
python scripts/list_experiments.py

# View training job status
kubectl get pods -n ml-training -l job-type=training

# Check Optuna study progress
python scripts/optuna_dashboard.py
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Model serving down (0 pods) | Immediate | Emergency rollback to last good model |
| **P1** | Training job failures > 50% | 15 minutes | Investigate data pipeline, restart jobs |
| **P1** | MLflow server unreachable | 15 minutes | Restart tracking server, check database |
| **P2** | Drift detected on production model | 1 hour | Trigger retraining workflow |
| **P2** | Model latency > 200ms (p95) | 30 minutes | Scale inference pods, optimize model |
| **P3** | Hyperparameter tuning timeout | 2 hours | Review study configuration, extend timeout |

#### Alert Queries

```bash
# Check model serving pod health
SERVING_PODS=$(kubectl get pods -n ml-serving -l app=model-server --field-selector=status.phase=Running --no-headers | wc -l)
if [ $SERVING_PODS -lt 2 ]; then
  echo "ALERT: Only $SERVING_PODS model serving pods running"
fi

# Check training job failures
FAILED_JOBS=$(kubectl get pods -n ml-training -l job-type=training --field-selector=status.phase=Failed --no-headers | wc -l)
if [ $FAILED_JOBS -gt 3 ]; then
  echo "ALERT: $FAILED_JOBS training jobs failed recently"
fi

# Check MLflow server status
curl -sf http://localhost:5000/health || echo "ALERT: MLflow tracking server unreachable"
```

---

## Standard Operations

### MLflow Tracking Server Management

#### Start MLflow Server

```bash
# Start tracking server with SQLite backend
mlflow server \
  --backend-store-uri sqlite:///mlruns.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000

# Start with PostgreSQL backend (production)
mlflow server \
  --backend-store-uri postgresql://user:pass@localhost:5432/mlflow \
  --default-artifact-root s3://mlflow-artifacts \
  --host 0.0.0.0 \
  --port 5000

# Verify server is running
curl http://localhost:5000/health
mlflow experiments list
```

#### Backup MLflow Data

```bash
# Backup SQLite database
cp mlruns.db backups/mlruns-$(date +%Y%m%d-%H%M).db

# Backup artifacts
aws s3 sync s3://mlflow-artifacts s3://mlflow-artifacts-backup/$(date +%Y%m%d)

# Backup PostgreSQL database
pg_dump mlflow > backups/mlflow-db-$(date +%Y%m%d).sql

# Verify backup
ls -lh backups/
```

### Model Training Operations

#### Run Training Experiment

```bash
# 1. Verify data availability
ls data/training/*.csv
aws s3 ls s3://feature-store/training-data/

# 2. Validate configuration
python scripts/validate_config.py configs/churn-experiment.yaml

# 3. Launch training job
./scripts/run_training.sh configs/churn-experiment.yaml

# 4. Monitor training progress
mlflow runs list --experiment-name "churn-classifier"
tail -f logs/training.log

# 5. Check experiment results
python scripts/get_best_run.py --experiment "churn-classifier"
```

#### Hyperparameter Tuning with Optuna

```bash
# 1. Define search space (edit configs/optuna_study.yaml)
cat configs/optuna_study.yaml

# 2. Create Optuna study
python scripts/create_study.py \
  --study-name "churn-optimization" \
  --storage "sqlite:///optuna.db"

# 3. Run optimization
python scripts/run_optimization.py \
  --study-name "churn-optimization" \
  --n-trials 100 \
  --timeout 14400  # 4 hours

# 4. Monitor study progress
python scripts/optuna_dashboard.py --study-name "churn-optimization"

# 5. Export best parameters
python scripts/export_best_params.py --study-name "churn-optimization" \
  > configs/best_params.json
```

#### Distributed Training (Kubernetes)

```bash
# 1. Create training job manifest
kubectl apply -f manifests/training-job.yaml

# 2. Monitor job progress
kubectl get jobs -n ml-training -w

# 3. Check pod logs
kubectl logs -n ml-training -l job-name=churn-training-001 -f

# 4. Collect results
kubectl exec -n ml-training <pod-name> -- \
  python scripts/export_model.py --run-id <mlflow-run-id>
```

### Model Deployment Operations

#### Register Model in MLflow

```bash
# 1. Get best run from experiment
BEST_RUN=$(python scripts/get_best_run.py --experiment "churn-classifier" --metric "f1_score")

# 2. Register model
mlflow models register \
  --model-uri "runs:/$BEST_RUN/model" \
  --name "churn-classifier"

# 3. Verify registration
mlflow models list --name "churn-classifier"

# 4. Transition to staging
mlflow models transition \
  --name "churn-classifier" \
  --version 1 \
  --stage Staging
```

#### Deploy to Kubernetes

```bash
# 1. Build model serving image
docker build -t model-server:v1.0 -f deployment/kubernetes/Dockerfile .

# 2. Push to registry
docker tag model-server:v1.0 <registry>/model-server:v1.0
docker push <registry>/model-server:v1.0

# 3. Deploy to Kubernetes
kubectl apply -f deployment/kubernetes/deployment.yaml

# 4. Verify deployment
kubectl rollout status deployment/model-server -n ml-serving
kubectl get pods -n ml-serving -l app=model-server

# 5. Test inference endpoint
kubectl port-forward -n ml-serving svc/model-server 8080:80 &
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d @test/sample_request.json
pkill -f "port-forward"
```

#### Deploy to AWS Lambda

```bash
# 1. Package model and dependencies
python scripts/package_lambda.py --model-name "churn-classifier" --version 1

# 2. Deploy using AWS SAM
cd deployment/lambda
sam build
sam deploy --guided

# 3. Test Lambda function
aws lambda invoke \
  --function-name ml-inference \
  --payload file://test/sample_event.json \
  output.json
cat output.json
```

#### Deploy to SageMaker

```bash
# 1. Create model package
python scripts/create_sagemaker_model.py \
  --model-name "churn-classifier" \
  --version 1 \
  --role "arn:aws:iam::123456789:role/SageMakerRole"

# 2. Deploy endpoint
python scripts/deploy_sagemaker.py \
  --model-name "churn-classifier" \
  --endpoint-name "churn-classifier-prod" \
  --instance-type "ml.m5.large" \
  --instance-count 2

# 3. Test endpoint
python scripts/test_sagemaker_endpoint.py \
  --endpoint "churn-classifier-prod" \
  --data test/sample_request.json
```

### Monitoring & Drift Detection

#### Check for Data Drift

```bash
# Run drift detection on recent data
python scripts/detect_drift.py \
  --reference-data data/reference/baseline.csv \
  --current-data data/production/$(date +%Y%m%d).csv \
  --threshold 0.05

# View drift report
cat reports/drift-report-$(date +%Y%m%d).json

# If drift detected, trigger retraining
if grep -q "drift_detected: true" reports/drift-report-$(date +%Y%m%d).json; then
  ./scripts/trigger_retraining.sh
fi
```

#### Monitor Model Performance

```bash
# Collect inference logs
python scripts/collect_inference_logs.py --date $(date +%Y-%m-%d)

# Calculate performance metrics
python scripts/calculate_metrics.py \
  --predictions data/predictions/$(date +%Y%m%d).csv \
  --actuals data/actuals/$(date +%Y%m%d).csv

# Generate performance report
python scripts/generate_report.py --date $(date +%Y-%m-%d) \
  > reports/performance-$(date +%Y%m%d).html
```

---

## Incident Response

### Detection

**Automated Detection:**

- MLflow server health check failures
- Model serving pod crashes
- Training job failures
- Drift detection alerts
- Inference latency SLO violations

**Manual Detection:**

```bash
# Check overall system health
./scripts/health_check.sh

# Check MLflow server
curl http://localhost:5000/health

# Check model serving pods
kubectl get pods -n ml-serving

# Check recent training jobs
kubectl get jobs -n ml-training --sort-by=.status.startTime

# Review recent drift reports
ls -lt reports/drift-*.json | head -5
```

### Triage

#### Severity Classification

### P0: Complete Outage

- MLflow tracking server down (cannot log experiments)
- All model serving pods down (no inference available)
- Critical data pipeline failure (no training data)

### P1: Degraded Service

- Model serving pods < 50% capacity
- Training job success rate < 50%
- High inference latency (p95 > 500ms)
- Significant data drift detected

### P2: Warning State

- Individual training job failures
- Moderate drift detected
- Increased inference latency (p95 > 200ms)
- Hyperparameter tuning timeouts

### P3: Informational

- Single experiment failure
- Minor drift detected
- Resource usage approaching limits

### Incident Response Procedures

#### P0: MLflow Tracking Server Down

**Immediate Actions (0-5 minutes):**

```bash
# 1. Check server status
curl http://localhost:5000/health
ps aux | grep mlflow

# 2. Check database connectivity
if using PostgreSQL:
psql -h localhost -U mlflow -c "SELECT 1"

if using SQLite:
ls -lh mlruns.db
sqlite3 mlruns.db "SELECT COUNT(*) FROM experiments;"

# 3. Check disk space
df -h
du -sh mlruns/

# 4. Restart MLflow server
pkill -f "mlflow server"
nohup mlflow server \
  --backend-store-uri sqlite:///mlruns.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000 > mlflow.log 2>&1 &

# 5. Verify restart
sleep 5
curl http://localhost:5000/health
mlflow experiments list
```

**Investigation (5-15 minutes):**

```bash
# Check MLflow logs
tail -100 mlflow.log

# Check database logs (PostgreSQL)
tail -100 /var/log/postgresql/postgresql-*.log

# Check system resources
top -n 1
free -h

# Check network connectivity
netstat -tulpn | grep 5000
```

**Mitigation:**

```bash
# If database corrupted (SQLite)
cp backups/mlruns-latest.db mlruns.db
mlflow server --backend-store-uri sqlite:///mlruns.db

# If disk full
# Clean up old artifacts
find mlruns/ -type f -mtime +30 -delete

# If network issue
# Restart with different port
mlflow server --port 5001

# Document incident
echo "MLflow server recovered at $(date)" >> incidents/mlflow-$(date +%Y%m%d).log
```

#### P0: All Model Serving Pods Down

**Immediate Actions (0-2 minutes):**

```bash
# 1. Check pod status
kubectl get pods -n ml-serving -l app=model-server

# 2. Check recent events
kubectl get events -n ml-serving --sort-by='.lastTimestamp' | head -20

# 3. Check deployment
kubectl describe deployment model-server -n ml-serving

# 4. Emergency: Deploy previous version
kubectl rollout undo deployment/model-server -n ml-serving

# 5. Monitor recovery
kubectl rollout status deployment/model-server -n ml-serving
```

**Investigation (2-10 minutes):**

```bash
# Check pod logs
kubectl logs -n ml-serving -l app=model-server --tail=100

# Check previous pod logs if crashed
POD=$(kubectl get pods -n ml-serving -l app=model-server -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD --previous -n ml-serving

# Check resource constraints
kubectl top pods -n ml-serving
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check image availability
kubectl describe pod $POD -n ml-serving | grep Image
```

**Common Causes & Fixes:**

**Model Loading Failure:**

```bash
# Verify model exists in MLflow
mlflow models list --name "churn-classifier"

# Re-register model
python scripts/register_model.py --run-id <valid-run-id>

# Redeploy with correct model version
kubectl set env deployment/model-server MODEL_VERSION=2 -n ml-serving
```

**OOM (Out of Memory):**

```bash
# Check memory usage
kubectl top pods -n ml-serving

# Increase memory limits
kubectl patch deployment model-server -n ml-serving -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "model-server",
          "resources": {
            "limits": {"memory": "2Gi"},
            "requests": {"memory": "1Gi"}
          }
        }]
      }
    }
  }
}'
```

#### P1: Training Job Failures

**Investigation:**

```bash
# List failed jobs
kubectl get jobs -n ml-training --field-selector status.successful=0

# Check job details
kubectl describe job <job-name> -n ml-training

# Check pod logs
kubectl logs -n ml-training -l job-name=<job-name> --tail=100

# Check data availability
aws s3 ls s3://feature-store/training-data/$(date +%Y%m%d)/
```

**Common Causes & Fixes:**

**Data Pipeline Failure:**

```bash
# Check data freshness
python scripts/check_data_freshness.py

# Trigger data pipeline
./scripts/trigger_data_pipeline.sh

# Wait for data and retry training
sleep 300
./scripts/run_training.sh configs/churn-experiment.yaml
```

**Resource Constraints:**

```bash
# Increase job resources
kubectl patch job <job-name> -n ml-training -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "trainer",
          "resources": {
            "requests": {"cpu": "4", "memory": "8Gi"},
            "limits": {"cpu": "8", "memory": "16Gi"}
          }
        }]
      }
    }
  }
}'

# Delete and recreate job
kubectl delete job <job-name> -n ml-training
kubectl apply -f manifests/training-job.yaml
```

**Dependency Issues:**

```bash
# Rebuild training image with updated dependencies
docker build -t training-image:v2.0 -f docker/Dockerfile.training .
docker push <registry>/training-image:v2.0

# Update job to use new image
kubectl set image job/<job-name> trainer=<registry>/training-image:v2.0 -n ml-training
```

#### P1: Significant Data Drift Detected

**Investigation:**

```bash
# Review drift report
python scripts/view_drift_report.py --date $(date +%Y-%m-%d)

# Analyze drift features
python scripts/analyze_drift_features.py \
  --reference data/reference/baseline.csv \
  --current data/production/$(date +%Y%m%d).csv

# Check model performance on recent data
python scripts/evaluate_on_recent.py --days 7
```

**Mitigation:**

```bash
# 1. Trigger emergency retraining
./scripts/trigger_retraining.sh --priority high

# 2. Monitor training progress
watch kubectl get jobs -n ml-training

# 3. Once complete, deploy new model
NEW_RUN=$(python scripts/get_latest_run.py --experiment "churn-classifier-retrain")
mlflow models register --model-uri "runs:/$NEW_RUN/model" --name "churn-classifier"
mlflow models transition --name "churn-classifier" --version 3 --stage Production

# 4. Deploy to production
kubectl set env deployment/model-server MODEL_VERSION=3 -n ml-serving

# 5. Monitor new model performance
python scripts/monitor_model.py --version 3 --duration 3600
```

### Post-Incident

**After Resolution:**

```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 45 minutes
**Affected Component:** Model serving

## Timeline
- 10:00: Drift detection alert triggered
- 10:05: Confirmed significant drift in production data
- 10:10: Triggered emergency retraining workflow
- 10:35: New model trained and registered
- 10:40: Deployed new model to production
- 10:45: Verified model performance, incident resolved

## Root Cause
Significant shift in customer behavior not captured in baseline data

## Action Items
- [ ] Update drift detection thresholds
- [ ] Implement automated retraining on drift
- [ ] Add more frequent baseline updates
- [ ] Review feature engineering process

EOF

# Update runbook if needed
# Archive incident report
git add incidents/incident-$(date +%Y%m%d-%H%M).md
git commit -m "docs: incident report for drift-triggered retraining"
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Experiment Not Logging to MLflow

**Symptoms:**

```bash
$ python train.py
Error: Failed to log parameters to MLflow
```

**Diagnosis:**

```bash
# Check MLflow server connectivity
curl http://localhost:5000/health

# Check environment variables
echo $MLFLOW_TRACKING_URI

# Check network connectivity
telnet localhost 5000
```

**Solution:**

```bash
# Set tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000

# Or use file-based tracking temporarily
export MLFLOW_TRACKING_URI=file:///path/to/mlruns

# Verify connectivity
mlflow experiments list
```

---

#### Issue: Model Loading Timeout in Serving Pod

**Symptoms:**

```bash
$ kubectl logs model-server-xxx -n ml-serving
Error: Model loading timeout after 60 seconds
```

**Diagnosis:**

```bash
# Check model size
mlflow artifacts list -r <run-id>

# Check pod resources
kubectl describe pod model-server-xxx -n ml-serving | grep -A 5 "Limits\|Requests"

# Check artifact store connectivity
aws s3 ls s3://mlflow-artifacts/<run-id>/
```

**Solution:**

```bash
# Increase readiness probe timeout
kubectl patch deployment model-server -n ml-serving -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "model-server",
          "readinessProbe": {
            "initialDelaySeconds": 120,
            "timeoutSeconds": 30
          }
        }]
      }
    }
  }
}'

# Or optimize model loading
python scripts/optimize_model.py --model-name "churn-classifier" --version 1
```

---

#### Issue: Hyperparameter Tuning Not Converging

**Symptoms:**

- Optuna study running for hours without improvement
- Trial results show high variance

**Diagnosis:**

```bash
# Check study progress
python scripts/view_study.py --study-name "churn-optimization"

# Review trial history
python scripts/export_trials.py --study-name "churn-optimization" > trials.csv

# Visualize optimization
python scripts/plot_optimization.py --study-name "churn-optimization"
```

**Solution:**

```bash
# Option 1: Narrow search space
# Edit configs/optuna_study.yaml to reduce parameter ranges

# Option 2: Use better sampler
python scripts/update_study_sampler.py \
  --study-name "churn-optimization" \
  --sampler "TPESampler"

# Option 3: Increase n_trials or add pruning
python scripts/run_optimization.py \
  --study-name "churn-optimization" \
  --n-trials 200 \
  --pruner "MedianPruner"
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
curl http://localhost:5000/health
kubectl get pods -n ml-serving
kubectl get jobs -n ml-training

# Check recent experiments
mlflow runs list --experiment-name "churn-classifier" | head -10

# Check model performance metrics
python scripts/daily_metrics_report.py

# Review drift reports
ls -lt reports/drift-*.json | head -1 | xargs cat
```

### Weekly Tasks

```bash
# Review model performance trends
python scripts/weekly_performance_report.py

# Clean up old experiments
python scripts/cleanup_experiments.py --older-than 30

# Update baseline data for drift detection
python scripts/update_baseline.py --source data/production/$(date -d "7 days ago" +%Y%m%d)/

# Review and optimize resource usage
kubectl top pods -n ml-serving
kubectl top pods -n ml-training

# Backup MLflow database
cp mlruns.db backups/mlruns-weekly-$(date +%Y%m%d).db
```

### Monthly Tasks

```bash
# Comprehensive model audit
python scripts/audit_models.py --report reports/model-audit-$(date +%Y-%m).html

# Review and update monitoring thresholds
vim configs/monitoring_config.yaml

# Update production baseline data
python scripts/update_production_baseline.py

# Archive old training data
aws s3 sync data/training/ s3://training-data-archive/$(date +%Y-%m)/
find data/training/ -type f -mtime +60 -delete

# Review and update this runbook
git pull
# Update procedures based on recent incidents and lessons learned
```

### Upgrade Procedures

#### Update MLflow Version

```bash
# 1. Backup current state
cp mlruns.db backups/mlruns-pre-upgrade-$(date +%Y%m%d).db

# 2. Stop MLflow server
pkill -f "mlflow server"

# 3. Upgrade MLflow
pip install --upgrade mlflow

# 4. Restart server
nohup mlflow server \
  --backend-store-uri sqlite:///mlruns.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000 > mlflow.log 2>&1 &

# 5. Verify upgrade
mlflow --version
curl http://localhost:5000/health
mlflow experiments list
```

#### Update Model Serving Image

```bash
# 1. Build new image
docker build -t model-server:v2.0 -f deployment/kubernetes/Dockerfile .

# 2. Test locally
docker run -p 8080:80 model-server:v2.0 &
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d @test/sample.json
docker stop $(docker ps -q --filter ancestor=model-server:v2.0)

# 3. Push to registry
docker tag model-server:v2.0 <registry>/model-server:v2.0
docker push <registry>/model-server:v2.0

# 4. Update deployment
kubectl set image deployment/model-server model-server=<registry>/model-server:v2.0 -n ml-serving

# 5. Monitor rollout
kubectl rollout status deployment/model-server -n ml-serving

# 6. Verify
kubectl get pods -n ml-serving
curl -X POST http://<service-url>/predict -d @test/sample.json

# 7. Rollback if issues
kubectl rollout undo deployment/model-server -n ml-serving
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective):
  - Experiments: 5 minutes (continuous MLflow logging)
  - Models: 1 hour (registry backup interval)
  - Training data: 24 hours (daily snapshots)

- **RTO** (Recovery Time Objective):
  - MLflow server: 5 minutes
  - Model serving: 10 minutes (redeploy from registry)
  - Training pipeline: 30 minutes

### Backup Strategy

**MLflow Backup:**

```bash
# Daily automated backup
cat > scripts/backup_mlflow.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup database
cp mlruns.db $BACKUP_DIR/mlruns.db

# Backup artifacts
aws s3 sync s3://mlflow-artifacts s3://mlflow-artifacts-backup/$(date +%Y%m%d)

# Backup metadata
mlflow models list > $BACKUP_DIR/models_list.txt
mlflow experiments list > $BACKUP_DIR/experiments_list.txt

echo "Backup completed at $(date)" | tee $BACKUP_DIR/backup.log
EOF

chmod +x scripts/backup_mlflow.sh

# Schedule daily via cron
# 0 2 * * * /path/to/scripts/backup_mlflow.sh
```

**Model Registry Backup:**

```bash
# Export all registered models
python scripts/export_models.py --output backups/models-$(date +%Y%m%d).json

# Backup model artifacts
for model in $(mlflow models list | awk '{print $1}'); do
  mlflow artifacts download --run-id $model --dst-path backups/models/$model
done
```

### Disaster Recovery Procedures

#### Complete MLflow Server Loss

**Recovery Steps (5-10 minutes):**

```bash
# 1. Stop any running MLflow processes
pkill -f "mlflow server"

# 2. Restore database from latest backup
LATEST_BACKUP=$(ls -t backups/mlruns-*.db | head -1)
cp $LATEST_BACKUP mlruns.db

# 3. Restore artifacts from S3
aws s3 sync s3://mlflow-artifacts-backup/latest s3://mlflow-artifacts

# 4. Restart MLflow server
nohup mlflow server \
  --backend-store-uri sqlite:///mlruns.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000 > mlflow.log 2>&1 &

# 5. Verify recovery
sleep 10
curl http://localhost:5000/health
mlflow experiments list
mlflow models list
```

#### Model Serving Disaster Recovery

**Recovery Steps (10-15 minutes):**

```bash
# 1. Identify last known good model version
mlflow models list --name "churn-classifier" | grep "Production"

# 2. Redeploy from registry
kubectl delete deployment model-server -n ml-serving
kubectl apply -f deployment/kubernetes/deployment.yaml

# 3. Verify deployment
kubectl rollout status deployment/model-server -n ml-serving
kubectl get pods -n ml-serving

# 4. Test inference
kubectl port-forward -n ml-serving svc/model-server 8080:80 &
curl -X POST http://localhost:8080/predict -d @test/sample.json
pkill -f "port-forward"

# 5. Update monitoring
./scripts/update_monitoring.sh
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Start MLflow server
mlflow server --backend-store-uri sqlite:///mlruns.db --port 5000

# Run training experiment
./scripts/run_training.sh configs/churn-experiment.yaml

# Register model
mlflow models register --model-uri "runs:/<run-id>/model" --name "churn-classifier"

# Deploy model to Kubernetes
kubectl apply -f deployment/kubernetes/deployment.yaml

# Check model serving status
kubectl get pods -n ml-serving

# Test inference
curl -X POST http://<endpoint>/predict -d @test/sample.json

# Detect drift
python scripts/detect_drift.py --current-data data/production/latest.csv

# View experiment results
mlflow ui
```

### Emergency Response

```bash
# P0: MLflow server down
pkill -f "mlflow"; mlflow server --backend-store-uri sqlite:///mlruns.db --port 5000

# P0: All serving pods down
kubectl rollout undo deployment/model-server -n ml-serving

# P1: Training jobs failing
kubectl delete job <job-name> -n ml-training
kubectl apply -f manifests/training-job.yaml

# P1: Significant drift detected
./scripts/trigger_retraining.sh --priority high
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** ML Platform Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

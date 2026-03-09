# Dashboards and Alerts (MLOps)

## Pipeline Reliability Dashboard

### Panels
1. **Pipeline Success Rate (%):** Count of successful vs failed runs per hour/day
2. **Average Pipeline Duration (minutes):** Trend line with p50/p95/p99
3. **Component Failure Breakdown:** Pie chart by component type (ingestion, training, evaluation, registration)
4. **Resource Utilization:** CPU/memory/GPU usage per component
5. **Artifact Size Trend:** Model size and dataset size over time

### Metrics Sources
- Kubeflow Pipelines API (`pipelinerun` CRD status)
- Prometheus metrics from pipeline pods (`container_cpu_usage_seconds`, `container_memory_working_set_bytes`)
- S3/GCS bucket metrics for artifact sizes

### Alerts
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| PipelineFailureRate | Failure rate > 10% over 6 hours | Warning | Page on-call; check runbook |
| PipelineStuck | Run duration > 2x p95 baseline | Warning | Investigate stuck component |
| ResourceExhaustion | Pod OOMKilled or EvictedByKubelet | Critical | Scale resources; optimize code |

---

## Model Performance Dashboard

### Panels
1. **Accuracy/MAE/RMSE Trend:** Time series per model version deployed
2. **Prediction Distribution:** Histogram of predictions vs actuals
3. **Error Budget Burn Rate:** SLO compliance tracking (e.g., 99% accuracy target)
4. **Model Degradation Alert History:** Timeline of drift/regression alerts
5. **Business KPI Impact:** Forecast accuracy effect on revenue/inventory

### Metrics Sources
- MLflow tracking server (logged metrics per run)
- Custom application metrics from predictor (prediction samples)
- Business data warehouse (actual sales vs forecasts)

### Alerts
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| ModelDegradation | MAE increases > 15% over 7-day rolling window | Critical | Trigger retraining; notify team |
| ErrorBudgetExhausted | Accuracy < SLO for 48 hours | Critical | Rollback model; escalate |
| PredictionAnomaly | Prediction distribution shift (KS test p < 0.01) | Warning | Review data quality |

---

## Serving Health Dashboard

### Panels
1. **Request Latency (ms):** p50/p95/p99 per model and version
2. **Error Rate (%):** 4xx and 5xx errors per endpoint
3. **Throughput (requests/sec):** Traffic volume with breakdown by model
4. **Autoscaler Activity:** Replica count over time with scale-up/down events
5. **Cold Start Frequency:** Count of first-request slow responses after scale-to-zero

### Metrics Sources
- Istio/Envoy metrics (request duration, status codes)
- KFServing controller metrics (`kserve_model_request_duration_seconds`, `kserve_model_request_count`)
- Kubernetes HPA events

### Alerts
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| HighLatency | p95 latency > 300ms for 10 minutes | Warning | Scale replicas; check feature store |
| ErrorRateSpike | Error rate > 2% for 5 minutes | Critical | Rollback deployment; check logs |
| ScalingIssue | Desired replicas > actual replicas for 15 minutes | Warning | Check HPA config; verify node capacity |

---

## Drift and Data Quality Dashboard

### Panels
1. **Feature Drift Scores:** Heat map of drift scores per feature over time (KS test, PSI)
2. **Prediction Drift:** Distribution comparison (reference vs current week)
3. **Data Freshness:** Time since last feature materialization
4. **Schema Violations:** Count of invalid records per data source
5. **Drift Alert History:** Timeline of fired alerts with resolution status

### Metrics Sources
- Drift detector job logs (custom metrics)
- Feast feature store metrics (`feast_materialization_lag_seconds`)
- Great Expectations validation results

### Alerts
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| FeatureDriftDetected | Drift score > threshold for 3 consecutive checks | Warning | Review data; consider retraining |
| StaleFeat

ures | Materialization lag > 30 minutes | Warning | Check Feast job status |
| DataQualityFailure | Schema validation failure rate > 5% | Critical | Pause pipeline; investigate source |

---

## Cost and Resource Optimization Dashboard

### Panels
1. **Training Cost per Run ($):** Breakdown by compute (CPU/GPU) and storage
2. **Inference Cost per 1k Requests ($):** Trend with optimization annotations
3. **Spot Instance Interruptions:** Count and impact on training duration
4. **Storage Growth:** S3/GCS artifact storage size and cost projection
5. **GPU Utilization (%):** Actual vs requested GPU across training jobs

### Metrics Sources
- Cloud billing APIs (AWS Cost Explorer, GCP Billing)
- Kubernetes resource usage metrics
- Custom cost allocation tags on resources

### Alerts
| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| CostAnomaly | Daily cost > 20% above 7-day average | Warning | Audit resource usage; check for leaks |
| LowGPUUtilization | GPU utilization < 50% for training jobs | Info | Optimize batch size; consider CPU |
| StorageGrowth | Artifact storage growth > 100 GB/day | Warning | Review retention policy; clean old artifacts |

---

## Alert Routing and Escalation

### Severity Levels
- **Critical:** Page on-call immediately (PagerDuty/Opsgenie); requires immediate action
- **Warning:** Slack alert to #ml-ops channel; review within 1 hour
- **Info:** Log to dashboard; review during daily standup

### Escalation Policy
1. On-call ML engineer (primary)
2. ML platform lead (after 30 minutes if unresolved)
3. Engineering manager (after 1 hour for critical issues)

### Notification Channels
- PagerDuty for Critical alerts
- Slack #ml-ops for Warning/Info
- Email digest for daily summary

---

## Dashboard Links
- **Grafana:** `https://grafana.company.com/d/mlops-overview`
- **MLflow:** `https://mlflow.company.com`
- **Kubeflow:** `https://kubeflow.company.com`
- **Cost Dashboard:** `https://cost.company.com/ml-platform`

# P07 — Enterprise Machine Learning Pipeline with Kubeflow and MLflow

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


**Tagline:** Production-grade MLOps platform delivering retail demand forecasting with automated retraining, model governance, and multi-stage deployment.

## Executive Summary: MLOps Philosophy
- **Continuous Training:** Automated pipelines retrain models on fresh data, eliminating manual notebook workflows and ensuring predictions stay current.
- **Model Governance:** MLflow registry with approval gates, lineage tracking, and A/B testing provides audit trails and safe rollouts.
- **End-to-End Automation:** From feature engineering in Feast to KFServing inference endpoints, the entire lifecycle is codified and repeatable.
- **Enterprise Rigor:** Includes drift detection, cost optimization (spot instances), security controls (RBAC, model signing), and comprehensive operational playbooks.

## Architecture Overview

### End-to-End Flow
**Data Sources** → **Feature Store (Feast)** → **Kubeflow Pipeline** → **MLflow Tracking/Registry** → **KFServing Deployment** → **Monitoring/Drift Detection** → **Retraining Trigger**

### Components
- **Kubeflow Pipelines:** Orchestrates data prep, training, evaluation, and registration steps as reusable containerized components.
- **MLflow:** Tracks experiments (hyperparameters, metrics, artifacts), manages model registry (staging/production versions), and provides model lineage.
- **Feast Feature Store:** Serves online/offline features with consistency, point-in-time correctness, and versioning.
- **Distributed Training:** PyTorch/TensorFlow jobs on GPU nodes with auto-scaling and spot instance support.
- **KFServing:** Deploys models with canary/shadow/A/B strategies, auto-scaling, and batching; supports rollback and traffic splitting.
- **Drift Detection:** Monitors feature distributions and model performance; triggers retraining when thresholds breached.

### Directory Layout
```
projects-new/p07/
├── README.md                  # Platform overview and setup
├── ARCHITECTURE.md            # Mermaid diagrams + explanations
├── TESTING.md                 # Testing strategy and cases
├── REPORT_TEMPLATES.md        # Release/ops/experiment templates
├── PLAYBOOK.md                # Model promotion playbook
├── RUNBOOKS.md                # Incident runbooks
├── SOP.md                     # Operational SOPs
├── METRICS.md                 # Dashboard/alert definitions
├── ADRS.md                    # Architecture decisions
├── THREAT_MODEL.md            # Security threat model
├── RISK_REGISTER.md           # Risk register
├── pipeline/
│   ├── training_pipeline.py   # Kubeflow Pipeline definition
│   ├── components/            # Reusable KFP components
│   └── requirements.txt
├── mlflow/
│   ├── mlflow-server.yaml     # MLflow deployment config
│   └── tracking_example.py    # Example experiment tracking
├── feast/
│   ├── feature_repo/          # Feast feature definitions
│   └── feature_store.yaml
├── serving/
│   ├── inferenceservice.yaml  # KFServing config
│   └── predictor.py           # Custom predictor logic
└── ci/
    └── workflows/
        └── ml-pipeline.yml    # CI/CD for ML pipeline
```

## Setup

### Prerequisites
- Kubernetes cluster (1.24+) with GPU nodes or node pools
- kubectl, kustomize, helm
- Python 3.10+
- Docker registry access
- S3/GCS/ABS bucket for MLflow artifacts and Feast offline store
- PostgreSQL for MLflow backend (or embedded SQLite for dev)

### Install Kubeflow Pipelines
```bash
export PIPELINE_VERSION=2.0.3
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic-pns?ref=$PIPELINE_VERSION"
```

### Deploy MLflow Server
```bash
cd projects-new/p07/mlflow
# Edit mlflow-server.yaml with backend-store-uri and artifact-root
kubectl apply -f mlflow-server.yaml
kubectl port-forward svc/mlflow-server 5000:5000
```
Access at http://localhost:5000. Configure `MLFLOW_TRACKING_URI=http://mlflow-server.mlops.svc.cluster.local:5000` in pipeline components.

### Deploy Feast Feature Store
```bash
cd projects-new/p07/feast/feature_repo
feast apply
feast materialize-incremental $(date -u +%Y-%m-%dT%H:%M:%S)
```
Configure online store (Redis/DynamoDB) and offline store (S3/BigQuery) in `feature_store.yaml`.

### Run Training Pipeline
```bash
cd projects-new/p07/pipeline
pip install -r requirements.txt
python training_pipeline.py \
  --experiment-name demand-forecast \
  --run-name run-$(date +%s) \
  --data-path s3://my-bucket/data/sales.parquet \
  --mlflow-uri http://mlflow-server.mlops.svc.cluster.local:5000
```
Pipeline stages: data validation → feature engineering → training → evaluation → model registration to MLflow.

### Deploy Model to KFServing
```bash
cd projects-new/p07/serving
# Update inferenceservice.yaml with model URI from MLflow registry
kubectl apply -f inferenceservice.yaml -n mlops
kubectl get inferenceservice demand-forecast -n mlops
```
Test inference:
```bash
curl -X POST http://demand-forecast.mlops.example.com/v1/models/demand-forecast:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": [{"store_id": 42, "date": "2025-01-15", "promo": 1}]}'
```

## Workflow

### Experimentation
1. Data scientists run experiments locally or in notebooks, logging to MLflow with `mlflow.start_run()`.
2. Compare runs in MLflow UI; select best hyperparameters and feature sets.
3. Promote experiment code to Kubeflow Pipeline component for productionization.

### Pipeline Productionization
1. Wrap training logic in KFP component with inputs/outputs as artifacts.
2. Add data validation (Great Expectations), feature consistency checks (Feast), and model evaluation gates.
3. Register passing models to MLflow registry with metadata (dataset version, git commit, approver).

### Automated Retraining
1. Schedule pipeline runs (cron/Argo Events) or trigger on data arrival/drift alerts.
2. Pipeline compares new model metrics against production baseline; auto-promotes if superior and within risk bounds.
3. Send notifications (Slack/email) and update dashboard with new model version.

## Observability

### Model Performance Monitoring
- Track accuracy/MAE/MAPE over time; compare actual vs predicted with business KPIs.
- Visualize in Grafana with Prometheus metrics exported from KFServing or custom predictor.

### Drift Detection
- Monitor feature distributions (KL divergence, population stability index) and prediction distributions.
- Alert when drift score exceeds threshold; capture samples for offline analysis.

### Infrastructure Metrics
- GPU utilization, training job duration, pipeline success rate, model serving latency/throughput.
- Cost per training run and per 1k inferences; track spot instance interruptions.

## Security & Compliance

### Model Approval Workflow
- Models transition through MLflow registry stages: `None` → `Staging` → `Production`.
- Approval requires sign-off from data science lead and compliance officer; audit log immutable.

### Data Privacy
- Feast feature store enforces column-level access control; PII fields encrypted at rest.
- Training jobs run in isolated namespaces with network policies; no egress to public internet without proxy.

### Access Control
- RBAC for Kubeflow/MLflow/KFServing; service accounts with least privilege.
- Model artifacts signed with Cosign; registry validates signatures before deployment.

## Cost Optimization
- **Spot Instances for Training:** Configure node pools with spot/preemptible VMs; Kubeflow handles retries.
- **Autoscaling Inference:** KFServing HPA scales replicas based on request rate; scale-to-zero for idle models.
- **Efficient Storage:** Use S3/GCS lifecycle policies for artifact expiration; deduplicate model checkpoints.

## Troubleshooting
- **Pipeline stuck:** Check pod logs via `kubectl logs -n kubeflow <pod>`; verify artifact paths and secrets.
- **MLflow unreachable:** Ensure service DNS resolves; check backend/artifact store connectivity.
- **Serving errors:** Inspect KFServing predictor logs; validate model format (ONNX/TorchScript/SavedModel).
- **Drift false positives:** Tune thresholds; ensure reference dataset represents production distribution.

## Hiring Manager Highlights
- Demonstrates **full MLOps lifecycle** from experimentation to production serving with governance gates.
- **Multi-tool integration:** Kubeflow, MLflow, Feast, KFServing show breadth across orchestration, tracking, features, and serving.
- **Production-minded:** Includes drift detection, cost controls, security (RBAC, signing), and operational runbooks.
- **Scalable architecture:** GPU training, auto-scaling inference, and spot instances mirror real enterprise ML platforms.

# Project 6: Machine Learning Pipeline (MLOps Platform)

## Overview
This project delivers an end-to-end MLOps workflow for training, evaluating, registering, and deploying machine learning models. The platform combines MLflow for experiment tracking, Optuna for automated hyperparameter tuning, and a modular deployment layer that targets Kubernetes, AWS Lambda, or Amazon SageMaker.

## Architecture
```mermaid
diagram LR
  data[Feature Store] --> prep[Data Preprocessing Service]
  prep --> tune[Optuna Study]
  tune --> train[Model Training Jobs]
  train --> mlflow[(MLflow Tracking + Registry)]
  mlflow --> deploy{Deployment Orchestrator}
  deploy -->|Kubernetes| kube[Model Serving on EKS]
  deploy -->|Lambda| lambda[AWS Lambda Inference]
  deploy -->|SageMaker| sm[Managed Endpoint]
  mlflow --> monitor[Monitoring + Drift Detection]
```

### Key Components
- **Experiment Runner** – wraps data ingestion, preprocessing, and training with tracked artifacts.
- **AutoML Optimizer** – Optuna search space with MLflow callback for metric logging.
- **Deployment Manager** – promotes registry versions and builds runtime-specific deployment manifests.
- **Monitoring Service** – performs drift checks and schedules retraining workflows.

## Implementations
- **Primary:** Python-based platform using MLflow, Optuna, and scikit-learn/XGBoost.
- **Alternative 1:** SageMaker Pipelines definition for managed workflows (template provided).
- **Alternative 2:** Kubeflow Pipelines component specification for on-cluster orchestration.

## Getting Started
```bash
# Set up virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Launch local MLflow tracking server (example)
mlflow server --backend-store-uri sqlite:///mlruns.db --default-artifact-root ./mlruns

# Run a training experiment
./scripts/run_training.sh configs/churn-experiment.yaml
```

## Observability & Ops
- MLflow metrics dashboards and artifacts for experiment traceability.
- Prometheus-compatible metrics exporter for inference endpoints.
- Drift detection callbacks that open tickets via Slack/webhook integrations.

## Documentation
Refer to the `docs/` directory for decision records, runbooks, and integration guides.

## Testing
```bash
# From repository root
python -m pytest projects/6-mlops-platform/tests
```

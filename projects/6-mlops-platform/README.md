# Project 6: Machine Learning Pipeline (MLOps Platform)

## Overview
This project delivers an end-to-end MLOps workflow for training, evaluating, registering, and deploying machine learning models. The platform combines MLflow for experiment tracking, Optuna for automated hyperparameter tuning, and a modular deployment layer that targets Kubernetes, AWS Lambda, or Amazon SageMaker.

## Phase 2 Architecture Diagram

![MLOps Platform – Phase 2](render locally to PNG; output is .gitignored)

- **Context**: Feature and label stores feed an experimentation boundary where preprocessing, AutoML, and training jobs log
  lineage and artifacts into MLflow before promotion.
- **Decision**: Separate delivery and serving trust zones so CI/CD and the deployment orchestrator can promote signed model
  versions into EKS, Lambda, or SageMaker with observability hooks per runtime.
- **Consequences**: Drift and telemetry signals loop back into the pipeline to trigger retraining while registry promotion
  remains auditable. Keep the [Mermaid source](assets/diagrams/architecture.mmd) synchronized with the exported PNG.

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

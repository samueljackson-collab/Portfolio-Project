# Project 6: Machine Learning Pipeline (MLOps Platform)

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
- **Experiment Runner** – wraps data ingestion, preprocessing, and training with tracked artifacts in [`src/mlops_pipeline.py`](src/mlops_pipeline.py).
- **Configurations** – sample experiment settings in [`configs/churn-experiment.yaml`](configs/churn-experiment.yaml) and dependency pinning in [`requirements.txt`](requirements.txt).
- **CI Pipeline** – GitHub Actions workflow [`./.github/workflows/ci.yml`](.github/workflows/ci.yml) executing pytest guardrails in [`tests/`](tests/).
- **Container + Runtime** – lightweight image definition in [`docker/Dockerfile`](docker/Dockerfile) and Kubernetes deployment in [`k8s/model-serving.yaml`](k8s/model-serving.yaml).
- **Observability** – Prometheus alerting rules in [`monitoring/monitoring-rules.yml`](monitoring/monitoring-rules.yml).
- **Validation** – Pytest coverage for the orchestrator and configs in [`tests/test_mlops_pipeline.py`](tests/test_mlops_pipeline.py).
- **Docs & Ops** – Runbook in [`RUNBOOK.md`](RUNBOOK.md) with supporting notes in [`wiki/overview.md`](wiki/overview.md).

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

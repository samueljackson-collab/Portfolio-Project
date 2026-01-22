# Project 6: Machine Learning Pipeline (MLOps Platform)

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


## Live Deployment
| Detail | Value |
| --- | --- |
| Live URL | `https://6-mlops-platform.staging.portfolio.example.com` |
| DNS | `6-mlops-platform.staging.portfolio.example.com` → `CNAME portfolio-gateway.staging.example.net` |
| Deployment environment | Staging (AWS us-east-1, containerized services) |

### Deployment automation
- **CI/CD:** GitHub Actions [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) gates builds; [`.github/workflows/deploy-portfolio.yml`](../../.github/workflows/deploy-portfolio.yml) publishes the staging stack.
- **Manual steps:** Follow the project Quick Start/Runbook instructions in this README to build artifacts, apply IaC, and validate health checks.

### Monitoring
- **Prometheus:** `https://prometheus.staging.portfolio.example.com` (scrape config: `prometheus/prometheus.yml`)
- **Grafana:** `https://grafana.staging.portfolio.example.com` (dashboard JSON: `grafana/dashboards/*.json`)

### Live deployment screenshots
Live deployment dashboard screenshot stored externally.


## 📊 Portfolio Status Board

🟢 Done · 🟠 In Progress · 🔵 Planned

**Current Status:** 🟢 Done (Implemented)


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


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Machine Learning Components

#### 1. Training Pipeline
```
Create a PyTorch training pipeline with data loaders, model checkpointing, TensorBoard logging, and early stopping for a classification task
```

#### 2. Model Serving
```
Generate a FastAPI service that serves ML model predictions with request validation, batch inference support, and Prometheus metrics for latency/throughput
```

#### 3. Feature Engineering
```
Write a feature engineering pipeline that handles missing values, encodes categorical variables, normalizes numerical features, and creates interaction terms
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables

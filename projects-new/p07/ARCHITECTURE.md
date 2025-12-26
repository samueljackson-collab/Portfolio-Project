# P07 Architecture Diagrams

## End-to-End ML Lifecycle
```mermaid
graph LR
    subgraph Sources
      DS[Data Sources]
    end
    subgraph FeatureStore
      FO[Feast Offline]
      FON[Feast Online]
    end
    subgraph Pipeline
      KFP[Kubeflow Pipeline]
      TR[Training Job GPU]
      EVAL[Evaluation]
    end
    subgraph Registry
      MLF[MLflow Tracking]
      REG[MLflow Registry]
    end
    subgraph Serving
      KFS[KFServing InferenceService]
      PRED[Predictor Pod]
    end
    subgraph Monitoring
      DRIFT[Drift Detector]
      DASH[Grafana Dashboard]
    end
    DS --> FO
    FO --> KFP
    KFP --> TR
    TR --> MLF
    TR --> EVAL
    EVAL --> REG
    REG --> KFS
    KFS --> PRED
    PRED --> DRIFT
    DRIFT --> DASH
    DRIFT -->|Retrain Trigger| KFP
    FON --> PRED
```
**Explanation:** Data flows from sources into Feast offline store for training. Kubeflow pipelines orchestrate training on GPU nodes, log experiments to MLflow, and register models. Approved models deploy to KFServing inference services backed by Feast online features. Drift detectors monitor predictions and feature distributions, triggering retraining when thresholds are breached. Dashboards visualize model performance and infrastructure health.

## Pipeline Topology
```mermaid
graph TB
    subgraph KubeflowPipeline
      direction TB
      INGEST[Data Ingestion Component]
      VALIDATE[Data Validation Component]
      FEAT[Feature Engineering Component]
      TRAIN[Training Component]
      EVAL[Evaluation Component]
      REG[Registration Component]
    end
    subgraph Artifacts
      DATA[Dataset Artifact]
      MODEL[Model Artifact]
      METRICS[Metrics Artifact]
    end
    INGEST --> DATA
    DATA --> VALIDATE
    VALIDATE --> FEAT
    FEAT --> TRAIN
    TRAIN --> MODEL
    TRAIN --> METRICS
    MODEL --> EVAL
    METRICS --> EVAL
    EVAL -->|Pass Gate| REG
    REG --> MLFLOW[(MLflow Registry)]
```
**Explanation:** Each pipeline component is a containerized step with defined inputs/outputs. Data ingestion loads raw data and outputs a dataset artifact. Validation runs quality checks (Great Expectations). Feature engineering pulls from Feast or computes on-the-fly. Training component consumes features and produces a model artifact plus metrics. Evaluation compares against baseline; if passing, registration component uploads model to MLflow registry with metadata (git SHA, dataset version, approver).

## Serving Strategies
```mermaid
graph LR
    subgraph Traffic
      USER[User Requests]
    end
    subgraph InferenceService
      ING[Istio Gateway]
      CANARY[Canary v2 10%]
      PROD[Production v1 90%]
    end
    subgraph Rollback
      RB[Rollback to v1]
    end
    USER --> ING
    ING -->|10%| CANARY
    ING -->|90%| PROD
    CANARY -->|Errors High| RB
    RB --> PROD
```
**Explanation:** KFServing leverages Istio VirtualServices for traffic splitting. New model version (v2) receives 10% canary traffic while v1 serves 90%. Monitoring compares error rates and latency; if v2 exceeds thresholds, traffic reverts to v1. Alternatively, shadow mode can mirror traffic to v2 without affecting responses, and A/B testing routes based on user cohort. Rollout completes when v2 metrics match or beat v1.

## Drift Detection & Retraining Loop
```mermaid
graph TB
    PRED[Prediction Service]
    LOG[Prediction Logs]
    DRIFT[Drift Detector Job]
    ALERT[Alert: Drift Detected]
    TRIGGER[Retraining Trigger]
    PIPELINE[Kubeflow Pipeline]
    PRED --> LOG
    LOG --> DRIFT
    DRIFT -->|Threshold Exceeded| ALERT
    ALERT --> TRIGGER
    TRIGGER --> PIPELINE
    PIPELINE -->|New Model| PRED
```
**Explanation:** Prediction service logs feature vectors and predictions to a data sink (S3/BigQuery). Drift detector runs periodically (hourly/daily), computing statistical tests (KS test, PSI, KL divergence) between current and reference distributions. When drift score exceeds threshold, an alert fires and triggers a retraining pipeline run. The new model is evaluated, registered, and deployed if it improves over the current production model. This closes the loop, ensuring models adapt to evolving data patterns.

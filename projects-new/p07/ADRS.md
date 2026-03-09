# Architecture Decision Records

## ADR-001: Kubeflow vs Airflow for ML Pipelines
- **Context:** Need orchestration for multi-step ML workflows with artifact passing, retries, and monitoring.
- **Decision:** Use Kubeflow Pipelines.
- **Alternatives:** Apache Airflow, Argo Workflows, AWS Step Functions.
- **Pros:** Native K8s integration, containerized components, ML-specific features (artifact lineage, experiment tracking integration), visual DAG editor.
- **Cons:** Learning curve; heavier weight than Airflow for simple workflows.
- **Consequences:** Standardize on KFP for all ML pipelines; invest in training and templates.
- **Revisit:** If team shifts to Airflow-first stack or managed ML services (SageMaker/Vertex AI) become preferred.

## ADR-002: MLflow for Experiment Tracking and Model Registry
- **Context:** Need centralized tracking of experiments, hyperparameters, metrics, and versioned model registry.
- **Decision:** Deploy MLflow Tracking Server with PostgreSQL backend and S3 artifact storage.
- **Alternatives:** Weights & Biases, Neptune.ai, cloud-native (SageMaker Experiments, Vertex AI).
- **Pros:** Open-source, self-hosted control, broad framework support, model registry with stage transitions.
- **Cons:** Requires infra maintenance; less polished UI than commercial tools.
- **Consequences:** All experiments must log to MLflow; model promotion workflow enforced via registry.
- **Revisit:** If operational burden too high or team requests advanced collaboration features.

## ADR-003: Feast for Feature Store
- **Context:** Need consistent feature serving for training (offline) and inference (online) with point-in-time correctness.
- **Decision:** Use Feast with S3 offline store and Redis online store.
- **Alternatives:** Tecton, AWS Feature Store, custom solution.
- **Pros:** Open-source, flexibility in storage backends, proven at scale (Gojek, Twitter).
- **Cons:** Operational complexity; community support variability.
- **Consequences:** Feature definitions codified in Feast repo; materialization jobs scheduled; online store monitored.
- **Revisit:** If Redis scalability issues arise or managed feature store (Tecton) budget approved.

## ADR-004: KFServing (KServe) vs Custom Inference Service
- **Context:** Need scalable, multi-framework model serving with canary/A/B testing and auto-scaling.
- **Decision:** Use KFServing (KServe) with Istio for traffic management.
- **Alternatives:** TorchServe/TensorFlow Serving standalone, custom FastAPI service, Seldon Core.
- **Pros:** Kubernetes-native, multi-framework, built-in canary/explainability, integrates with Kubeflow.
- **Cons:** Istio dependency adds complexity; custom predictors require Python SDK knowledge.
- **Consequences:** All production models deployed via InferenceService CRD; Istio VirtualServices managed automatically.
- **Revisit:** If Istio operational burden too high or team prefers simpler REST API approach.

## ADR-005: GPU Node Strategy (On-Demand vs Spot)
- **Context:** Training jobs require expensive GPU compute; budget constraints require cost optimization.
- **Decision:** Use spot/preemptible instances for training with checkpoint-based fault tolerance; on-demand for critical inference.
- **Alternatives:** On-demand only, reserved instances, serverless (SageMaker Training Jobs).
- **Pros:** 60-90% cost savings on spot; Kubeflow handles retries on interruption.
- **Cons:** Training duration variability; requires checkpointing discipline.
- **Consequences:** All training pipelines must save checkpoints; spot interruption metrics tracked; inference never on spot.
- **Revisit:** If spot unavailability > 20% or training SLAs tighten.

## ADR-006: Retraining Trigger Design (Schedule vs Drift-Based)
- **Context:** Models degrade over time due to data drift; need automated retraining without manual intervention.
- **Decision:** Hybrid approach: weekly scheduled retraining + drift-triggered retraining when threshold exceeded.
- **Alternatives:** Schedule-only (e.g., daily/weekly), drift-only, manual trigger.
- **Pros:** Scheduled ensures freshness even without drift; drift-triggered catches sudden shifts.
- **Cons:** Potential for frequent retraining if drift thresholds too sensitive; compute cost.
- **Consequences:** Drift detector runs daily; thresholds tuned monthly; retraining cost budgeted.
- **Revisit:** If drift alerts too noisy or business prefers longer retrain cycles.

## ADR-007: Model Serving Runtime (Python vs ONNX vs TorchScript)
- **Context:** Need performant inference with flexibility for custom preprocessing and multi-framework support.
- **Decision:** Use Python-based KFServing predictors with optional ONNX conversion for latency-critical models.
- **Alternatives:** Pure ONNX Runtime, TorchScript, TensorFlow SavedModel.
- **Pros:** Python flexibility for custom logic, Feast integration; ONNX for optimized serving when needed.
- **Cons:** Python interpreter overhead vs compiled runtimes; serialization/versioning complexity.
- **Consequences:** Standard predictor template provided; ONNX conversion added to pipeline for latency SLAs < 100ms.
- **Revisit:** If latency requirements tighten or Rust/C++ predictors needed.

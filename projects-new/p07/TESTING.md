# P07 Testing Strategy (MLOps)

## Strategy Overview
- **Data Quality:** Validate schema, ranges, distributions with Great Expectations; fail pipeline on critical violations.
- **Training Reproducibility:** Pin seeds, versions, and data snapshots; verify deterministic outputs.
- **Pipeline Reliability:** Contract tests for component I/O; integration tests for full pipeline on sample data.
- **Serving Correctness:** Unit tests for predictor logic; load tests for latency/throughput SLAs.
- **Drift Detection Accuracy:** Synthetic drift scenarios; verify alerts fire and thresholds tuned.
- **Security:** Model signature validation; RBAC enforcement; secret scanning in images.
- **CI Stages:**
  - **Per-commit:** Lint (flake8/mypy), unit tests (pytest), component contract tests.
  - **Nightly:** Full pipeline dry-run on staging data, serving smoke tests, drift detector validation.
  - **Pre-prod:** Load tests, security scans (Trivy), promotion gate checks.

## Test Matrix
| ID | Category | Description | Preconditions | Steps | Expected | Tools |
|----|----------|-------------|---------------|-------|----------|-------|
| T01 | Data/Feature | Validate feature store consistency | Feast repo deployed | Query offline/online stores for same entity+timestamp | Values match within tolerance | pytest, Feast SDK |
| T02 | Training | Reproducible training run | Fixed seed, dataset version | Run training twice with same params | Model weights identical (hash match) | pytest, MLflow |
| T03 | Pipeline | Component contract: data ingestion | Sample CSV in S3 | Run ingestion component | Output artifact schema valid, row count correct | kfp, pytest |
| T04 | Pipeline | Component contract: feature engineering | Valid dataset artifact | Run feature component | Output features match schema, no nulls | kfp, pytest |
| T05 | Pipeline | Full pipeline execution | Staging Kubeflow cluster | Submit pipeline with test data | All steps succeed, model registered to MLflow staging | kfp SDK, assertions |
| T06 | Serving | Model metrics threshold gate | Trained model with known accuracy | Evaluation component runs | Only models above threshold proceed to registration | pytest, MLflow |
| T07 | Serving | Inference latency SLA | KFServing deployed | Send 100 requests, measure p95 latency | p95 < 200ms | locust, pytest |
| T08 | Serving | Inference error rate | KFServing with valid/invalid payloads | Send mixed requests | Error rate < 1% for valid; 100% rejection for invalid | locust, assertions |
| T09 | Drift | Drift detection alert | Inject synthetic drift (shifted distribution) | Run drift detector | Alert fires; retraining triggered | pytest, mocked data |
| T10 | Drift | False positive rate | Reference data resampled | Run drift detector on non-drifted data | No alerts fired | pytest |
| T11 | Security | Model signature validation | Signed model with cosign | Deploy unsigned model | KFServing rejects deployment | kubectl, cosign verify |
| T12 | Security | RBAC enforcement | Non-privileged service account | Attempt to create InferenceService | Permission denied | kubectl, pytest |
| T13 | Security | Secret scanning in images | Pipeline component images | Scan with Trivy/Grype | No secrets or critical CVEs | CI pipeline |
| T14 | Performance | Training on GPU nodes | GPU node pool available | Submit training job | Job scheduled on GPU, completes faster than CPU baseline | kubectl, metrics |
| T15 | Performance | Autoscaling inference replicas | KFServing HPA configured | Send burst traffic | Replicas scale up; requests served without 503s | locust, kubectl |
| T16 | Rollback | Canary rollback on error spike | v2 deployed with canary | Inject errors in v2 predictor | Traffic reverts to v1; alerts fire | pytest, Istio metrics |
| T17 | Cost | Spot instance training | Spot node pool configured | Submit training job | Job uses spot nodes; cost < on-demand baseline | kubectl, cost reports |
| T18 | Integration | MLflow registry promotion | Model in staging | Promote to production via API | Model version transitions; tags updated | pytest, MLflow SDK |
| T19 | Integration | Feast feature retrieval in serving | Online store populated | Request features for entity | Features returned with correct timestamp | pytest, Feast SDK |
| T20 | Compliance | Model lineage captured | Pipeline run complete | Query MLflow for model metadata | Git SHA, dataset version, approver recorded | pytest, MLflow API |

## Performance/Load Notes
- Baseline inference latency on 1 replica; scale to N replicas and verify linear throughput.
- Simulate burst traffic with locust; validate HPA scales within 60s and maintains SLA.
- Training on GPU should complete in < 50% of CPU time for same dataset/model.

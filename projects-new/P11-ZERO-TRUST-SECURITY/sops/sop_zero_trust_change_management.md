# SOP: Zero-Trust Change Management
- Submit change request documenting SPIRE entries, Envoy config, and OPA policy modifications.
- Obtain security approval and schedule maintenance window.
- Apply changes via GitOps pipeline with mandatory `opa test` and `kubectl diff` gates.
- Post-change verification using integration script and dashboard review.

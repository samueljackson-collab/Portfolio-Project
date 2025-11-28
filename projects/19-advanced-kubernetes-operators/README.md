# Project 19: Advanced Kubernetes Operators

## Overview
Custom resource operator built with Kopf (Kubernetes Operator Pythonic Framework) that manages portfolio deployments and orchestrates database migrations.

## Architecture
- **Context:** Portfolio deployment intents are expressed as custom resources that must be validated, reconciled, and translated into app rollouts and database migrations with observability hooks.
- **Decision:** Use admission webhooks for pre-flight validation, Kopf reconcilers to drive workloads, and a metrics endpoint to track reconciliation health and drift corrections.
- **Consequences:** Simplifies multi-step rollouts via declarative CRDs, but operator health must be closely monitored to avoid stalled migrations or silent drift.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Run Locally
```bash
pip install -r requirements.txt
kopf run src/operator.py
```

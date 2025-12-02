# Project 12: Quantum Computing Integration

## Overview
Prototype hybrid workloads that offload optimization subproblems to quantum circuits using Qiskit, while orchestrating classical pipelines in AWS Batch.

## Architecture
- **Context:** Portfolio optimizations are launched from notebooks or batch jobs and must transparently route work to either quantum hardware or a classical fallback while capturing performance telemetry.
- **Decision:** Use an AWS Batch control plane to pre-process inputs, transpile Qiskit circuits, and dispatch to a quantum provider queue with a CloudWatch-observed fallback to simulated annealing when QPU capacity is constrained.
- **Consequences:** Enables reliable experimentation with QPUs without blocking delivery timelines, but requires careful monitoring of queue latency and fidelity drift between quantum and classical paths.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Usage
```bash
pip install -r requirements.txt
python src/portfolio_optimizer.py
```

## Highlights
- Implements a variational quantum eigensolver (VQE) for portfolio optimization.
- Automatic fallback to classical simulated annealing when quantum job queue is unavailable.
- Metrics exported to CloudWatch for performance tracking.

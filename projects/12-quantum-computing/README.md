# Project 12: Quantum Computing Integration

## Overview
Prototype hybrid workloads that offload optimization subproblems to quantum circuits using Qiskit, while orchestrating classical pipelines in AWS Batch.

## Usage
```bash
pip install -r requirements.txt
python src/portfolio_optimizer.py
```

## Highlights
- Implements a variational quantum eigensolver (VQE) for portfolio optimization.
- Automatic fallback to classical simulated annealing when quantum job queue is unavailable.
- Metrics exported to CloudWatch for performance tracking.

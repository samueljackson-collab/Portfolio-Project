# Project 18: GPU-Accelerated Computing Platform

## Overview
CUDA-based risk simulation engine with Dask integration for scale-out workloads.

## Architecture
- **Context:** Quant workloads must submit GPU-intensive simulations through a shared control plane that schedules containers across GPU nodes while exposing metrics back to analysts.
- **Decision:** Provide a job API backed by Dask scheduling, container registry images for reproducibility, and shared storage with Prometheus telemetry for feedback loops.
- **Consequences:** Unlocks elastic GPU capacity with traceability, but requires careful image governance and capacity planning to avoid queue congestion.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Running Locally
```bash
pip install -r requirements.txt
python src/monte_carlo.py --iterations 1000000
```

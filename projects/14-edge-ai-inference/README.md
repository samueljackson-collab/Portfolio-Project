# Project 14: Edge AI Inference Platform

## Overview
Containerized ONNX Runtime microservice optimized for NVIDIA Jetson devices with automatic model updates via Azure IoT Edge.

## Architecture
- **Context:** Edge cameras send frames to a Jetson-hosted inference microservice that must run offline, accept OTA model updates, and forward telemetry to the cloud.
- **Decision:** Use an IoT Edge runtime with MQTT routing, ONNX Runtime for accelerated inference, and a cloud model registry feeding OTA updates with monitoring hooks.
- **Consequences:** Maintains low-latency local predictions with controlled rollouts, but requires disciplined OTA governance to prevent regressions on constrained devices.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Running Locally
```bash
pip install -r requirements.txt
python src/inference_service.py --model models/resnet50.onnx --image sample.jpg
```

## Deployment
- Build container using provided `Dockerfile`.
- Push to Azure Container Registry.
- Deploy IoT Edge deployment manifest under `deployments/`.

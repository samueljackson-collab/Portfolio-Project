# Project 14: Edge AI Inference Platform

## Overview
Containerized ONNX Runtime microservice optimized for NVIDIA Jetson devices with automatic model updates via Azure IoT Edge.

## Running Locally
```bash
pip install -r requirements.txt
python src/inference_service.py --model models/resnet50.onnx --image sample.jpg
```

## Deployment
- Build container using provided `Dockerfile`.
- Push to Azure Container Registry.
- Deploy IoT Edge deployment manifest under `deployments/`.

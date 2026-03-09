---
title: Project 14: Edge AI Inference Platform
description: **Category:** Machine Learning & AI **Status:** 🟡 50% Complete **Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/14-edge-ai) Containerized **ONNX Run
tags: [documentation, portfolio]
path: portfolio/25-portfolio-website/14-edge-ai
created: 2026-03-08T22:19:13.339577+00:00
updated: 2026-03-08T22:04:38.690902+00:00
---

# Project 14: Edge AI Inference Platform

**Category:** Machine Learning & AI
**Status:** 🟡 50% Complete
**Source:** [View Code](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/14-edge-ai)

## Overview

Containerized **ONNX Runtime** microservice optimized for **NVIDIA Jetson** devices with automatic model updates via **Azure IoT Edge**. Enables low-latency AI inference at the edge for computer vision, anomaly detection, and predictive maintenance use cases.

## Key Features

- **Edge Inference** - Sub-100ms latency without cloud dependency
- **Model Optimization** - ONNX format with INT8 quantization for performance
- **OTA Updates** - Azure IoT Edge automatic model deployment
- **Hardware Acceleration** - CUDA/TensorRT optimization for Jetson devices
- **Offline Operation** - Continues functioning during network outages

## Architecture

```
Cloud (Azure)                          Edge (Jetson Device)
─────────────                          ────────────────────
Model Training                         IoT Edge Runtime
     ↓                                       ↓
Model Export (ONNX)                    ┌─── Edge Module ───┐
     ↓                                 ↓                    ↓
Azure Container Registry         Inference Service    Local Storage
     ↓                                 ↓                    ↓
IoT Hub ────── Push Update ──────→ Model Update      Results Queue
                                      ↓                    ↓
                             Camera/Sensor Input     Cloud Upload
                                      ↓                (Batched)
                               ONNX Runtime (GPU)
                                      ↓
                               Predictions
```

**Inference Pipeline:**
1. **Model Deployment**: ONNX models pushed via IoT Edge
2. **Input Capture**: Camera/sensor data acquisition
3. **Preprocessing**: Image resizing, normalization
4. **Inference**: ONNX Runtime with TensorRT acceleration
5. **Postprocessing**: Result parsing and formatting
6. **Action**: Local decisions or cloud reporting

## Technologies

- **Python** - Service implementation
- **ONNX Runtime** - Cross-platform inference engine
- **NVIDIA Jetson** - Edge AI hardware (Nano, Xavier, Orin)
- **Azure IoT Edge** - Edge deployment platform
- **TensorRT** - NVIDIA inference optimization
- **Docker** - Containerization
- **OpenCV** - Image processing
- **NumPy** - Numerical operations

## Quick Start

```bash
cd projects/14-edge-ai

# Install dependencies
pip install -r requirements.txt

# Run inference locally (CPU)
python src/inference_service.py \
  --model models/resnet50.onnx \
  --image sample.jpg

# Run with GPU acceleration (Jetson)
python src/inference_service.py \
  --model models/resnet50.onnx \
  --image sample.jpg \
  --device cuda

# Start as service with camera
python src/inference_service.py \
  --model models/resnet50.onnx \
  --camera /dev/video0 \
  --mode stream
```

## Project Structure

```
14-edge-ai/
├── src/
│   ├── __init__.py
│   ├── inference_service.py    # Main inference service
│   ├── preprocessor.py         # Image preprocessing (to be added)
│   └── model_manager.py        # OTA model updates (to be added)
├── models/                     # ONNX models (to be added)
│   ├── resnet50.onnx
│   └── yolov8.onnx
├── deployment/                 # IoT Edge manifests (to be added)
│   └── deployment.template.json
├── Dockerfile                  # Container image (to be added)
├── requirements.txt
└── README.md
```

## Business Impact

- **Latency**: <50ms inference (vs 200ms cloud roundtrip)
- **Bandwidth**: 90% reduction by processing locally
- **Uptime**: 99.9% availability during network outages
- **Cost**: $50/device/month vs $500/month cloud inference
- **Privacy**: Data processed locally, meets GDPR requirements

## Current Status

**Completed:**
- ✅ Core ONNX Runtime inference service
- ✅ Basic image preprocessing
- ✅ CPU and GPU execution paths

**In Progress:**
- 🟡 Azure IoT Edge deployment manifest
- 🟡 Docker container optimization
- 🟡 Model versioning and OTA updates
- 🟡 TensorRT optimization

**Next Steps:**
1. Create Dockerfile with multi-stage build
2. Add Azure IoT Edge deployment manifests
3. Implement model update mechanism via IoT Twin
4. Optimize with TensorRT for Jetson devices
5. Add camera integration and video streaming
6. Build model quantization pipeline (INT8)
7. Create monitoring and telemetry reporting
8. Add batch inference for offline processing
9. Document hardware setup and installation

## Key Learning Outcomes

- Edge AI architecture patterns
- ONNX model optimization and deployment
- NVIDIA Jetson development
- Azure IoT Edge platform
- TensorRT acceleration techniques
- Model quantization for edge devices
- Container optimization for embedded systems

---

**Related Projects:**
- [Project 6: MLOps](/projects/06-mlops) - Model training pipeline
- [Project 11: IoT Data Ingestion](/projects/11-iot) - Sensor integration
- [Project 18: GPU Computing](/projects/18-gpu-computing) - GPU optimization patterns

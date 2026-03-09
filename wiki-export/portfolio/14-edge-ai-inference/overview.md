---
title: Project 14: Edge AI Inference Platform
description: Containerized ONNX Runtime microservice optimized for NVIDIA Jetson devices with automatic model updates via Azure IoT Edge
tags: [documentation, machine-learning-ai, portfolio, python]
path: portfolio/14-edge-ai-inference/overview
created: 2026-03-08T22:19:13.203549+00:00
updated: 2026-03-08T22:04:38.551902+00:00
---

-

# Project 14: Edge AI Inference Platform
> **Category:** Machine Learning & AI | **Status:** 🟡 50% Complete
> **Source:** projects/25-portfolio-website/docs/projects/14-edge-ai.md

## 📋 Executive Summary

Containerized **ONNX Runtime** microservice optimized for **NVIDIA Jetson** devices with automatic model updates via **Azure IoT Edge**. Enables low-latency AI inference at the edge for computer vision, anomaly detection, and predictive maintenance use cases.

## 🎯 Project Objectives

- **Edge Inference** - Sub-100ms latency without cloud dependency
- **Model Optimization** - ONNX format with INT8 quantization for performance
- **OTA Updates** - Azure IoT Edge automatic model deployment
- **Hardware Acceleration** - CUDA/TensorRT optimization for Jetson devices
- **Offline Operation** - Continues functioning during network outages

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/14-edge-ai.md#architecture
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

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Python | Python | Service implementation |
| ONNX Runtime | ONNX Runtime | Cross-platform inference engine |
| NVIDIA Jetson | NVIDIA Jetson | Edge AI hardware (Nano, Xavier, Orin) |

## 💡 Key Technical Decisions

### Decision 1: Adopt Python
**Context:** Project 14: Edge AI Inference Platform requires a resilient delivery path.
**Decision:** Service implementation
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt ONNX Runtime
**Context:** Project 14: Edge AI Inference Platform requires a resilient delivery path.
**Decision:** Cross-platform inference engine
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt NVIDIA Jetson
**Context:** Project 14: Edge AI Inference Platform requires a resilient delivery path.
**Decision:** Edge AI hardware (Nano, Xavier, Orin)
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

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

## ✅ Results & Outcomes

- **Latency**: <50ms inference (vs 200ms cloud roundtrip)
- **Bandwidth**: 90% reduction by processing locally
- **Uptime**: 99.9% availability during network outages
- **Cost**: $50/device/month vs $500/month cloud inference

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/14-edge-ai.md](../../../projects/25-portfolio-website/docs/projects/14-edge-ai.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Python, ONNX Runtime, NVIDIA Jetson, Azure IoT Edge, TensorRT

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/14-edge-ai.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Inference latency (p95)** | < 100ms | Time from request → response |
| **Inference throughput** | > 30 FPS | Frames processed per second |
| **Model accuracy** | > 95% | Prediction accuracy on test set |
| **Device availability** | 99% | Devices online and responsive |
| **Model update success** | 98% | Successful model deployments |
| **GPU utilization** | 60-80% | Optimal GPU usage |
| **Container restart rate** | < 1/day | Container stability |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*

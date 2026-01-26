# Runbook — Project 14 (Edge AI Inference Platform)

## Overview

Production operations runbook for Edge AI Inference Platform. This runbook covers ONNX Runtime microservice operations, NVIDIA Jetson device management, Azure IoT Edge deployment, model lifecycle management, and performance monitoring for edge AI workloads.

**System Components:**
- ONNX Runtime (inference engine)
- Docker containers (microservice deployment)
- NVIDIA Jetson devices (edge hardware)
- Azure IoT Edge (edge runtime and orchestration)
- Azure Container Registry (model and container storage)
- Model update service (automatic model deployment)
- Telemetry and monitoring (metrics, logs)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Inference latency (p95)** | < 100ms | Time from request → response |
| **Inference throughput** | > 30 FPS | Frames processed per second |
| **Model accuracy** | > 95% | Prediction accuracy on test set |
| **Device availability** | 99% | Devices online and responsive |
| **Model update success** | 98% | Successful model deployments |
| **GPU utilization** | 60-80% | Optimal GPU usage |
| **Container restart rate** | < 1/day | Container stability |

---

## Dashboards & Alerts

### Dashboards

#### Edge Device Health
```bash
# Check device status via Azure IoT Hub
az iot hub device-identity list \
  --hub-name edge-ai-hub \
  --query "[].{deviceId:deviceId,status:connectionState}" \
  --output table

# Check specific device
DEVICE_ID="jetson-device-01"
az iot hub device-identity show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub

# SSH to device and check health
ssh jetson@jetson-device-01.local
nvidia-smi
docker ps
df -h
```

#### Inference Performance
```bash
# Check inference metrics (on device)
ssh jetson@jetson-device-01.local
curl -s http://localhost:8000/metrics | grep inference

# Expected output:
# inference_requests_total 15234
# inference_latency_ms_p95 87.3
# inference_fps 32.5
# model_load_time_seconds 2.1

# Check GPU utilization
ssh jetson@jetson-device-01.local "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv"

# Check inference logs
ssh jetson@jetson-device-01.local "docker logs inference-service --tail 100"
```

#### Model Deployment Status
```bash
# Check deployed models across fleet
az iot hub query \
  --hub-name edge-ai-hub \
  --query-command "SELECT deviceId, properties.reported.model.name, properties.reported.model.version FROM devices"

# Check model versions in ACR
az acr repository list \
  --name edgeairegistry \
  --output table

az acr repository show-tags \
  --name edgeairegistry \
  --repository models/resnet50 \
  --output table

# Check pending deployments
az iot edge deployment list \
  --hub-name edge-ai-hub \
  --output table
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All edge devices offline | Immediate | Check IoT Hub, network connectivity |
| **P0** | Inference service crashed | Immediate | Restart container, check logs |
| **P1** | Device offline > 5 minutes | 15 minutes | Check device, investigate connectivity |
| **P1** | Inference latency > 200ms | 15 minutes | Check model, GPU, optimize |
| **P1** | Model deployment failed | 30 minutes | Review deployment manifest, rollback |
| **P2** | High GPU temperature (>80°C) | 1 hour | Check cooling, reduce workload |
| **P2** | Low GPU utilization (<40%) | 2 hours | Review batching, optimize pipeline |
| **P2** | Disk usage > 80% | 2 hours | Clean old models, logs |
| **P3** | Container restart | 4 hours | Review logs, investigate cause |

#### Alert Queries

```bash
# Check device connectivity
OFFLINE_DEVICES=$(az iot hub device-identity list \
  --hub-name edge-ai-hub \
  --query "[?connectionState=='Disconnected'].deviceId" \
  --output tsv | wc -l)

if [ $OFFLINE_DEVICES -gt 0 ]; then
  echo "ALERT: $OFFLINE_DEVICES edge devices offline"
fi

# Check inference latency (on device)
ssh jetson@jetson-device-01.local << 'EOF'
LATENCY=$(curl -s http://localhost:8000/metrics | grep inference_latency_ms_p95 | awk '{print $2}')
if [ $(echo "$LATENCY > 200" | bc) -eq 1 ]; then
  echo "ALERT: Inference latency is ${LATENCY}ms (threshold: 200ms)"
fi
EOF

# Check GPU temperature
ssh jetson@jetson-device-01.local << 'EOF'
TEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
if [ $TEMP -gt 80 ]; then
  echo "ALERT: GPU temperature is ${TEMP}°C"
fi
EOF

# Check container status
ssh jetson@jetson-device-01.local << 'EOF'
if ! docker ps | grep -q inference-service; then
  echo "ALERT: Inference service container not running"
  exit 1
fi
EOF

# Check model deployment failures
FAILED_DEPLOYMENTS=$(az iot edge deployment show \
  --deployment-id model-deployment-latest \
  --hub-name edge-ai-hub \
  --query "systemMetrics.results.failedCount" \
  --output tsv)

if [ "$FAILED_DEPLOYMENTS" -gt 0 ]; then
  echo "ALERT: $FAILED_DEPLOYMENTS devices failed model deployment"
fi
```

---

## Standard Operations

### Edge Device Management

#### Provision New Device
```bash
# Create device identity in IoT Hub
DEVICE_ID="jetson-device-02"
az iot hub device-identity create \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub \
  --edge-enabled

# Get device connection string
CONNECTION_STRING=$(az iot hub device-identity connection-string show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub \
  --query connectionString \
  --output tsv)

# Configure device (on Jetson device)
ssh jetson@jetson-device-02.local << EOF
sudo apt-get update
sudo apt-get install -y iotedge

# Configure IoT Edge
sudo bash -c "cat > /etc/iotedge/config.yaml << 'IOTCONFIG'
provisioning:
  source: \"manual\"
  device_connection_string: \"$CONNECTION_STRING\"
IOTCONFIG"

# Start IoT Edge
sudo systemctl restart iotedge
EOF

# Verify device connected
az iot hub device-identity show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub \
  --query connectionState
```

#### Check Device Health
```bash
# Check device from Azure
DEVICE_ID="jetson-device-01"
az iot hub device-identity show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub

# Check device twin (reported properties)
az iot hub device-twin show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub \
  --query "properties.reported" | jq .

# SSH to device for detailed check
ssh jetson@jetson-device-01.local << 'EOF'
# Check IoT Edge runtime
sudo systemctl status iotedge

# Check running modules
sudo iotedge list

# Check system resources
echo "=== CPU ==="
top -bn1 | grep "Cpu(s)"

echo "=== Memory ==="
free -h

echo "=== Disk ==="
df -h

echo "=== GPU ==="
nvidia-smi

echo "=== Temperature ==="
cat /sys/devices/virtual/thermal/thermal_zone*/temp
EOF
```

#### Restart Device or Service
```bash
# Restart IoT Edge runtime (on device)
ssh jetson@jetson-device-01.local "sudo systemctl restart iotedge"

# Restart specific module
DEVICE_ID="jetson-device-01"
MODULE_NAME="inference-service"
az iot hub module-twin update \
  --device-id $DEVICE_ID \
  --module-id $MODULE_NAME \
  --hub-name edge-ai-hub \
  --set properties.desired.restartModule=true

# Reboot device
ssh jetson@jetson-device-01.local "sudo reboot"

# Verify after restart
sleep 60
az iot hub device-identity show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub \
  --query connectionState
```

### Container and Service Management

#### Deploy Inference Service
```bash
# Build Docker image
cd /home/user/Portfolio-Project/projects/14-edge-ai-inference
docker build -t inference-service:v1.0 .

# Tag for ACR
ACR_NAME="edgeairegistry"
docker tag inference-service:v1.0 ${ACR_NAME}.azurecr.io/inference-service:v1.0

# Push to ACR
az acr login --name $ACR_NAME
docker push ${ACR_NAME}.azurecr.io/inference-service:v1.0

# Create deployment manifest
cat > deployments/inference-deployment.json << 'EOF'
{
  "modulesContent": {
    "$edgeAgent": {
      "properties.desired": {
        "schemaVersion": "1.1",
        "runtime": {
          "type": "docker",
          "settings": {
            "minDockerVersion": "v1.25",
            "registryCredentials": {
              "edgeairegistry": {
                "username": "$REGISTRY_USERNAME",
                "password": "$REGISTRY_PASSWORD",
                "address": "edgeairegistry.azurecr.io"
              }
            }
          }
        },
        "systemModules": {
          "edgeAgent": {
            "type": "docker",
            "settings": {
              "image": "mcr.microsoft.com/azureiotedge-agent:1.4",
              "createOptions": {}
            }
          },
          "edgeHub": {
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": "mcr.microsoft.com/azureiotedge-hub:1.4",
              "createOptions": {
                "HostConfig": {
                  "PortBindings": {
                    "5671/tcp": [{"HostPort": "5671"}],
                    "8883/tcp": [{"HostPort": "8883"}],
                    "443/tcp": [{"HostPort": "443"}]
                  }
                }
              }
            }
          }
        },
        "modules": {
          "inference-service": {
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": "edgeairegistry.azurecr.io/inference-service:v1.0",
              "createOptions": {
                "HostConfig": {
                  "Runtime": "nvidia",
                  "PortBindings": {
                    "8000/tcp": [{"HostPort": "8000"}]
                  },
                  "Binds": [
                    "/data/models:/models"
                  ]
                }
              }
            },
            "env": {
              "MODEL_PATH": {
                "value": "/models/resnet50.onnx"
              },
              "DEVICE": {
                "value": "cuda"
              }
            }
          }
        }
      }
    }
  }
}
EOF

# Deploy to device
az iot edge set-modules \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub \
  --content deployments/inference-deployment.json

# Verify deployment
az iot hub module-identity list \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub \
  --output table

# Check on device
ssh jetson@jetson-device-01.local "sudo iotedge list"
```

#### Update Container Image
```bash
# Build new version
docker build -t inference-service:v1.1 .
docker tag inference-service:v1.1 ${ACR_NAME}.azurecr.io/inference-service:v1.1
docker push ${ACR_NAME}.azurecr.io/inference-service:v1.1

# Update deployment manifest
vim deployments/inference-deployment.json
# Change: "image": "edgeairegistry.azurecr.io/inference-service:v1.1"

# Rolling update to all devices
az iot edge deployment create \
  --deployment-id inference-update-$(date +%Y%m%d-%H%M%S) \
  --hub-name edge-ai-hub \
  --content deployments/inference-deployment.json \
  --target-condition "tags.environment='production'" \
  --priority 10

# Monitor rollout
watch -n 5 'az iot edge deployment show \
  --deployment-id inference-update-latest \
  --hub-name edge-ai-hub \
  --query "systemMetrics.results"'
```

#### View Container Logs
```bash
# View logs on device
ssh jetson@jetson-device-01.local << 'EOF'
# All IoT Edge module logs
sudo iotedge logs inference-service

# Follow logs
sudo iotedge logs -f inference-service

# Last 100 lines
sudo iotedge logs --tail 100 inference-service

# Or use Docker directly
docker logs inference-service
EOF

# Stream logs to Azure Log Analytics (if configured)
az monitor log-analytics query \
  --workspace edge-ai-workspace \
  --analytics-query "ContainerLog | where Image contains 'inference-service' | order by TimeGenerated desc | limit 100"
```

### Model Management

#### Deploy New Model
```bash
# Convert model to ONNX (if needed)
python src/convert_to_onnx.py \
  --input-model models/pytorch_model.pth \
  --output models/resnet50.onnx

# Test model locally
python src/inference_service.py \
  --model models/resnet50.onnx \
  --image sample.jpg \
  --test

# Upload model to Azure Blob Storage
az storage blob upload \
  --account-name edgeaistorage \
  --container-name models \
  --name resnet50_v2.onnx \
  --file models/resnet50.onnx

# Generate SAS token for model download
SAS_TOKEN=$(az storage blob generate-sas \
  --account-name edgeaistorage \
  --container-name models \
  --name resnet50_v2.onnx \
  --permissions r \
  --expiry $(date -u -d '+30 days' +%Y-%m-%dT%H:%M:%SZ) \
  --output tsv)

MODEL_URL="https://edgeaistorage.blob.core.windows.net/models/resnet50_v2.onnx?${SAS_TOKEN}"

# Update device twin to trigger model update
az iot hub device-twin update \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub \
  --set properties.desired.model="{\"name\":\"resnet50\",\"version\":\"v2\",\"url\":\"$MODEL_URL\"}"

# Monitor update on device
ssh jetson@jetson-device-01.local "tail -f /var/log/model-updater.log"
```

#### Rollback Model
```bash
# Get previous model version
PREVIOUS_MODEL_URL="https://edgeaistorage.blob.core.windows.net/models/resnet50_v1.onnx?${SAS_TOKEN}"

# Rollback via device twin
az iot hub device-twin update \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub \
  --set properties.desired.model="{\"name\":\"resnet50\",\"version\":\"v1\",\"url\":\"$PREVIOUS_MODEL_URL\"}"

# Or rollback entire deployment
az iot edge deployment create \
  --deployment-id model-rollback-$(date +%Y%m%d-%H%M%S) \
  --hub-name edge-ai-hub \
  --content deployments/inference-deployment-v1.json \
  --target-condition "tags.environment='production'" \
  --priority 20  # Higher priority

# Verify rollback
az iot hub device-twin show \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub \
  --query "properties.reported.model"
```

#### List and Manage Models
```bash
# List models on device
ssh jetson@jetson-device-01.local "ls -lh /data/models/"

# Check current active model
ssh jetson@jetson-device-01.local "readlink /data/models/current"

# Remove old models to free space
ssh jetson@jetson-device-01.local << 'EOF'
# Keep only last 3 model versions
cd /data/models
ls -t *.onnx | tail -n +4 | xargs rm -f
EOF

# List models in Azure storage
az storage blob list \
  --account-name edgeaistorage \
  --container-name models \
  --output table
```

### Performance Optimization

#### Optimize Inference Performance
```bash
# Enable TensorRT acceleration (on device)
ssh jetson@jetson-device-01.local << 'EOF'
# Stop service
docker stop inference-service

# Run with TensorRT
docker run -d \
  --name inference-service \
  --runtime nvidia \
  -p 8000:8000 \
  -v /data/models:/models \
  -e MODEL_PATH=/models/resnet50.onnx \
  -e USE_TENSORRT=true \
  -e TENSORRT_PRECISION=fp16 \
  edgeairegistry.azurecr.io/inference-service:latest

# Verify TensorRT is active
docker logs inference-service | grep TensorRT
EOF

# Adjust batch size for throughput
ssh jetson@jetson-device-01.local << 'EOF'
# Update configuration
docker exec inference-service curl -X POST http://localhost:8000/config \
  -H "Content-Type: application/json" \
  -d '{"batch_size": 4, "num_threads": 4}'
EOF

# Monitor performance impact
ssh jetson@jetson-device-01.local << 'EOF'
watch -n 1 'curl -s http://localhost:8000/metrics | grep -E "fps|latency"'
EOF
```

#### Monitor GPU Performance
```bash
# Real-time GPU monitoring
ssh jetson@jetson-device-01.local << 'EOF'
# Install jetson-stats if not present
sudo pip3 install jetson-stats

# Monitor with jtop
sudo jtop

# Or use nvidia-smi
watch -n 1 nvidia-smi
EOF

# Check power mode
ssh jetson@jetson-device-01.local "sudo nvpmodel -q"

# Set to maximum performance mode
ssh jetson@jetson-device-01.local "sudo nvpmodel -m 0"

# Set jetson clocks for maximum performance
ssh jetson@jetson-device-01.local "sudo jetson_clocks"
```

#### Optimize Docker Configuration
```bash
# Update Docker daemon settings (on device)
ssh jetson@jetson-device-01.local << 'EOF'
sudo bash -c 'cat > /etc/docker/daemon.json << DOCKER_CONFIG
{
  "default-runtime": "nvidia",
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  },
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
DOCKER_CONFIG'

sudo systemctl restart docker
EOF
```

### Monitoring and Telemetry

#### Configure Telemetry
```bash
# Enable Azure Monitor integration
az iot hub update \
  --name edge-ai-hub \
  --set properties.enableFileUploadNotifications=true

# Configure metrics collection on device
ssh jetson@jetson-device-01.local << 'EOF'
# Install monitoring agent
pip3 install azure-iot-device prometheus-client

# Configure metrics endpoint
cat > /etc/inference/metrics_config.yaml << METRICS
metrics:
  enabled: true
  port: 9090
  interval_seconds: 30

  collectors:
    - system  # CPU, memory, disk
    - gpu     # GPU utilization, temperature
    - inference  # Latency, throughput, accuracy

  azure_monitor:
    enabled: true
    workspace_id: $WORKSPACE_ID
    workspace_key: $WORKSPACE_KEY
METRICS

# Restart metrics collector
sudo systemctl restart metrics-collector
EOF
```

#### Query Telemetry
```bash
# Query device metrics from Azure
az monitor metrics list \
  --resource "/subscriptions/$SUB_ID/resourceGroups/edge-ai-rg/providers/Microsoft.Devices/IotHubs/edge-ai-hub" \
  --metric "d2c.telemetry.egress.success" \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)

# Query inference metrics from Log Analytics
az monitor log-analytics query \
  --workspace edge-ai-workspace \
  --analytics-query "
    InferenceMetrics
    | where DeviceId == 'jetson-device-01'
    | where TimeGenerated > ago(1h)
    | summarize
        avg(InferenceLatencyMs),
        avg(FPS),
        avg(GPUUtilization)
      by bin(TimeGenerated, 5m)
    | order by TimeGenerated desc
  "

# Export metrics for analysis
az monitor log-analytics query \
  --workspace edge-ai-workspace \
  --analytics-query "InferenceMetrics | where TimeGenerated > ago(24h)" \
  --output json > metrics_export_$(date +%Y%m%d).json
```

---

## Incident Response

### Detection

**Automated Detection:**
- Azure IoT Hub alerts
- Device twin property changes
- Container health checks
- Performance threshold breaches

**Manual Detection:**
```bash
# Check overall fleet health
az iot hub device-identity list \
  --hub-name edge-ai-hub \
  --query "[?connectionState=='Disconnected']" \
  --output table

# Check inference service health
for device in jetson-device-{01..10}; do
  echo "=== $device ==="
  ssh jetson@$device.local "docker ps | grep inference-service" || echo "ISSUE: Service not running"
done

# Review recent alerts
az monitor activity-log list \
  --resource-group edge-ai-rg \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --query "[?contains(category, 'Alert')]"

# Check device logs
ssh jetson@jetson-device-01.local "sudo journalctl -u iotedge --since '10 minutes ago' | grep -i error"
```

### Triage

#### Severity Classification

### P0: Service Outage
- All edge devices offline
- Inference service crashed on critical devices
- Model serving completely failed
- Data loss occurring

### P1: Degraded Service
- Multiple devices offline (>20%)
- High inference latency (>200ms)
- Model deployment failed across fleet
- GPU failures

### P2: Performance Issues
- Single device offline
- Elevated latency (100-200ms)
- Container restart loops
- Disk space warnings

### P3: Minor Issues
- Non-critical telemetry gaps
- Individual inference errors
- Minor performance degradation

### Incident Response Procedures

#### P0: Inference Service Crashed

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check service status
DEVICE_ID="jetson-device-01"
ssh jetson@jetson-device-01.local "docker ps -a | grep inference-service"

# 2. Check logs for crash reason
ssh jetson@jetson-device-01.local "docker logs inference-service --tail 100" | grep -i "error\|exception\|killed"

# 3. Attempt restart
ssh jetson@jetson-device-01.local "docker restart inference-service"

# 4. If restart fails, redeploy
ssh jetson@jetson-device-01.local << 'EOF'
docker stop inference-service
docker rm inference-service
docker pull edgeairegistry.azurecr.io/inference-service:latest
docker run -d \
  --name inference-service \
  --runtime nvidia \
  --restart always \
  -p 8000:8000 \
  -v /data/models:/models \
  edgeairegistry.azurecr.io/inference-service:latest
EOF

# 5. Verify service restored
ssh jetson@jetson-device-01.local "curl -f http://localhost:8000/health"
```

**Investigation (5-20 minutes):**
```bash
# Check system resources
ssh jetson@jetson-device-01.local << 'EOF'
# Check OOM kills
dmesg | grep -i "out of memory"

# Check disk space
df -h

# Check GPU status
nvidia-smi

# Check for core dumps
ls -lh /var/crash/
EOF

# Check recent device twin updates
az iot hub device-twin show \
  --device-id $DEVICE_ID \
  --hub-name edge-ai-hub \
  --query "properties.desired" | jq .

# Review model file integrity
ssh jetson@jetson-device-01.local << 'EOF'
cd /data/models
md5sum *.onnx
ls -lh current
EOF
```

**Recovery:**
```bash
# If model corruption, re-download
ssh jetson@jetson-device-01.local << 'EOF'
# Backup current model
mv /data/models/current /data/models/current.bak

# Download fresh model
MODEL_URL="https://edgeaistorage.blob.core.windows.net/models/resnet50.onnx?${SAS_TOKEN}"
wget -O /data/models/resnet50.onnx "$MODEL_URL"
ln -s /data/models/resnet50.onnx /data/models/current

# Restart service
docker restart inference-service
EOF

# If resource exhaustion, clean up
ssh jetson@jetson-device-01.local << 'EOF'
# Clean Docker
docker system prune -af --volumes

# Clean logs
sudo journalctl --vacuum-time=7d

# Remove old models
cd /data/models
ls -t *.onnx | tail -n +3 | xargs rm -f
EOF

# If persistent issues, rollback to known-good config
az iot edge deployment create \
  --deployment-id emergency-rollback-$(date +%Y%m%d-%H%M%S) \
  --hub-name edge-ai-hub \
  --content deployments/inference-deployment-stable.json \
  --target-condition "deviceId='$DEVICE_ID'" \
  --priority 100

# Verify recovery
sleep 30
ssh jetson@jetson-device-01.local "curl -s http://localhost:8000/metrics | grep fps"
```

#### P1: High Inference Latency

**Investigation:**
```bash
# Check inference metrics
ssh jetson@jetson-device-01.local "curl -s http://localhost:8000/metrics"

# Check GPU utilization
ssh jetson@jetson-device-01.local "nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv"

# Check CPU load
ssh jetson@jetson-device-01.local "uptime; ps aux --sort=-%cpu | head -10"

# Check thermal throttling
ssh jetson@jetson-device-01.local "cat /sys/devices/virtual/thermal/thermal_zone*/temp"

# Test inference locally
ssh jetson@jetson-device-01.local << 'EOF'
time curl -X POST http://localhost:8000/infer \
  -F "image=@/data/test_images/sample.jpg"
EOF
```

**Mitigation:**
```bash
# Enable maximum performance mode
ssh jetson@jetson-device-01.local << 'EOF'
sudo nvpmodel -m 0
sudo jetson_clocks
EOF

# Reduce batch size if GPU memory pressure
ssh jetson@jetson-device-01.local << 'EOF'
docker exec inference-service curl -X POST http://localhost:8000/config \
  -d '{"batch_size": 1}'
EOF

# Enable TensorRT if not already
ssh jetson@jetson-device-01.local << 'EOF'
docker exec inference-service curl -X POST http://localhost:8000/config \
  -d '{"use_tensorrt": true, "tensorrt_precision": "fp16"}'
EOF

# If model is too large, deploy smaller variant
az iot hub device-twin update \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub \
  --set properties.desired.model="{\"name\":\"mobilenet\",\"version\":\"v2\"}"

# Restart with optimizations
ssh jetson@jetson-device-01.local "docker restart inference-service"

# Monitor improvement
ssh jetson@jetson-device-01.local << 'EOF'
for i in {1..10}; do
  curl -s http://localhost:8000/metrics | grep -E "latency|fps"
  sleep 5
done
EOF
```

#### P1: Model Deployment Failed

**Investigation:**
```bash
# Check deployment status
DEPLOYMENT_ID="model-deployment-latest"
az iot edge deployment show \
  --deployment-id $DEPLOYMENT_ID \
  --hub-name edge-ai-hub \
  --query "{targetCondition, systemMetrics, labels}"

# List devices with failed deployment
az iot hub query \
  --hub-name edge-ai-hub \
  --query-command "
    SELECT deviceId, properties.reported.lastDesiredStatus
    FROM devices
    WHERE properties.reported.lastDesiredStatus.code != 200
  "

# Check specific device logs
DEVICE_ID="jetson-device-01"
ssh jetson@$DEVICE_ID.local "sudo iotedge logs edgeAgent --tail 100"

# Check model download logs
ssh jetson@$DEVICE_ID.local "tail -100 /var/log/model-updater.log"
```

**Recovery:**
```bash
# Verify model URL is accessible
ssh jetson@jetson-device-01.local << 'EOF'
MODEL_URL=$(sudo iotedge logs edgeAgent | grep "Downloading model" | tail -1 | awk '{print $NF}')
wget --spider "$MODEL_URL" || echo "Model URL inaccessible"
EOF

# Re-generate SAS token if expired
NEW_SAS=$(az storage blob generate-sas \
  --account-name edgeaistorage \
  --container-name models \
  --name resnet50_v2.onnx \
  --permissions r \
  --expiry $(date -u -d '+30 days' +%Y-%m-%dT%H:%M:%SZ) \
  --output tsv)

NEW_URL="https://edgeaistorage.blob.core.windows.net/models/resnet50_v2.onnx?${NEW_SAS}"

# Update deployment with new URL
vim deployments/inference-deployment.json
# Update model URL

az iot edge deployment create \
  --deployment-id model-deployment-retry-$(date +%Y%m%d-%H%M%S) \
  --hub-name edge-ai-hub \
  --content deployments/inference-deployment.json \
  --target-condition "tags.environment='production'" \
  --priority 15

# Or manually download model on device
ssh jetson@jetson-device-01.local << 'EOF'
wget -O /data/models/resnet50_v2.onnx "$NEW_URL"
ln -sf /data/models/resnet50_v2.onnx /data/models/current
docker restart inference-service
EOF

# Verify deployment success
watch -n 10 'az iot edge deployment show \
  --deployment-id model-deployment-retry-latest \
  --hub-name edge-ai-hub \
  --query "systemMetrics.results"'
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/edge-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Edge AI Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 1 hour
**Affected Devices:** jetson-device-01, jetson-device-02

## Timeline
- 14:00: Alert - high inference latency detected
- 14:05: Identified thermal throttling due to cooling fan failure
- 14:15: Reduced workload, enabled max cooling
- 14:30: Cooling restored, performance recovered
- 15:00: Incident closed

## Root Cause
Cooling fan failure on Jetson devices caused thermal throttling

## Actions Taken
- Enabled maximum cooling policy
- Reduced inference batch size temporarily
- Replaced cooling fans

## Action Items
- [ ] Implement fan health monitoring
- [ ] Add thermal alerts
- [ ] Create cooling failure runbook
- [ ] Order spare cooling fans

EOF

# Update monitoring
# Add fan RPM monitoring
ssh jetson@jetson-device-01.local << 'EOF'
# Install fan monitoring
sudo apt-get install -y lm-sensors
sudo sensors-detect --auto

# Add to monitoring
echo "fan_rpm=$(sensors | grep 'fan' | awk '{print $2}')" >> /etc/telegraf/telegraf.conf
EOF

# Test improvements
./scripts/thermal_stress_test.sh jetson-device-01
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (model and config backup frequency)
- **RTO** (Recovery Time Objective): 15 minutes (device reprovisioning)

### Backup Strategy

**Device Configuration Backup:**
```bash
# Backup device twin
az iot hub device-twin show \
  --device-id jetson-device-01 \
  --hub-name edge-ai-hub > backups/device-twin-jetson-01-$(date +%Y%m%d).json

# Backup IoT Edge configuration (on device)
ssh jetson@jetson-device-01.local << 'EOF'
sudo tar czf /tmp/iotedge-backup-$(date +%Y%m%d).tar.gz \
  /etc/iotedge/ \
  /data/models/ \
  /etc/inference/

# Transfer to central storage
scp /tmp/iotedge-backup-*.tar.gz backup-server:/backups/edge-devices/
EOF
```

**Model Backup:**
```bash
# Models are already backed up in Azure Blob Storage
# Verify backup
az storage blob list \
  --account-name edgeaistorage \
  --container-name models \
  --output table

# Create additional backup
az storage blob copy start-batch \
  --source-account-name edgeaistorage \
  --source-container models \
  --destination-account-name edgeaibackup \
  --destination-container models-backup
```

### Disaster Recovery Procedures

#### Device Failure - Complete Replacement

**Recovery Steps (15-30 minutes):**
```bash
# 1. Provision new device in IoT Hub
NEW_DEVICE_ID="jetson-device-01-new"
az iot hub device-identity create \
  --device-id $NEW_DEVICE_ID \
  --hub-name edge-ai-hub \
  --edge-enabled

# 2. Copy tags from old device
OLD_TAGS=$(az iot hub device-twin show --device-id jetson-device-01 --hub-name edge-ai-hub --query tags)
az iot hub device-twin update \
  --device-id $NEW_DEVICE_ID \
  --hub-name edge-ai-hub \
  --set tags="$OLD_TAGS"

# 3. Setup new Jetson device
CONNECTION_STRING=$(az iot hub device-identity connection-string show \
  --device-id $NEW_DEVICE_ID \
  --hub-name edge-ai-hub \
  --query connectionString \
  --output tsv)

ssh jetson@new-device.local << EOF
# Install IoT Edge
./scripts/install_iotedge.sh

# Configure
sudo bash -c "echo 'device_connection_string: \"$CONNECTION_STRING\"' > /etc/iotedge/config.yaml"

# Start
sudo systemctl start iotedge
EOF

# 4. Deployment will auto-apply based on tags
# Verify
watch -n 5 'az iot hub module-identity list --device-id $NEW_DEVICE_ID --hub-name edge-ai-hub'

# 5. Decommission old device
az iot hub device-identity delete --device-id jetson-device-01 --hub-name edge-ai-hub
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check device connectivity
az iot hub device-identity list --hub-name edge-ai-hub \
  --query "[?connectionState=='Disconnected'].deviceId"

# Review inference metrics
./scripts/daily_metrics_report.sh

# Check container health
for device in jetson-device-{01..10}; do
  ssh jetson@$device.local "docker ps" || echo "$device: Issue"
done
```

### Weekly Tasks
```bash
# Review and clean old models
for device in jetson-device-{01..10}; do
  ssh jetson@$device.local "cd /data/models && ls -t *.onnx | tail -n +3 | xargs rm -f"
done

# Update container images
docker pull edgeairegistry.azurecr.io/inference-service:latest

# Review performance trends
az monitor log-analytics query --workspace edge-ai-workspace \
  --analytics-query "InferenceMetrics | summarize avg(InferenceLatencyMs) by bin(TimeGenerated, 1d) | order by TimeGenerated"

# Backup device configurations
./scripts/backup_device_configs.sh
```

### Monthly Tasks
```bash
# Update IoT Edge runtime
for device in jetson-device-{01..10}; do
  ssh jetson@$device.local << 'EOF'
    sudo apt-get update
    sudo apt-get upgrade -y iotedge
    sudo systemctl restart iotedge
EOF
done

# Review and optimize models
python src/model_optimization_analysis.py

# Security updates
for device in jetson-device-{01..10}; do
  ssh jetson@$device.local "sudo apt-get update && sudo apt-get upgrade -y"
done

# Disaster recovery drill
./scripts/dr_drill.sh
```

---

## Quick Reference

### Most Common Operations
```bash
# Check device status
az iot hub device-identity show --device-id jetson-device-01 --hub-name edge-ai-hub

# Restart inference service
ssh jetson@jetson-device-01.local "docker restart inference-service"

# Check inference metrics
ssh jetson@jetson-device-01.local "curl http://localhost:8000/metrics"

# Deploy new model
az iot hub device-twin update --device-id jetson-device-01 \
  --set properties.desired.model='{"name":"resnet50","version":"v2"}'

# View container logs
ssh jetson@jetson-device-01.local "sudo iotedge logs inference-service"

# Check GPU status
ssh jetson@jetson-device-01.local "nvidia-smi"
```

### Emergency Response
```bash
# P0: Service crashed - Restart
ssh jetson@jetson-device-01.local "docker restart inference-service"

# P1: High latency - Enable max performance
ssh jetson@jetson-device-01.local "sudo nvpmodel -m 0 && sudo jetson_clocks"

# P1: Deployment failed - Manual model download
ssh jetson@jetson-device-01.local "wget -O /data/models/model.onnx $MODEL_URL"

# P2: Device offline - Check IoT Edge
ssh jetson@jetson-device-01.local "sudo systemctl restart iotedge"
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Edge AI Platform Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates

# Runbook — Project 18 (GPU-Accelerated Computing Platform)

## Overview

Production operations runbook for the GPU-Accelerated Computing Platform, implementing CUDA-based Monte Carlo risk simulations with Dask for distributed scale-out workloads and GPU cluster management.

**System Components:**
- CUDA runtime and GPU compute kernels
- Dask distributed scheduler for parallel processing
- GPU cluster with NVIDIA GPUs (V100/A100/T4)
- Kubernetes GPU operator for resource management
- RAPIDS libraries (cuDF, cuML) for accelerated analytics
- GPU monitoring (nvidia-smi, dcgm-exporter)
- Job queue management system
- Result storage and caching layer

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **GPU compute availability** | 99% | GPU worker node uptime |
| **Simulation job success rate** | 98% | Completed jobs / submitted jobs |
| **Job queue wait time (p95)** | < 5 minutes | Time from submission → execution |
| **GPU utilization** | 70-90% | Average GPU compute utilization |
| **Simulation accuracy** | > 99.9% | Monte Carlo convergence validation |
| **Memory error rate** | < 0.01% | GPU memory ECC errors per day |
| **Job completion time (p95)** | < 30 minutes | Time to complete 1M iteration simulation |

---

## Dashboards & Alerts

### Dashboards

#### GPU Cluster Health Dashboard
```bash
# Check GPU node status
kubectl get nodes -l nvidia.com/gpu=true -o wide

# Check GPU resources
kubectl describe nodes -l nvidia.com/gpu=true | grep -A 10 "Allocatable:\|Allocated resources:"

# Check GPU pods
kubectl get pods -A -o json | \
  jq '.items[] | select(.spec.containers[].resources.limits."nvidia.com/gpu" != null) | {name: .metadata.name, namespace: .metadata.namespace, gpu: .spec.containers[0].resources.limits."nvidia.com/gpu"}'

# Check GPU device plugin
kubectl get daemonset -n kube-system nvidia-device-plugin-daemonset
```

#### GPU Utilization Dashboard
```bash
# Check GPU utilization on all nodes
for node in $(kubectl get nodes -l nvidia.com/gpu=true -o name); do
  echo "=== $node ==="
  kubectl debug $node -it --image=nvidia/cuda:11.8.0-base-ubuntu22.04 -- nvidia-smi --query-gpu=index,name,utilization.gpu,utilization.memory,memory.used,memory.total --format=csv
done

# Check DCGM metrics (if deployed)
kubectl port-forward -n monitoring svc/dcgm-exporter 9400:9400 &
curl -s http://localhost:9400/metrics | grep -E "(DCGM_FI_DEV_GPU_UTIL|DCGM_FI_DEV_MEM_COPY_UTIL)"
```

#### Job Status Dashboard
```bash
# Check Dask scheduler status
kubectl get pods -n compute -l component=scheduler

# Check Dask worker status
kubectl get pods -n compute -l component=worker

# Access Dask dashboard
kubectl port-forward -n compute svc/dask-scheduler 8787:8787
# Open http://localhost:8787 in browser

# Check job queue status
kubectl exec -n compute deploy/dask-scheduler -- \
  dask-scheduler --show-tasks
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | GPU node down | Immediate | Drain workloads, investigate hardware |
| **P0** | GPU memory ECC errors | Immediate | Cordon node, run diagnostics |
| **P0** | All Dask workers down | Immediate | Restart scheduler/workers, check logs |
| **P1** | GPU utilization < 20% | 30 minutes | Investigate job scheduling, resource allocation |
| **P1** | Job failure rate > 5% | 15 minutes | Check CUDA errors, memory issues |
| **P2** | High GPU temperature (> 85°C) | 1 hour | Check cooling, reduce workload |
| **P2** | Job queue backlog > 100 | 1 hour | Scale up workers, optimize jobs |

#### Alert Queries (Prometheus)

```promql
# GPU node down
up{job="nvidia-dcgm-exporter"} == 0

# Low GPU utilization
avg_over_time(DCGM_FI_DEV_GPU_UTIL[5m]) < 20

# High GPU temperature
DCGM_FI_DEV_GPU_TEMP > 85

# GPU memory errors
increase(DCGM_FI_DEV_ECC_DBE_VOL_TOTAL[1h]) > 0

# High job failure rate
(
  rate(dask_jobs_failed_total[5m])
  /
  rate(dask_jobs_total[5m])
) > 0.05

# Dask worker down
absent(up{job="dask-worker"})
```

---

## Standard Operations

### GPU Cluster Management

#### Verify GPU Setup
```bash
# Check NVIDIA driver version on nodes
kubectl get nodes -l nvidia.com/gpu=true -o json | \
  jq '.items[] | {name: .metadata.name, driver: .status.nodeInfo.kubeletVersion}'

# Check GPU device plugin is running
kubectl get daemonset -n kube-system nvidia-device-plugin-daemonset
kubectl get pods -n kube-system -l name=nvidia-device-plugin-ds

# Verify GPU resources are advertised
kubectl get nodes -l nvidia.com/gpu=true -o json | \
  jq '.items[] | {name: .metadata.name, gpu: .status.capacity."nvidia.com/gpu"}'

# Test GPU access from pod
kubectl run gpu-test --rm -it --restart=Never \
  --image=nvidia/cuda:11.8.0-base-ubuntu22.04 \
  --limits=nvidia.com/gpu=1 -- nvidia-smi
```

#### Scale GPU Workers
```bash
# Scale up Dask GPU workers
kubectl scale deployment dask-worker -n compute --replicas=10

# Check worker registration
kubectl exec -n compute deploy/dask-scheduler -- \
  python -c "from dask.distributed import Client; c = Client('localhost:8786'); print(c.scheduler_info())"

# Verify GPU allocation
kubectl get pods -n compute -l component=worker -o json | \
  jq '.items[] | {name: .metadata.name, gpu: .spec.containers[0].resources.limits."nvidia.com/gpu"}'

# Scale down workers
kubectl scale deployment dask-worker -n compute --replicas=5
```

#### Monitor GPU Health
```bash
# Check GPU health on specific node
NODE_NAME="gpu-node-1"
kubectl debug node/$NODE_NAME -it --image=nvidia/cuda:11.8.0-base-ubuntu22.04 -- bash

# Inside debug pod:
nvidia-smi
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total,power.draw --format=csv

# Check for GPU errors
nvidia-smi -q | grep -A 5 "ECC Errors"

# Run GPU diagnostics
nvidia-smi -r  # Reset GPU (requires root)
nvidia-smi --applications-clocks-permission=UNRESTRICTED
```

### Job Management

#### Submit Simulation Job
```python
# submit_job.py
from dask.distributed import Client
import numpy as np
from numba import cuda

# Connect to Dask cluster
client = Client('dask-scheduler.compute.svc.cluster.local:8786')

@cuda.jit
def monte_carlo_kernel(rng_states, results, iterations):
    """CUDA kernel for Monte Carlo simulation"""
    idx = cuda.grid(1)
    if idx < len(results):
        # Simulate risk scenario
        total = 0.0
        for i in range(iterations):
            # Generate random walk
            step = cuda.random.xoroshiro128p_normal_float32(rng_states, idx)
            total += step
        results[idx] = total / iterations

def run_simulation(num_simulations=1000000, iterations=1000):
    """Run Monte Carlo simulation on GPU"""
    # Allocate GPU memory
    results = cuda.device_array(num_simulations, dtype=np.float32)
    rng_states = cuda.random.create_xoroshiro128p_states(
        num_simulations, seed=42
    )

    # Launch kernel
    threads_per_block = 256
    blocks = (num_simulations + threads_per_block - 1) // threads_per_block
    monte_carlo_kernel[blocks, threads_per_block](
        rng_states, results, iterations
    )

    # Copy results back to host
    return results.copy_to_host()

# Submit job to Dask
future = client.submit(run_simulation, num_simulations=1000000, iterations=1000)
result = future.result()

print(f"Simulation complete: Mean={result.mean():.4f}, StdDev={result.std():.4f}")
```

```bash
# Submit job
python submit_job.py

# Or use command line
python -c "
from dask.distributed import Client
client = Client('dask-scheduler.compute.svc.cluster.local:8786')
future = client.submit(lambda: 'test')
print(future.result())
"
```

#### Monitor Running Jobs
```bash
# Check job status via Dask dashboard
kubectl port-forward -n compute svc/dask-scheduler 8787:8787

# Query job status programmatically
kubectl exec -n compute deploy/dask-scheduler -- python3 <<EOF
from dask.distributed import Client
c = Client('localhost:8786')
print("Active tasks:", len(c.processing()))
print("Queued tasks:", len(c.queued()))
print("Workers:", len(c.scheduler_info()['workers']))
for worker, info in c.scheduler_info()['workers'].items():
    print(f"  {worker}: {info['nthreads']} threads, {info['memory_limit']/(1024**3):.1f} GB")
EOF
```

#### Cancel Job
```python
# cancel_job.py
from dask.distributed import Client

client = Client('dask-scheduler.compute.svc.cluster.local:8786')

# Cancel specific task
future.cancel()

# Cancel all tasks
client.cancel(client.futures)

# Restart workers if needed
client.restart()
```

### Performance Optimization

#### Optimize GPU Memory
```python
# optimize_memory.py
import cupy as cp
from numba import cuda

# Use memory pools for faster allocation
pool = cp.cuda.MemoryPool()
cp.cuda.set_allocator(pool.malloc)

# Profile memory usage
@cuda.jit
def my_kernel(data, result):
    idx = cuda.grid(1)
    if idx < len(result):
        result[idx] = data[idx] * 2

# Use streams for concurrent execution
stream1 = cuda.stream()
stream2 = cuda.stream()

# Launch kernels on different streams
data1 = cuda.to_device(arr1, stream=stream1)
data2 = cuda.to_device(arr2, stream=stream2)

# Synchronize streams
stream1.synchronize()
stream2.synchronize()

# Free memory
pool.free_all_blocks()
```

#### Tune Job Parameters
```python
# tune_parameters.py
from dask.distributed import Client

client = Client('dask-scheduler.compute.svc.cluster.local:8786')

# Optimize chunk sizes
client.set_task_duration_threshold('10s')

# Adjust memory limits
client.amm.start_fraction = 0.7  # Use 70% of memory before spilling
client.amm.stop_fraction = 0.8   # Stop at 80%

# Configure retries
client.retry_policy = {'max_retries': 3, 'retry_delay': '5s'}

# Enable GPU memory pinning
client.set_metadata('gpu_memory_pinned', True)
```

---

## Incident Response

### P0: GPU Node Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Identify down GPU nodes
kubectl get nodes -l nvidia.com/gpu=true | grep NotReady

# 2. Check node events
kubectl describe node <node-name> | grep -A 20 Events

# 3. Drain workloads from node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 4. Check GPU device plugin logs
kubectl logs -n kube-system -l name=nvidia-device-plugin-ds --tail=100

# 5. Attempt node recovery
kubectl uncordon <node-name>
```

**Investigation (5-20 minutes):**
```bash
# SSH to node (if accessible) and check GPU status
ssh <node-name>
nvidia-smi
dmesg | grep -i nvidia
journalctl -u kubelet -n 100

# Check for GPU hardware errors
nvidia-smi -q | grep -A 10 "GPU Current Temp\|GPU Shutdown Temp\|ECC Errors"

# Check CUDA runtime
nvidia-smi --query-gpu=driver_version,cuda_version --format=csv

# Check GPU processes
nvidia-smi pmon -c 1
```

**Recovery:**
```bash
# If driver issue, reload NVIDIA modules
sudo modprobe -r nvidia_uvm nvidia_drm nvidia_modeset nvidia
sudo modprobe nvidia nvidia_modeset nvidia_drm nvidia_uvm

# Restart containerd/docker
sudo systemctl restart containerd

# Restart kubelet
sudo systemctl restart kubelet

# Verify node is Ready
kubectl get node <node-name>

# Uncordon node
kubectl uncordon <node-name>

# If hardware failure, replace node
kubectl delete node <node-name>
# Provision new GPU node
```

### P0: GPU Memory ECC Errors

**Immediate Actions:**
```bash
# 1. Identify nodes with ECC errors
for node in $(kubectl get nodes -l nvidia.com/gpu=true -o name); do
  echo "=== $node ==="
  kubectl debug $node -it --image=nvidia/cuda:11.8.0-base-ubuntu22.04 -- \
    nvidia-smi -q | grep -A 10 "ECC Errors"
done

# 2. Cordon affected nodes
kubectl cordon <node-name>

# 3. Drain workloads
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force

# 4. Document error details
kubectl debug node/<node-name> -it --image=nvidia/cuda:11.8.0-base-ubuntu22.04 -- \
  nvidia-smi -q > gpu-errors-<node-name>-$(date +%Y%m%d).log
```

**Investigation:**
```bash
# Check error counts
nvidia-smi --query-gpu=ecc.errors.corrected.volatile.total,ecc.errors.uncorrected.volatile.total --format=csv

# Run GPU memory test
nvidia-smi -r  # Reset GPU error counters
# Run test workload
# Check if errors recur

# If errors persist, GPU is faulty
```

**Mitigation:**
```bash
# If correctable errors only, may continue with monitoring
kubectl uncordon <node-name>
# Set up enhanced monitoring for the node

# If uncorrectable errors, replace GPU/node
kubectl delete node <node-name>
# RMA GPU hardware
```

### P0: All Dask Workers Down

**Immediate Actions:**
```bash
# 1. Check worker pods
kubectl get pods -n compute -l component=worker

# 2. Check worker logs
kubectl logs -n compute -l component=worker --tail=100 --all-containers=true

# 3. Check scheduler status
kubectl get pods -n compute -l component=scheduler
kubectl logs -n compute -l component=scheduler --tail=100

# 4. Restart workers
kubectl rollout restart deployment/dask-worker -n compute

# 5. Verify worker registration
kubectl exec -n compute deploy/dask-scheduler -- python3 -c "
from dask.distributed import Client
c = Client('localhost:8786')
print('Workers:', len(c.scheduler_info()['workers']))
"
```

**Common Causes & Fixes:**

**CUDA Out of Memory:**
```bash
# Check GPU memory usage
kubectl exec -n compute <worker-pod> -- nvidia-smi

# Reduce batch size in jobs
kubectl set env deployment/dask-worker -n compute BATCH_SIZE=1024

# Scale up workers to distribute load
kubectl scale deployment/dask-worker -n compute --replicas=10
```

**Network Connectivity Issue:**
```bash
# Check network between workers and scheduler
kubectl exec -n compute <worker-pod> -- \
  ping -c 3 dask-scheduler.compute.svc.cluster.local

# Check firewall rules
kubectl exec -n compute <worker-pod> -- \
  nc -zv dask-scheduler 8786

# Restart network plugin if needed
kubectl rollout restart daemonset/calico-node -n kube-system
```

### P1: High Job Failure Rate

**Investigation:**
```bash
# 1. Check failed job logs
kubectl logs -n compute -l component=worker --tail=500 | grep -i "error\|failed"

# 2. Check for CUDA errors
kubectl exec -n compute <worker-pod> -- \
  dmesg | grep -i "cuda\|gpu"

# 3. Monitor job metrics
kubectl exec -n compute deploy/dask-scheduler -- python3 <<EOF
from dask.distributed import Client
c = Client('localhost:8786')
print("Failed tasks:", c.get_task_metadata(state='error'))
EOF

# 4. Check GPU memory pressure
kubectl exec -n compute <worker-pod> -- nvidia-smi --query-compute-apps=pid,used_memory --format=csv
```

**Common Issues:**

**Insufficient GPU Memory:**
```python
# Reduce memory footprint
import cupy as cp

# Use smaller data types
data = cp.array(input_data, dtype=cp.float16)  # Instead of float32

# Process in chunks
for chunk in chunks(data, chunk_size=10000):
    process_chunk(chunk)
    cp.get_default_memory_pool().free_all_blocks()
```

**CUDA Kernel Timeout:**
```bash
# Increase timeout (node-level)
kubectl debug node/<node-name> -- bash
echo 60 > /proc/driver/nvidia/params/compute_timeout

# Or reduce kernel complexity
# Break large kernels into smaller ones
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "CUDA out of memory"

**Symptoms:**
```
RuntimeError: CUDA error: out of memory
CUDA_ERROR_OUT_OF_MEMORY
```

**Diagnosis:**
```bash
# Check GPU memory usage
kubectl exec -n compute <worker-pod> -- nvidia-smi --query-gpu=memory.used,memory.total --format=csv

# Check process memory
kubectl exec -n compute <worker-pod> -- nvidia-smi pmon -c 1
```

**Solution:**
```python
# Free GPU memory
import cupy as cp
cp.get_default_memory_pool().free_all_blocks()
cp.get_default_pinned_memory_pool().free_all_blocks()

# Use smaller batch sizes
BATCH_SIZE = 512  # Reduce from 2048

# Use memory-efficient algorithms
# Process data in streaming fashion instead of loading all at once
```

---

#### Issue: "No GPU devices found"

**Symptoms:**
```
CUDA error: no CUDA-capable device is detected
nvidia.com/gpu: 0 (no GPU resources)
```

**Diagnosis:**
```bash
# Check GPU device plugin
kubectl get daemonset -n kube-system nvidia-device-plugin-daemonset
kubectl logs -n kube-system -l name=nvidia-device-plugin-ds

# Check GPU visibility
kubectl debug node/<node-name> -it --image=nvidia/cuda:11.8.0-base-ubuntu22.04 -- nvidia-smi
```

**Solution:**
```bash
# Restart device plugin
kubectl rollout restart daemonset/nvidia-device-plugin-daemonset -n kube-system

# Verify GPU resources are advertised
kubectl get node <node-name> -o json | jq '.status.capacity'

# If still not working, check node labels
kubectl label nodes <node-name> nvidia.com/gpu=true --overwrite
```

---

#### Issue: "Dask worker not connecting to scheduler"

**Symptoms:**
```
Error: Cannot connect to scheduler
Connection refused: dask-scheduler:8786
```

**Diagnosis:**
```bash
# Check scheduler service
kubectl get svc -n compute dask-scheduler

# Check scheduler pod
kubectl get pods -n compute -l component=scheduler

# Test connectivity from worker
kubectl exec -n compute <worker-pod> -- \
  nc -zv dask-scheduler 8786
```

**Solution:**
```bash
# Restart scheduler
kubectl rollout restart deployment/dask-scheduler -n compute

# Restart workers
kubectl rollout restart deployment/dask-worker -n compute

# Check service endpoints
kubectl get endpoints -n compute dask-scheduler

# Verify network policies
kubectl get networkpolicies -n compute
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
# 1. Check GPU node status
kubectl get nodes -l nvidia.com/gpu=true

# 2. Check GPU utilization
kubectl get pods -n monitoring -l app=dcgm-exporter
kubectl port-forward -n monitoring svc/dcgm-exporter 9400:9400 &
curl -s http://localhost:9400/metrics | grep DCGM_FI_DEV_GPU_UTIL

# 3. Check Dask cluster health
kubectl get pods -n compute -l app=dask

# 4. Review job metrics
kubectl exec -n compute deploy/dask-scheduler -- python3 -c "
from dask.distributed import Client
c = Client('localhost:8786')
info = c.scheduler_info()
print(f'Workers: {len(info[\"workers\"])}')
print(f'Tasks: {info[\"tasks\"]}')
"

# 5. Check for GPU errors
for node in $(kubectl get nodes -l nvidia.com/gpu=true -o name); do
  kubectl debug $node --image=nvidia/cuda:11.8.0-base-ubuntu22.04 -- \
    nvidia-smi -q | grep -A 5 "ECC Errors"
done
```

### Weekly Tasks

```bash
# 1. Review GPU utilization trends
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
# Query: avg_over_time(DCGM_FI_DEV_GPU_UTIL[7d])

# 2. Clean up completed jobs
kubectl delete pods -n compute --field-selector=status.phase=Succeeded

# 3. Optimize Dask performance
kubectl exec -n compute deploy/dask-scheduler -- python3 -c "
from dask.distributed import Client
c = Client('localhost:8786')
c.rebalance()  # Rebalance data across workers
"

# 4. Update GPU drivers (if needed)
# Plan maintenance window
# Update nodes one by one

# 5. Review and optimize job parameters
# Analyze slow jobs
# Tune batch sizes, chunk sizes
```

### Monthly Tasks

```bash
# 1. GPU benchmark testing
kubectl run gpu-benchmark --rm -it --restart=Never \
  --image=nvidia/cuda:11.8.0-base-ubuntu22.04 \
  --limits=nvidia.com/gpu=1 -- bash
# Inside pod:
# Run CUDA samples or custom benchmarks

# 2. Capacity planning review
# Analyze GPU utilization trends
# Plan for scaling up/down

# 3. Update CUDA/driver versions
# Test on single node first
# Roll out to cluster

# 4. Disaster recovery drill
# Simulate GPU node failure
# Verify job rescheduling
# Test backup/restore procedures

# 5. Cost optimization
# Review GPU usage patterns
# Consider spot instances for non-critical workloads
# Implement auto-scaling policies
```

### Disaster Recovery

**Backup Strategy:**
```bash
# 1. Backup Dask cluster configuration
kubectl get deployment,service,configmap -n compute -o yaml > backup/dask-config.yaml

# 2. Backup GPU node configurations
kubectl get nodes -l nvidia.com/gpu=true -o yaml > backup/gpu-nodes.yaml

# 3. Backup job definitions
kubectl get jobs,cronjobs -n compute -o yaml > backup/jobs.yaml

# 4. Export monitoring configurations
kubectl get configmap,servicemonitor -n monitoring -o yaml > backup/monitoring.yaml
```

**Recovery Procedures:**
```bash
# 1. Recreate Dask cluster
kubectl apply -f backup/dask-config.yaml

# 2. Verify GPU resources
kubectl get nodes -l nvidia.com/gpu=true
kubectl describe nodes -l nvidia.com/gpu=true | grep nvidia.com/gpu

# 3. Restore jobs
kubectl apply -f backup/jobs.yaml

# 4. Validate with test job
python3 <<EOF
from dask.distributed import Client
import cupy as cp

client = Client('dask-scheduler.compute.svc.cluster.local:8786')
def gpu_test():
    x = cp.array([1, 2, 3])
    return (x * 2).get()

future = client.submit(gpu_test)
print("Test result:", future.result())
EOF
```

---

## Quick Reference

### Common Commands

```bash
# Check GPU status
kubectl get nodes -l nvidia.com/gpu=true
nvidia-smi  # On GPU node

# Submit GPU job
kubectl run gpu-job --image=my-cuda-app --limits=nvidia.com/gpu=1

# Check Dask cluster
kubectl get pods -n compute -l app=dask
kubectl port-forward -n compute svc/dask-scheduler 8787:8787

# Monitor GPU utilization
kubectl port-forward -n monitoring svc/dcgm-exporter 9400:9400
curl http://localhost:9400/metrics | grep GPU_UTIL
```

### Emergency Response

```bash
# P0: GPU node down
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data
kubectl uncordon <node-name>

# P0: ECC errors
kubectl cordon <node-name>
kubectl drain <node-name> --force

# P0: Dask workers down
kubectl rollout restart deployment/dask-worker -n compute

# P1: High job failures
kubectl logs -n compute -l component=worker --tail=100
# Fix issues and resubmit jobs
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** ML/Compute Platform Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Submit PR with updates

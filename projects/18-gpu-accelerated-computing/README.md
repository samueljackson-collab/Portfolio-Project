# Project 18 · GPU-Accelerated Compute Grid

## 📌 Overview
Build a portable GPU workload platform supporting ML training, rendering, and scientific simulation workloads. The grid delivers automated provisioning, job scheduling, and cost-aware scaling across on-premises GPU nodes and cloud bursts.

## 🏗️ Architecture Highlights
- **Kubernetes + NVIDIA GPU Operator** managing driver lifecycle, CUDA toolkit, and DCGM telemetry.
- **Slurm and KubeFlow** integration for batch and ML workloads with shared artifact storage via Ceph or FSx for Lustre.
- **Job queue and quota controls** using Volcano scheduler with fairness policies, priority classes, and preemption.
- **Hybrid bursting** via Cluster API to attach managed node groups in AWS/GCP when on-premises capacity is exhausted.
- **Observability** using DCGM Exporter, Prometheus, and Grafana dashboards with GPU temperature, utilization, and memory metrics.

```
+-------------+      +------------------+      +------------------+
| Users / CI  | ---> | Job Gateway      | ---> | GPU Node Pools   |
| (Notebooks) |      | (Kubeflow, Slurm)|      | On-prem & Cloud |
+-------------+      +------------------+      +------------------+
        |                    |                          |
        v                    v                          v
   Artifact Store     Metrics & Alerts             Auto-scaling
```

## 🚀 Implementation Steps
1. **Provision GPU nodes** with Terraform + Ansible to install base OS, container runtime, and GPU drivers for bare metal.
2. **Deploy Kubernetes** with kubeadm and install NVIDIA GPU Operator for driver lifecycle and monitoring components.
3. **Install Kubeflow** pipelines, notebooks, and Katib for hyperparameter tuning with namespace isolation.
4. **Integrate Slurm** using `slurm-operator` to schedule legacy HPC workloads while sharing the same GPU resources.
5. **Configure Volcano** scheduler queues with resource quotas and fairness policies to prioritize critical training jobs.
6. **Implement hybrid bursting** with Cluster API provider AWS to scale `g5`/`p3` instances on-demand when queue depth exceeds threshold.
7. **Publish dashboards** detailing GPU utilization, queue wait times, and per-team cost allocation metrics.

## 🧩 Key Components
```yaml
# projects/18-gpu-accelerated-computing/k8s/volcano-queue.yaml
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: research-priority
spec:
  reclaimable: true
  weight: 3
  capability:
    resources:
      - name: nvidia.com/gpu
        quantity: 16
  dispatchPolicy:
    minAvailable: 2
```

## 🛡️ Fail-safes & Operations
- **Job checkpointing** using Kubernetes `EmptyDir` + CSI snapshots or Horovod elastic training to recover from node failures.
- **Thermal safeguards** via DCGM thresholds triggering node cordoning when temperatures exceed safe limits.
- **Budget enforcement** through Kubecost with alerting when GPU-hour consumption approaches team allocations.
- **Disaster recovery** with nightly snapshots of persistent volumes replicated to cloud object storage.

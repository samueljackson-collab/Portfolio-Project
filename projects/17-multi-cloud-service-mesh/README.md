# Project 17 · Multi-Cloud Service Mesh Fabric

## 📌 Overview
Implement a federated service mesh spanning AWS, Azure, and GCP clusters to deliver consistent security, traffic policy, and observability. The mesh supports blue/green rollouts, zero-trust mTLS, and cross-cloud failover for Kubernetes microservices.

## 🏗️ Architecture Highlights
- **Consul + Istio hybrid mesh** with Consul as global control plane and Istio sidecars for workload-level policy.
- **Multi-cloud networking** using Cloud WAN / Azure Virtual WAN / Cloud Interconnect bridged via Aviatrix or Cilium Cluster Mesh.
- **Unified identity** delivered by SPIFFE/SPIRE issuing workload identities and plugging into existing IAM providers.
- **Traffic management** with weighted routing, circuit breaking, and locality-aware failover across regions.
- **Unified observability** streaming Envoy metrics to Prometheus, traces to Tempo, and logs to Loki with multi-tenant Grafana dashboards.

```
+--------------+      +-----------------+      +-----------------+
| AWS EKS Mesh |<---->| Consul Control  |<---->| Azure AKS Mesh  |
| (Istio)      |      | Plane + SPIRE   |      | (Istio)         |
+--------------+      +-----------------+      +-----------------+
        ^                                            |
        |                                            v
        +-----------------> GCP GKE Mesh (Istio) <---+
```

## 🚀 Implementation Steps
1. **Provision baseline clusters** in each cloud with Terraform modules that install CNI, ingress gateways, and node pools.
2. **Deploy Consul Enterprise** as the global catalog, enabling WAN gossip across cloud providers with mesh gateways.
3. **Install Istio** with meshConfig configured for Consul service discovery and SPIRE-issued workload certificates.
4. **Establish trust bundles** by federating SPIRE servers per cloud with a common upstream CA stored in HashiCorp Vault.
5. **Configure traffic policies** including destination rules, virtual services, outlier detection, and locality-weighted failover.
6. **Implement zero-trust** by enforcing STRICT mTLS, JWT verification, and authorization policies referencing SPIFFE IDs.
7. **Wire observability** shipping Envoy access logs to Loki, metrics to Prometheus, and traces to Tempo using OpenTelemetry collectors.

## 🧩 Key Components
```hcl
# projects/17-multi-cloud-service-mesh/terraform/istio-policy.tf
resource "kubectl_manifest" "mesh_authorization" {
  yaml_body = <<-YAML
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-cross-cloud-traffic
  namespace: payments
spec:
  selector:
    matchLabels:
      app: payments-api
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["spiffe://mesh.global/ns/frontend/sa/frontend-service"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/payments"]
YAML
}
```

## 🛡️ Fail-safes & Operations
- **Fallback routing policies** that automatically direct traffic to local cloud if global catalog becomes unavailable.
- **Continuous verification** via Chaos Mesh scenarios that sever inter-cloud links to validate graceful degradation.
- **Certificate rotation runbooks** using SPIRE agents with 24-hour TTL and Vault-signed roots rotated quarterly.
- **Cost visibility** with cloud-specific dashboards and aggregated showback reports for mesh gateway traffic.

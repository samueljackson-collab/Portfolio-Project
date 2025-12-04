# Zero-Trust Security (P11)

This lab packages a minimal SPIRE + OPA demo to showcase workload identity, sidecar policy enforcement, and namespace-level network isolation. All manifests referenced in the quick start live under `k8s/` and can be applied directly with `kubectl`.

## Prerequisites
- Kubernetes cluster with `kubectl` configured
- SPIRE-compatible nodes (Linux) and CNI that honors NetworkPolicies

## Quick Start
1. Create namespaces for SPIRE control plane and the demo workloads:
   ```bash
   kubectl apply -f k8s/namespaces.yaml
   ```
2. Deploy the SPIRE server control plane (self-signed for the lab) and its service endpoint:
   ```bash
   kubectl apply -f k8s/spire-server.yaml
   ```
3. Deploy the SPIRE agents as a DaemonSet so every node can issue SVIDs:
   ```bash
   kubectl apply -f k8s/spire-agent.yaml
   ```
4. Create the OPA sidecar configuration (policy + bootstrap config) consumed by both demo apps:
   ```bash
   kubectl apply -f k8s/opa-config.yaml
   ```
5. Launch the demo frontend and API deployments with OPA sidecars and Services:
   ```bash
   kubectl apply -f k8s/demo-apps.yaml
   ```
6. Enforce namespace isolation and app-to-app allowlists with NetworkPolicies:
   ```bash
   kubectl apply -f k8s/network-policies.yaml
   ```

After the above, you should see SPIRE pods in the `spire` namespace plus `demo-frontend` and `demo-api` (each with an OPA sidecar) in `zero-trust-demo`. Use `kubectl port-forward svc/demo-frontend 8080:80 -n zero-trust-demo` to reach the frontend locally.

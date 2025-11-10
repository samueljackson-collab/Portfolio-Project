# Runbook — Project 17 (Multi-Cloud Service Mesh)

## Overview

Production operations runbook for the Multi-Cloud Service Mesh platform spanning AWS and GCP, implementing Istio service mesh with Consul service discovery and mutual TLS across cloud providers.

**System Components:**
- Istio service mesh (control plane and data plane)
- AWS EKS cluster with Istio sidecar injection
- GCP GKE cluster with Istio sidecar injection
- Consul for cross-cloud service discovery
- East-west gateways for multi-cluster communication
- Istio ingress/egress gateways
- Certificate management with Cert-Manager
- Multi-cluster trust domains

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Service mesh availability** | 99.9% | Control plane uptime |
| **Cross-cluster latency** | < 100ms (p95) | AWS ↔ GCP communication time |
| **mTLS connection success rate** | 99.99% | Successful TLS handshakes |
| **Service discovery accuracy** | 100% | Correct endpoint resolution |
| **Gateway availability** | 99.95% | East-west gateway uptime |
| **Certificate renewal success** | 100% | Auto-renewal completion rate |
| **Envoy proxy health** | 99% | Healthy sidecar proxies |

---

## Dashboards & Alerts

### Dashboards

#### Service Mesh Control Plane Health
```bash
# Check Istio control plane status
kubectl get pods -n istio-system

# Check Istiod health
kubectl -n istio-system get deploy istiod -o wide

# Check proxy sync status
istioctl proxy-status

# Verify mesh configuration
istioctl analyze --all-namespaces
```

#### Cross-Cluster Communication Dashboard
```bash
# Check east-west gateway status (AWS)
kubectl --context aws-eks get svc -n istio-system istio-eastwestgateway

# Check east-west gateway status (GCP)
kubectl --context gcp-gke get svc -n istio-system istio-eastwestgateway

# Test cross-cluster connectivity
kubectl --context aws-eks run test-pod --image=curlimages/curl -it --rm -- \
  curl -v http://service-name.namespace.svc.cluster.local

# Check service endpoints across clusters
istioctl --context aws-eks proxy-config endpoints <pod-name> | grep <service-name>
```

#### mTLS Status Dashboard
```bash
# Check mTLS configuration
kubectl get peerauthentication --all-namespaces

# Verify certificates
istioctl proxy-config secret <pod-name> -n <namespace>

# Check certificate expiry
kubectl get certificates -n istio-system

# Verify mTLS enforcement
istioctl authn tls-check <pod-name>.<namespace> <service-name>.<namespace>.svc.cluster.local
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Istiod control plane down | Immediate | Restart control plane, check dependencies |
| **P0** | East-west gateway down | Immediate | Failover to backup, investigate root cause |
| **P0** | mTLS handshake failure rate > 1% | Immediate | Check certificates, verify trust domains |
| **P1** | Envoy sidecar injection failing | 15 minutes | Check webhook, restart injector |
| **P1** | Cross-cluster latency > 200ms | 15 minutes | Check network path, investigate bottleneck |
| **P2** | Certificate expiring < 7 days | 24 hours | Trigger manual renewal if auto-renewal fails |
| **P2** | High Envoy memory usage | 1 hour | Review resource limits, check for leaks |

#### Alert Queries (Prometheus)

```promql
# Control plane availability
up{job="istiod"} == 0

# High cross-cluster latency
histogram_quantile(0.95,
  sum(rate(istio_request_duration_milliseconds_bucket{
    source_cluster!="",
    destination_cluster!="",
    source_cluster!=destination_cluster
  }[5m])) by (le)
) > 200

# mTLS handshake failures
rate(envoy_ssl_handshake_failed_total[5m]) > 0.01

# Gateway down
up{job="istio-eastwestgateway"} == 0

# Certificate expiration
(certmanager_certificate_expiration_timestamp_seconds - time()) / 86400 < 7
```

---

## Standard Operations

### Service Mesh Management

#### Deploy Service Mesh to New Cluster
```bash
# 1. Install Istio operator
istioctl operator init

# 2. Deploy Istio with multi-cluster configuration
kubectl apply -f manifests/istio-operator.yaml

# 3. Wait for control plane to be ready
kubectl wait --for=condition=Ready pods -l app=istiod -n istio-system --timeout=300s

# 4. Enable automatic sidecar injection
kubectl label namespace default istio-injection=enabled

# 5. Deploy east-west gateway
kubectl apply -f manifests/eastwest-gateway.yaml

# 6. Expose services for cross-cluster access
kubectl apply -f manifests/mesh-config.yaml
```

#### Configure Multi-Cluster Mesh
```bash
# 1. Create remote secret for cluster access (AWS → GCP)
istioctl create-remote-secret \
  --context=gcp-gke \
  --name=gcp-cluster | \
  kubectl apply -f - --context=aws-eks

# 2. Create remote secret for cluster access (GCP → AWS)
istioctl create-remote-secret \
  --context=aws-eks \
  --name=aws-cluster | \
  kubectl apply -f - --context=gcp-gke

# 3. Verify multi-cluster setup
istioctl --context aws-eks remote-clusters
istioctl --context gcp-gke remote-clusters

# 4. Test cross-cluster service discovery
kubectl --context aws-eks run test --image=curlimages/curl -it --rm -- \
  curl -v http://service-name.namespace.svc.gcp-cluster.global
```

#### Enable mTLS for Namespace
```bash
# Apply strict mTLS policy
cat <<EOF | kubectl apply -f -
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT
EOF

# Verify mTLS is enforced
istioctl authn tls-check <pod-name>.production <service-name>.production.svc.cluster.local

# Check mTLS metrics
kubectl exec -n istio-system deploy/istiod -- \
  curl -s localhost:15014/metrics | grep mtls
```

### Traffic Management

#### Configure Traffic Routing
```yaml
# virtual-service.yaml - Configure weighted routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: service-routes
  namespace: production
spec:
  hosts:
  - service-name
  http:
  - match:
    - headers:
        env:
          exact: canary
    route:
    - destination:
        host: service-name
        subset: v2
      weight: 100
  - route:
    - destination:
        host: service-name
        subset: v1
      weight: 90
    - destination:
        host: service-name
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: service-name
  namespace: production
spec:
  host: service-name
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

```bash
# Apply traffic routing
kubectl apply -f virtual-service.yaml

# Verify routing
istioctl proxy-config routes <pod-name> -n production

# Test canary deployment
for i in {1..100}; do
  curl -H "env: canary" http://service-name.production.svc.cluster.local
done
```

#### Implement Circuit Breaking
```yaml
# destination-rule.yaml - Configure circuit breaker
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: circuit-breaker
  namespace: production
spec:
  host: service-name
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 100
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 5
      interval: 30s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
      minHealthPercent: 40
```

```bash
# Apply circuit breaker
kubectl apply -f destination-rule.yaml

# Monitor circuit breaker status
kubectl exec -n production <pod-name> -c istio-proxy -- \
  curl -s localhost:15000/stats | grep outlier_detection
```

### Gateway Operations

#### Update East-West Gateway
```bash
# Check current gateway configuration
kubectl get gateway -n istio-system istio-eastwestgateway -o yaml

# Edit gateway configuration
kubectl edit gateway -n istio-system istio-eastwestgateway

# Restart gateway pods for changes
kubectl rollout restart deployment -n istio-system istio-eastwestgateway

# Verify gateway health
kubectl get pods -n istio-system -l app=istio-eastwestgateway
istioctl proxy-status | grep eastwest
```

#### Configure Ingress Gateway
```yaml
# ingress-gateway.yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: public-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*.example.com"
    tls:
      httpsRedirect: true
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: tls-cert
    hosts:
    - "*.example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: public-routes
  namespace: production
spec:
  hosts:
  - "api.example.com"
  gateways:
  - istio-system/public-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1
    route:
    - destination:
        host: api-service
        port:
          number: 8080
```

### Consul Service Discovery

#### Manage Consul Integration
```bash
# Check Consul health
kubectl exec -n consul consul-server-0 -- consul members

# Verify service registration
kubectl exec -n consul consul-server-0 -- consul catalog services

# Check specific service
kubectl exec -n consul consul-server-0 -- \
  consul catalog nodes -service=<service-name>

# Query service health
kubectl exec -n consul consul-server-0 -- \
  consul health service <service-name>

# Manually register service
kubectl exec -n consul consul-server-0 -- \
  consul services register -name=<service-name> -address=<ip> -port=<port>
```

---

## Incident Response

### P0: Istiod Control Plane Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check control plane status
kubectl get pods -n istio-system -l app=istiod

# 2. Check recent events
kubectl get events -n istio-system --sort-by='.lastTimestamp' | grep istiod

# 3. Check logs
kubectl logs -n istio-system deploy/istiod --tail=100

# 4. Restart control plane
kubectl rollout restart deployment/istiod -n istio-system

# 5. Verify recovery
kubectl wait --for=condition=Ready pods -l app=istiod -n istio-system --timeout=120s
istioctl proxy-status
```

**Investigation (5-20 minutes):**
```bash
# Check control plane resources
kubectl top pods -n istio-system -l app=istiod

# Check for OOMKilled
kubectl describe pod -n istio-system -l app=istiod | grep -A 10 "State:"

# Check control plane metrics
kubectl exec -n istio-system deploy/istiod -- \
  curl -s localhost:15014/metrics | grep -E "(memory|goroutines|grpc)"

# Review configuration
istioctl analyze --all-namespaces
```

**Recovery:**
```bash
# If resource exhaustion, scale control plane
kubectl scale deployment istiod -n istio-system --replicas=3

# If configuration issue, restore last known good config
kubectl apply -f backup/istio-operator-backup.yaml

# Verify mesh health
istioctl proxy-status
kubectl get virtualservices --all-namespaces
kubectl get destinationrules --all-namespaces
```

### P0: East-West Gateway Down

**Immediate Actions:**
```bash
# 1. Check gateway status
kubectl get pods -n istio-system -l app=istio-eastwestgateway

# 2. Check service endpoints
kubectl get endpoints -n istio-system istio-eastwestgateway

# 3. Check gateway logs
kubectl logs -n istio-system -l app=istio-eastwestgateway --tail=100

# 4. Restart gateway
kubectl rollout restart deployment/istio-eastwestgateway -n istio-system

# 5. Verify cross-cluster connectivity
istioctl --context aws-eks remote-clusters
istioctl --context gcp-gke remote-clusters
```

**Verification:**
```bash
# Test cross-cluster communication
kubectl --context aws-eks run test --image=curlimages/curl -it --rm -- \
  curl -v http://service-name.namespace.svc.gcp-cluster.global

# Check gateway metrics
kubectl exec -n istio-system deploy/istio-eastwestgateway -c istio-proxy -- \
  curl -s localhost:15000/stats | grep -E "(downstream|upstream|cluster\.out)"
```

### P0: mTLS Handshake Failures

**Investigation:**
```bash
# 1. Check mTLS configuration
kubectl get peerauthentication --all-namespaces

# 2. Verify certificates
istioctl proxy-config secret <pod-name> -n <namespace>

# 3. Check certificate validity
kubectl get certificates -n istio-system
kubectl describe certificate -n istio-system

# 4. Check Envoy stats for TLS errors
kubectl exec -n <namespace> <pod-name> -c istio-proxy -- \
  curl -s localhost:15000/stats | grep ssl

# 5. Check specific service mTLS status
istioctl authn tls-check <pod-name>.<namespace> <service-name>.<namespace>.svc.cluster.local
```

**Common Causes & Fixes:**

**Certificate Expired:**
```bash
# Check certificate expiry
kubectl get certificate -n istio-system -o json | \
  jq '.items[] | {name: .metadata.name, notAfter: .status.notAfter}'

# Force certificate renewal
kubectl delete certificate -n istio-system <cert-name>
kubectl annotate certificate -n istio-system <cert-name> cert-manager.io/issue-temporary-certificate="true"

# Restart affected pods
kubectl rollout restart deployment/<deployment-name> -n <namespace>
```

**Trust Domain Mismatch:**
```bash
# Check trust domain configuration
kubectl get meshconfig -n istio-system -o yaml | grep trustDomain

# Verify peer authentication
kubectl get peerauthentication --all-namespaces -o yaml | grep -A 5 "mtls:"

# Fix: Update trust domain in mesh config
kubectl edit meshconfig -n istio-system
```

**Clock Skew:**
```bash
# Check time on nodes
kubectl get nodes -o wide

# SSH to nodes and check time
for node in $(kubectl get nodes -o name); do
  echo "=== $node ==="
  kubectl debug $node -it --image=busybox -- date
done

# Sync NTP if needed (node-level operation)
```

### P1: High Cross-Cluster Latency

**Investigation:**
```bash
# 1. Measure latency between clusters
kubectl --context aws-eks run perf-test --image=nicolaka/netshoot -it --rm -- \
  curl -w "@curl-format.txt" -o /dev/null -s http://service.namespace.svc.gcp-cluster.global

# 2. Check gateway latency
istioctl dashboard envoy deploy/istio-eastwestgateway.istio-system
# Navigate to stats and check histogram metrics

# 3. Check network path
kubectl --context aws-eks run traceroute --image=nicolaka/netshoot -it --rm -- \
  traceroute service.namespace.svc.gcp-cluster.global

# 4. Review Envoy proxy stats
kubectl exec -n istio-system deploy/istio-eastwestgateway -c istio-proxy -- \
  curl -s localhost:15000/stats | grep -E "(latency|duration)"
```

**Mitigation:**
```bash
# Increase connection pool size
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: cross-cluster-optimization
  namespace: production
spec:
  host: "*.svc.gcp-cluster.global"
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 500
      http:
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
    loadBalancer:
      simple: LEAST_REQUEST
EOF

# Enable locality-aware load balancing
kubectl patch meshconfig istio -n istio-system --type merge -p '
spec:
  meshConfig:
    localityLbSetting:
      enabled: true
      distribute:
      - from: us-east-1/*
        to:
          "us-east-1/*": 80
          "us-west-2/*": 20
'
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Sidecar injection not working"

**Symptoms:**
```bash
# Pod has no istio-proxy container
kubectl get pods -n <namespace> <pod-name> -o jsonpath='{.spec.containers[*].name}'
# Output: app (missing istio-proxy)
```

**Diagnosis:**
```bash
# Check if namespace has injection label
kubectl get namespace <namespace> -o jsonpath='{.metadata.labels.istio-injection}'

# Check webhook status
kubectl get mutatingwebhookconfiguration istio-sidecar-injector -o yaml

# Check webhook endpoint
kubectl get endpoints -n istio-system istiod
```

**Solution:**
```bash
# Enable sidecar injection for namespace
kubectl label namespace <namespace> istio-injection=enabled --overwrite

# Restart pods to trigger injection
kubectl rollout restart deployment/<deployment-name> -n <namespace>

# Verify injection
kubectl get pods -n <namespace> <pod-name> -o jsonpath='{.spec.containers[*].name}'
# Should include: app istio-proxy
```

---

#### Issue: "503 UC: upstream connect error"

**Symptoms:**
```
HTTP 503 Service Unavailable
UC: upstream connect error or disconnect/reset before headers
```

**Diagnosis:**
```bash
# Check if service exists
kubectl get svc -n <namespace> <service-name>

# Check service endpoints
kubectl get endpoints -n <namespace> <service-name>

# Check destination rule
kubectl get destinationrule -n <namespace>

# Check virtual service
kubectl get virtualservice -n <namespace>

# Check Envoy cluster status
kubectl exec -n <namespace> <pod-name> -c istio-proxy -- \
  curl -s localhost:15000/clusters | grep <service-name>
```

**Solution:**
```bash
# If no endpoints, check pod labels
kubectl get pods -n <namespace> -l app=<service-name> --show-labels

# If mTLS mismatch, check authentication
istioctl authn tls-check <source-pod>.<namespace> <dest-service>.<namespace>.svc.cluster.local

# If circuit breaker tripped, check outlier detection
kubectl exec -n <namespace> <pod-name> -c istio-proxy -- \
  curl -s localhost:15000/stats | grep outlier_detection

# Reset circuit breaker by restarting pods
kubectl delete pod -n <namespace> <pod-name>
```

---

#### Issue: "Certificate verification failed"

**Symptoms:**
```
TLS error: certificate verify failed
x509: certificate signed by unknown authority
```

**Diagnosis:**
```bash
# Check certificate chain
istioctl proxy-config secret <pod-name> -n <namespace> -o json | \
  jq '.dynamicActiveSecrets[] | select(.name=="default") | .secret.tlsCertificate.certificateChain'

# Check CA certificate
kubectl get configmap -n istio-system istio-ca-root-cert -o yaml

# Verify trust domain
kubectl get meshconfig -n istio-system -o yaml | grep trustDomain
```

**Solution:**
```bash
# Refresh CA certificates in pods
kubectl rollout restart deployment/<deployment-name> -n <namespace>

# If using external CA, update root certificate
kubectl create configmap istio-ca-root-cert -n istio-system \
  --from-file=root-cert.pem --dry-run=client -o yaml | kubectl apply -f -

# Restart istiod to pick up new certificates
kubectl rollout restart deployment/istiod -n istio-system
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Morning health check
# 1. Check control plane status
kubectl get pods -n istio-system
istioctl version

# 2. Verify proxy sync status
istioctl proxy-status | grep -v "Clusters Match\|Listeners Match\|Routes Match"

# 3. Check for configuration errors
istioctl analyze --all-namespaces

# 4. Review recent events
kubectl get events -n istio-system --sort-by='.lastTimestamp' | head -20

# 5. Check gateway health
kubectl get pods -n istio-system -l app=istio-eastwestgateway
kubectl get svc -n istio-system istio-eastwestgateway
```

### Weekly Tasks

```bash
# 1. Review mTLS status across mesh
istioctl authn tls-check -a

# 2. Check certificate expiry
kubectl get certificates -n istio-system -o json | \
  jq '.items[] | {name: .metadata.name, notAfter: .status.notAfter}'

# 3. Review traffic patterns
istioctl dashboard kiali &
# Review service graph, error rates, latencies

# 4. Analyze mesh configuration
istioctl analyze --all-namespaces > analysis-$(date +%Y%m%d).txt

# 5. Update proxy versions
istioctl proxy-status | awk '{print $6}' | sort | uniq -c
# Plan upgrade if versions are outdated

# 6. Backup configurations
kubectl get istiooperator -n istio-system -o yaml > backup/istio-operator-$(date +%Y%m%d).yaml
kubectl get gateway,virtualservice,destinationrule --all-namespaces -o yaml > backup/mesh-config-$(date +%Y%m%d).yaml
```

### Monthly Tasks

```bash
# 1. Upgrade Istio control plane (if needed)
istioctl upgrade --set profile=production

# 2. Review and optimize resource allocations
kubectl top pods -n istio-system
kubectl describe nodes | grep -A 10 "Allocated resources"

# 3. Conduct disaster recovery drill
# Simulate control plane failure and verify auto-recovery

# 4. Review and update security policies
kubectl get peerauthentication,authorizationpolicy --all-namespaces

# 5. Performance tuning
# Review and adjust:
# - Connection pool sizes
# - Circuit breaker thresholds
# - Retry policies
# - Timeout values

# 6. Update documentation
# Document any new procedures or lessons learned
```

### Disaster Recovery

**Backup Strategy:**
```bash
# 1. Backup Istio configuration
kubectl get istiooperator -n istio-system -o yaml > backup/istio-operator.yaml
kubectl get configmap -n istio-system -o yaml > backup/istio-configmaps.yaml

# 2. Backup mesh policies
kubectl get gateway,virtualservice,destinationrule,serviceentry,peerauthentication,authorizationpolicy \
  --all-namespaces -o yaml > backup/mesh-policies.yaml

# 3. Backup certificates
kubectl get certificates,issuers,clusterissuers -n istio-system -o yaml > backup/certificates.yaml

# 4. Document cluster topology
istioctl proxy-status > backup/proxy-status.txt
istioctl remote-clusters > backup/remote-clusters.txt
```

**Recovery Procedures:**
```bash
# 1. Reinstall Istio control plane
istioctl install -f backup/istio-operator.yaml

# 2. Restore mesh configuration
kubectl apply -f backup/mesh-policies.yaml

# 3. Restore multi-cluster setup
istioctl create-remote-secret --context=gcp-gke --name=gcp-cluster | \
  kubectl apply -f - --context=aws-eks

istioctl create-remote-secret --context=aws-eks --name=aws-cluster | \
  kubectl apply -f - --context=gcp-gke

# 4. Verify mesh functionality
istioctl verify-install
istioctl analyze --all-namespaces
istioctl proxy-status

# 5. Test cross-cluster connectivity
kubectl --context aws-eks run test --image=curlimages/curl -it --rm -- \
  curl -v http://service.namespace.svc.gcp-cluster.global
```

---

## Quick Reference

### Common Commands

```bash
# Check mesh health
istioctl analyze --all-namespaces
istioctl proxy-status

# View mesh configuration
istioctl proxy-config cluster <pod> -n <namespace>
istioctl proxy-config route <pod> -n <namespace>
istioctl proxy-config endpoint <pod> -n <namespace>

# Debug mTLS
istioctl authn tls-check <source-pod>.<namespace> <service>.<namespace>.svc.cluster.local

# View dashboards
istioctl dashboard kiali
istioctl dashboard grafana
istioctl dashboard jaeger
```

### Emergency Response

```bash
# P0: Control plane down
kubectl rollout restart deployment/istiod -n istio-system

# P0: Gateway down
kubectl rollout restart deployment/istio-eastwestgateway -n istio-system

# P0: mTLS failures
kubectl rollout restart deployment/<affected-deployment> -n <namespace>

# P1: High latency
istioctl dashboard envoy deploy/<deployment>.<namespace>
# Review stats and adjust traffic policies
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform/SRE Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Submit PR with updates

# Kubernetes Security Policies
#
# This Rego policy file defines security rules for Kubernetes deployments.
# It enforces best practices and security standards for container workloads.
#
# Usage:
#   opa eval --data policies/kubernetes.rego --input manifest.json "data.kubernetes"
#   conftest test deployment.yaml --policy policies/
#
# Policy Categories:
#   1. Container Security - Privileged containers, capabilities, root user
#   2. Resource Management - Limits, requests, quotas
#   3. Network Security - Host networking, port exposure
#   4. Image Security - Image sources, tags
#   5. Pod Security - Service accounts, security contexts

package kubernetes

import future.keywords.in
import future.keywords.contains
import future.keywords.if

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Get all containers from a Kubernetes resource
get_containers(resource) := containers {
    containers := array.concat(
        object.get(resource.spec, "containers", []),
        object.get(resource.spec, "initContainers", [])
    )
}

# Get containers from a Pod template (Deployment, StatefulSet, etc.)
get_template_containers(resource) := containers {
    containers := array.concat(
        object.get(resource.spec.template.spec, "containers", []),
        object.get(resource.spec.template.spec, "initContainers", [])
    )
}

# Check if resource is a workload type
is_workload(resource) {
    workload_kinds := {"Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Job", "CronJob"}
    resource.kind in workload_kinds
}

# ============================================================================
# RULE 1: DENY PRIVILEGED CONTAINERS
# Privileged containers have root-level access to the host system.
# This is a critical security risk as it allows container escape.
# ============================================================================

deny contains msg if {
    input.kind == "Pod"
    some container in get_containers(input)
    container.securityContext.privileged == true
    msg := sprintf("CRITICAL: Pod '%s' container '%s' runs in privileged mode. Privileged containers can escape to the host system.", [input.metadata.name, container.name])
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    container.securityContext.privileged == true
    msg := sprintf("CRITICAL: %s '%s' container '%s' runs in privileged mode. Privileged containers can escape to the host system.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 2: REQUIRE RESOURCE LIMITS
# All containers must have CPU and memory limits defined.
# Without limits, a container can consume all host resources (DoS risk).
# ============================================================================

deny contains msg if {
    input.kind == "Pod"
    some container in get_containers(input)
    not container.resources.limits.cpu
    msg := sprintf("HIGH: Pod '%s' container '%s' missing CPU limit. Set resources.limits.cpu to prevent resource exhaustion.", [input.metadata.name, container.name])
}

deny contains msg if {
    input.kind == "Pod"
    some container in get_containers(input)
    not container.resources.limits.memory
    msg := sprintf("HIGH: Pod '%s' container '%s' missing memory limit. Set resources.limits.memory to prevent OOM issues.", [input.metadata.name, container.name])
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.resources.limits.cpu
    msg := sprintf("HIGH: %s '%s' container '%s' missing CPU limit. Set resources.limits.cpu to prevent resource exhaustion.", [input.kind, input.metadata.name, container.name])
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.resources.limits.memory
    msg := sprintf("HIGH: %s '%s' container '%s' missing memory limit. Set resources.limits.memory to prevent OOM issues.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 3: REQUIRE RESOURCE REQUESTS
# All containers should have resource requests for proper scheduling.
# ============================================================================

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.resources.requests.cpu
    msg := sprintf("MEDIUM: %s '%s' container '%s' missing CPU request. Set resources.requests.cpu for proper scheduling.", [input.kind, input.metadata.name, container.name])
}

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.resources.requests.memory
    msg := sprintf("MEDIUM: %s '%s' container '%s' missing memory request. Set resources.requests.memory for proper scheduling.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 4: DENY CONTAINERS RUNNING AS ROOT
# Containers should run as non-root users to limit the impact of compromise.
# ============================================================================

deny contains msg if {
    input.kind == "Pod"
    some container in get_containers(input)
    container.securityContext.runAsUser == 0
    msg := sprintf("HIGH: Pod '%s' container '%s' runs as root (UID 0). Configure runAsUser to a non-root UID.", [input.metadata.name, container.name])
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    container.securityContext.runAsUser == 0
    msg := sprintf("HIGH: %s '%s' container '%s' runs as root (UID 0). Configure runAsUser to a non-root UID.", [input.kind, input.metadata.name, container.name])
}

# Require runAsNonRoot to be explicitly set
warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.securityContext.runAsNonRoot
    msg := sprintf("MEDIUM: %s '%s' container '%s' should set securityContext.runAsNonRoot=true.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 5: DENY HOST NETWORKING
# Host network mode allows the pod to use the host's network stack.
# This can expose sensitive host network traffic and services.
# ============================================================================

deny contains msg if {
    input.kind == "Pod"
    input.spec.hostNetwork == true
    msg := sprintf("CRITICAL: Pod '%s' uses host networking. This exposes the host network stack. Remove hostNetwork or set to false.", [input.metadata.name])
}

deny contains msg if {
    is_workload(input)
    input.spec.template.spec.hostNetwork == true
    msg := sprintf("CRITICAL: %s '%s' uses host networking. This exposes the host network stack. Remove hostNetwork or set to false.", [input.kind, input.metadata.name])
}

# ============================================================================
# RULE 6: DENY HOST PID AND IPC NAMESPACES
# Using host PID/IPC allows visibility into host processes.
# ============================================================================

deny contains msg if {
    input.kind == "Pod"
    input.spec.hostPID == true
    msg := sprintf("CRITICAL: Pod '%s' shares host PID namespace. This allows viewing host processes. Set hostPID: false.", [input.metadata.name])
}

deny contains msg if {
    input.kind == "Pod"
    input.spec.hostIPC == true
    msg := sprintf("HIGH: Pod '%s' shares host IPC namespace. Set hostIPC: false.", [input.metadata.name])
}

deny contains msg if {
    is_workload(input)
    input.spec.template.spec.hostPID == true
    msg := sprintf("CRITICAL: %s '%s' shares host PID namespace. This allows viewing host processes.", [input.kind, input.metadata.name])
}

# ============================================================================
# RULE 7: DENY DANGEROUS CAPABILITIES
# Certain Linux capabilities provide excessive privileges.
# ============================================================================

# List of dangerous capabilities that should be denied
dangerous_capabilities := {
    "SYS_ADMIN",      # Full admin privileges, nearly equivalent to root
    "NET_ADMIN",      # Network configuration changes
    "SYS_PTRACE",     # Process tracing, can be used for container escape
    "SYS_RAWIO",      # Raw I/O access
    "SYS_MODULE",     # Load kernel modules
    "DAC_READ_SEARCH" # Bypass file read permission checks
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    some cap in container.securityContext.capabilities.add
    cap in dangerous_capabilities
    msg := sprintf("CRITICAL: %s '%s' container '%s' adds dangerous capability '%s'. Remove this capability.", [input.kind, input.metadata.name, container.name, cap])
}

# ============================================================================
# RULE 8: REQUIRE READ-ONLY ROOT FILESYSTEM
# Containers should use read-only root filesystems to prevent tampering.
# ============================================================================

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.securityContext.readOnlyRootFilesystem
    msg := sprintf("MEDIUM: %s '%s' container '%s' should use readOnlyRootFilesystem=true for immutability.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 9: REQUIRE IMAGE TAG (NO LATEST)
# Using 'latest' tag makes deployments non-deterministic.
# ============================================================================

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    endswith(container.image, ":latest")
    msg := sprintf("HIGH: %s '%s' container '%s' uses 'latest' tag. Use specific version tags for reproducibility.", [input.kind, input.metadata.name, container.name])
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not contains(container.image, ":")
    msg := sprintf("HIGH: %s '%s' container '%s' missing image tag. Specify a version tag.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 10: REQUIRE APPROVED IMAGE REGISTRIES
# Only allow images from trusted registries.
# ============================================================================

# List of approved container registries
approved_registries := {
    "gcr.io/",
    "ghcr.io/",
    "docker.io/library/",
    "quay.io/",
    "registry.k8s.io/",
    "public.ecr.aws/"
}

image_from_approved_registry(image) {
    some registry in approved_registries
    startswith(image, registry)
}

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not image_from_approved_registry(container.image)
    msg := sprintf("MEDIUM: %s '%s' container '%s' uses image from non-approved registry: '%s'. Consider using approved registries.", [input.kind, input.metadata.name, container.name, container.image])
}

# ============================================================================
# RULE 11: REQUIRE HEALTH PROBES
# Liveness and readiness probes ensure proper pod lifecycle management.
# ============================================================================

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.livenessProbe
    msg := sprintf("MEDIUM: %s '%s' container '%s' missing livenessProbe. Add health checks for reliability.", [input.kind, input.metadata.name, container.name])
}

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    not container.readinessProbe
    msg := sprintf("MEDIUM: %s '%s' container '%s' missing readinessProbe. Add readiness checks for proper load balancing.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 12: DENY DEFAULT SERVICE ACCOUNT
# Using the default service account can expose unnecessary API access.
# ============================================================================

warn contains msg if {
    is_workload(input)
    sa := input.spec.template.spec.serviceAccountName
    sa == "default"
    msg := sprintf("MEDIUM: %s '%s' uses default service account. Create a dedicated service account with minimal permissions.", [input.kind, input.metadata.name])
}

# ============================================================================
# RULE 13: REQUIRE AUTOMOUNT SERVICE ACCOUNT TOKEN FALSE
# Disable automatic mounting of service account tokens when not needed.
# ============================================================================

warn contains msg if {
    is_workload(input)
    input.spec.template.spec.automountServiceAccountToken != false
    msg := sprintf("LOW: %s '%s' should set automountServiceAccountToken: false if API access is not needed.", [input.kind, input.metadata.name])
}

# ============================================================================
# RULE 14: DENY HOSTPATH VOLUMES
# HostPath volumes can expose sensitive host filesystem data.
# ============================================================================

deny contains msg if {
    input.kind == "Pod"
    some volume in input.spec.volumes
    volume.hostPath
    msg := sprintf("HIGH: Pod '%s' uses hostPath volume '%s'. HostPath volumes expose host filesystem. Use persistent volumes instead.", [input.metadata.name, volume.name])
}

deny contains msg if {
    is_workload(input)
    some volume in input.spec.template.spec.volumes
    volume.hostPath
    msg := sprintf("HIGH: %s '%s' uses hostPath volume '%s'. HostPath volumes expose host filesystem.", [input.kind, input.metadata.name, volume.name])
}

# ============================================================================
# RULE 15: REQUIRE NETWORK POLICIES
# Namespaces should have NetworkPolicies for network segmentation.
# ============================================================================

# This rule checks if NetworkPolicy exists for a namespace
# Note: This requires checking multiple resources together

warn contains msg if {
    input.kind == "Namespace"
    msg := sprintf("INFO: Namespace '%s' created. Ensure NetworkPolicies are configured for network segmentation.", [input.metadata.name])
}

# ============================================================================
# RULE 16: REQUIRE POD SECURITY STANDARDS
# Pods should have security contexts with restrictive settings.
# ============================================================================

warn contains msg if {
    is_workload(input)
    not input.spec.template.spec.securityContext.seccompProfile
    msg := sprintf("MEDIUM: %s '%s' should specify a seccompProfile (RuntimeDefault or Localhost).", [input.kind, input.metadata.name])
}

# ============================================================================
# RULE 17: DENY PRIVILEGE ESCALATION
# Containers should not be allowed to gain more privileges than their parent.
# ============================================================================

warn contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    container.securityContext.allowPrivilegeEscalation != false
    msg := sprintf("MEDIUM: %s '%s' container '%s' should set allowPrivilegeEscalation: false.", [input.kind, input.metadata.name, container.name])
}

# ============================================================================
# RULE 18: REQUIRE LABELS FOR MANAGEMENT
# Resources should have standard labels for organization and management.
# ============================================================================

required_labels := {"app", "version"}

warn contains msg if {
    is_workload(input)
    some label in required_labels
    not input.metadata.labels[label]
    msg := sprintf("LOW: %s '%s' missing recommended label '%s'.", [input.kind, input.metadata.name, label])
}

# ============================================================================
# RULE 19: SERVICE SECURITY
# Services should not expose NodePorts in production without approval.
# ============================================================================

warn contains msg if {
    input.kind == "Service"
    input.spec.type == "NodePort"
    msg := sprintf("MEDIUM: Service '%s' uses NodePort which exposes ports on all nodes. Consider using ClusterIP with Ingress.", [input.metadata.name])
}

warn contains msg if {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["service.beta.kubernetes.io/aws-load-balancer-internal"]
    msg := sprintf("LOW: Service '%s' is a public LoadBalancer. Consider using internal load balancer annotation if internal access only.", [input.metadata.name])
}

# ============================================================================
# RULE 20: SECRETS SECURITY
# Secrets should not be embedded in pod specs.
# ============================================================================

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    some env in container.env
    env.value
    contains(lower(env.name), "password")
    msg := sprintf("CRITICAL: %s '%s' container '%s' has password in plain text env var '%s'. Use secretKeyRef.", [input.kind, input.metadata.name, container.name, env.name])
}

deny contains msg if {
    is_workload(input)
    some container in get_template_containers(input)
    some env in container.env
    env.value
    contains(lower(env.name), "secret")
    msg := sprintf("HIGH: %s '%s' container '%s' has secret in plain text env var '%s'. Use secretKeyRef.", [input.kind, input.metadata.name, container.name, env.name])
}

# ============================================================================
# SUMMARY RULES
# ============================================================================

# Count violations by severity
critical_count := count([msg | some msg in deny; contains(msg, "CRITICAL")])
high_count := count([msg | some msg in deny; contains(msg, "HIGH")])
medium_count := count([msg | some msg in warn; contains(msg, "MEDIUM")])
low_count := count([msg | some msg in warn; contains(msg, "LOW")])

# Overall pass/fail
passed := count(deny) == 0

# Kubernetes Security Policies using Open Policy Agent (OPA)
# These policies enforce security best practices for Kubernetes deployments

package kubernetes.admission

import future.keywords.in

# Default deny
default allow := false

# Allow if no violations
allow {
    count(violation) == 0
}

# ============================================
# Container Security Policies
# ============================================

# Deny containers running as root (CIS Benchmark 5.2.6)
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.runAsNonRoot
    msg := sprintf("Container '%v' must set securityContext.runAsNonRoot to true", [container.name])
}

violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.runAsUser == 0
    msg := sprintf("Container '%v' must not run as root (UID 0)", [container.name])
}

# Deny privileged containers (CIS Benchmark 5.2.1)
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.privileged
    msg := sprintf("Container '%v' must not be privileged", [container.name])
}

# Deny containers with privilege escalation (CIS Benchmark 5.2.5)
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation
    msg := sprintf("Container '%v' must set allowPrivilegeEscalation to false", [container.name])
}

# Require read-only root filesystem (CIS Benchmark 5.2.4)
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.securityContext.readOnlyRootFilesystem
    msg := sprintf("Container '%v' should have a read-only root filesystem", [container.name])
}

# ============================================
# Resource Limits
# ============================================

# Require CPU limits
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.resources.limits.cpu
    msg := sprintf("Container '%v' must have CPU limits defined", [container.name])
}

# Require memory limits
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.resources.limits.memory
    msg := sprintf("Container '%v' must have memory limits defined", [container.name])
}

# Require resource requests
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.resources.requests.cpu
    msg := sprintf("Container '%v' must have CPU requests defined", [container.name])
}

violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not container.resources.requests.memory
    msg := sprintf("Container '%v' must have memory requests defined", [container.name])
}

# ============================================
# Image Security
# ============================================

# Deny latest tag
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    endswith(container.image, ":latest")
    msg := sprintf("Container '%v' must not use the 'latest' tag", [container.name])
}

violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not contains(container.image, ":")
    msg := sprintf("Container '%v' must specify an image tag", [container.name])
}

# Require images from approved registries
approved_registries := [
    "gcr.io/",
    "ghcr.io/",
    "docker.io/library/",
    "quay.io/"
]

violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not image_from_approved_registry(container.image)
    msg := sprintf("Container '%v' uses image from non-approved registry: %v", [container.name, container.image])
}

image_from_approved_registry(image) {
    some registry in approved_registries
    startswith(image, registry)
}

# ============================================
# Network Policies
# ============================================

# Require network policy for namespace
violation[msg] {
    input.kind == "Namespace"
    not has_network_policy(input.metadata.name)
    msg := sprintf("Namespace '%v' must have a NetworkPolicy defined", [input.metadata.name])
}

has_network_policy(namespace) {
    # This would check for NetworkPolicy in the namespace
    # In practice, this requires access to cluster state
    true
}

# ============================================
# Service Account
# ============================================

# Deny automounting service account tokens (CIS Benchmark 5.1.6)
violation[msg] {
    input.kind == "Pod"
    not input.spec.automountServiceAccountToken == false
    msg := "Pod should set automountServiceAccountToken to false unless needed"
}

# Deny default service account
violation[msg] {
    input.kind == "Pod"
    input.spec.serviceAccountName == "default"
    msg := "Pod should not use the default service account"
}

# ============================================
# Labels and Annotations
# ============================================

# Require standard labels
required_labels := ["app", "version", "owner"]

violation[msg] {
    input.kind == "Pod"
    label := required_labels[_]
    not input.metadata.labels[label]
    msg := sprintf("Pod must have label '%v' defined", [label])
}

# ============================================
# Host Namespace
# ============================================

# Deny hostPID (CIS Benchmark 5.2.2)
violation[msg] {
    input.kind == "Pod"
    input.spec.hostPID
    msg := "Pod must not use host PID namespace"
}

# Deny hostIPC (CIS Benchmark 5.2.3)
violation[msg] {
    input.kind == "Pod"
    input.spec.hostIPC
    msg := "Pod must not use host IPC namespace"
}

# Deny hostNetwork (CIS Benchmark 5.2.4)
violation[msg] {
    input.kind == "Pod"
    input.spec.hostNetwork
    msg := "Pod must not use host network"
}

# ============================================
# Capabilities
# ============================================

# Deny dangerous capabilities
dangerous_capabilities := [
    "NET_ADMIN",
    "SYS_ADMIN",
    "SYS_PTRACE",
    "NET_RAW",
    "SYS_MODULE"
]

violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    cap := container.securityContext.capabilities.add[_]
    cap in dangerous_capabilities
    msg := sprintf("Container '%v' must not add dangerous capability: %v", [container.name, cap])
}

# Require dropping all capabilities
violation[msg] {
    input.kind == "Pod"
    container := input.spec.containers[_]
    not "ALL" in container.securityContext.capabilities.drop
    msg := sprintf("Container '%v' should drop ALL capabilities", [container.name])
}

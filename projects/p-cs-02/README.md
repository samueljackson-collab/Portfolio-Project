# Kubernetes Runtime Hardening

- **Role Category:** Cloud Security
- **Status:** In Progress

## Executive Summary
Elevating cluster security with PSP replacements, runtime scanning, and managed identities.

## Scenario & Scope
EKS and AKS clusters running internal services with GitOps delivery.

## Responsibilities
- Defined baseline policies for pods and namespaces
- Integrated admission controllers and image scanning
- Enabled managed identities for service-to-service auth

## Tools & Technologies
- Kyverno
- Trivy
- OPA Gatekeeper
- IRSA
- Azure AD Workload Identity

## Architecture Notes
Policy bundles managed via GitOps; scanners run pre-deploy and at runtime; secrets offloaded to cloud KMS.

## Process Walkthrough
- Audited existing cluster settings
- Implemented admission policies
- Added runtime and supply chain scanning
- Tested break-glass scenarios and RBAC controls

## Outcomes & Metrics
- Blocked privileged pod deployments
- Achieved 100% image scanning coverage
- Improved service identity posture without secrets in pods

## Evidence Links
- clusters/p-cs-02/k8s-hardening.md

## Reproduction Steps
- Apply Kyverno policies via Helm
- Run Trivy scans on images pre-deploy
- Validate IRSA/Workload Identity mappings

## Interview Points
- Admission control vs runtime controls
- Identity handling for Kubernetes workloads
- Testing policies without blocking deploys

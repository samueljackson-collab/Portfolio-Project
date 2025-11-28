# GitOps Platform Build

- **Role Category:** DevOps / SRE
- **Status:** Completed

## Executive Summary
Built GitOps delivery for microservices with policy checks, progressive delivery, and secrets handling.

## Scenario & Scope
Kubernetes clusters with Argo CD and progressive delivery for internal APIs.

## Responsibilities
- Implemented repo layout and templates
- Added policy checks and image attestations
- Enabled blue/green and canary strategies

## Tools & Technologies
- Argo CD
- Argo Rollouts
- Kyverno
- Cosign
- Helm

## Architecture Notes
App-of-apps pattern with per-env overlays; admission policies enforce signed images; metrics drive rollout gates.

## Process Walkthrough
- Structured repos for apps and ops
- Configured Argo CD projects and RBAC
- Enabled rollout strategies with metrics
- Documented secrets patterns with external vaults

## Outcomes & Metrics
- Reduced deployment lead time by 50%
- Achieved 100% signed image enforcement
- Improved rollback time via Git history

## Evidence Links
- platform/p-devops-01/gitops-build.md

## Reproduction Steps
- Install Argo CD and Rollouts via Helm
- Apply the app-of-apps manifests
- Trigger a canary and monitor metrics

## Interview Points
- Structuring GitOps repos
- Progressive delivery patterns
- Policy checks in the delivery pipeline

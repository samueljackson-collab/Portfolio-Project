# Complete Portfolio Overview

This page contains the full portfolio README with all diagrams rendered properly.

## GitHub Status Snapshot (Local Repository)

**Repository Pulse (local Git snapshot)**
- **Active branch:** `work`
- **Last update:** 2026-01-05
- **Commits:** 777 total revisions
- **Tracked files:** 3,062 assets
- **Projects:** 25 portfolio showcases
- **READMEs:** 46 published guides

**Documentation & Infra Inventory**
- **Markdown files:** 407 references · **Total words:** 506,150
- **Docker compose files:** 25 · **Terraform files:** 81 · **Config packs:** 54

```mermaid
flowchart LR
  A[Commit] --> B[CI Workflows]
  B --> C[Docs + Evidence]
  C --> D[Release Artifacts]
  D --> E[GitHub Pages]
```

```mermaid
pie title Repository Evidence Mix
  "Docs + Runbooks" : 46
  "Infrastructure as Code" : 25
  "Validation + Tests" : 23
  "Blueprints" : 25
```

## Project Visuals (Charts + Diagrams)

### Project 1: AWS Infrastructure Automation
```mermaid
flowchart LR
  A[Plan] --> B[Apply]
  B --> C[Operate]
```
```mermaid
pie title Coverage: AWS Infra
  "IaC Modules" : 40
  "CI Validation" : 30
  "Ops Runbooks" : 30
```

### Project 2: Database Migration Platform
```mermaid
flowchart LR
  A[Source DB] --> B[CDC]
  B --> C[Target DB]
```
```mermaid
pie title Coverage: Migration
  "CDC Pipelines" : 35
  "Validation" : 35
  "Rollback" : 30
```

### Project 3: Kubernetes CI/CD Pipeline
```mermaid
flowchart LR
  A[Commit] --> B[CI Gates]
  B --> C[ArgoCD Sync]
```
```mermaid
pie title Coverage: K8s CI/CD
  "Policy Gates" : 35
  "Delivery" : 35
  "Telemetry" : 30
```

### Project 4: DevSecOps Pipeline
```mermaid
flowchart LR
  A[Build] --> B[Scan]
  B --> C[Release]
```
```mermaid
pie title Coverage: DevSecOps
  "SAST/SCA" : 40
  "DAST" : 30
  "SBOM" : 30
```

### Project 5: Real-time Data Streaming
```mermaid
flowchart LR
  A[Producers] --> B[Kafka/Flink]
  B --> C[Sinks]
```
```mermaid
pie title Coverage: Streaming
  "Throughput" : 35
  "Latency" : 35
  "Recovery" : 30
```

::: tip Success!
If you can see the diagrams above rendered as flowcharts and pie charts, Mermaid is working correctly!
:::

## All 25 Projects Overview

For the complete list of all projects with their diagrams, continue scrolling below or navigate using the sidebar.

[View Individual Projects](/projects/01-aws-infrastructure)

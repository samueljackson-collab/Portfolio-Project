---
title: Orchestration Architecture
description: graph TD subgraph Console UI[React Operations Console] end subgraph API ORCH[Orchestration Router] SRV[Orchestration Service] end subgraph Automation TF[Terraform Environments] ANS[Ansible Playbook] e
tags: [documentation, portfolio]
path: portfolio/docs/diagrams/orchestration-architecture
created: 2026-03-08T22:19:14.079817+00:00
updated: 2026-03-08T22:04:37.812902+00:00
---

# Orchestration Architecture

```mermaid
graph TD
  subgraph Console
    UI[React Operations Console]
  end
  subgraph API
    ORCH[Orchestration Router]
    SRV[Orchestration Service]
  end
  subgraph Automation
    TF[Terraform Environments]
    ANS[Ansible Playbook]
  end
  subgraph Observability
    OTEL[OTel Collector]
    GRAF[Grafana Dashboard]
  end

  UI -->|Triggers| ORCH
  ORCH --> SRV
  SRV -->|Reads| TF
  SRV -->|Delegates| ANS
  SRV -->|Emits traces| OTEL
  OTEL --> GRAF
  TF -->|State + outputs| SRV
  ANS -->|Deployment logs| SRV
```

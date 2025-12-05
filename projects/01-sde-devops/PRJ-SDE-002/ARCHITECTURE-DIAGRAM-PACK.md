# Architecture Diagram Pack — PRJ-SDE-002

## High-Level Platform (Mermaid)
```mermaid
graph TD
  subgraph DataPlane[Data Plane]
    Targets[Hosts/VMs/Containers]
    Exporters[Node/App/Proxmox Exporters]
    Prometheus[(Prometheus TSDB)]
    Loki[(Loki Object Storage)]
    Promtail[Promtail Agents]
    PBS[(Proxmox Backup Server)]
  end

  subgraph ControlPlane[Control & UX]
    Grafana[Grafana]
    Alertmanager[Alertmanager]
    OnCall[On-call Integrations]
    DashboardUsers[Operators/Engineers]
  end

  Targets --> Exporters --> Prometheus
  Targets --> Promtail --> Loki
  Prometheus --> Alertmanager --> OnCall
  Prometheus --> Grafana
  Loki --> Grafana
  PBS --> DashboardUsers
  Prometheus -. annotations .-> Grafana
  Prometheus --> PBS
```

## Deployment Topology (Mermaid)
```mermaid
graph LR
  subgraph Core[Core Cluster]
    PVE[Proxmox Host]
    VM1[Monitoring VM]
    VM2[Backup VM]
  end

  subgraph Services
    PrometheusS[Prometheus]
    AlertmanagerS[Alertmanager]
    GrafanaS[Grafana]
    LokiS[Loki]
    PromtailS[Promtail Agents]
    PBSS[PBS]
  end

  PVE --> VM1 --> PrometheusS
  VM1 --> AlertmanagerS
  VM1 --> GrafanaS
  VM1 --> LokiS
  VM1 --> PromtailS
  PVE --> VM2 --> PBSS
  PrometheusS --- GrafanaS
  LokiS --- GrafanaS
  PrometheusS --> AlertmanagerS
  PBSS --> VM1
```

## Data & Alert Flow (ASCII)
```
[Targets] --metrics--> [Exporters] --scrape--> [Prometheus] --rules--> [Alertmanager] --routes--> [Slack/Email/PagerDuty]
[Targets] --logs--> [Promtail] --push--> [Loki] --queries--> [Grafana]
[Prometheus/Loki] --dashboards--> [Grafana] --links--> [Operators]
[VM Snapshots] --schedule--> [PBS] --store--> [NFS/SMB] --restore--> [VMs]
```

## Component Responsibilities
- **Prometheus:** Metrics ingestion, rule evaluation, recording rules, alert generation.
- **Grafana:** Dashboard UX, alert annotations, SSO integration, dashboard versioning via git.
- **Loki:** Log aggregation with object storage backend; index and chunk retention split by service tier.
- **Promtail:** Target discovery, relabeling, multi-tenant labels, TLS/mTLS to Loki.
- **Alertmanager:** Routing, grouping, inhibition, silencing, webhooks for runbook automation.
- **PBS:** Incremental, deduplicated backups of Proxmox VMs/CTs; retention and pruning; encryption at rest.

## Deployment Notes
- Run Prometheus + Alertmanager on SSD-backed volumes; Loki data on object storage or RAID-backed disks.
- Secure with mTLS between Promtail→Loki and Prometheus→Alertmanager; SSO (OIDC) for Grafana.
- Pin exporters via service discovery (Consul/SDN) to avoid static target drift.
- Use Infrastructure as Code (Terraform/Ansible) to provision services and apply config via GitOps.

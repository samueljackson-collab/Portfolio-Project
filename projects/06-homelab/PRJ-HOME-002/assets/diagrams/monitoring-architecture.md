# Monitoring Architecture

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
graph TB
    subgraph Targets["< Monitored Targets"]
        direction TB

        subgraph VMs["Virtual Machines"]
            VM1["Wiki.js<br/>192.168.40.20<br/>Port 9100"]
            VM2["Home Assistant<br/>192.168.40.21<br/>Port 9100"]
            VM3["Immich<br/>192.168.40.22<br/>Port 9100"]
            VM4["PostgreSQL<br/>192.168.40.23<br/>Port 9187"]
            VM5["Nginx Proxy<br/>192.168.40.25<br/>Port 9100"]
        end

        subgraph Infrastructure["Infrastructure"]
            PVE["Proxmox VE<br/>192.168.40.10<br/>Port 9221"]
            TrueNAS["TrueNAS<br/>192.168.40.5<br/>API"]
            PBS["Proxmox Backup<br/>192.168.40.15<br/>Port 9092"]
            UDM["UniFi Dream Machine<br/>192.168.40.1<br/>SNMP"]
        end
    end

    subgraph Exporters["= Metrics Exporters"]
        direction TB

        NodeExporter["Node Exporter<br/>System Metrics<br/>CPU, RAM, Disk, Network"]
        PostgresExporter["PostgreSQL Exporter<br/>Database Metrics<br/>Connections, Queries, Cache"]
        ProxmoxExporter["Proxmox Exporter<br/>Hypervisor Metrics<br/>VMs, Storage, Cluster"]
        SNMPExporter["SNMP Exporter<br/>Network Metrics<br/>Switch, Router, APs"]
        BlackboxExporter["Blackbox Exporter<br/>HTTP/HTTPS Probes<br/>SSL Cert Validation"]
    end

    subgraph Prometheus["= Prometheus Server<br/>192.168.40.30<br/>LXC Container 200"]
        direction TB

        Scraper["Metric Scraper<br/>15s interval"]
        TSDB["Time Series Database<br/>30 day retention"]
        Rules["Alert Rules Engine<br/>24 rules configured"]
        PromAPI["HTTP API<br/>Port 9090"]
    end

    subgraph Grafana["= Grafana Dashboard<br/>192.168.40.30<br/>LXC Container 200"]
        direction TB

        WebUI["Web Interface<br/>Port 3000"]
        Dashboards["Dashboards<br/>8 configured"]

        subgraph DashboardList["Dashboard List"]
            D1["1. Homelab Overview"]
            D2["2. VM Resources"]
            D3["3. Storage Analytics"]
            D4["4. Network Traffic"]
            D5["5. PostgreSQL Performance"]
            D6["6. Backup Status"]
            D7["7. SSL Certificates"]
            D8["8. Service Uptime"]
        end
    end

    subgraph Logging["= Loki + Promtail<br/>192.168.40.31<br/>LXC Container 201"]
        direction TB

        Promtail["Promtail Agent<br/>Log Collector"]
        Loki["Loki<br/>Log Aggregation<br/>7 day retention"]
        LogAPI["HTTP API<br/>Port 3100"]
    end

    subgraph Alerting["= AlertManager<br/>192.168.40.30<br/>Co-located with Prometheus"]
        direction TB

        AlertReceiver["Alert Receiver<br/>Port 9093"]
        Router["Routing Rules<br/>Severity-based"]

        subgraph Channels["Notification Channels"]
            Slack["Slack<br/>#homelab-alerts"]
            Email["Email<br/>admin@homelab.local"]
            Pushover["Pushover<br/>Mobile Notifications"]
        end
    end

    subgraph Users["=e Users"]
        Admin["Admin User<br/>Full Access"]
        Viewer["Read-Only User<br/>Dashboard View"]
        Mobile["Mobile App<br/>Grafana Mobile"]
    end

    %% Connections: Targets to Exporters
    VM1 & VM2 & VM3 & VM5 --> NodeExporter
    VM4 --> PostgresExporter
    PVE --> ProxmoxExporter
    UDM --> SNMPExporter
    TrueNAS --> BlackboxExporter

    %% Connections: Exporters to Prometheus
    NodeExporter -->|Scrape<br/>:9100/metrics| Scraper
    PostgresExporter -->|Scrape<br/>:9187/metrics| Scraper
    ProxmoxExporter -->|Scrape<br/>:9221/metrics| Scraper
    SNMPExporter -->|Scrape<br/>:9116/metrics| Scraper
    BlackboxExporter -->|Probe<br/>HTTPS endpoints| Scraper

    %% Prometheus internal flow
    Scraper --> TSDB
    TSDB --> Rules
    TSDB --> PromAPI

    %% Prometheus to Grafana
    PromAPI -->|Query<br/>PromQL| Dashboards
    Dashboards --> D1 & D2 & D3 & D4 & D5 & D6 & D7 & D8

    %% Logging flow
    VM1 & VM2 & VM3 & VM4 & VM5 -.->|Ship Logs<br/>Docker JSON| Promtail
    Promtail --> Loki
    Loki --> LogAPI
    LogAPI -.->|Log Query<br/>LogQL| Dashboards

    %% Alerting flow
    Rules -->|Fire Alerts| AlertReceiver
    AlertReceiver --> Router
    Router -->|Critical| Slack
    Router -->|Warning| Email
    Router -->|Info| Pushover

    %% User access
    Admin --> WebUI
    Viewer --> WebUI
    Mobile --> WebUI
    WebUI --> Dashboards

    %% Styling
    classDef vm fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef infra fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#000
    classDef exporter fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#000
    classDef monitoring fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#000
    classDef logging fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000
    classDef alerting fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000
    classDef user fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#000
    classDef dashboard fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000

    class VM1,VM2,VM3,VM4,VM5 vm
    class PVE,TrueNAS,PBS,UDM infra
    class NodeExporter,PostgresExporter,ProxmoxExporter,SNMPExporter,BlackboxExporter exporter
    class Scraper,TSDB,Rules,PromAPI monitoring
    class Promtail,Loki,LogAPI logging
    class AlertReceiver,Router,Slack,Email,Pushover alerting
    class Admin,Viewer,Mobile user
    class D1,D2,D3,D4,D5,D6,D7,D8 dashboard
```

## Source File

Original: `monitoring-architecture.mmd`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*

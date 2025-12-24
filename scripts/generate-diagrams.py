#!/usr/bin/env python3
"""
Architecture Diagram Generator
Generates Mermaid diagram files for portfolio projects
"""

import os
from pathlib import Path
from datetime import datetime


class DiagramGenerator:
    """Generate architecture diagrams for portfolio projects"""

    def __init__(self, output_dir="assets/diagrams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_homelab_architecture(self):
        """Generate homelab infrastructure diagram"""
        diagram = """graph TB
    subgraph Internet
        EXTERNAL[External Users]
        CLOUDFLARE[Cloudflare DNS/CDN]
    end

    subgraph "Network Layer"
        ROUTER[OPNsense Router<br/>Firewall + VPN]
        SWITCH[Managed Switch<br/>VLAN Segmentation]
        AP[UniFi Access Points<br/>WiFi Networks]
    end

    subgraph "Proxmox VE Host"
        subgraph "Virtual Machines"
            WIKIJS[Wiki.js Documentation<br/>Port 3000]
            HOMEASSISTANT[Home Assistant<br/>Port 8123]
            IMMICH[Immich Photo Management<br/>Port 2283]
            POSTGRES[PostgreSQL Database<br/>Port 5432]
        end

        subgraph "LXC Containers"
            NGINX[Nginx Proxy Manager<br/>Port 80/443]
            PROMETHEUS[Prometheus<br/>Port 9090]
            GRAFANA[Grafana Dashboards<br/>Port 3001]
            LOKI[Loki Log Aggregation<br/>Port 3100]
        end
    end

    subgraph "Storage"
        ZFS[ZFS Storage Pool<br/>2TB RAID-Z]
        BACKUP[Proxmox Backup Server<br/>External Drives]
    end

    EXTERNAL --> CLOUDFLARE
    CLOUDFLARE --> ROUTER
    ROUTER --> SWITCH
    SWITCH --> AP
    SWITCH --> NGINX
    NGINX --> WIKIJS
    NGINX --> HOMEASSISTANT
    NGINX --> IMMICH
    NGINX --> GRAFANA

    WIKIJS --> POSTGRES
    IMMICH --> POSTGRES

    PROMETHEUS --> GRAFANA
    LOKI --> GRAFANA

    POSTGRES --> ZFS
    WIKIJS --> ZFS
    IMMICH --> ZFS

    ZFS --> BACKUP

    style EXTERNAL fill:#e1f5ff
    style NGINX fill:#90ee90
    style GRAFANA fill:#ffcc99
    style PROMETHEUS fill:#ff9999
"""
        self._write_diagram("homelab-architecture", diagram)

    def generate_aws_vpc_architecture(self):
        """Generate AWS VPC infrastructure diagram"""
        diagram = """graph TB
    subgraph "AWS Cloud"
        subgraph "VPC 10.0.0.0/16"
            IGW[Internet Gateway]

            subgraph "Availability Zone A"
                subgraph "Public Subnet A<br/>10.0.1.0/24"
                    NAT1[NAT Gateway]
                    ALB1[Application Load Balancer]
                end

                subgraph "Private Subnet A<br/>10.0.3.0/24"
                    APP1[Application Server]
                    WORKER1[Background Worker]
                end

                subgraph "Database Subnet A<br/>10.0.5.0/24"
                    RDS1[RDS Primary<br/>PostgreSQL]
                end
            end

            subgraph "Availability Zone B"
                subgraph "Public Subnet B<br/>10.0.2.0/24"
                    NAT2[NAT Gateway]
                end

                subgraph "Private Subnet B<br/>10.0.4.0/24"
                    APP2[Application Server]
                    WORKER2[Background Worker]
                end

                subgraph "Database Subnet B<br/>10.0.6.0/24"
                    RDS2[RDS Standby<br/>PostgreSQL]
                end
            end
        end

        subgraph "Monitoring & Security"
            CLOUDWATCH[CloudWatch Logs & Metrics]
            GUARDDUTY[GuardDuty]
            CLOUDTRAIL[CloudTrail Audit]
        end
    end

    INTERNET[Internet] --> IGW
    IGW --> ALB1
    ALB1 --> APP1
    ALB1 --> APP2

    APP1 --> NAT1
    APP2 --> NAT2
    NAT1 --> IGW
    NAT2 --> IGW

    APP1 --> RDS1
    APP2 --> RDS1
    WORKER1 --> RDS1
    WORKER2 --> RDS1

    RDS1 -.replication.-> RDS2

    APP1 --> CLOUDWATCH
    APP2 --> CLOUDWATCH
    WORKER1 --> CLOUDWATCH
    WORKER2 --> CLOUDWATCH

    style IGW fill:#ff9999
    style ALB1 fill:#90ee90
    style RDS1 fill:#ffcc99
    style RDS2 fill:#ffffcc
    style CLOUDWATCH fill:#e1f5ff
"""
        self._write_diagram("aws-vpc-architecture", diagram)

    def generate_monitoring_stack(self):
        """Generate observability stack diagram"""
        diagram = """graph TB
    subgraph "Data Sources"
        APP[Application Servers]
        INFRA[Infrastructure Metrics]
        LOGS[Application Logs]
        TRACES[Distributed Traces]
    end

    subgraph "Collection Layer"
        PROMETHEUS[Prometheus<br/>Metrics Scraping]
        LOKI[Loki<br/>Log Aggregation]
        TEMPO[Tempo<br/>Trace Storage]
        EXPORTERS[Node/Service Exporters]
    end

    subgraph "Storage Layer"
        TSDB[Time Series Database]
        OBJECT[Object Storage<br/>S3/MinIO]
    end

    subgraph "Visualization & Alerting"
        GRAFANA[Grafana Dashboards]
        ALERTMANAGER[Alert Manager]
        PAGERDUTY[PagerDuty/Slack]
    end

    APP --> EXPORTERS
    INFRA --> EXPORTERS
    LOGS --> LOKI
    TRACES --> TEMPO

    EXPORTERS --> PROMETHEUS
    PROMETHEUS --> TSDB
    LOKI --> OBJECT
    TEMPO --> OBJECT

    TSDB --> GRAFANA
    OBJECT --> GRAFANA

    PROMETHEUS --> ALERTMANAGER
    ALERTMANAGER --> PAGERDUTY

    style PROMETHEUS fill:#ff9999
    style LOKI fill:#90ee90
    style GRAFANA fill:#ffcc99
    style ALERTMANAGER fill:#e1f5ff
"""
        self._write_diagram("monitoring-stack", diagram)

    def generate_kubernetes_cicd(self):
        """Generate Kubernetes CI/CD pipeline diagram"""
        diagram = """graph LR
    subgraph "Development"
        DEV[Developer]
        GIT[Git Repository]
    end

    subgraph "CI Pipeline"
        TRIGGER[GitHub Actions Trigger]
        BUILD[Build Container Image]
        TEST[Run Tests]
        SCAN[Security Scan<br/>Trivy/Snyk]
        PUSH[Push to Registry]
    end

    subgraph "GitOps"
        ARGOCD[ArgoCD]
        HELM[Helm Charts]
        MANIFESTS[K8s Manifests]
    end

    subgraph "Kubernetes Cluster"
        subgraph "Staging Namespace"
            STAGING[Staging Deployment]
        end

        subgraph "Production Namespace"
            CANARY[Canary Deployment]
            PROD[Production Deployment]
        end

        INGRESS[Ingress Controller]
        MONITORING[Prometheus/Grafana]
    end

    DEV --> GIT
    GIT --> TRIGGER
    TRIGGER --> BUILD
    BUILD --> TEST
    TEST --> SCAN
    SCAN --> PUSH

    PUSH --> ARGOCD
    HELM --> ARGOCD
    MANIFESTS --> ARGOCD

    ARGOCD --> STAGING
    STAGING -.manual approval.-> CANARY
    CANARY -.automated promotion.-> PROD

    INGRESS --> STAGING
    INGRESS --> CANARY
    INGRESS --> PROD

    MONITORING --> STAGING
    MONITORING --> CANARY
    MONITORING --> PROD

    style BUILD fill:#90ee90
    style SCAN fill:#ff9999
    style ARGOCD fill:#ffcc99
    style PROD fill:#e1f5ff
"""
        self._write_diagram("kubernetes-cicd", diagram)

    def generate_database_ha(self):
        """Generate PostgreSQL HA architecture"""
        diagram = """graph TB
    subgraph "Application Layer"
        APP1[Application Instance 1]
        APP2[Application Instance 2]
        APP3[Application Instance 3]
    end

    subgraph "Connection Pooling"
        PGBOUNCER[PgBouncer Connection Pool]
    end

    subgraph "Database Cluster"
        PRIMARY[PostgreSQL Primary<br/>Read/Write]
        REPLICA1[PostgreSQL Replica 1<br/>Read-Only]
        REPLICA2[PostgreSQL Replica 2<br/>Read-Only]
    end

    subgraph "High Availability"
        PATRONI[Patroni Cluster Manager]
        ETCD[etcd Consensus Store]
        HAPROXY[HAProxy Load Balancer]
    end

    subgraph "Backup & Recovery"
        WAL[WAL Archiving<br/>S3/MinIO]
        BACKUP[pgBackRest<br/>Point-in-Time Recovery]
    end

    subgraph "Monitoring"
        EXPORTER[PostgreSQL Exporter]
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana Dashboards]
    end

    APP1 --> PGBOUNCER
    APP2 --> PGBOUNCER
    APP3 --> PGBOUNCER

    PGBOUNCER --> HAPROXY
    HAPROXY --> PRIMARY
    HAPROXY --> REPLICA1
    HAPROXY --> REPLICA2

    PRIMARY -.streaming replication.-> REPLICA1
    PRIMARY -.streaming replication.-> REPLICA2

    PATRONI --> PRIMARY
    PATRONI --> REPLICA1
    PATRONI --> REPLICA2
    PATRONI --> ETCD

    PRIMARY --> WAL
    PRIMARY --> BACKUP

    EXPORTER --> PROMETHEUS
    PROMETHEUS --> GRAFANA

    PRIMARY --> EXPORTER
    REPLICA1 --> EXPORTER
    REPLICA2 --> EXPORTER

    style PRIMARY fill:#90ee90
    style REPLICA1 fill:#ffffcc
    style REPLICA2 fill:#ffffcc
    style HAPROXY fill:#ff9999
    style PATRONI fill:#ffcc99
"""
        self._write_diagram("postgresql-ha", diagram)

    def _write_diagram(self, name, content):
        """Write diagram content to file"""
        filepath = self.output_dir / f"{name}.mmd"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✅ Generated: {filepath}")

    def generate_all(self):
        """Generate all diagrams"""
        print("🎨 Generating Architecture Diagrams...")
        print("=" * 60)

        self.generate_homelab_architecture()
        self.generate_aws_vpc_architecture()
        self.generate_monitoring_stack()
        self.generate_kubernetes_cicd()
        self.generate_database_ha()

        print("=" * 60)
        print(f"✨ Complete! Diagrams saved to: {self.output_dir}")
        print(f"📊 Total diagrams: {len(list(self.output_dir.glob('*.mmd')))}")
        print("\n💡 Next Steps:")
        print("1. View diagrams using Mermaid Live Editor: https://mermaid.live")
        print("2. Convert to PNG using mermaid-cli:")
        print("   npx -p @mermaid-js/mermaid-cli mmdc -i diagram.mmd -o diagram.png")
        print("3. Add diagrams to project documentation")


def main():
    """Main entry point"""
    generator = DiagramGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()

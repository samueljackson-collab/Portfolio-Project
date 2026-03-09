---
title: Database Infrastructure
description: This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file. graph TB subgraph Internet['🌐 Internet'] Users[End Users] end subgraph AWSCloud['☁️ AWS Cloud
tags: [documentation, portfolio]
path: portfolio/01-sde-devops/database-infrastructure
created: 2026-03-08T22:19:12.939478+00:00
updated: 2026-03-08T22:04:38.169902+00:00
---

# Database Infrastructure

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        Users[End Users]
    end

    subgraph AWSCloud["☁️ AWS Cloud - Region: us-east-1"]
        subgraph VPC["VPC - 10.0.0.0/16"]
            subgraph PublicSubnets["Public Subnets (10.0.1.0/24, 10.0.2.0/24)"]
                ALB[Application Load Balancer<br/>Port 443 HTTPS]
                NAT[NAT Gateway<br/>Internet Access for Private]
            end

            subgraph PrivateSubnets["Private Subnets - AZ1 & AZ2<br/>(10.0.10.0/24, 10.0.11.0/24)"]
                subgraph AppTier["Application Tier"]
                    APP1[App Server 1<br/>ECS/EC2<br/>10.0.10.10]
                    APP2[App Server 2<br/>ECS/EC2<br/>10.0.11.10]
                end

                subgraph SecurityGroups["Security Groups"]
                    AppSG[App Security Group<br/>sg-app-xxxx<br/>Allows: 443 from ALB]
                    DBSG[DB Security Group<br/>sg-db-xxxx<br/>Allows: 5432 from App SG only]
                end
            end

            subgraph DatabaseSubnets["Database Subnets - AZ1 & AZ2<br/>(10.0.20.0/24, 10.0.21.0/24)"]
                subgraph RDSInstance["AWS RDS PostgreSQL"]
                    subgraph Primary["Primary Instance - AZ1"]
                        RDSPrimary[RDS Primary<br/>PostgreSQL 15.4<br/>db.t3.small<br/>Endpoint: mydb.xxx.rds.amazonaws.com:5432]
                    end

                    subgraph Standby["Standby Instance - AZ2<br/>(Multi-AZ)"]
                        RDSStandby[RDS Standby<br/>Synchronous Replication<br/>Automatic Failover <60s]
                    end
                end

                Storage[EBS Storage<br/>20-100 GB (Auto-scaling)<br/>Encrypted at Rest<br/>gp3 SSD]
            end
        end

        subgraph Monitoring["📊 Monitoring & Alerting"]
            CW[CloudWatch<br/>Metrics & Logs]
            CWAlarms[CloudWatch Alarms<br/>CPU >80%<br/>Storage <2GB<br/>Connections >80]
            SNS[SNS Topic<br/>Alert Notifications]
        end

        subgraph Backup["💾 Backup & Recovery"]
            AutoBackup[Automated Backups<br/>7-day retention<br/>Daily at 3:00 AM UTC]
            Snapshots[Manual Snapshots<br/>Point-in-time Recovery<br/>35-day retention available]
            S3Backup[S3 Bucket<br/>Backup Storage<br/>Cross-region Replication]
        end

        subgraph IAC["🤖 Infrastructure as Code"]
            TF[Terraform<br/>Database Module<br/>Root Configuration]
            CICD[GitHub Actions<br/>terraform plan/apply<br/>Automated Deployment]
            StateBackend[S3 State Backend<br/>+ DynamoDB Lock<br/>Remote State Management]
        end
    end

    %% User Flow
    Users -->|HTTPS| ALB
    ALB -->|Forward| APP1
    ALB -->|Forward| APP2

    %% Application to Database
    APP1 -->|PostgreSQL:5432| RDSPrimary
    APP2 -->|PostgreSQL:5432| RDSPrimary

    %% Security Group Rules
    AppSG -.->|Protect| APP1
    AppSG -.->|Protect| APP2
    DBSG -.->|Protect| RDSPrimary
    DBSG -.->|Protect| RDSStandby

    %% High Availability
    RDSPrimary <-->|Sync Replication| RDSStandby
    RDSPrimary --> Storage
    RDSStandby --> Storage

    %% Monitoring Connections
    RDSPrimary -.->|Metrics| CW
    APP1 -.->|Logs| CW
    APP2 -.->|Logs| CW
    CW --> CWAlarms
    CWAlarms -->|Trigger| SNS

    %% Backup Connections
    RDSPrimary -.->|Auto Backup| AutoBackup
    RDSPrimary -.->|Manual Snapshot| Snapshots
    AutoBackup --> S3Backup
    Snapshots --> S3Backup

    %% Infrastructure as Code
    TF -.->|Provision| VPC
    TF -.->|Provision| RDSInstance
    TF -.->|Configure| SecurityGroups
    TF -.->|Create| CWAlarms
    CICD -.->|Run| TF
    TF -.->|Store State| StateBackend

    %% Styling
    classDef internet fill:#f9f,stroke:#333,stroke-width:2px
    classDef public fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef private fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef database fill:#c8e6c9,stroke:#1b5e20,stroke-width:3px
    classDef security fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    classDef monitoring fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef backup fill:#e0f2f1,stroke:#004d40,stroke-width:2px
    classDef iac fill:#fff9c4,stroke:#f57f17,stroke-width:2px

    class Users internet
    class ALB,NAT public
    class APP1,APP2 private
    class RDSPrimary,RDSStandby,Storage database
    class AppSG,DBSG security
    class CW,CWAlarms,SNS monitoring
    class AutoBackup,Snapshots,S3Backup backup
    class TF,CICD,StateBackend iac

    %% Legend
    Legend["📋 Architecture Components:<br/><br/>🔵 Internet - User Access<br/>🔷 Public Tier - Load Balancer<br/>🟠 Private Tier - App Servers<br/>🟢 Database Tier - RDS PostgreSQL<br/>🔴 Security - SGs & Network ACLs<br/>🟣 Monitoring - CloudWatch & Alarms<br/>🟦 Backup - Automated & Manual<br/>🟡 IaC - Terraform & CI/CD<br/><br/>━━ Data Flow<br/>┄┄ Management/Monitoring"]

    style Legend fill:#F0F8FF,stroke:#4169E1,stroke-width:2px,text-align:left

    %% Technical Specifications
    Specs["⚙️ Technical Specifications:<br/><br/>Database:<br/>• Engine: PostgreSQL 15.4<br/>• Instance: db.t3.small (2 vCPU, 2GB RAM)<br/>• Storage: 20GB (auto-scale to 100GB)<br/>• Multi-AZ: Enabled (2 AZs)<br/>• Encryption: AES-256 at rest<br/>• Public Access: Disabled<br/><br/>High Availability:<br/>• RTO: <60 seconds (auto-failover)<br/>• RPO: <5 seconds (sync replication)<br/>• Availability: 99.95% SLA<br/><br/>Security:<br/>• Private subnets only<br/>• SG whitelist (port 5432 app only)<br/>• Encrypted connections (SSL/TLS)<br/>• IAM auth support<br/><br/>Backup:<br/>• Daily automated backups<br/>• 7-day retention (configurable)<br/>• Point-in-time recovery<br/>• Cross-region snapshot copies"]

    style Specs fill:#F5F5DC,stroke:#8B4513,stroke-width:2px,text-align:left
```

## Source File

Original: `database-infrastructure.mermaid`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*

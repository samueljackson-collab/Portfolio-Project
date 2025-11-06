# Architecture Diagrams - AWS RDS Terraform Module

**Project:** PRJ-SDE-001 - Production Database Infrastructure
**Format:** Mermaid diagrams (render on GitHub, VS Code, or https://mermaid.live)

---

## Diagram 1: Infrastructure Overview

```mermaid
graph TB
    subgraph "AWS Cloud"
        subgraph "VPC 10.0.0.0/16"
            subgraph "Availability Zone A"
                PrivateSubnetA["Private Subnet A<br/>10.0.10.0/24"]
                RDS_Primary["RDS PostgreSQL<br/>Primary Instance<br/>✓ Encrypted<br/>✓ Automated Backups"]
            end

            subgraph "Availability Zone B"
                PrivateSubnetB["Private Subnet B<br/>10.0.11.0/24"]
                RDS_Standby["RDS PostgreSQL<br/>Standby Instance<br/>(Multi-AZ)"]
            end

            DBSubnetGroup["DB Subnet Group<br/>Spans AZ-A & AZ-B"]
            SecurityGroup["Security Group<br/>✓ Port 5432<br/>✓ Dynamic Rules<br/>✓ Least Privilege"]

            AppEC2["Application Servers<br/>(EC2/ECS)"]
        end
    end

    AppEC2 -->|PostgreSQL<br/>Port 5432| SecurityGroup
    SecurityGroup --> RDS_Primary
    DBSubnetGroup -.contains.-> PrivateSubnetA
    DBSubnetGroup -.contains.-> PrivateSubnetB
    RDS_Primary -.in.-> PrivateSubnetA
    RDS_Standby -.in.-> PrivateSubnetB
    RDS_Primary -.Sync Replication.-> RDS_Standby

    style RDS_Primary fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    style RDS_Standby fill:#3498db,stroke:#2980b9,stroke-width:2px
    style SecurityGroup fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style AppEC2 fill:#9b59b6,stroke:#8e44ad,stroke-width:2px
```

---

## Diagram 2: Security Layers (Defense-in-Depth)

```mermaid
graph LR
    Internet([Internet]) -.blocked.->|No Public Access| RDS

    subgraph "Security Layer 1: Network Isolation"
        PrivateSubnet["Private Subnets<br/>No IGW Route"]
    end

    subgraph "Security Layer 2: Access Control"
        SG["Security Group<br/>Port 5432<br/>Whitelisted Sources Only"]
    end

    subgraph "Security Layer 3: Encryption"
        Encryption["✓ At Rest (AES-256)<br/>✓ In Transit (TLS)<br/>✓ Backup Encryption"]
    end

    subgraph "Security Layer 4: Database"
        RDS["RDS PostgreSQL<br/>✓ IAM Auth Available<br/>✓ Audit Logs"]
    end

    App["Authorized<br/>Applications"] --> SG
    SG --> PrivateSubnet
    PrivateSubnet --> Encryption
    Encryption --> RDS

    style Internet fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style RDS fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    style SG fill:#f39c12,stroke:#e67e22,stroke-width:2px
    style App fill:#3498db,stroke:#2980b9,stroke-width:2px
```

---

## Diagram 3: Terraform Resource Dependencies

```mermaid
graph TD
    VPC["AWS VPC<br/>(External)"]
    Subnets["Private Subnets<br/>(External)"]

    VPC --> SG["Security Group<br/>aws_security_group.db"]
    Subnets --> DBSubnetGroup["DB Subnet Group<br/>aws_db_subnet_group.this"]

    SG --> RDS["RDS Instance<br/>aws_db_instance.this"]
    DBSubnetGroup --> RDS

    RDS --> Output1["Output:<br/>db_endpoint"]
    SG --> Output2["Output:<br/>db_security_group_id"]

    style VPC fill:#ecf0f1,stroke:#95a5a6,stroke-width:1px,stroke-dasharray: 5 5
    style Subnets fill:#ecf0f1,stroke:#95a5a6,stroke-width:1px,stroke-dasharray: 5 5
    style SG fill:#3498db,stroke:#2980b9,stroke-width:2px
    style DBSubnetGroup fill:#3498db,stroke:#2980b9,stroke-width:2px
    style RDS fill:#2ecc71,stroke:#27ae60,stroke-width:3px
    style Output1 fill:#f39c12,stroke:#e67e22,stroke-width:2px
    style Output2 fill:#f39c12,stroke:#e67e22,stroke-width:2px
```

---

## Diagram 4: Multi-AZ Failover Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant DNS as RDS Endpoint DNS
    participant Primary as Primary DB (AZ-A)
    participant Standby as Standby DB (AZ-B)
    participant AWS as AWS RDS Service

    Note over App,Standby: Normal Operations
    App->>DNS: Connect to db-endpoint.rds.amazonaws.com
    DNS->>Primary: Route to Primary (Active)
    Primary->>App: Handle read/write queries
    Primary-->>Standby: Synchronous replication

    Note over Primary: ⚠️ Primary Failure Detected
    AWS->>Primary: Health check fails
    AWS->>Standby: Promote to Primary
    AWS->>DNS: Update DNS to Standby IP

    Note over App,Standby: Automatic Failover (<60s)
    App->>DNS: Connect to same endpoint
    DNS->>Standby: Route to new Primary (Promoted)
    Standby->>App: Handle read/write queries

    Note over App: Application requires no code changes!
```

---

## Diagram 5: Deployment Workflow

```mermaid
flowchart TD
    Start([Developer]) --> Clone[Clone Repository]
    Clone --> Configure[Configure terraform.tfvars]

    Configure --> Init[terraform init]
    Init --> Validate[terraform validate]
    Validate --> Plan[terraform plan]

    Plan --> Review{Review Plan<br/>Acceptable?}
    Review -->|No| Configure
    Review -->|Yes| Apply[terraform apply]

    Apply --> Create1[Create Security Group]
    Create1 --> Create2[Create DB Subnet Group]
    Create2 --> Create3[Create RDS Instance]

    Create3 --> Wait[Wait 10-15 minutes<br/>RDS provisioning]
    Wait --> Ready[Database Ready]

    Ready --> Output[terraform output<br/>Get DB endpoint]
    Output --> Connect[Applications Connect]

    Connect --> Monitor[Monitor CloudWatch]
    Monitor --> End([In Production])

    style Start fill:#3498db,stroke:#2980b9,stroke-width:2px
    style Apply fill:#f39c12,stroke:#e67e22,stroke-width:2px
    style Ready fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    style End fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    style Review fill:#e74c3c,stroke:#c0392b,stroke-width:2px
```

---

## Diagram 6: Cost Optimization Decision Tree

```mermaid
flowchart TD
    Start{What environment?}

    Start -->|Development| Dev[Development Config]
    Start -->|Staging| Staging[Staging Config]
    Start -->|Production| Prod[Production Config]

    Dev --> DevSpecs["Instance: db.t3.micro<br/>Multi-AZ: false<br/>Backups: 1 day<br/>Cost: ~$15/month"]

    Staging --> StagingSpecs["Instance: db.t3.small<br/>Multi-AZ: false<br/>Backups: 7 days<br/>Cost: ~$40/month"]

    Prod --> HA{High Availability<br/>Required?}
    HA -->|Yes| ProdHA["Instance: db.r6g.large<br/>Multi-AZ: true<br/>Backups: 30 days<br/>Deletion Protection: true<br/>Cost: ~$300/month"]
    HA -->|No| ProdSingle["Instance: db.t3.medium<br/>Multi-AZ: false<br/>Backups: 30 days<br/>Cost: ~$150/month"]

    DevSpecs --> Deploy[Deploy with<br/>terraform apply]
    StagingSpecs --> Deploy
    ProdHA --> Deploy
    ProdSingle --> Deploy

    style Start fill:#3498db,stroke:#2980b9,stroke-width:2px
    style Dev fill:#95a5a6,stroke:#7f8c8d,stroke-width:2px
    style Staging fill:#f39c12,stroke:#e67e22,stroke-width:2px
    style Prod fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style ProdHA fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    style Deploy fill:#9b59b6,stroke:#8e44ad,stroke-width:2px
```

---

## Diagram 7: Backup & Recovery Strategy

```mermaid
flowchart LR
    subgraph "Backup Layer 1: Automated Daily"
        RDS[(RDS Instance)] -->|Automated<br/>Daily Backup| Snapshots1["Automated Snapshots<br/>Retention: 7-30 days<br/>Point-in-time Recovery"]
    end

    subgraph "Backup Layer 2: Manual Milestones"
        RDS -->|Before Major<br/>Deployments| Snapshots2["Manual Snapshots<br/>Retention: Custom<br/>Long-term Archive"]
    end

    subgraph "Backup Layer 3: Cross-Region (Prod)"
        Snapshots1 -->|Weekly<br/>Copy| CrossRegion["Cross-Region Snapshots<br/>Disaster Recovery<br/>Secondary Region"]
    end

    subgraph "Recovery Scenarios"
        Snapshots1 --> |Scenario 1:<br/>Accidental Deletion| PITR[Point-in-Time Restore<br/>RPO: <1 hour<br/>RTO: 15-30 min]
        Snapshots1 --> |Scenario 2:<br/>DB Corruption| SnapshotRestore[Snapshot Restore<br/>RPO: 24 hours<br/>RTO: 20-45 min]
        CrossRegion --> |Scenario 3:<br/>Regional Disaster| DRRestore[DR Restore<br/>RPO: 1 week<br/>RTO: 1-4 hours]
    end

    style RDS fill:#3498db,stroke:#2980b9,stroke-width:2px
    style Snapshots1 fill:#2ecc71,stroke:#27ae60,stroke-width:2px
    style Snapshots2 fill:#f39c12,stroke:#e67e22,stroke-width:2px
    style CrossRegion fill:#9b59b6,stroke:#8e44ad,stroke-width:2px
    style PITR fill:#1abc9c,stroke:#16a085,stroke-width:2px
```

---

## Diagram 8: Security Group Dynamic Rules

```mermaid
flowchart TD
    Input["variable allowed_security_group_ids<br/>List of SG IDs"]

    Input --> ForEach{dynamic block<br/>for_each loop}

    ForEach --> Rule1["Ingress Rule 1:<br/>from: sg-app-web<br/>port: 5432"]
    ForEach --> Rule2["Ingress Rule 2:<br/>from: sg-app-api<br/>port: 5432"]
    ForEach --> Rule3["Ingress Rule 3:<br/>from: sg-app-worker<br/>port: 5432"]
    ForEach --> RuleN["Ingress Rule N:<br/>from: sg-app-X<br/>port: 5432"]

    Rule1 --> SG[AWS Security Group]
    Rule2 --> SG
    Rule3 --> SG
    RuleN --> SG

    SG --> RDS[(RDS Instance<br/>Port 5432)]

    Note["✅ Scales from 0 to unlimited SGs<br/>✅ No hardcoded rules<br/>✅ Least-privilege access"]

    style Input fill:#3498db,stroke:#2980b9,stroke-width:2px
    style ForEach fill:#f39c12,stroke:#e67e22,stroke-width:2px
    style SG fill:#e74c3c,stroke:#c0392b,stroke-width:2px
    style RDS fill:#2ecc71,stroke:#27ae60,stroke-width:2px
```

---

## How to Use These Diagrams

### Rendering Mermaid Diagrams

**GitHub/GitLab:**
- Automatically rendered in Markdown files
- No action needed

**VS Code:**
```bash
# Install Mermaid extension
ext install bierner.markdown-mermaid
```

**Online Editor:**
- Visit https://mermaid.live
- Paste diagram code
- Export as PNG/SVG

**Generate Images:**
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i ARCHITECTURE-DIAGRAMS.md -o diagrams/

# Generate SVG (better quality)
mmdc -i ARCHITECTURE-DIAGRAMS.md -o diagrams/ -t svg
```

### In Presentations

1. **For slides:** Export as PNG/SVG and insert
2. **For docs:** Embed directly (GitHub renders automatically)
3. **For interviews:** Have https://mermaid.live open with diagrams ready

---

## Diagram Purpose Reference

| Diagram | Purpose | Best For |
|---------|---------|----------|
| **1. Infrastructure Overview** | High-level architecture | Executives, interviews |
| **2. Security Layers** | Defense-in-depth approach | Security-focused audiences |
| **3. Resource Dependencies** | Terraform execution order | Technical deep-dives |
| **4. Multi-AZ Failover** | HA mechanism explanation | Architects, SREs |
| **5. Deployment Workflow** | Step-by-step process | New team members, docs |
| **6. Cost Optimization** | Environment sizing decisions | Managers, FinOps |
| **7. Backup & Recovery** | DR strategy and RPO/RTO | Compliance, audits |
| **8. Dynamic Security Groups** | Code pattern explanation | Engineers, code reviews |

---

*Architecture Diagrams v1.0 - Last Updated: November 2025*

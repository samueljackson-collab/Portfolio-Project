# P01 – Diagrams

## System Topology (Mermaid)
```mermaid
flowchart LR
  User[User] -->|HTTPS| ALB[Application Load Balancer]
  ALB --> ASG[Auto Scaling Group]
  ASG --> App[App Instances]
  App --> RDS[(Amazon RDS)]
  App --> Redis[(ElastiCache Redis)]
  ALB -->|Health Checks| Route53[Route 53]
  CloudWatch[CloudWatch Alarms] -->|Notify| SNS[PagerDuty/Webhook]
```

## System Topology (ASCII)
```
User --> Route53 --> ALB ==> ASG -> App Nodes -> RDS
                          \--> CloudWatch Alarms -> SNS/PagerDuty
                          \--> Redis Cache
```

## CI/CD Flow (Mermaid)
```mermaid
flowchart LR
  Dev[Developer Commit] --> GH[GitHub Actions]
  GH -->|Lint/Test| QA[Quality Gate]
  QA -->|Build| AMI[AMI/Container Build]
  AMI -->|Deploy| CD[CD Stage]
  CD -->|Apply| Terraform[Terraform Plan/Apply]
  CD -->|Run| Ansible[Ansible Playbooks]
  QA -->|Scan| Sec[Security Scans]
  Sec -->|Report| GH
```

## CI/CD Flow (ASCII)
```
Dev commit -> GitHub Actions -> Lint/Test -> Security Scan -> Build Artifact -> CD Stage
        -> Terraform plan/apply -> Ansible config -> Notify
```

## IaC Layering (Mermaid)
```mermaid
flowchart TB
  TF[Terraform Modules]
  CF[CloudFormation Templates]
  DSC[Desired State Config]
  TF --> CF --> DSC
  TF --> RemoteState[(S3 + DynamoDB State)]
  CF --> Hooks[Lambda Hooks]
```

## IaC Layering (ASCII)
```
Terraform modules -> CloudFormation stack -> Desired state configs
         |-> Remote state (S3/DynamoDB)
         |-> Lambda hooks
```

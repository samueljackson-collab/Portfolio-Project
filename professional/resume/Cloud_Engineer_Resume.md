# Samuel Jackson
**Cloud Engineer & Infrastructure Architect**

📍 Seattle, WA | 📧 samuel.jackson@example.com | 📞 (555) 123-4567  
🔗 [GitHub](https://github.com/samueljackson-collab) | 🔗 [Portfolio](https://samueljackson.dev)

---

## Professional Summary

Cloud-focused infrastructure engineer with hands-on experience designing and deploying AWS environments, implementing Infrastructure as Code (Terraform), and building observability solutions. Proven track record of translating on-premises concepts to cloud-native architectures through extensive homelab experimentation. Strong understanding of cloud security, cost optimization, and high-availability design patterns.

---

## Cloud & Technical Skills

**Cloud Platforms:** AWS (EC2, RDS, S3, VPC, IAM, CloudFormation, CloudWatch), Azure (VMs, VNets, Storage), GCP (Compute Engine)  
**Infrastructure as Code:** Terraform (modules, state management), CloudFormation, Ansible  
**Containers & Orchestration:** Docker, Docker Compose, Kubernetes (EKS), AWS ECS/Fargate  
**Networking:** VPC design, subnets, security groups, NACLs, VPN (site-to-site, client), load balancers  
**Monitoring & Observability:** Prometheus, Grafana, Loki, CloudWatch, AWS X-Ray  
**Security:** IAM policies, encryption (KMS), secrets management, CIS benchmarks, security hardening  
**Databases:** RDS (PostgreSQL, MySQL), DynamoDB, Redis (ElastiCache), backup/restore strategies  
**CI/CD:** GitHub Actions, GitLab CI, AWS CodePipeline, infrastructure automation  
**Scripting & Automation:** Python, Bash, PowerShell, Git

---

## Professional Experience

### Desktop Support Technician — 3DM, Redmond, WA
**February 2025 – Present**

- Support cloud-connected enterprise applications (Office 365, Azure AD)
- Troubleshoot VPN connectivity for remote workers accessing cloud resources
- Document cloud service configurations and access procedures
- Assist with Azure AD user provisioning and MFA setup

### Freelance IT & Web Manager — Self-Employed
**2015 – 2022**

- Migrated client websites from on-premises hosting to AWS and managed cloud infrastructure
- Designed cost-effective cloud architectures balancing performance and budget
- Implemented automated backup solutions using S3 and Glacier for long-term retention
- Managed DNS, CDN (CloudFront), and SSL certificate lifecycle

**Cloud Migration Project:**
- Migrated 5 WordPress sites from shared hosting to AWS (EC2 + RDS)
- Achieved 99.95% uptime improvement and 50% cost reduction
- Implemented auto-scaling and CloudWatch monitoring

---

## Cloud Projects & Portfolio

### AWS Database Infrastructure Module (Terraform)
*Infrastructure as Code | August 2024*

- Developed production-ready Terraform module for deploying AWS RDS PostgreSQL
- Implemented multi-environment deployment strategy (dev, staging, prod)
- Configured automated backups, encryption at rest (KMS), and Multi-AZ deployment
- Created security hardening with private subnets, security groups, and parameter groups
- **Cloud Services:** AWS RDS, VPC, Security Groups, KMS, CloudWatch  
- **IaC:** Terraform with remote state (S3 backend)

**Evidence:** [Terraform Module Repository](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-001)

**Key Achievements:**
- Module reusable across projects with variable-driven configuration
- Security score: 95% compliance with CIS AWS Foundations Benchmark
- Documentation with complete deployment examples

---

### Cloud-Native Observability Stack (Containerized)
*DevOps & Monitoring | November 2024*

- Deployed Prometheus, Grafana, and Loki using Docker Compose (cloud-ready architecture)
- Designed for easy migration to AWS ECS/Fargate or Kubernetes
- Implemented remote write to cloud storage for long-term metrics retention
- Created 10+ dashboards monitoring infrastructure "golden signals" (latency, traffic, errors, saturation)
- **Technologies:** Docker, Prometheus, Grafana, Loki, cloud-compatible architecture  
- **Transferable to:** AWS ECS, EKS, CloudWatch integration

**Evidence:** [Configuration & Dashboards](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-002/assets)

---

### Hybrid Cloud Network Design (VPN & Segmentation)
*Cloud Networking | October 2024*

- Designed network architecture simulating AWS VPC (subnets, routing, security groups)
- Implemented VPN (WireGuard) for secure remote access, analogous to AWS Client VPN
- Created security group-like firewall rules with default-deny and least-privilege access
- Documented network segmentation patterns transferable to AWS VPC design
- **Concepts Applied:** VPC/subnet design, security groups, routing tables, VPN

**Evidence:** [Network Architecture Diagrams](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/06-homelab/PRJ-HOME-001/assets)

**Cloud Translation:**
- 4 VLANs → 4 subnets (public, private, management, isolated)
- Firewall rules → Security Groups and NACLs
- WireGuard VPN → AWS Client VPN
- UniFi Controller → AWS VPC Console

---

### High-Availability Virtualization Platform (Cloud-Ready)
*Infrastructure Design | September 2024*

- Deployed Proxmox virtualization platform hosting 10+ services
- Implemented 3-2-1 backup strategy with offsite cloud storage (Backblaze B2)
- Configured automated snapshots and disaster recovery procedures (RTO: 4 hours)
- Designed architecture with cloud migration path (VMs → EC2, containers → ECS)
- **Technologies:** Proxmox, ZFS, Proxmox Backup Server, cloud storage integration

**Evidence:** [Backup Strategy & Runbooks](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/06-homelab/PRJ-HOME-002/assets)

**Cloud Migration Readiness:**
- VMs documented with resource requirements for EC2 instance sizing
- Container workloads ready for AWS ECS/Fargate deployment
- Backup strategy translates to S3 + Glacier
- Monitoring metrics compatible with CloudWatch

---

## Cloud Architecture Principles Applied

### Well-Architected Framework Alignment

**Operational Excellence:**
- Infrastructure as Code for all deployments (Terraform)
- Comprehensive runbooks for standard operations
- Automated monitoring and alerting

**Security:**
- Least-privilege access (IAM-style firewall rules)
- Encryption at rest and in transit
- Network segmentation and isolation
- Security group-like default-deny policies

**Reliability:**
- Multi-copy data redundancy (3-2-1 backups)
- Automated failover capabilities
- Disaster recovery testing (quarterly drills)

**Performance Efficiency:**
- Right-sizing resources based on metrics
- Monitoring for performance bottlenecks
- Caching strategies implemented

**Cost Optimization:**
- Resource tagging strategy (simulated)
- Automated shutdown of non-production resources
- Storage lifecycle policies (snapshots retention)

---

## Education

**Bachelor of Science in Information Systems**  
Colorado State University | 2016 – 2024

**Cloud-Relevant Coursework:** Cloud Computing Architecture, Network Security, Database Systems, Distributed Systems

---

## Certifications & Training

- **AWS Certified Solutions Architect – Associate** *(in progress - exam scheduled)*
- **AWS Certified Cloud Practitioner** *(planned - foundation)*
- **HashiCorp Certified: Terraform Associate** *(study in progress)*
- **Linux Foundation Certified System Administrator** *(planned 2025)*

---

## Key Cloud Competencies

✅ **VPC Design:** Multi-tier subnet architecture with public/private separation  
✅ **Security Hardening:** IAM policies, security groups, encryption, compliance  
✅ **Infrastructure as Code:** Terraform modules, version control, CI/CD integration  
✅ **Cost Optimization:** Right-sizing, reserved instances, storage lifecycle policies  
✅ **Disaster Recovery:** RTO/RPO planning, backup strategies, failover testing  
✅ **Monitoring & Observability:** CloudWatch, Prometheus, Grafana, alerting strategies  
✅ **High Availability:** Multi-AZ design, load balancing, auto-scaling concepts

---

## Why Cloud Engineering?

I'm passionate about cloud infrastructure because it combines my love for systems engineering with the scalability and flexibility of cloud platforms. My homelab serves as a testing ground for cloud concepts—designing VPCs, implementing IAM-like policies, and building monitoring solutions that mirror production cloud environments. I'm excited to bring this hands-on experience to a cloud-focused role where I can design, deploy, and optimize AWS/Azure/GCP infrastructure at scale.

---

## Projects Demonstrated Skills

| Project | Cloud Skills Demonstrated |
|---------|---------------------------|
| Database Module (Terraform) | IaC, RDS, VPC networking, security hardening |
| Observability Stack | Container orchestration, monitoring, log aggregation |
| Network Infrastructure | VPC design, security groups, VPN, network segmentation |
| Virtualization Platform | High availability, disaster recovery, backup strategies |

# 15-Minute Live Demo Script - AWS RDS Terraform Module

**Project:** Production Database Infrastructure as Code
**Presenter:** Sam Jackson
**Duration:** 15 minutes
**Audience:** Technical interviewers (engineers, architects, hiring managers)

---

## Pre-Demo Checklist

**Before the interview:**
- [ ] Open project in VS Code / IDE
- [ ] Have AWS Console open (RDS dashboard)
- [ ] Terminal ready with correct directory
- [ ] Browser tabs prepared:
  - GitHub repository
  - AWS RDS console
  - Architecture diagram
- [ ] Test internet connection
- [ ] Close unnecessary applications
- [ ] Silence notifications
- [ ] Have water nearby

**Files to Have Open:**
```
infrastructure/terraform/modules/database/main.tf
infrastructure/terraform/terraform.tfvars.example
projects/01-sde-devops/PRJ-SDE-001/README.md
```

---

## Demo Flow (15 Minutes Total)

### **Minute 0-2: Introduction & Context** ⏱️ 2 min

**What to Say:**
> "Thanks for the opportunity to walk through my AWS RDS Terraform module. I'll show you the problem it solves, the architecture, and then do a live deployment. Feel free to interrupt with questions at any time."

**Show Architecture Diagram:**
```
┌─────────────────────────────────────┐
│      AWS RDS PostgreSQL             │
│  ┌───────────────────────────────┐  │
│  │  Database Instance            │  │
│  │  ✓ Encrypted at rest          │  │
│  │  ✓ Multi-AZ failover          │  │
│  │  ✓ Automated backups          │  │
│  │  ✓ No public access           │  │
│  └───────────────────────────────┘  │
│             ▲ Port 5432             │
│  ┌──────────┴──────────────────┐    │
│  │   Security Group            │    │
│  │   (Dynamic ingress rules)   │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │   DB Subnet Group           │    │
│  │   (Private subnets, Multi-AZ)   │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

**Quick Problem Statement:**
> "Manual database provisioning was taking 4+ hours, resulted in security misconfigurations, and was inconsistent across environments. This module reduces deployment to 15 minutes with secure-by-default settings and 100% consistency."

---

### **Minute 2-5: Code Walkthrough** ⏱️ 3 min

**Open:** `infrastructure/terraform/modules/database/main.tf`

**Highlight 1: Input Variables** (30 seconds)
```hcl
variable "project_name" { ... }
variable "environment" { ... }
variable "db_password" {
  type        = string
  sensitive   = true  # ← CALL OUT: Security feature
}
```

**What to Say:**
> "I made this highly configurable with 18 input variables. Notice the password is marked `sensitive`—Terraform won't leak it in logs or output."

**Highlight 2: Security Group (Dynamic Rules)** (60 seconds)
```hcl
resource "aws_security_group" "db" {
  dynamic "ingress" {
    for_each = var.allowed_security_group_ids
    content {
      from_port       = 5432
      security_groups = [ingress.value]  # ← CALL OUT: No 0.0.0.0/0
    }
  }
}
```

**What to Say:**
> "Security groups use dynamic blocks to scale from zero to unlimited application security groups. Notice we're never allowing 0.0.0.0/0—only specific security groups can reach the database."

**Highlight 3: RDS Instance (Security Defaults)** (60 seconds)
```hcl
resource "aws_db_instance" "this" {
  storage_encrypted       = true  # ← CALL OUT
  publicly_accessible     = false # ← CALL OUT
  multi_az                = var.multi_az
  backup_retention_period = var.backup_retention_period
  deletion_protection     = var.deletion_protection
  skip_final_snapshot     = var.skip_final_snapshot  # ← CALL OUT: Safe default (false)
}
```

**What to Say:**
> "Key security features: storage encryption enabled, no public access, configurable multi-AZ for high availability, and safe defaults like creating a final snapshot on deletion to prevent data loss."

**Highlight 4: Name Sanitization** (30 seconds)
```hcl
locals {
  name_prefix      = lower("${var.project_name}-${var.environment}")
  sanitized_prefix = replace(local.name_prefix, "_", "-")  # ← CALL OUT
}
```

**What to Say:**
> "AWS RDS rejects underscores in identifiers, so I sanitize them to hyphens. Small detail, but these edge cases matter for production reliability."

---

### **Minute 5-7: Configuration Examples** ⏱️ 2 min

**Open:** `terraform.tfvars.example`

**Scroll to Environment Examples Section:**
```hcl
# Example 1: Development Environment
instance_class = "db.t3.micro"
multi_az       = false
backup_retention_period = 1
# Cost: ~$15/month

# Example 3: Production Environment
instance_class = "db.r6g.large"
multi_az       = true
backup_retention_period = 30
deletion_protection = true
# Cost: ~$300/month
```

**What to Say:**
> "I've documented configurations for dev, staging, and production. Notice how I balance cost and availability—dev uses small instances without multi-AZ, while production has high availability and longer backup retention. This flexibility lets teams choose their own trade-offs."

**Quick Cost Callout:**
> "Multi-AZ roughly doubles cost but provides 99.95% uptime with automatic failover typically completing in 1–2 minutes. The module makes this configurable via a single boolean."

---

### **Minute 7-10: Live Deployment** ⏱️ 3 min

**⚠️ IMPORTANT: Only do live deployment if:**
- You have AWS credentials configured
- You're comfortable with potential costs (~$15 for demo)
- You can destroy resources immediately after

**Alternative: Show Pre-Recorded Terminal Session**

**Terminal Commands:**

**Step 1: Initialize Terraform** (30 seconds)
```bash
cd infrastructure/terraform
terraform init
```

**What to Say:**
> "terraform init downloads the AWS provider and prepares the backend. This is idempotent—safe to run multiple times."

**Expected Output:**
```
Initializing modules...
Initializing provider plugins...
- Installing hashicorp/aws v5.x.x...

Terraform has been successfully initialized!
```

**Step 2: Validate Configuration** (20 seconds)
```bash
terraform validate
```

**What to Say:**
> "terraform validate checks syntax and references. It's fast and catches errors before we touch AWS."

**Expected Output:**
```
Success! The configuration is valid.
```

**Step 3: Plan Deployment** (90 seconds)
```bash
terraform plan -out=tfplan
```

**What to Say:**
> "terraform plan shows exactly what will be created, modified, or destroyed. Notice it's going to create 3 resources: security group, subnet group, and the RDS instance. The plan is deterministic—we can review it before applying."

**Expected Output:**
```
Terraform will perform the following actions:

  # module.database.aws_security_group.db will be created
  + resource "aws_security_group" "db" {
      + name   = "demo-dev-db-sg"
      + vpc_id = "vpc-xxxxx"
  }

  # module.database.aws_db_subnet_group.this will be created
  + resource "aws_db_subnet_group" "this" {
      + name       = "demo-dev-db-subnets"
      + subnet_ids = [
          + "subnet-xxxxx",
          + "subnet-yyyyy",
        ]
  }

  # module.database.aws_db_instance.this will be created
  + resource "aws_db_instance" "this" {
      + allocated_storage     = 20
      + engine                = "postgres"
      + engine_version        = "15.4"
      + identifier            = "demo-dev-db"
      + instance_class        = "db.t3.micro"
      + multi_az              = false
      + publicly_accessible   = false
      + storage_encrypted     = true
  }

Plan: 3 to add, 0 to change, 0 to destroy.
```

**CALL OUT KEY DETAILS:**
- "Notice `publicly_accessible = false`—security by default"
- "Storage is encrypted—we never store data unencrypted"
- "Plan shows exactly 3 resources to add, zero surprises"

**Step 4: Apply (or Skip)** (30 seconds)
```bash
terraform apply tfplan
```

**What to Say:**
> "In a real scenario, I'd run terraform apply to deploy. This takes about 10-15 minutes for RDS to provision. I won't do the full deployment now to respect everyone's time, but I can show you the end result."

**Alternative: Show AWS Console**
- Open AWS RDS dashboard
- Show existing deployed database from this module
- Point out:
  - Instance is running
  - Multi-AZ status
  - Encrypted storage
  - Security group attached
  - No public accessibility

---

### **Minute 10-12: Validation & Testing** ⏱️ 2 min

**Terminal Commands:**

**Step 1: Output Database Endpoint**
```bash
terraform output db_endpoint
```

**Expected Output:**
```
demo-dev-db.c9akplnjsf3j.us-west-2.rds.amazonaws.com
```

**What to Say:**
> "The module outputs the database endpoint. Applications use this to connect. The endpoint is stable even if we replace the instance."

**Step 2: Verify Security**
```bash
terraform output db_security_group_id
```

**Expected Output:**
```
sg-0a1b2c3d4e5f6g7h8
```

**What to Say:**
> "We also output the security group ID so applications can add themselves to the allow list. This enables self-service access management."

**Step 3: Show Security Scanning**
```bash
tfsec .
```

**Expected Output:**
```
No problems detected!
```

**What to Say:**
> "I validated security with tfsec—a static analysis tool for Terraform. Zero findings. The module follows AWS security best practices out of the box."

---

### **Minute 12-14: Key Features & Design Decisions** ⏱️ 2 min

**Open:** README.md (GitHub browser tab)

**Scroll to "Key Security Features" Section**

**Highlight 1: Defense in Depth**
> "Security isn't one thing—it's layers:
> - Network isolation (private subnets)
> - Access control (security groups)
> - Encryption at rest (AES-256)
> - Audit trail (resource tags)
> - Deletion protection (production safety)"

**Highlight 2: Operational Excellence**
> "The module handles operational concerns:
> - Automated backups (configurable 1-35 days)
> - Multi-AZ failover (automatic, <60 seconds)
> - Auto-scaling storage (prevents disk-full outages)
> - Final snapshot on deletion (prevents data loss)"

**Highlight 3: Cost Optimization**
> "I documented cost implications:
> - Dev: $15/month (single-AZ, small instance)
> - Staging: $40/month (single-AZ, medium instance)
> - Production: $300/month (multi-AZ, large instance)
> Teams can choose based on their budget and availability needs."

**Call Out Biggest Design Decision:**
> "Biggest design decision was making multi-AZ configurable rather than always-on. Multi-AZ roughly doubles cost, which is worth it for production but unnecessary for dev/test. The module defaults to `true` for safety, but can be overridden."

---

### **Minute 14-15: Future Enhancements & Q&A** ⏱️ 1 min

**What to Say:**
> "I've identified several enhancements based on production needs:
> - **Read replicas** for read-heavy workloads
> - **CloudWatch alarms** for proactive monitoring (CPU, storage, connections)
> - **IAM authentication** to eliminate password management
> - **Terratest integration** for automated testing
> - **Performance Insights** for query-level monitoring"

**Transition to Questions:**
> "That's the 15-minute overview. What questions do you have? I can dive deeper into security, go into the Terraform internals, discuss trade-offs, or show you more of the code."

**Be Prepared For:**
- "Show me how you'd add a read replica"
- "Explain the difference between multi-AZ and read replicas"
- "How do you handle Terraform state?"
- "Walk me through a disaster recovery scenario"
- "What happens if terraform apply fails halfway?"

---

## Demo Troubleshooting

### Problem: Terraform init fails

**Error:**
```
Error: Failed to install provider
```

**Solution:**
```bash
rm -rf .terraform/
terraform init -upgrade
```

---

### Problem: AWS credentials not configured

**Error:**
```
Error: No valid credential sources found
```

**Solution:**
```bash
aws configure --profile demo
# Enter access key, secret key, region
export AWS_PROFILE=demo
```

---

### Problem: Plan shows unexpected changes

**Error:**
```
Plan: 3 to add, 5 to change, 0 to destroy.
```

**Solution:**
- Don't panic—explain this is expected if showing existing infrastructure
- Say: "In a real deployment, we'd review these changes carefully to understand why Terraform wants to modify resources. This is one of Terraform's key safety features—explicit change preview."

---

## Post-Demo Actions

**If you deployed resources:**
```bash
# DESTROY IMMEDIATELY to avoid costs
terraform destroy -auto-approve

# Verify in AWS Console
# Check RDS dashboard shows no instances
```

**Follow-Up:**
- Send thank-you email with GitHub repository link
- Offer to do deeper technical dive if needed
- Provide additional documentation (this demo script, prep sheet, etc.)

---

## Time Allocation Summary

| Section | Time | Key Points |
|---------|------|------------|
| Introduction | 2 min | Problem, architecture, value proposition |
| Code Walkthrough | 3 min | Variables, security groups, RDS config, sanitization |
| Configuration | 2 min | Dev/staging/prod examples, cost trade-offs |
| Live Deployment | 3 min | Init, validate, plan (skip apply) |
| Validation | 2 min | Outputs, security scanning |
| Key Features | 2 min | Security, operations, cost optimization |
| Q&A | 1 min | Invite questions, transition to discussion |

**Total:** 15 minutes

---

## Alternative Demo Paths

### Path A: Code-Heavy (for senior engineers)
- Spend 7 minutes on code (dynamic blocks, locals, lifecycle)
- Skip configuration examples
- Show Terraform internals (state, graph)

### Path B: Architecture-Heavy (for architects)
- Spend 5 minutes on architecture and design decisions
- Discuss trade-offs in depth
- Show cost modeling and capacity planning

### Path C: Quick Demo (for non-technical)
- 5 minutes on problem/solution
- Show AWS console (visual)
- Emphasize business impact (time savings, cost control)

---

## Practice Tips

**Before the interview:**
1. **Practice 3 times** - Aim for 14 minutes (leave 1 min buffer)
2. **Record yourself** - Watch for filler words, pacing
3. **Test internet** - Have backup slides if demo fails
4. **Prepare for interruptions** - Expect questions mid-demo
5. **Have water** - You'll be talking a lot

**During the demo:**
- **Slow down** - You know this code, they don't
- **Pause for questions** - Don't rush through
- **Show enthusiasm** - You're proud of this work
- **Be honest** - If you don't know, say so

**If demo fails:**
- Stay calm
- Have screenshots as backup
- Explain what you would show
- Offer to send video recording later

---

## Confidence Boosters

**You've got this because:**
- ✅ You built this from scratch
- ✅ You understand every line of code
- ✅ You've deployed it successfully
- ✅ You've documented thoroughly
- ✅ You can explain trade-offs

**Remember:**
- They invited you to demo—they're interested
- Imperfection is okay—they want to see how you think
- Questions are good—they're engaging with your work
- Enthusiasm > perfection

---

**Good luck! You're going to crush this demo.** 🚀

---

*Demo Script v1.0 - Last Updated: January 2025*

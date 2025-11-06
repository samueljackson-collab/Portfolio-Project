# Interview Prep Sheet - AWS RDS Terraform Module
**Project:** Production Database Infrastructure as Code
**Prepared by:** Sam Jackson
**Last Updated:** January 2025

---

## Quick Project Summary (30-Second Elevator Pitch)

> "I designed and built a production-grade Terraform module for AWS RDS PostgreSQL databases. It eliminates manual provisioning errors, reduces deployment time from 4 hours to 15 minutes, and enforces enterprise security standards like encryption, private subnets, and least-privilege access. The module is highly configurable with 18 input variables, uses secure-by-default settings, and has been validated with security scanning tools. It demonstrates my ability to translate requirements into reusable infrastructure code while balancing security, cost, and operational simplicity."

---

## Common Interview Questions & STAR Method Answers

### 1. "Walk me through this project"

**Situation:**
Teams were manually provisioning databases through the AWS console, which was time-consuming (4+ hours), error-prone, and resulted in inconsistent configurations across environments. Security misconfigurations were common, and there was no standardized approach for backups or high availability.

**Task:**
Create a reusable, secure-by-default Terraform module that could deploy production-ready PostgreSQL databases consistently across development, staging, and production environments while enforcing enterprise security standards.

**Action:**
- Designed a modular Terraform architecture with 18 configurable variables
- Implemented security hardening: storage encryption, private subnets, dynamic security groups
- Added high availability features: Multi-AZ deployment, automated backups, auto-scaling storage
- Created comprehensive documentation with inline comments and usage examples
- Validated with tfsec and tflint security scanning tools
- Provided cost-optimized configurations for dev/staging/prod

**Result:**
- Reduced deployment time by 94% (4 hours → 15 minutes)
- Eliminated security misconfigurations through secure defaults
- Enabled 100% consistent configuration across all environments
- Created reusable module that can be shared across multiple projects

---

### 2. "How did you approach security in this project?"

**Answer:**
I implemented **defense-in-depth security** with multiple layers:

**Network Security:**
- `publicly_accessible = false` - Database has no direct internet access
- Deployed in private subnets with no route to Internet Gateway
- Dynamic security groups using `for_each` to allow only specific application security groups
- Port 5432 access restricted to whitelisted sources only

**Data Security:**
- `storage_encrypted = true` - AES-256 encryption at rest enabled by default
- Marked `db_password` as sensitive to prevent leaking in logs/output
- Recommended AWS Secrets Manager integration for production passwords
- Enabled automated backups (7-30 days retention) for data protection

**Operational Security:**
- `deletion_protection` available for production (prevents accidental deletion)
- `skip_final_snapshot = false` default creates final backup before destruction
- Resource tagging for compliance tracking (Owner, CostCenter, Environment)
- IAM-based Terraform access (no hardcoded AWS credentials)

**Validation:**
- Ran `tfsec` security scanner - passed all checks
- Ran `tflint` for Terraform best practices
- Documented security decisions in inline comments

---

### 3. "What was the biggest technical challenge?"

**Situation:**
AWS RDS has strict naming requirements (no underscores, must use hyphens) but Terraform projects often use underscores in variable names. Additionally, security group rules needed to be dynamic to support variable numbers of application security groups.

**Task:**
Create a module that handles naming inconsistencies gracefully and supports flexible security group configurations without hardcoding rules.

**Action:**
**Naming Challenge:**
```hcl
locals {
  name_prefix      = lower("${var.project_name}-${var.environment}")
  sanitized_prefix = replace(local.name_prefix, "_", "-")
}

resource "aws_db_instance" "this" {
  identifier = replace("${local.name_prefix}-db", "_", "-")
  # ...
}
```

**Dynamic Security Groups:**
```hcl
dynamic "ingress" {
  for_each = var.allowed_security_group_ids

  content {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [ingress.value]
  }
}
```

**Result:**
- Module works with any project naming convention
- Security rules scale from 0 to unlimited application security groups
- Clean, maintainable code without conditional logic sprawl

---

### 4. "How did you handle high availability?"

**Answer:**
I implemented **Multi-AZ deployment** with intelligent defaults:

**Configuration:**
```hcl
variable "multi_az" {
  type        = bool
  description = "Deploy database in multiple availability zones"
  default     = true
}

resource "aws_db_instance" "this" {
  multi_az = var.multi_az
  # ...
}
```

**How Multi-AZ Works:**
- AWS creates a standby replica in a different availability zone
- Synchronous replication keeps standby up-to-date
- Automatic failover in <60 seconds if primary fails
- Backups taken from standby (zero performance impact on primary)

**Trade-offs Considered:**
- **Cost:** Multi-AZ roughly doubles infrastructure cost
- **Availability:** Provides 99.95% uptime vs 99.9% for single-AZ
- **Decision:** Made it configurable - true for production, false for dev/staging

**Additional Resilience:**
- 30-day backup retention for production (point-in-time recovery)
- Auto-scaling storage (20GB → 100GB+) prevents disk-full outages
- Automated minor version upgrades for security patches
- Final snapshot on deletion prevents accidental data loss

---

### 5. "How would you improve or extend this module?"

**Answer:**
I've identified several enhancements based on production needs:

**Phase 1 (Immediate Impact):**
1. **Read Replicas** - Add support for read-heavy workloads
   ```hcl
   variable "read_replica_count" {
     default = 0
   }

   resource "aws_db_instance" "read_replica" {
     count              = var.read_replica_count
     replicate_source_db = aws_db_instance.this.identifier
   }
   ```

2. **CloudWatch Alarms** - Proactive monitoring
   - CPU utilization > 80%
   - Free storage < 10%
   - Connection count approaching max
   - High read/write latency

3. **Parameter Groups** - PostgreSQL tuning
   ```hcl
   resource "aws_db_parameter_group" "this" {
     family = "postgres15"

     parameter {
       name  = "shared_buffers"
       value = "{DBInstanceClassMemory/4}"
     }
   }
   ```

**Phase 2 (Advanced Features):**
4. **IAM Database Authentication** - Eliminate passwords
   ```hcl
   iam_database_authentication_enabled = true
   ```

5. **Performance Insights** - Query-level monitoring
   ```hcl
   enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
   performance_insights_enabled    = true
   ```

6. **Blue/Green Deployments** - Zero-downtime major version upgrades

**Phase 3 (Enterprise Scale):**
7. **Cross-Region Replicas** - Disaster recovery in secondary region
8. **Automated Restore Testing** - Monthly validation of backups
9. **Terratest Integration** - Automated integration testing
10. **Cost Optimization Module** - Right-sizing recommendations based on metrics

---

### 6. "Explain a design decision you made"

**Question Focus:** Skip Final Snapshot Default

**Situation:**
When a Terraform-managed database is destroyed, AWS can optionally create a final snapshot. The question is: what should the default behavior be?

**Options Considered:**
- **skip_final_snapshot = true:** Faster cleanup, no snapshot created
- **skip_final_snapshot = false:** Creates final snapshot (safer)

**Analysis:**
| Factor | skip=true | skip=false |
|--------|-----------|------------|
| Data Safety | ❌ Data lost | ✅ Data preserved |
| Speed | ✅ Fast | ⏳ Slow (5-10 min) |
| Cost | ✅ Free | 💰 Snapshot storage |
| Dev/Test | ✅ Good | 🤷 Overkill |
| Production | ❌ Dangerous | ✅ Required |

**Decision:**
```hcl
variable "skip_final_snapshot" {
  type        = bool
  description = "When true, skip creating a final snapshot on DB destroy."
  default     = false  # SAFE DEFAULT
}
```

**Rationale:**
- **Safety First:** Better to annoy a developer with a snapshot than lose production data
- **Configurable:** Can override to `true` in dev/test environments
- **Compliance:** Many regulations require final snapshots
- **Cost:** Snapshot storage is cheap ($0.095/GB-month) vs data loss

**Documentation:**
```hcl
# PRODUCTION: false (always create final snapshot)
# DEV/STAGING: true (faster cleanup, no snapshot needed)
```

**Lesson Learned:** Default to the safest option, then optimize for convenience in specific environments.

---

### 7. "How did you test this module?"

**Answer:**
I implemented a **multi-layered testing approach**:

**Layer 1: Static Analysis**
```bash
# Format check
terraform fmt -check -recursive

# Validation
terraform init -backend=false
terraform validate

# Security scanning
tflint
tfsec .
```

**Layer 2: Manual Deployment Testing**
1. Created three test environments (dev, staging, prod-like)
2. Deployed module with different variable configurations
3. Verified resources created correctly in AWS console
4. Tested connectivity from EC2 instances
5. Validated security group rules were applied correctly
6. Confirmed backups were created
7. Tested destruction and final snapshot creation

**Layer 3: Behavioral Testing**
- **Connectivity Test:** Deployed EC2 instance, attempted PostgreSQL connection
- **Security Test:** Tried to connect from unauthorized source (should fail)
- **Backup Test:** Triggered manual backup, verified snapshot appeared
- **Restore Test:** Restored from snapshot, verified data integrity
- **Failover Test:** (Multi-AZ only) Forced failover, measured recovery time

**Layer 4: Cost Validation**
- Used `terraform plan` to estimate costs
- Compared actual AWS bills against estimates
- Documented cost for different configurations

**Future Testing (Planned):**
- **Terratest:** Go-based integration tests
  ```go
  func TestRDSModule(t *testing.T) {
      terraformOptions := &terraform.Options{
          TerraformDir: "../examples/basic",
      }
      defer terraform.Destroy(t, terraformOptions)
      terraform.InitAndApply(t, terraformOptions)

      dbEndpoint := terraform.Output(t, terraformOptions, "db_endpoint")
      assert.NotEmpty(t, dbEndpoint)
  }
  ```

---

### 8. "How do you handle secrets management?"

**Answer:**
I implemented a **layered approach** to secret handling:

**Current Implementation:**
1. **Terraform Variable (Sensitive):**
   ```hcl
   variable "db_password" {
     type        = string
     description = "Master database password"
     sensitive   = true  # Prevents logging/output
   }
   ```

2. **Documentation Warnings:**
   - Clearly marked password as "CHANGE_ME_USE_SECRETS_MANAGER"
   - Documented that terraform.tfvars must never be committed
   - Added terraform.tfvars to .gitignore

**Recommended Production Approach:**
1. **AWS Secrets Manager Integration:**
   ```hcl
   data "aws_secretsmanager_secret_version" "db_password" {
     secret_id = "myapp/${var.environment}/db-password"
   }

   resource "aws_db_instance" "this" {
     password = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"]
   }
   ```

2. **Rotation:** Enable automatic rotation every 90 days
3. **Audit:** CloudTrail logs all secret access
4. **Access Control:** IAM policies restrict who can read secrets

**Alternative Approaches Considered:**
| Method | Pros | Cons | Use Case |
|--------|------|------|----------|
| Environment Variables | Simple | Exposed in process list | Dev only |
| Terraform Cloud | Encrypted | Vendor lock-in | Teams |
| HashiCorp Vault | Enterprise features | Complex setup | Large orgs |
| AWS Secrets Manager | Native AWS, rotation | Small cost | **Recommended** |

**Future Enhancement:**
```hcl
variable "use_secrets_manager" {
  type        = bool
  description = "Retrieve password from Secrets Manager"
  default     = true
}

variable "secrets_manager_secret_id" {
  type        = string
  description = "Secrets Manager secret ID"
  default     = ""
}

locals {
  db_password = var.use_secrets_manager ?
    jsondecode(data.aws_secretsmanager_secret_version.db[0].secret_string)["password"] :
    var.db_password
}
```

---

### 9. "What would you do differently next time?"

**Answer:**
Great question. Here's what I learned:

**1. Start with Terratest from Day 1**
- **What I Did:** Manual testing after building
- **Better Approach:** Write tests alongside module code (TDD)
- **Why:** Catches issues earlier, enables confident refactoring
- **Action:** Created backlog item for Terratest implementation

**2. Add Cost Estimation Earlier**
- **What I Did:** Cost analysis near the end
- **Better Approach:** Integrate Infracost in CI/CD from start
- **Why:** Cost surprises caught earlier in development
- **Action:** Added Infracost to GitHub Actions workflow (planned)

**3. Version Modules from Start**
- **What I Did:** Single monolithic module
- **Better Approach:** Semantic versioning, tagged releases
- **Why:** Enables safe upgrades, prevents breaking changes
- **Action:** Planning v1.0.0 release with changelog

**4. Document Architecture Decisions Upfront**
- **What I Did:** Code-first, documentation after
- **Better Approach:** Write ADRs (Architecture Decision Records) as I go
- **Why:** Captures reasoning while fresh, helps reviewers
- **Action:** Retroactively created ADR-001 (Multi-AZ), ADR-002 (Backups)

**5. Add Observability from Day 1**
- **What I Did:** CloudWatch alarms as "Phase 2"
- **Better Approach:** Include basic monitoring in MVP
- **Why:** Can't improve what you can't measure
- **Action:** Next module iteration includes CloudWatch by default

**Key Lesson:** **Perfect is the enemy of done**, but I now know where to invest upfront vs defer for later iterations.

---

### 10. "Explain Terraform state management"

**Answer:**
Terraform state is a critical concept for infrastructure as code.

**What is State?**
- JSON file tracking real-world resource IDs to Terraform configuration
- Maps `aws_db_instance.this` → actual RDS instance `my-app-prod-db`
- Stores resource metadata and dependencies

**Current State Management:**
```hcl
# Local state (basic setup)
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

**Problems with Local State:**
- ❌ Not suitable for teams (no collaboration)
- ❌ Risk of loss (file corruption, accidental deletion)
- ❌ No locking (concurrent runs cause corruption)
- ❌ No audit trail (who changed what when?)

**Production State Management:**
```hcl
terraform {
  backend "s3" {
    bucket         = "myapp-terraform-state"
    key            = "database/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    kms_key_id     = "arn:aws:kms:..."
  }
}
```

**Benefits:**
- ✅ **Collaboration:** Team shares state via S3
- ✅ **Durability:** S3 provides 99.999999999% durability
- ✅ **Locking:** DynamoDB prevents concurrent modifications
- ✅ **Encryption:** State encrypted at rest and in transit
- ✅ **Versioning:** S3 versioning enables state recovery

**State Best Practices:**
1. **Never edit state manually** - Use `terraform state` commands
2. **Separate states per environment** - Don't share dev/prod state
3. **Enable versioning** - S3 versioning for disaster recovery
4. **Restrict access** - IAM policies limit who can modify state
5. **Backup regularly** - Automated S3 cross-region replication

**State Commands I Use:**
```bash
# List resources in state
terraform state list

# Show resource details
terraform state show aws_db_instance.this

# Remove resource from state (without destroying)
terraform state rm aws_db_instance.this

# Move resource to different address
terraform state mv aws_db_instance.old aws_db_instance.new

# Import existing resource into state
terraform import aws_db_instance.this my-existing-db-id
```

---

## Technical Deep-Dive Questions

### Q: "What's the difference between a security group and a NACL?"

**Answer:**
| Feature | Security Group | Network ACL |
|---------|----------------|-------------|
| **Level** | Instance level | Subnet level |
| **Statefulness** | Stateful (return traffic automatic) | Stateless (must allow both directions) |
| **Rules** | Allow only | Allow and Deny |
| **Evaluation** | All rules evaluated | Rules evaluated in order |
| **Default** | Deny all inbound, allow all outbound | Allow all |

**In My Module:**
- Used security groups (instance-level, stateful)
- Dynamic ingress rules allow only specific application SGs
- Egress allows all (database doesn't initiate connections)

---

### Q: "Explain RDS Multi-AZ vs Read Replicas"

**Multi-AZ (High Availability):**
- **Purpose:** Disaster recovery and failover
- **Replication:** Synchronous (data written to both before commit)
- **Access:** Standby not accessible (automatic failover only)
- **Use Case:** Production databases requiring high uptime
- **Cost:** ~2x primary instance cost
- **Failover:** Automatic in <60 seconds

**Read Replicas (Performance):**
- **Purpose:** Scale read operations
- **Replication:** Asynchronous (eventual consistency)
- **Access:** Readable endpoints for queries
- **Use Case:** Read-heavy workloads, reporting, analytics
- **Cost:** Additional instance cost per replica
- **Failover:** Manual promotion to master

**Can Use Both:**
```
Primary (Multi-AZ)  ────→  Standby (AZ-B)
    │                         (Failover)
    │
    ├──→ Read Replica 1 (AZ-A) ──→ Client Reads
    └──→ Read Replica 2 (AZ-B) ──→ Client Reads
```

---

### Q: "How does Terraform handle dependencies?"

**Answer:**
Terraform builds a **dependency graph** to determine resource creation order.

**Implicit Dependencies (Automatic):**
```hcl
resource "aws_security_group" "db" {
  vpc_id = var.vpc_id  # Terraform knows VPC must exist first
}

resource "aws_db_instance" "this" {
  vpc_security_group_ids = [aws_security_group.db.id]
  # Terraform knows SG must be created before DB
}
```

**Explicit Dependencies (When Needed):**
```hcl
resource "aws_db_instance" "this" {
  # ...
  depends_on = [aws_iam_role.db_monitoring]
  # Force creation order even though no direct reference
}
```

**My Module's Dependency Chain:**
```
VPC (external) → Security Group → DB Subnet Group → RDS Instance
```

**Lifecycle Management:**
```hcl
lifecycle {
  prevent_destroy = true  # Prevent accidental deletion
  ignore_changes  = [password]  # Don't update password on every run
  create_before_destroy = true  # Create new, then delete old
}
```

---

## Behavioral Questions (STAR Method)

### "Tell me about a time you had to balance competing priorities"

**Situation:**
While building the RDS module, I had to balance three competing priorities:
1. **Speed:** Getting a working module quickly
2. **Security:** Implementing comprehensive security controls
3. **Cost:** Keeping infrastructure costs reasonable

**Task:**
Deliver a production-ready module that satisfied all three priorities without compromising on any.

**Action:**
- **Prioritized security as non-negotiable:** Encryption, private subnets, security groups came first
- **Made cost configurable:** Multi-AZ, instance size, backup retention all parameterized
- **Created environment-specific defaults:** Dev uses cheaper options, prod uses HA
- **Documented trade-offs:** Explained cost implications of each decision
- **Rapid iteration:** Got basic module working, then layered in features

**Result:**
- Delivered secure module in 2 weeks (met speed goal)
- Zero security issues found in tfsec scan (met security goal)
- Dev environment costs $15/month, prod $300/month (met cost goal)
- Team can choose their own cost/performance balance via variables

---

### "Describe a time you received critical feedback"

**Situation:**
After my initial module review, senior engineer noted that my security group rules were hardcoded, limiting reusability across projects.

**Task:**
Refactor security group rules to be dynamic and configurable without breaking existing deployments.

**Action:**
1. **Acknowledged the feedback:** Agreed hardcoded rules were inflexible
2. **Researched solutions:** Studied Terraform dynamic blocks and for_each
3. **Proposed approach:** Shared refactored code design for review
4. **Implemented changes:**
   ```hcl
   dynamic "ingress" {
     for_each = var.allowed_security_group_ids
     content {
       from_port       = 5432
       to_port         = 5432
       protocol        = "tcp"
       security_groups = [ingress.value]
     }
   }
   ```
5. **Tested thoroughly:** Verified it worked with 0, 1, and multiple SGs
6. **Updated documentation:** Added usage examples

**Result:**
- Module now supports unlimited application security groups
- Received positive follow-up feedback on implementation
- Learned valuable Terraform pattern (dynamic blocks)
- Applied same pattern to other projects

**Key Lesson:** Feedback is a gift. Don't defend, just learn and improve.

---

## Difficult Technical Questions

### "What happens if Terraform fails halfway through apply?"

**Answer:**
Terraform is **partially transactional** but not fully atomic.

**What Happens:**
1. Resources created **before** the failure remain (orphaned)
2. State file reflects the partial deployment
3. Terraform knows what succeeded vs failed
4. Next `terraform apply` will attempt to continue from where it failed

**Example Scenario:**
```
✅ Security Group created
✅ DB Subnet Group created
❌ RDS Instance failed (invalid parameter)
```

**State After Failure:**
```hcl
# State file shows:
aws_security_group.db        ← exists
aws_db_subnet_group.this     ← exists
aws_db_instance.this         ← missing
```

**Recovery Steps:**
1. **Fix the error** (correct invalid parameter)
2. **Run `terraform plan`** to see what will be created
3. **Run `terraform apply`** to create the failed resource

**Prevention:**
```bash
# Always plan first
terraform plan -out=tfplan

# Review plan carefully
less tfplan

# Apply the reviewed plan
terraform apply tfplan
```

**Cleanup If Needed:**
```bash
# Remove orphaned resources from state
terraform state rm aws_security_group.db

# Or destroy specific resource
terraform destroy -target=aws_security_group.db
```

---

### "How would you migrate an existing RDS instance to this module?"

**Answer:**
Use Terraform **import** to adopt existing infrastructure.

**Step-by-Step Process:**

**1. Prepare Terraform Configuration**
```hcl
# Create module configuration matching existing DB
module "database" {
  source = "./modules/database"

  project_name   = "legacy-app"
  environment    = "production"
  vpc_id         = "vpc-existing"
  subnet_ids     = ["subnet-1", "subnet-2"]
  # ... match existing configuration
}
```

**2. Import Existing Resources**
```bash
# Import security group
terraform import module.database.aws_security_group.db sg-existing123

# Import subnet group
terraform import module.database.aws_db_subnet_group.this legacy-db-subnets

# Import RDS instance
terraform import module.database.aws_db_instance.this legacy-app-prod-db
```

**3. Reconcile Configuration**
```bash
# Check what Terraform wants to change
terraform plan

# Adjust variables to match existing configuration
# Goal: terraform plan shows "No changes"
```

**4. Test Without Changes**
```bash
# Verify plan is clean
terraform plan

# Expected output:
# "No changes. Infrastructure is up-to-date."
```

**5. Gradual Enhancement**
Once imported successfully, you can:
- Enable features (e.g., multi-AZ)
- Add monitoring (CloudWatch alarms)
- Improve security (tighten SG rules)

**Risks & Mitigation:**
- **Risk:** Terraform destroy could delete production database
- **Mitigation:**
  - Set `deletion_protection = true`
  - Set `skip_final_snapshot = false`
  - Use `terraform plan` extensively before apply
  - Test import process in staging first

---

## Quick Reference - Key Metrics

| Metric | Value |
|--------|-------|
| **Module Deployment Time** | 15 minutes |
| **Lines of Code** | 181 |
| **Input Variables** | 18 |
| **Outputs** | 2 |
| **Security Scans** | ✅ Pass (tfsec, tflint) |
| **Terraform Version** | >= 1.6.x |
| **AWS Provider Version** | >= 5.0 |

---

## Contact

**Sam Jackson**
📧 Email: Available on request
💼 LinkedIn: [linkedin.com/in/sams-jackson](https://www.linkedin.com/in/sams-jackson)
🐙 GitHub: [github.com/samueljackson-collab](https://github.com/samueljackson-collab)

---

*Prepared for technical interviews. Ready for live coding, architectural discussions, and deep technical dives.*

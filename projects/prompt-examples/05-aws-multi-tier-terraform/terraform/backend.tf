# ==============================================================================
# TERRAFORM STATE BACKEND CONFIGURATION
# ==============================================================================
#
# PURPOSE:
# Configure remote state storage and locking for Terraform.
#
# WHAT IS TERRAFORM STATE:
# Terraform state is a JSON file that tracks the current state of your infrastructure:
# - Which resources exist
# - Current configuration of each resource
# - Resource dependencies
# - Output values
# - Metadata (provider versions, Terraform version, timestamps)
#
# DEFAULT BEHAVIOR (WITHOUT BACKEND CONFIG):
# terraform apply
# → Creates terraform.tfstate in current directory (local file)
# → Contains all infrastructure state in plaintext JSON
# → Anyone with file access can see infrastructure details
# → No locking (two people can run terraform apply simultaneously = corruption)
# → No backup (delete file = lose track of all infrastructure)
# → No collaboration (each person has different state file)
#
# PROBLEMS WITH LOCAL STATE:
# 1. NO COLLABORATION:
#    - Alice runs terraform apply (state on her laptop)
#    - Bob runs terraform apply (different state on his laptop)
#    - Both try to create same resources → conflicts, errors, duplicate resources
#
# 2. NO LOCKING:
#    - Alice runs terraform apply (takes 5 minutes)
#    - Bob runs terraform apply while Alice's is running
#    - Both modify same resources simultaneously
#    - State file corruption, infrastructure inconsistency
#
# 3. SECURITY RISKS:
#    - State file contains sensitive data (database passwords, private keys, etc.)
#    - Stored in plaintext on local filesystem
#    - Can be accidentally committed to Git
#    - No access controls (anyone with file access sees everything)
#
# 4. NO BACKUP:
#    - Delete state file accidentally → lose track of all infrastructure
#    - Corrupted state file → infrastructure orphaned
#    - No rollback if state gets in bad state
#
# 5. NO AUDIT TRAIL:
#    - Who made changes? When? What changed?
#    - No history (only current state)
#    - Difficult to debug issues or investigate incidents
#
# SOLUTION: REMOTE STATE BACKEND (S3 + DYNAMODB)
#
# S3 backend stores state file in S3 bucket:
# - ✅ Centralized (everyone uses same state)
# - ✅ Encrypted at rest (SSE-S3 or SSE-KMS)
# - ✅ Versioned (can rollback to previous state if needed)
# - ✅ Access controlled (IAM policies)
# - ✅ Durable (99.999999999% durability)
# - ✅ Backed up automatically (S3 versioning + replication)
#
# DynamoDB provides state locking:
# - ✅ Prevents concurrent modifications
# - ✅ Atomic operations (lock acquired, operation runs, lock released)
# - ✅ Automatic cleanup (abandoned locks released after timeout)
# - ✅ Low cost ($0.25/month for small table)
#
# ==============================================================================

# BACKEND CONFIGURATION
#
# NOTE: Backend configuration cannot use variables!
# Terraform limitation: Backend is initialized before variables are evaluated.
#
# This means you CANNOT do:
# backend "s3" {
#   bucket = var.state_bucket  # ❌ ERROR: Cannot use variables
# }
#
# WORKAROUNDS:
#
# Option 1: Hardcode values (simple, but not DRY):
# backend "s3" {
#   bucket = "myapp-terraform-state"
#   key    = "multi-tier-app/terraform.tfstate"
#   region = "us-east-1"
# }
#
# Option 2: Use environment-specific backend files (recommended):
# - backend-dev.tfbackend
# - backend-staging.tfbackend
# - backend-prod.tfbackend
#
# Then init with:
# terraform init -backend-config=backend-dev.tfbackend
#
# Option 3: Pass backend config via CLI:
# terraform init \
#   -backend-config="bucket=myapp-terraform-state" \
#   -backend-config="key=multi-tier-app/terraform.tfstate" \
#   -backend-config="region=us-east-1"
#
# Option 4: Partial configuration (define some here, override via CLI):
# backend "s3" {
#   # Core config here
#   encrypt        = true
#   dynamodb_table = "terraform-state-lock"
#
#   # Override these per environment via -backend-config
#   # bucket = ...
#   # key = ...
#   # region = ...
# }
#
# ==============================================================================

# IMPORTANT: BACKEND MUST BE CREATED BEFORE USING IT
#
# Chicken-and-egg problem:
# - Terraform state backend uses S3 bucket
# - S3 bucket is created with Terraform
# - How do you create S3 bucket if state backend doesn't exist yet?
#
# SOLUTION - Two-phase initialization:
#
# Phase 1: Create backend resources with local state
# ```bash
# # Comment out backend block temporarily
# terraform init
# terraform apply  # Creates S3 bucket, DynamoDB table
# # State stored locally in terraform.tfstate
# ```
#
# Phase 2: Migrate to remote backend
# ```bash
# # Uncomment backend block
# terraform init  # Terraform asks: "Copy existing state to new backend?"
# # Answer: yes
# # State migrated from local file to S3
# rm terraform.tfstate  # Delete local state (now in S3)
# ```
#
# ALTERNATIVE: Create backend resources separately
# - Use AWS Console or CLI to create S3 bucket + DynamoDB table
# - Then configure Terraform to use them
# - Avoids circular dependency
#
# ==============================================================================

terraform {
  backend "s3" {
    # S3 BUCKET FOR STATE STORAGE
    #
    # BUCKET NAMING:
    # Format: {organization}-terraform-state
    # Example: myapp-terraform-state
    #
    # REQUIREMENTS:
    # - Must be globally unique across all AWS accounts
    # - Use organization name or project name as prefix
    # - Do NOT include environment name (shared across environments)
    # - Do NOT include region (specify separately)
    #
    # WHY ONE BUCKET FOR ALL ENVIRONMENTS:
    # - Simpler management (one bucket to secure, monitor, backup)
    # - Key-based separation (dev/terraform.tfstate, prod/terraform.tfstate)
    # - Centralized access controls
    # - Easier cost tracking
    #
    # BUCKET MUST HAVE:
    # ✅ Versioning enabled (recover from accidental deletes or corruption)
    # ✅ Encryption enabled (SSE-S3 or SSE-KMS)
    # ✅ Public access blocked (state contains secrets)
    # ✅ Bucket policy restricting access (least privilege)
    # ✅ Logging enabled (audit who accessed state)
    # ✅ MFA delete enabled (prevent accidental permanent deletion)
    #
    # EXAMPLE BUCKET CONFIGURATION:
    # ```hcl
    # resource "aws_s3_bucket" "terraform_state" {
    #   bucket = "myapp-terraform-state"
    # }
    #
    # resource "aws_s3_bucket_versioning" "terraform_state" {
    #   bucket = aws_s3_bucket.terraform_state.id
    #   versioning_configuration {
    #     status     = "Enabled"
    #     mfa_delete = "Enabled"  # Requires MFA to delete versions
    #   }
    # }
    #
    # resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
    #   bucket = aws_s3_bucket.terraform_state.id
    #   rule {
    #     apply_server_side_encryption_by_default {
    #       sse_algorithm = "AES256"  # Or "aws:kms" for KMS encryption
    #     }
    #   }
    # }
    #
    # resource "aws_s3_bucket_public_access_block" "terraform_state" {
    #   bucket                  = aws_s3_bucket.terraform_state.id
    #   block_public_acls       = true
    #   block_public_policy     = true
    #   ignore_public_acls      = true
    #   restrict_public_buckets = true
    # }
    # ```
    #
    # NOTE: Replace "myapp-terraform-state" with your actual bucket name
    # This value is environment-specific (pass via -backend-config)
    #
    bucket = "YOUR_ORG_NAME-terraform-state"  # REPLACE THIS

    # STATE FILE PATH (KEY)
    #
    # S3 key (path) for the state file within the bucket.
    #
    # KEY ORGANIZATION PATTERN:
    #
    # Option 1: By environment and project
    # - dev/multi-tier-app/terraform.tfstate
    # - staging/multi-tier-app/terraform.tfstate
    # - prod/multi-tier-app/terraform.tfstate
    #
    # Option 2: By project and environment
    # - multi-tier-app/dev/terraform.tfstate
    # - multi-tier-app/staging/terraform.tfstate
    # - multi-tier-app/prod/terraform.tfstate
    #
    # Option 3: Flat structure with naming convention
    # - multi-tier-app-dev.tfstate
    # - multi-tier-app-staging.tfstate
    # - multi-tier-app-prod.tfstate
    #
    # Option 4: Layer-based (separate state per infrastructure layer)
    # - multi-tier-app/dev/network/terraform.tfstate (VPC, subnets)
    # - multi-tier-app/dev/compute/terraform.tfstate (EC2, ASG, ALB)
    # - multi-tier-app/dev/data/terraform.tfstate (RDS, ElastiCache)
    #
    # RECOMMENDED: Option 2 (by project and environment)
    # - Easy to understand (project → environment → state)
    # - Scales well (add more projects, each with own environments)
    # - Works well with terraform_remote_state data source
    #
    # WHY SEPARATE STATE FILES PER ENVIRONMENT:
    # - Blast radius: Destroying dev doesn't affect prod
    # - Access control: Different IAM policies per environment
    # - Locking: Dev and prod can be modified simultaneously
    # - Testing: Can test state operations in dev without risk to prod
    #
    # STATE FILE STRUCTURE:
    # {project}/{environment}/terraform.tfstate
    #
    # Examples:
    # - multi-tier-app/dev/terraform.tfstate
    # - multi-tier-app/staging/terraform.tfstate
    # - multi-tier-app/prod/terraform.tfstate
    #
    # WHY .tfstate EXTENSION:
    # - Convention (makes purpose obvious)
    # - Editor syntax highlighting (some editors recognize .tfstate)
    # - Scripts can filter *.tfstate files
    #
    # NOTE: This value is environment-specific (pass via -backend-config)
    #
    key = "multi-tier-app/${var.environment}/terraform.tfstate"  # This will error!
    # Backend doesn't support variables, so use:
    # terraform init -backend-config="key=multi-tier-app/dev/terraform.tfstate"
    # Or create backend-dev.tfbackend file with correct key
    #
    # For this example, use a placeholder and override:
    key = "multi-tier-app/ENVIRONMENT/terraform.tfstate"  # OVERRIDE WITH -backend-config

    # AWS REGION
    #
    # Region where S3 bucket exists.
    #
    # IMPORTANT: This is the bucket's region, NOT your infrastructure's region!
    # - Infrastructure can be in us-west-2
    # - State bucket can be in us-east-1
    # - They don't have to match
    #
    # REGION SELECTION FOR STATE BUCKET:
    #
    # Option 1: Same region as infrastructure
    # - Pros: Simpler (one region to manage)
    # - Cons: Regional outage affects both infrastructure AND state
    # - Use when: Simplicity is priority, not operating at global scale
    #
    # Option 2: Different region (disaster recovery)
    # - Pros: State survives regional outage, can rebuild infrastructure
    # - Cons: More complex, cross-region data transfer for state updates
    # - Use when: Running critical infrastructure, need DR capabilities
    #
    # Option 3: us-east-1 (default region)
    # - Pros: Cheapest region, most AWS services, most stable
    # - Cons: Further from infrastructure if in other regions
    # - Use when: Centralizing state for multi-region deployments
    #
    # RECOMMENDATION:
    # - Single-region deployment: Use same region as infrastructure
    # - Multi-region deployment: Use us-east-1 for state (central location)
    # - High-availability requirement: Use S3 Cross-Region Replication
    #
    # S3 CROSS-REGION REPLICATION:
    # For ultimate durability, replicate state bucket to multiple regions:
    # ```hcl
    # resource "aws_s3_bucket_replication_configuration" "state_replication" {
    #   bucket = aws_s3_bucket.terraform_state.id
    #   role   = aws_iam_role.replication.arn
    #
    #   rule {
    #     id     = "replicate-state-to-dr-region"
    #     status = "Enabled"
    #
    #     destination {
    #       bucket        = aws_s3_bucket.terraform_state_replica.arn
    #       storage_class = "STANDARD_IA"  # Cheaper for infrequent access
    #     }
    #   }
    # }
    # ```
    #
    # NOTE: This value is static (same for all environments typically)
    #
    region = "us-east-1"

    # STATE ENCRYPTION
    #
    # Enable server-side encryption for state file in S3.
    #
    # WHY ENCRYPT STATE:
    # State file contains sensitive data:
    # - Database passwords (from random_password or AWS Secrets Manager)
    # - Private keys (TLS certificates, SSH keys)
    # - API tokens and credentials
    # - Internal IP addresses and network topology
    # - Resource IDs that reveal infrastructure details
    #
    # ENCRYPTION OPTIONS:
    #
    # Option 1: SSE-S3 (AWS-managed keys)
    # encrypt = true  # Default: Uses AES-256 with AWS-managed keys
    # - Pros: Free, automatic, no key management
    # - Cons: AWS controls keys (government could theoretically access)
    # - Use when: Standard security requirements, not compliance-heavy
    #
    # Option 2: SSE-KMS (Customer-managed keys)
    # encrypt        = true
    # kms_key_id     = "arn:aws:kms:us-east-1:123456789012:key/abc-def-123"
    # - Pros: You control keys, audit trail via CloudTrail, key rotation
    # - Cons: Costs $1/month per key + $0.03/10,000 requests
    # - Use when: Compliance requires customer-managed keys (HIPAA, PCI-DSS)
    #
    # KMS KEY SETUP:
    # ```hcl
    # resource "aws_kms_key" "terraform_state" {
    #   description             = "KMS key for Terraform state encryption"
    #   deletion_window_in_days = 30  # Prevent accidental deletion
    #   enable_key_rotation     = true  # Automatic annual rotation
    # }
    #
    # resource "aws_kms_alias" "terraform_state" {
    #   name          = "alias/terraform-state"
    #   target_key_id = aws_kms_key.terraform_state.key_id
    # }
    # ```
    #
    # KMS KEY POLICY (grant access to Terraform):
    # ```json
    # {
    #   "Version": "2012-10-17",
    #   "Statement": [
    #     {
    #       "Sid": "Enable IAM User Permissions",
    #       "Effect": "Allow",
    #       "Principal": {
    #         "AWS": "arn:aws:iam::123456789012:root"
    #       },
    #       "Action": "kms:*",
    #       "Resource": "*"
    #     },
    #     {
    #       "Sid": "Allow Terraform State Encryption",
    #       "Effect": "Allow",
    #       "Principal": {
    #         "AWS": [
    #           "arn:aws:iam::123456789012:role/TerraformExecutionRole",
    #           "arn:aws:iam::123456789012:user/terraform-ci"
    #         ]
    #       },
    #       "Action": [
    #         "kms:Decrypt",
    #         "kms:Encrypt",
    #         "kms:DescribeKey",
    #         "kms:GenerateDataKey"
    #       ],
    #       "Resource": "*"
    #     }
    #   ]
    # }
    # ```
    #
    # RECOMMENDATION:
    # - dev: SSE-S3 (simple, free)
    # - staging: SSE-KMS (test KMS setup before prod)
    # - prod: SSE-KMS (compliance, audit trail, key control)
    #
    encrypt = true

    # DYNAMODB TABLE FOR STATE LOCKING
    #
    # DynamoDB table name for state locking and consistency checking.
    #
    # WHY STATE LOCKING:
    # Prevents two people/processes from running terraform apply simultaneously.
    #
    # WITHOUT LOCKING:
    # 1. Alice runs terraform apply (reads state, modifies resources)
    # 2. Bob runs terraform apply (reads same state, modifies same resources)
    # 3. Alice finishes, writes new state
    # 4. Bob finishes, writes new state (overwrites Alice's changes!)
    # 5. Result: State corruption, infrastructure inconsistency
    #
    # WITH LOCKING:
    # 1. Alice runs terraform apply
    # 2. Terraform acquires lock in DynamoDB (atomic operation)
    # 3. Bob runs terraform apply
    # 4. Terraform tries to acquire lock → fails (Alice has lock)
    # 5. Bob gets error: "State locked. Lock ID: xxx. Created: xxx. Info: Alice's laptop"
    # 6. Bob waits for Alice to finish
    # 7. Alice finishes, releases lock
    # 8. Bob can now acquire lock and proceed
    #
    # DYNAMODB TABLE REQUIREMENTS:
    #
    # 1. Table name: Can be anything (terraform-state-lock is convention)
    # 2. Partition key: Must be named "LockID" (string type)
    # 3. Billing mode: PAY_PER_REQUEST recommended (no capacity planning needed)
    # 4. No other attributes required
    #
    # TABLE CREATION:
    # ```hcl
    # resource "aws_dynamodb_table" "terraform_state_lock" {
    #   name         = "terraform-state-lock"
    #   billing_mode = "PAY_PER_REQUEST"  # Or "PROVISIONED" with read/write capacity
    #   hash_key     = "LockID"  # MUST be exactly "LockID"
    #
    #   attribute {
    #     name = "LockID"
    #     type = "S"  # String
    #   }
    #
    #   # Optional: Point-in-time recovery (backup every second)
    #   point_in_time_recovery {
    #     enabled = true
    #   }
    #
    #   # Optional: Server-side encryption
    #   server_side_encryption {
    #     enabled = true
    #   }
    #
    #   # Optional: Tags
    #   tags = {
    #     Name        = "Terraform State Lock Table"
    #     Environment = "shared"  # Shared across all environments
    #     Purpose     = "terraform-state-locking"
    #   }
    # }
    # ```
    #
    # COST:
    # - PAY_PER_REQUEST mode: $1.25 per million write requests
    # - Typical usage: 2 writes per terraform apply (acquire lock, release lock)
    # - 100 applies/day = 200 writes/day = 6,000 writes/month = $0.0075/month
    # - Effectively free for most use cases
    # - Storage: First 25 GB free, then $0.25/GB/month (state locks are tiny)
    #
    # ONE TABLE FOR ALL ENVIRONMENTS:
    # Unlike S3 bucket (one bucket, multiple keys), DynamoDB uses one table.
    # - All environments share same lock table
    # - Each state file gets unique lock entry (identified by S3 bucket + key)
    # - No conflicts between environments (different lock IDs)
    #
    # LOCK LIFECYCLE:
    # 1. terraform apply starts
    # 2. Attempt to write lock entry to DynamoDB (conditional write, fails if exists)
    # 3. If write succeeds → lock acquired, proceed with plan and apply
    # 4. If write fails → lock already exists, print error and wait
    # 5. After apply completes (or fails), delete lock entry from DynamoDB
    # 6. Next terraform apply can now acquire lock
    #
    # ABANDONED LOCKS:
    # If terraform process crashes or is killed, lock might not be released.
    # - Lock remains in DynamoDB
    # - Next terraform apply fails with "state locked" error
    # - Manual intervention required: terraform force-unlock <lock-id>
    # - Force unlock deletes lock entry from DynamoDB
    #
    # FORCE UNLOCK:
    # ```bash
    # terraform force-unlock abc123  # Lock ID from error message
    # # Are you sure? yes
    # # Lock deleted, can now terraform apply
    # ```
    #
    # ⚠️ WARNING: Only force-unlock if you're sure no other process is running!
    # If Alice's terraform apply is still running and you force-unlock, you've
    # defeated the purpose of locking.
    #
    dynamodb_table = "terraform-state-lock"

    # ADDITIONAL BACKEND OPTIONS (OPTIONAL)

    # WORKSPACE PREFIX (for Terraform workspaces)
    #
    # If using Terraform workspaces, this prefix is added to state key.
    #
    # WITHOUT workspace_key_prefix:
    # - Default workspace: multi-tier-app/terraform.tfstate
    # - dev workspace: multi-tier-app/terraform.tfstate (same! ❌)
    #
    # WITH workspace_key_prefix = "env":
    # - Default workspace: multi-tier-app/terraform.tfstate
    # - dev workspace: multi-tier-app/env/dev/terraform.tfstate
    # - prod workspace: multi-tier-app/env/prod/terraform.tfstate
    #
    # RECOMMENDATION: Don't use Terraform workspaces for environments.
    # Use separate directories and backend configs instead (more explicit, less magic).
    #
    # workspace_key_prefix = "env"  # Uncomment if using workspaces

    # ACL (Access Control List)
    #
    # S3 bucket ACL for state file.
    #
    # OPTIONS:
    # - "private" (default, recommended): Owner has full control, no one else
    # - "bucket-owner-full-control": Useful for cross-account access
    #
    # RECOMMENDATION: Use "private" + IAM policies (more fine-grained control)
    #
    # acl = "private"

    # SKIP CREDENTIALS VALIDATION
    #
    # Skip validation of AWS credentials (faster init, but errors delayed to apply).
    #
    # skip_credentials_validation = false  # Default: false (validate credentials)

    # SKIP METADATA API CHECK
    #
    # Skip EC2 metadata API check (faster on non-EC2 machines).
    #
    # skip_metadata_api_check = true  # Set to true if running on non-EC2 (laptops, CI/CD)

    # SKIP REGION VALIDATION
    #
    # Skip validation of region (useful for new regions not yet in AWS SDK).
    #
    # skip_region_validation = false  # Default: false (validate region)

    # FORCE PATH STYLE
    #
    # Use path-style S3 URLs (s3.amazonaws.com/bucket/key) instead of virtual-hosted
    # style (bucket.s3.amazonaws.com/key).
    #
    # Required for some S3-compatible services (MinIO, Localstack).
    #
    # force_path_style = false  # Default: false (use virtual-hosted style)

    # MAX RETRIES
    #
    # Maximum number of retries for S3 operations.
    #
    # Useful for flaky networks or rate-limited environments.
    #
    # max_retries = 5  # Default: 5

    # SSE CUSTOMER KEY (for customer-provided encryption keys)
    #
    # Provide your own encryption key instead of AWS-managed or KMS keys.
    # Rarely used (key management burden on you).
    #
    # sse_customer_key = "base64-encoded-256-bit-key"  # Bring your own key
  }
}

# ==============================================================================
# BACKEND INITIALIZATION
# ==============================================================================
#
# FIRST TIME SETUP:
#
# Step 1: Create S3 bucket and DynamoDB table (separate Terraform config or AWS console)
# Step 2: Create backend config file per environment
#
# backend-dev.tfbackend:
# ```hcl
# bucket         = "myapp-terraform-state"
# key            = "multi-tier-app/dev/terraform.tfstate"
# region         = "us-east-1"
# encrypt        = true
# dynamodb_table = "terraform-state-lock"
# ```
#
# backend-prod.tfbackend:
# ```hcl
# bucket         = "myapp-terraform-state"
# key            = "multi-tier-app/prod/terraform.tfstate"
# region         = "us-east-1"
# encrypt        = true
# dynamodb_table = "terraform-state-lock"
# ```
#
# Step 3: Initialize Terraform with backend config
# ```bash
# terraform init -backend-config=backend-dev.tfbackend
# ```
#
# Step 4: Verify backend configuration
# ```bash
# terraform state list  # Should work if backend is configured correctly
# ```
#
# MIGRATING FROM LOCAL TO REMOTE STATE:
# ```bash
# # Currently using local state (terraform.tfstate in current directory)
# # Want to migrate to S3 backend
#
# # 1. Add backend configuration to backend.tf (this file)
# # 2. Run terraform init
# terraform init -backend-config=backend-prod.tfbackend
# # Terraform detects existing local state
# # "Do you want to copy existing state to new backend?" → yes
# # State migrated to S3
# # 3. Delete local state file
# rm terraform.tfstate
# rm terraform.tfstate.backup
# ```
#
# SWITCHING BACKENDS:
# ```bash
# # Migrate from one S3 bucket to another
# # Or from local to S3, or S3 to Terraform Cloud
#
# # 1. Update backend configuration
# # 2. Run terraform init -reconfigure
# terraform init -reconfigure -backend-config=new-backend.tfbackend
# # -reconfigure flag tells Terraform to re-initialize backend
# ```
#
# REMOVING BACKEND (back to local state):
# ```bash
# # 1. Comment out entire backend block
# # 2. Run terraform init -reconfigure
# terraform init -reconfigure
# # "Do you want to copy existing state from backend to local?" → yes
# # State migrated from S3 to local terraform.tfstate file
# ```
#
# ==============================================================================

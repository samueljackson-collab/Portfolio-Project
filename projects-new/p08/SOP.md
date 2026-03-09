# Standard Operating Procedures

## SOP-001: Onboarding New Data Flow (New S3 Bucket Source)

**Purpose:** Add a new upstream data source to the ETL pipeline while maintaining security, monitoring, and data quality standards.

**Frequency:** As needed (estimated 2-4 times per year)

**Roles:**
- **Requester:** Data producer team or business stakeholder
- **Implementer:** Data Engineering team
- **Approvers:** Security team (IAM/encryption), Data Governance (schema/retention)

**Prerequisites:**
- [ ] Data source specification document (format, schema, volume, frequency)
- [ ] Sample data files (at least 10 representative samples)
- [ ] Business justification and downstream consumers identified
- [ ] Retention requirements defined (compliance, GDPR, etc.)

**Steps:**

1. **Requirements Gathering (1-2 days):**
   - Meet with requester to document:
     - Data format (JSON, CSV, Parquet, Avro)
     - Schema (provide JSON Schema or Avro schema file)
     - Volume (files per day, average file size)
     - SLA (latency tolerance: real-time, hourly, daily batch)
     - Sensitivity (PII, PHI, financial data)
   - Create Jira ticket: `[DATA-ONBOARD] Add source: <source-name>`

2. **Schema Validation Setup:**
   ```bash
   # Add JSON Schema to schemas/ directory
   cat > schemas/new-source-schema.json <<EOF
   {
     "$schema": "http://json-schema.org/draft-07/schema#",
     "type": "object",
     "required": ["id", "timestamp", "event_type"],
     "properties": {
       "id": {"type": "string"},
       "timestamp": {"type": "string", "format": "date-time"},
       "event_type": {"type": "string", "enum": ["create", "update", "delete"]}
     }
   }
   EOF

   # Update validate Lambda to reference new schema
   # Edit lambda/validate/handler.py to load new-source-schema.json
   ```

3. **IAM & Security Configuration:**
   ```bash
   # Create dedicated S3 bucket or prefix for new source
   aws s3api create-bucket \
     --bucket raw-data-new-source \
     --region us-east-1 \
     --create-bucket-configuration LocationConstraint=us-east-1

   # Enable versioning and encryption
   aws s3api put-bucket-versioning \
     --bucket raw-data-new-source \
     --versioning-configuration Status=Enabled

   aws s3api put-bucket-encryption \
     --bucket raw-data-new-source \
     --server-side-encryption-configuration file://encryption-config.json

   # Grant producer IAM role PutObject permission (least privilege)
   # Update bucket policy to allow specific producer role
   ```

4. **EventBridge Rule Configuration:**
   ```bash
   # Create EventBridge rule for new bucket
   aws events put-rule \
     --name etl-s3-events-new-source \
     --event-pattern '{
       "source": ["aws.s3"],
       "detail-type": ["Object Created"],
       "detail": {
         "bucket": {"name": ["raw-data-new-source"]}
       }
     }' \
     --state ENABLED

   # Add Step Functions as target
   aws events put-targets \
     --rule etl-s3-events-new-source \
     --targets Id=1,Arn=arn:aws:states:REGION:ACCOUNT:stateMachine:etl-workflow,RoleArn=ROLE_ARN
   ```

5. **Update Lambda Functions:**
   - **Ingest Lambda:** Add logic to handle new source format
   - **Validate Lambda:** Load new schema file, apply validation rules
   - **Transform Lambda:** Implement source-specific business logic (if needed)
   - **Output Lambda:** Configure output partitioning (e.g., `source=new-source/year=2024/`)

6. **Testing (Dev Environment):**
   ```bash
   # Upload test files to dev raw bucket
   aws s3 cp test-data/sample-001.json s3://raw-data-new-source-dev/sample-001.json

   # Verify Step Functions execution
   aws stepfunctions list-executions \
     --state-machine-arn arn:aws:states:REGION:ACCOUNT:stateMachine:etl-workflow-dev \
     --status-filter SUCCEEDED

   # Validate output in processed bucket
   aws s3 ls s3://processed-data-dev/source=new-source/ --recursive

   # Check DynamoDB for metadata
   aws dynamodb scan --table-name etl-metadata-dev \
     --filter-expression "source_name = :src" \
     --expression-attribute-values '{":src":{"S":"new-source"}}'
   ```

7. **Monitoring & Alerting:**
   ```bash
   # Add CloudWatch dashboard widget for new source
   # Metrics: file count, error rate, processing latency

   # Create alarm for validation failures
   aws cloudwatch put-metric-alarm \
     --alarm-name etl-new-source-validation-errors \
     --metric-name ValidationErrors \
     --namespace ETL/Pipeline \
     --statistic Sum \
     --period 300 \
     --threshold 5 \
     --comparison-operator GreaterThanThreshold \
     --evaluation-periods 1 \
     --dimensions Name=Source,Value=new-source
   ```

8. **Documentation:**
   - Update `README.md` with new source details
   - Add entry to `DATA_CATALOG.md` (schema, owner, SLA, retention)
   - Create runbook entry for source-specific errors

9. **Production Deployment:**
   - Deploy via SAM/CDK with staged rollout (dev → staging → prod)
   - Run smoke test in production (upload 5 test files, verify processing)
   - Monitor for 48 hours before declaring success

10. **Handoff:**
    - Train on-call engineers on new source troubleshooting
    - Notify downstream consumers of data availability
    - Schedule 30-day review to validate volume/cost assumptions

**Success Criteria:**
- [ ] 100 production files processed successfully without errors
- [ ] Validation schema catches all malformed samples
- [ ] Latency SLA met (p95 <30s for hourly batch, <10s for real-time)
- [ ] No IAM/encryption gaps identified in security review
- [ ] Monitoring dashboards show healthy metrics

---

## SOP-002: Versioning & Rollback of Lambda Functions

**Purpose:** Safely deploy new Lambda function versions with rollback capability in case of errors.

**Frequency:** Per deployment (estimated 2-4 times per month)

**Roles:**
- **Developer:** Implements Lambda code changes
- **Reviewer:** Reviews code and approves PR
- **Deployer:** Executes deployment (can be automated via CI/CD)

**Steps:**

1. **Pre-Deployment:**
   ```bash
   # Ensure all tests pass
   pytest tests/ -v --cov=lambda

   # Build Lambda packages
   sam build --use-container

   # Create Git tag for version tracking
   git tag -a v1.5.0 -m "Add retry logic for DynamoDB throttling"
   git push origin v1.5.0
   ```

2. **Publish New Lambda Version:**
   ```bash
   # Deploy with SAM (automatically publishes new version)
   sam deploy --config-file samconfig-prod.toml --no-confirm-changeset

   # Verify new version published
   aws lambda list-versions-by-function --function-name ingest-handler \
     --query 'Versions[-1].{Version:Version,CodeSha256:CodeSha256}'
   ```

3. **Create Alias with Traffic Shifting:**
   ```bash
   # Update alias to point 10% traffic to new version (canary)
   NEW_VERSION=$(aws lambda list-versions-by-function --function-name ingest-handler \
     --query 'Versions[-1].Version' --output text)

   aws lambda update-alias \
     --function-name ingest-handler \
     --name production \
     --function-version $NEW_VERSION \
     --routing-config AdditionalVersionWeights={$OLD_VERSION=0.9}

   # Monitor for 30 minutes (error rate, latency)
   ```

4. **Full Cutover (If Canary Successful):**
   ```bash
   # Route 100% traffic to new version
   aws lambda update-alias \
     --function-name ingest-handler \
     --name production \
     --function-version $NEW_VERSION
   ```

5. **Rollback (If Errors Detected):**
   ```bash
   # Immediate: Revert alias to previous version
   aws lambda update-alias \
     --function-name ingest-handler \
     --name production \
     --function-version $OLD_VERSION

   # Verify rollback successful
   aws lambda get-alias --function-name ingest-handler --name production
   ```

**Rollback Decision Criteria:**
- Error rate >5% sustained for 10 minutes
- Latency p95 >2x baseline
- Critical bug identified in new code
- Failed integration test post-deployment

---

## SOP-003: Rotating Secrets (DynamoDB Encryption Keys, API Tokens)

**Purpose:** Rotate KMS keys, database passwords, and API tokens on a quarterly schedule to maintain security posture.

**Frequency:** Quarterly (every 90 days)

**Steps:**

1. **KMS Key Rotation (Automated):**
   ```bash
   # Enable automatic key rotation (AWS manages)
   aws kms enable-key-rotation --key-id KEY_ID

   # Verify rotation enabled
   aws kms get-key-rotation-status --key-id KEY_ID
   # Note: AWS rotates keys annually; no manual action required for KMS-managed rotation
   ```

2. **Secrets Manager Secret Rotation (e.g., API tokens):**
   ```bash
   # Configure automatic rotation for secret
   aws secretsmanager rotate-secret \
     --secret-id etl/external-api-token \
     --rotation-lambda-arn arn:aws:lambda:REGION:ACCOUNT:function:secret-rotator \
     --rotation-rules AutomaticallyAfterDays=90

   # Verify rotation succeeded
   aws secretsmanager describe-secret --secret-id etl/external-api-token
   ```

3. **Update Lambda Environment Variables (If Hardcoded):**
   ```bash
   # Retrieve new secret value
   NEW_TOKEN=$(aws secretsmanager get-secret-value \
     --secret-id etl/external-api-token \
     --query SecretString --output text)

   # Update Lambda environment variable (avoid this - use Secrets Manager SDK instead)
   aws lambda update-function-configuration \
     --function-name ingest-handler \
     --environment Variables={API_TOKEN=$NEW_TOKEN}

   # Better: Modify Lambda code to call Secrets Manager at runtime
   ```

4. **Validation:**
   - Trigger test Step Functions execution
   - Verify Lambda can decrypt S3 objects with new KMS key
   - Confirm API calls succeed with rotated token

**Post-Rotation:**
- Document rotation in audit log
- Update incident response runbooks if credentials change
- Notify team in Slack: "Quarterly secret rotation complete"

---

## SOP-004: Monthly Cost Review & Optimization

**Purpose:** Review AWS costs monthly, identify waste, and implement optimizations to stay within budget.

**Frequency:** Monthly (first Monday of each month)

**Attendees:** Data Engineering Lead, FinOps, Product Owner

**Agenda:**

1. **Cost Explorer Review:**
   - Total spend vs budget (target: <95% of monthly allocation)
   - Service breakdown (Lambda, Step Functions, S3, DynamoDB)
   - Cost trends (MoM growth rate)

2. **Identify Top 3 Cost Drivers:**
   - Use Cost Explorer grouping by tag (Function, Source, Environment)
   - Example: `transform-handler` Lambda = 40% of total cost

3. **Optimization Actions:**
   - **Lambda:** Right-size memory, switch to ARM64, reduce duration via code optimization
   - **DynamoDB:** Evaluate on-demand vs provisioned, implement TTL for old data
   - **S3:** Enable Intelligent Tiering, delete orphaned objects, compress large files
   - **Step Functions:** Batch small jobs, migrate to Express Workflows for <5min tasks

4. **Implement Quick Wins:**
   ```bash
   # Example: Reduce Lambda memory from 1024MB to 512MB (saves ~$X/month)
   aws lambda update-function-configuration \
     --function-name transform-handler \
     --memory-size 512
   ```

5. **Track Savings:**
   - Create Cost Explorer report showing before/after optimization
   - Add to cumulative savings dashboard

6. **Next Month's Actions:**
   - Assign ownership for deferred optimizations
   - Set reminder for next review

**Success Metrics:**
- Monthly cost growth <10% (aligned with data volume growth)
- Identified savings of >$500/month per review
- 100% of quick wins implemented within 7 days

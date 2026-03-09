# P08 Architecture Diagrams

## Event-Driven ETL Flow
```mermaid
graph LR
    subgraph DataSources
      UP[Upstream Systems]
      API[External APIs]
    end
    subgraph Ingestion
      S3RAW[S3 Raw Bucket]
      EVTS3[S3 Event Notification]
    end
    subgraph Processing
      SF[Step Functions ETL Workflow]
      L1[Lambda: Ingest]
      L2[Lambda: Validate]
      L3[Lambda: Transform]
      L4[Lambda: Output]
    end
    subgraph Storage
      DDB[DynamoDB Metadata Table]
      S3PROC[S3 Processed Bucket]
      DLQ[SQS Dead Letter Queue]
    end
    subgraph Monitoring
      CW[CloudWatch Logs/Metrics]
      SNS[SNS Alerts]
    end
    UP --> S3RAW
    API --> S3RAW
    S3RAW --> EVTS3
    EVTS3 --> SF
    SF --> L1
    L1 --> DDB
    L1 --> L2
    L2 --> L3
    L2 -->|Invalid| DLQ
    L3 --> L4
    L4 --> S3PROC
    L1 --> CW
    L2 --> CW
    L3 --> CW
    L4 --> CW
    CW --> SNS
```
**Explanation:** Files land in raw S3 bucket, triggering EventBridge rules that start Step Functions workflows. The ingest Lambda writes metadata to DynamoDB and passes data to validate Lambda. Invalid records route to DLQ; valid records proceed to transform Lambda for business logic application, then output Lambda writes to processed bucket. CloudWatch captures logs/metrics; SNS sends alerts on failures.

## Step Functions State Machine
```mermaid
stateDiagram-v2
    [*] --> IngestState
    IngestState --> ValidateState: Success
    IngestState --> ErrorHandler: Error
    ValidateState --> TransformState: Valid
    ValidateState --> DLQRoute: Invalid
    TransformState --> ParallelOutput: Success
    TransformState --> ErrorHandler: Error

    state ParallelOutput {
        [*] --> OutputToS3
        [*] --> UpdateMetadata
        OutputToS3 --> [*]
        UpdateMetadata --> [*]
    }

    ParallelOutput --> SuccessNotification
    ErrorHandler --> RetryLogic
    RetryLogic --> IngestState: Retry < 3
    RetryLogic --> FailureNotification: Max Retries
    DLQRoute --> [*]
    SuccessNotification --> [*]
    FailureNotification --> [*]
```
**Explanation:** State machine orchestrates Lambda invocations with explicit error handling. Ingest and Transform states have retry logic (3 attempts with exponential backoff). Validation failures route to DLQ without retry (data quality issue). Parallel state writes output to S3 and updates DynamoDB concurrently. Catch blocks handle Lambda errors and send SNS notifications.

## Data Lifecycle & Retention
```mermaid
graph TB
    subgraph Ingestion
      RAW[Raw Bucket<br/>Lifecycle: 30 days]
      GLACIER[Glacier<br/>After 30 days]
      DELETE[Delete After 365 days]
    end
    subgraph Processing
      PROC[Processed Bucket<br/>Lifecycle: 90 days]
      IA[Infrequent Access<br/>After 90 days]
    end
    subgraph Metadata
      DDB[DynamoDB<br/>TTL: 180 days]
    end
    RAW -->|30d| GLACIER
    GLACIER -->|365d| DELETE
    PROC -->|90d| IA
    DDB -->|TTL| DDB
```
**Explanation:** Raw files transition to Glacier after 30 days for archival, deleted after 365 days for compliance. Processed files move to Infrequent Access tier after 90 days (cost optimization). DynamoDB items have 180-day TTL to auto-expire old metadata. Lifecycle policies configured via S3 object lifecycle rules and DynamoDB TTL attribute.

## Security Architecture
```mermaid
graph TB
    subgraph IAM
      ROLE[Lambda Execution Role]
      POLICY[Least Privilege Policy]
    end
    subgraph Encryption
      KMS[KMS Customer Managed Key]
      S3ENC[S3 SSE-KMS]
      DDBENC[DynamoDB Encryption at Rest]
    end
    subgraph Network
      VPC[VPC Endpoints for S3/DynamoDB]
      SG[Security Groups]
      NACL[Network ACLs]
    end
    subgraph Logging
      CT[CloudTrail Data Events]
      CWLOGS[CloudWatch Logs Encrypted]
      AUDIT[Audit Trail to S3]
    end
    ROLE --> POLICY
    POLICY --> S3ENC
    POLICY --> DDBENC
    S3ENC --> KMS
    DDBENC --> KMS
    ROLE --> VPC
    VPC --> SG
    SG --> NACL
    CT --> AUDIT
    CWLOGS --> KMS
```
**Explanation:** Lambda functions assume execution role with least privilege IAM policies (read raw bucket, write processed bucket, DynamoDB access). S3 and DynamoDB encrypted with KMS CMK for key rotation and auditability. Lambdas deployed in VPC with VPC endpoints to avoid internet routing. CloudTrail logs S3 data events; CloudWatch logs encrypted with KMS. Security groups and NACLs restrict network traffic.

## Error Handling & Retry Strategy
```mermaid
graph LR
    subgraph ErrorTypes
      TRANS[Transient Error<br/>Throttle, Network]
      PERM[Permanent Error<br/>Schema Mismatch]
    end
    subgraph Handling
      RETRY[Retry with Backoff<br/>Max 3 attempts]
      DLQ2[DLQ for Manual Review]
      ALERT[SNS Alert to Ops]
    end
    subgraph Resolution
      AUTO[Auto-Resolve<br/>Retry Success]
      MANUAL[Manual Fix<br/>Reprocess from DLQ]
    end
    TRANS --> RETRY
    PERM --> DLQ2
    RETRY --> AUTO
    RETRY -->|Max Retries| DLQ2
    DLQ2 --> ALERT
    ALERT --> MANUAL
```
**Explanation:** Step Functions retry logic differentiates transient vs permanent errors. Transient errors (DynamoDB throttling, network timeouts) trigger exponential backoff retries (3 attempts, 2s/4s/8s delays). Permanent errors (schema validation failures, malformed JSON) skip retries and route directly to DLQ. SNS alerts fire on DLQ arrival and max retry exhaustion. Operators review DLQ, fix root cause, and replay messages via Step Functions re-execution.

## Cost Optimization Architecture
```mermaid
graph TB
    subgraph Compute
      ARM[Lambda ARM64 Graviton2<br/>20% Cost Reduction]
      MEM[Right-Sized Memory<br/>Profiled per Function]
    end
    subgraph Storage
      S3TIERS[S3 Intelligent Tiering<br/>Auto-optimize Access Patterns]
      DDBOD[DynamoDB On-Demand<br/>Pay Per Request]
    end
    subgraph Monitoring
      BUDGETS[AWS Budgets Alerts]
      COSTEXP[Cost Explorer Dashboards]
    end
    ARM --> MEM
    S3TIERS --> DDBOD
    BUDGETS --> COSTEXP
```
**Explanation:** Lambdas use ARM64 architecture for 20% cost savings. Memory allocations tuned per function (ingest 512MB, validate 256MB, transform 1024MB, output 512MB) based on profiling. S3 Intelligent Tiering auto-adjusts storage class. DynamoDB on-demand pricing eliminates over-provisioning. AWS Budgets alert at 80%/100% thresholds; Cost Explorer tracks daily spend by service/tag.

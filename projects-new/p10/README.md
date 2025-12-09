# P10 — Data Lake & Analytics Platform with Apache Iceberg

**Tagline:** Modern lakehouse delivering ACID tables, time travel, and governed analytics with Apache Iceberg, Spark, AWS Glue, and Athena.

## Executive Summary
- **ACID Guarantees:** Iceberg tables provide transactional consistency, enabling reliable upserts, deletes, and schema evolution
- **Time Travel:** Query historical snapshots for auditing, debugging, and reproducibility
- **Multi-Engine Access:** Spark, Presto, Trino, and Athena read/write same tables with serializable isolation
- **Governance at Scale:** AWS Lake Formation enforces row/column-level security; audit logs track all access
- **Cost Efficiency:** Partitioning, z-ordering, and compaction optimize query performance and storage costs

## Architecture Overview

### Medallion Architecture
**Bronze (Raw)** → **Silver (Staged/Cleansed)** → **Gold (Curated/Aggregated)**

Each zone uses Apache Iceberg tables for ACID, versioning, and schema evolution.

### Components
- **Ingestion:** Batch (Spark/Glue jobs) and streaming (Kafka → Flink → Iceberg) pipelines
- **Storage:** S3 with Iceberg metadata (manifests, snapshots) and data files (Parquet)
- **Catalog:** AWS Glue Data Catalog integrated with Iceberg for metadata management
- **Compute:** Spark on EMR/EMR-on-EKS for ETL; Glue jobs for managed transforms
- **Query Engines:** Athena/Presto/Trino for ad-hoc analytics and BI tool integration
- **Governance:** Lake Formation for column-level permissions, row filters, and audit logging
- **Maintenance:** Scheduled jobs for compaction, snapshot expiry, and orphan file cleanup

### Directory Layout
```
projects-new/p10/
├── README.md
├── ARCHITECTURE.md
├── TESTING.md
├── REPORT_TEMPLATES.md
├── PLAYBOOK.md
├── RUNBOOKS.md
├── SOP.md
├── METRICS.md
├── ADRS.md
├── THREAT_MODEL.md
├── RISK_REGISTER.md
├── terraform/
│   └── main.tf               # S3, Glue, IAM, KMS, Lake Formation
├── spark/
│   ├── iceberg_write_job.py  # Batch ingestion with partitioning
│   ├── iceberg_read_job.py   # Reads, time-travel, rollback
│   └── maintenance.py        # Compaction and cleanup
└── athena/
    └── queries.sql           # Sample validation and views
```

## Setup

### Prerequisites
- AWS account with IAM permissions for S3, Glue, Lake Formation, Athena
- Terraform 1.5+ for infrastructure provisioning
- Spark 3.3+ with Iceberg runtime JAR
- Python 3.10+ for job development

### Deploy Infrastructure
```bash
cd projects-new/p10/terraform
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Creates:
- S3 buckets (bronze, silver, gold with versioning and encryption)
- Glue Data Catalog database
- Lake Formation permissions and data lake settings
- IAM roles for Spark/Glue/Athena
- KMS key for encryption

### Run Spark Ingestion Job
```bash
spark-submit \
  --jars /opt/iceberg/iceberg-spark-runtime-3.3_2.12-1.4.0.jar \
  --conf spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog \
  --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog \
  --conf spark.sql.catalog.glue_catalog.warehouse=s3://my-data-lake/warehouse/ \
  spark/iceberg_write_job.py --source s3://raw-data/ --table glue_catalog.bronze.events
```

### Query with Athena
```sql
-- Query current data
SELECT * FROM glue_catalog.silver.transactions WHERE date >= '2025-01-01' LIMIT 10;

-- Time travel to yesterday
SELECT * FROM glue_catalog.silver.transactions FOR SYSTEM_TIME AS OF '2025-01-14 00:00:00' LIMIT 10;

-- Query specific snapshot
SELECT * FROM glue_catalog.silver.transactions FOR SYSTEM_VERSION AS OF 1234567890;
```

## Data Flow
1. **Raw Ingestion:** Batch files land in bronze S3 bucket; Spark job reads and writes to bronze Iceberg table
2. **Cleansing:** Spark job reads bronze, applies validation/dedupe, writes to silver
3. **Aggregation:** Scheduled job computes metrics, writes to gold tables
4. **Compaction:** Maintenance job rewrites small files, updates manifests
5. **Consumption:** Athena/Presto queries gold tables; BI tools connect via JDBC

## Operations

### Table Maintenance
```bash
# Compact small files
spark-sql --conf spark.sql.catalog.glue_catalog.warehouse=s3://... \
  -e "CALL glue_catalog.system.rewrite_data_files('silver.transactions');"

# Expire old snapshots (retain 7 days)
spark-sql -e "CALL glue_catalog.system.expire_snapshots('silver.transactions', TIMESTAMP '2025-01-07 00:00:00');"

# Remove orphan files
spark-sql -e "CALL glue_catalog.system.remove_orphan_files('silver.transactions');"
```

### Schema Evolution
```python
# Add column with default
spark.sql("""
  ALTER TABLE glue_catalog.silver.transactions
  ADD COLUMN customer_segment STRING AFTER customer_id
""")

# Rename column (Iceberg supports)
spark.sql("""
  ALTER TABLE glue_catalog.silver.transactions
  RENAME COLUMN old_name TO new_name
""")
```

### Time Travel & Rollback
```python
# Read historical snapshot
df = spark.read \
  .format("iceberg") \
  .option("snapshot-id", "1234567890") \
  .table("glue_catalog.silver.transactions")

# Rollback to previous snapshot
spark.sql("""
  CALL glue_catalog.system.rollback_to_snapshot('silver.transactions', 1234567890)
""")
```

## Performance Optimization
- **Partitioning:** Partition by date/region for query pruning
- **Z-Ordering:** Sort within files by frequently filtered columns
- **File Sizing:** Target 128-512 MB files via compaction
- **Caching:** Athena result caching; Presto coordinator caching
- **Concurrency:** Use optimistic concurrency for writes; retry on conflict

## Security & Governance
- **Encryption:** S3-SSE with KMS for data at rest; TLS for data in transit
- **Access Control:** Lake Formation column/row filters; IAM roles for compute
- **Audit Logging:** CloudTrail for API calls; Lake Formation audit logs for data access
- **Data Classification:** Tag tables/columns with sensitivity (PII, confidential); enforce policies

## Cost Management
- **S3 Lifecycle:** Transition bronze to Glacier after 90 days; delete after 1 year
- **Compaction:** Reduce file count to minimize S3 LIST costs
- **Athena Optimization:** Partition pruning, compression (Parquet Snappy), column projection
- **Spot Instances:** Use spot for EMR clusters with checkpointing

## Hiring Manager Highlights
- **Modern Lakehouse Expertise:** Iceberg ACID tables, time travel, and schema evolution demonstrate cutting-edge data engineering
- **Multi-Engine Integration:** Spark, Glue, Athena, Presto show breadth across compute engines
- **Production Operations:** Table maintenance, governance, cost optimization, and monitoring reflect real-world platform experience
- **Security & Compliance:** Lake Formation, encryption, and audit logging show enterprise-readiness

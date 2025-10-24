# Project 16 · Advanced Data Lake & Analytics Platform

## 📌 Overview
Design and operate a multi-zone data lake that ingests raw, curated, and trusted data tiers with automated governance. The solution covers data ingestion, cataloging, schema evolution, and lakehouse-style analytics optimized for both batch and streaming workloads.

## 🏗️ Architecture Highlights
- **Multi-account landing zone** with separate production, staging, and sandbox environments connected by AWS Lake Formation.
- **Bronze/Silver/Gold zones** stored in Amazon S3 buckets with lifecycle rules and object versioning.
- **Metadata control plane** using AWS Glue Data Catalog and Apache Atlas for lineage capture.
- **Query and processing layer** powered by Amazon Athena, Apache Spark on EMR, and Apache Hudi/Delta Lake tables for ACID transactions.
- **Streaming enrichment** using Amazon Kinesis Data Streams + AWS Lambda for near-real-time upserts.
- **Observability** via AWS CloudWatch dashboards, Prometheus exporters for Spark jobs, and automated data quality alerts in Slack.

```
+-------------+      +-------------------+      +----------------+      +-------------------+
|  Sources    | ---> | Ingestion Landing | ---> | Data Lake Zones| ---> | Consumption Layer |
| (DB, APIs)  |      | (Kinesis, DMS)    |      | Bronze/Silver  |      | (Athena, EMR)     |
+-------------+      +-------------------+      +----------------+      +-------------------+
        ^                                                                                 |
        |                                                                                 v
        +-------------------- Governance, Catalog, Lineage -------------------------------+
```

## 🚀 Implementation Steps
1. **Provision storage** with Terraform modules that create versioned S3 buckets, IAM policies, and Glue databases per zone.
2. **Configure security perimeter** using Lake Formation permissions, column-level access policies, and CloudTrail logging.
3. **Deploy ingestion pipelines** using AWS DMS for databases and Kinesis Data Firehose for streaming events.
4. **Build ETL workflows** on AWS Step Functions orchestrating PySpark jobs on EMR with automated retries and cost controls.
5. **Enable ACID transactions** by writing curated datasets into Hudi tables, exposed via Athena and EMR for analytics.
6. **Automate data quality** checks using Great Expectations executed as part of the Step Functions workflow.
7. **Publish dashboards and lineage** into QuickSight and Atlas, with nightly exports to Confluence for stakeholders.

## 🧩 Key Components
```python
# projects/16-data-lake-analytics/jobs/bronze_to_silver.py
from pyspark.sql import SparkSession
from great_expectations.dataset.sparkdf_dataset import SparkDFDataset

spark = SparkSession.builder.appName("bronze-to-silver").getOrCreate()

raw_df = spark.read.json("s3://portfolio-bronze/orders/date={{ds}}/")
validated = SparkDFDataset(raw_df)

results = validated.expect_column_values_to_not_be_null("order_id")
if not results.success:
    raise ValueError("Data quality failure: null order_id detected")

enriched_df = raw_df.withColumn("order_total_usd", raw_df.order_total * raw_df.fx_rate)

enriched_df.write.format("hudi").options(
    **{
        "hoodie.table.name": "orders_silver",
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.recordkey.field": "order_id",
        "hoodie.datasource.write.precombine.field": "updated_at",
        "hoodie.datasource.hive_sync.enable": "true",
        "hoodie.datasource.hive_sync.table": "orders_silver",
    }
).mode("append").save("s3://portfolio-silver/orders/")
```

## 🛡️ Fail-safes & Operations
- **Blueprinted rollbacks** using S3 object versioning and Hudi time-travel queries to revert corrupted loads.
- **Schema drift detection** alerts triggered by Glue crawlers feeding into EventBridge rules.
- **Cost guardrails** with AWS Budgets and EMR managed scaling policies to enforce spending limits.
- **Disaster recovery** playbook replicating curated zones to a secondary region using S3 Cross-Region Replication.

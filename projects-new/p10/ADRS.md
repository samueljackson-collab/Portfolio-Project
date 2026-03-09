# Architecture Decision Records

## ADR-001: Apache Iceberg vs Delta Lake vs Apache Hudi
- **Context:** Need ACID lakehouse with time travel, schema evolution, and multi-engine support
- **Decision:** Use Apache Iceberg
- **Alternatives:** Delta Lake (Databricks-centric), Apache Hudi (complex), plain Parquet (no ACID)
- **Pros:** Engine-agnostic (Spark/Trino/Athena), mature time travel, hidden partitioning, AWS Glue integration
- **Cons:** Newer than Hive, requires learning curve
- **Consequences:** Standardize on Iceberg format; train team; monitor ecosystem maturity
- **Revisit:** If Delta Lake adds better multi-engine support or Hudi simplifies

## ADR-002: Write Engine (AWS Glue vs Spark on EMR vs EMR on EKS)
- **Context:** Need scalable, cost-effective Spark execution for ETL workloads
- **Decision:** Use AWS Glue for managed ETL, EMR on EKS for custom Spark jobs
- **Alternatives:** EMR clusters (less elastic), Athena CTAS (limited transforms), Lambda (not suitable for large data)
- **Pros:** Glue serverless for simple ETL, EKS for complex logic with spot instances
- **Cons:** Glue debugging harder than EMR, EKS requires cluster management
- **Consequences:** Use Glue for 80% of jobs; EKS for ML feature engineering and complex aggregations
- **Revisit:** If Glue adds better debugging or cost becomes prohibitive

## ADR-003: Partitioning Strategy (Date-based vs Hash vs Z-Order)
- **Context:** Need query performance optimization with partition pruning
- **Decision:** Use date-based partitioning (year/month or date) for time-series data; z-ordering for hot columns
- **Alternatives:** Hash partitioning (less intuitive), no partitioning (slow), multi-column partitioning (too granular)
- **Pros:** Natural query patterns (filter by date range), easy to understand, good pruning
- **Cons:** Skew possible for low-cardinality dates
- **Consequences:** Partition all silver/gold tables by date; z-order on category/customer_id within partitions
- **Revisit:** If query patterns shift to non-temporal filters

## ADR-004: Catalog Choice (AWS Glue vs Hive Metastore vs Iceberg REST Catalog)
- **Context:** Need metadata catalog integrated with AWS services
- **Decision:** Use AWS Glue Data Catalog
- **Alternatives:** Self-hosted Hive Metastore (operational burden), Iceberg REST catalog (immature)
- **Pros:** Managed service, native Athena/Glue integration, Lake Formation support, versioned
- **Cons:** AWS lock-in, API rate limits for heavy metadata operations
- **Consequences:** Accept AWS dependency; monitor API throttling; use batch catalog updates
- **Revisit:** If Iceberg REST catalog matures or multi-cloud requirement emerges

## ADR-005: Concurrency Model (Optimistic vs Pessimistic Locking)
- **Context:** Multiple writers/readers accessing same tables
- **Decision:** Rely on Iceberg's optimistic concurrency control with snapshot isolation
- **Alternatives:** Pessimistic locking (reduces parallelism), serialized writes (bottleneck)
- **Pros:** High parallelism, readers never blocked, atomic commits
- **Cons:** Write conflicts possible (retry needed), complex conflict resolution for high-frequency updates
- **Consequences:** Implement retry logic in Spark jobs; partition writes by time to reduce conflicts
- **Revisit:** If write conflict rate > 5%

## ADR-006: Retention and Time-Travel Policy
- **Context:** Balance query-ability of historical data with storage costs
- **Decision:** Retain snapshots for 7 days, data files for 90 days in silver/gold; 30 days in bronze
- **Alternatives:** Shorter retention (less auditability), longer retention (higher cost), Glacier archival (slower access)
- **Pros:** Supports weekly rollbacks and monthly audits; controls storage growth
- **Cons:** Cannot time-travel beyond 7 days
- **Consequences:** Schedule snapshot expiry and vacuum jobs; document retention in SLAs
- **Revisit:** If compliance requires longer retention or costs exceed budget

## ADR-007: Query Engine Strategy (Athena vs Presto/Trino Self-Hosted)
- **Context:** Need ad-hoc query capability for analysts and BI tools
- **Decision:** Use Athena as primary; self-hosted Presto for power users with complex queries
- **Alternatives:** Athena-only (limited concurrency), Redshift Spectrum (expensive), Presto-only (operational burden)
- **Pros:** Athena serverless and cost-effective for most use cases; Presto for optimization and advanced features
- **Cons:** Maintain two query paths; Presto requires cluster management
- **Consequences:** Default to Athena; provide Presto for ML teams and heavy analysts; monitor cost split
- **Revisit:** If Athena v3 adds sufficient features to deprecate Presto

# P10 Architecture Diagrams

## End-to-End Data Flow
```mermaid
graph LR
    subgraph Sources
      RAW[Raw Data Sources]
    end
    subgraph Bronze
      S3B[(S3 Bronze Bucket)]
      ICEB[Iceberg Bronze Tables]
    end
    subgraph Silver
      S3S[(S3 Silver Bucket)]
      ICES[Iceberg Silver Tables]
    end
    subgraph Gold
      S3G[(S3 Gold Bucket)]
      ICEG[Iceberg Gold Tables]
    end
    subgraph Consumption
      ATH[Athena]
      PRESTO[Presto/Trino]
      BI[BI Tools]
      ML[ML Pipelines]
    end
    RAW --> S3B
    S3B --> ICEB
    ICEB --> ICES
    ICES --> S3S
    ICES --> ICEG
    ICEG --> S3G
    ICEG --> ATH
    ICEG --> PRESTO
    ATH --> BI
    PRESTO --> ML
```
**Explanation:** Raw data lands in bronze S3 bucket and is written to bronze Iceberg tables by Spark/Glue jobs. Cleansing transforms bronze to silver, and aggregation creates gold tables. Multiple query engines (Athena, Presto, Trino) access gold tables for analytics and BI. Medallion architecture ensures data quality improves through each zone.

## Table Lifecycle
```mermaid
graph TB
    WRITE[Spark/Glue Write]
    DATA[Data Files: Parquet]
    MANIFEST[Manifest Files]
    SNAP[Snapshot Metadata]
    CATALOG[Glue Catalog]
    COMPACT[Compaction Job]
    EXPIRE[Snapshot Expiry]
    ORPHAN[Orphan File Cleanup]

    WRITE --> DATA
    WRITE --> MANIFEST
    MANIFEST --> SNAP
    SNAP --> CATALOG
    DATA --> COMPACT
    COMPACT --> DATA
    SNAP --> EXPIRE
    DATA --> ORPHAN
```
**Explanation:** Writes create Parquet data files and manifests tracking file locations. Snapshots provide point-in-time table versions registered in Glue Catalog. Maintenance jobs compact small files, expire old snapshots per retention policy, and remove orphan files not referenced by any snapshot.

## Governance Topology
```mermaid
graph TB
    subgraph Users
      ANALYST[Data Analyst]
      SCI[Data Scientist]
      ENG[Data Engineer]
    end
    subgraph LakeFormation
      PERMS[Permissions Manager]
      ROWFILT[Row-Level Filters]
      COLFILT[Column-Level Filters]
      AUDIT[Audit Logs]
    end
    subgraph Catalog
      GLUE[Glue Data Catalog]
      TABLES[Iceberg Tables]
    end
    subgraph Data
      S3[S3 Buckets]
      KMS[KMS Encryption]
    end

    ANALYST --> PERMS
    SCI --> PERMS
    ENG --> PERMS
    PERMS --> ROWFILT
    PERMS --> COLFILT
    ROWFILT --> GLUE
    COLFILT --> GLUE
    GLUE --> TABLES
    TABLES --> S3
    S3 --> KMS
    PERMS --> AUDIT
```
**Explanation:** Lake Formation enforces fine-grained access control via row/column filters. Users request access through RBAC; filters apply transparently in Athena/Presto queries. All data access logged for compliance. Glue Catalog stores table metadata; S3 stores encrypted data.

## Multi-Engine Concurrency
```mermaid
graph LR
    subgraph Writers
      SPARK[Spark Job]
      GLUE[Glue ETL]
    end
    subgraph Readers
      ATH[Athena]
      PRESTO[Presto]
      TRINO[Trino]
    end
    subgraph Iceberg
      SNAP[Snapshot Isolation]
      OPTLOCK[Optimistic Concurrency]
    end
    SPARK --> SNAP
    GLUE --> SNAP
    SNAP --> OPTLOCK
    OPTLOCK --> ATH
    OPTLOCK --> PRESTO
    OPTLOCK --> TRINO
```
**Explanation:** Iceberg provides snapshot isolation allowing concurrent reads and writes. Writers create new snapshots atomically; readers use consistent snapshot view. Optimistic concurrency control handles write conflicts via retry. Multiple engines (Spark, Athena, Presto, Trino) can safely access same tables simultaneously.

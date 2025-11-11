# Backend Data & Snowflake Engineer - Comprehensive Glossary

## Purpose
This glossary covers all data engineering, Snowflake, ETL, and big data terminology for the T-Mobile Backend Data & Snowflake Engineer role. Use as quick reference during study and interviews.

---

## A

**ACID (Atomicity, Consistency, Isolation, Durability)**
- Properties guaranteeing reliable database transactions
- Atomicity: All-or-nothing (transaction fully completes or fully rolls back)
- Consistency: Data remains in valid state
- Isolation: Concurrent transactions don't interfere
- Durability: Committed data survives system failures
- Snowflake provides ACID compliance

**Aggregate Function**
- SQL function operating on multiple rows, returning single value
- Examples: SUM(), COUNT(), AVG(), MIN(), MAX()
- Used with GROUP BY clause
- Window functions extend this concept

**Apache Airflow**
- Open-source workflow orchestration platform
- Defines workflows as DAGs (Directed Acyclic Graphs)
- Python-based task definitions
- Features: Scheduling, retries, monitoring, dependencies

**Apache Spark**
- Distributed computing framework for big data processing
- In-memory processing (faster than Hadoop MapReduce)
- APIs: Scala, Python (PySpark), Java, R
- Components: Spark Core, Spark SQL, Spark Streaming, MLlib

**Auto-Suspend (Snowflake)**
- Feature that automatically stops virtual warehouse after period of inactivity
- Default: 10 minutes
- Saves compute costs (no charges when suspended)
- Set with: `ALTER WAREHOUSE ... SET AUTO_SUSPEND = 600` (seconds)

**Auto-Resume (Snowflake)**
- Feature that automatically starts suspended warehouse when query submitted
- Transparent to users (query just takes few extra seconds to start)
- Prevents "warehouse not running" errors

**Avro**
- Row-based data serialization format (Apache)
- Schema stored with data (self-describing)
- Compact binary format
- Common in Kafka, Hadoop ecosystems

---

## B

**Batch Processing**
- Processing large volumes of data at scheduled intervals
- Example: Nightly ETL loading previous day's transactions
- Contrasts with: Streaming (real-time processing)
- Tools: Spark, Airflow, SSIS

**Broadcast Join**
- Spark optimization for joining small table to large table
- Small table copied to all worker nodes (broadcast)
- Avoids expensive shuffle operation
- Example: `df_large.join(broadcast(df_small), "key")`

---

## C

**CDC (Change Data Capture)**
- Technique to identify and capture changes in source data
- Methods: Timestamp-based, trigger-based, log-based (reading transaction logs)
- Enables incremental ETL (only process changed records)
- Example: Only load orders modified since last run

**Clustering Key (Snowflake)**
- Column(s) used to organize micro-partitions for better pruning
- Similar to index but automatic and different implementation
- Best for: Large tables (>1TB), commonly filtered columns
- Example: `ALTER TABLE orders CLUSTER BY (order_date)`

**Columnar Storage**
- Data stored column-by-column (not row-by-row)
- Benefits: Better compression, faster analytics queries (read only needed columns)
- Drawbacks: Slower inserts/updates
- Used by: Snowflake, Parquet, Redshift, BigQuery

**Compute (Snowflake)**
- Virtual warehouse processing power
- Scales: XS, S, M, L, XL, 2XL, 3XL, 4XL (doubles with each size)
- Billed per-second when running
- Separate from storage (architecture benefit)

**COPY INTO (Snowflake)**
- Command to bulk load data from files into tables
- Supports: CSV, JSON, Avro, Parquet, ORC, XML
- Stages: Internal or external (S3, Azure Blob, GCS)
- Example: `COPY INTO orders FROM @my_stage/orders.csv FILE_FORMAT = (TYPE = CSV)`

**CTE (Common Table Expression)**
- Temporary named result set in SQL query
- Defined with WITH clause
- Improves readability and modularity
- Example: `WITH recent_orders AS (SELECT * FROM orders WHERE date > '2024-01-01') SELECT ...`

---

## D

**DAG (Directed Acyclic Graph)**
- Workflow structure with tasks and dependencies
- Directed: Tasks have defined order (A → B → C)
- Acyclic: No loops (can't go B → C → B)
- Used in: Airflow, Spark

**Data Lake**
- Centralized repository storing raw data at any scale
- Schema-on-read (structure applied when reading)
- Supports: Structured, semi-structured, unstructured data
- Technologies: S3, Azure Data Lake, Google Cloud Storage

**Data Mart**
- Subset of data warehouse focused on specific business area
- Example: Sales data mart, HR data mart
- Optimized for department's needs
- Often built from data warehouse

**Data Pipeline**
- Series of steps processing data from source to destination
- Stages: Extract → Transform → Load (ETL) or Extract → Load → Transform (ELT)
- Orchestrated by: Airflow, Azure Data Factory, AWS Glue
- Example: S3 → Spark → Snowflake → Tableau

**Data Warehouse**
- Centralized repository optimized for analytics
- Schema-on-write (structure defined before loading)
- OLAP workloads (aggregations, reporting)
- Examples: Snowflake, Redshift, BigQuery, Synapse

**DataFrame (Spark/Pandas)**
- Tabular data structure (rows and columns)
- Spark: Distributed, immutable, lazily evaluated
- Pandas: In-memory, single-machine
- Operations: filter(), select(), groupBy(), join()

**Dimension Table**
- Descriptive reference data in star/snowflake schema
- Contains attributes (customer name, address, product category)
- Typically smaller than fact tables
- Joined to fact tables via foreign keys

---

## E

**ELT (Extract, Load, Transform)**
- Data pipeline pattern: Load raw data first, transform in warehouse
- Benefits: Leverage warehouse's compute power, maintain raw data
- Snowflake excels at ELT (powerful compute, separation of storage/compute)
- Contrasts with: ETL (transform before loading)

**ETL (Extract, Transform, Load)**
- Traditional data pipeline pattern: Transform before loading
- Benefits: Load only clean data, less storage in warehouse
- Tools: Informatica, Talend, SSIS, custom Python/Spark
- Contrasts with: ELT

**Executor (Spark)**
- Worker process running tasks on data partitions
- Multiple executors run in parallel across cluster
- Configured: Number of executors, cores per executor, memory per executor
- Example: 10 executors × 4 cores = 40 tasks in parallel

---

## F

**Fact Table**
- Central table in star/snowflake schema containing measurements
- Example: Sales fact (quantity, amount, discount)
- Large (millions/billions of rows)
- Foreign keys to dimension tables
- Grain: Level of detail (e.g., one row per transaction)

**File Format (Snowflake)**
- Named object defining how to parse files
- Properties: Delimiter, compression, null string, date format
- Example: `CREATE FILE FORMAT my_csv TYPE = CSV FIELD_DELIMITER = ',' SKIP_HEADER = 1`

---

## G

**Grain (Data Modeling)**
- Level of detail in fact table
- Example: Transaction grain = one row per line item, daily grain = one row per day
- Consistent grain critical for accurate aggregations
- Lower grain = more rows but more flexibility

---

## I

**Idempotent**
- Operation that produces same result no matter how many times executed
- Critical for ETL reliability (can safely rerun)
- Example: `DELETE WHERE date = '2024-01-01'; INSERT ... ` (idempotent) vs. `INSERT ...` alone (not idempotent, creates duplicates)

**Incremental Load**
- Loading only new/changed records since last run
- Methods: Timestamp-based, CDC, watermarks
- Benefits: Faster, less resource-intensive than full load
- Example: `WHERE updated_at > '2024-01-01 00:00:00'`

---

## J

**JSON (JavaScript Object Notation)**
- Lightweight text-based data format
- Structure: Key-value pairs, nested objects, arrays
- Human-readable
- Snowflake: Native support with VARIANT data type, parsing functions

**Join (SQL)**
- Combining rows from two or more tables based on related column
- Types: INNER, LEFT, RIGHT, FULL OUTER, CROSS
- Example: `SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id`

---

## K

**Kimball Methodology**
- Data warehouse design approach (Ralph Kimball)
- Star schema preferred (denormalized dimensions)
- Bottom-up: Build data marts first, integrate later
- Focus: Business process, user-friendliness
- Alternative: Inmon methodology (normalized, top-down)

---

## L

**Lazy Evaluation (Spark)**
- Transformations not executed until action called
- Benefits: Optimizes execution plan, avoids unnecessary computation
- Transformations: filter(), map(), groupBy() (lazy)
- Actions: collect(), count(), show(), write() (trigger execution)

**LDP (Label Distribution Protocol)** *(Note: Typically networking term, but included for completeness)*
- MPLS protocol (see Network glossary for details)

---

## M

**Materialized View**
- Pre-computed query results stored as table
- Automatically refreshed when base tables change
- Benefits: Fast query performance, especially for complex aggregations
- Snowflake: `CREATE MATERIALIZED VIEW daily_sales AS SELECT ...`

**Metadata**
- Data about data
- Examples: Table schema, column data types, row count, last modified date
- Snowflake stores in: INFORMATION_SCHEMA, ACCOUNT_USAGE
- Critical for: Data catalog, lineage, discovery

**Micro-Partition (Snowflake)**
- Snowflake's internal storage unit (~16MB compressed)
- Immutable (once written, never changed)
- Columnar format
- Automatic: No user configuration required
- Pruning: Skip reading irrelevant partitions based on metadata

**Multi-Cluster Warehouse (Snowflake)**
- Warehouse that automatically scales out (adds clusters) under load
- Example: 1-10 clusters, adds clusters when query queue builds
- Benefits: Handle concurrency spikes, maintain performance
- Costs: More clusters = higher credit consumption

---

## N

**Normalization**
- Database design technique to reduce redundancy
- Normal forms: 1NF, 2NF, 3NF, BCNF
- Benefits: Data integrity, less storage
- Drawbacks: More joins (slower analytics queries)
- Data warehouses often denormalized (opposite)

**NULL**
- Special SQL value representing absence of data
- NOT the same as: Empty string, zero, false
- Handling: IS NULL, IS NOT NULL, COALESCE(), IFNULL()

---

## O

**OLAP (Online Analytical Processing)**
- Workload optimized for complex queries and aggregations
- Characteristics: Read-heavy, large datasets, historical data
- Example: "Total sales by region by quarter for last 5 years"
- Databases: Snowflake, Redshift, BigQuery (columnar storage)

**OLTP (Online Transaction Processing)**
- Workload optimized for fast, frequent transactions
- Characteristics: Write-heavy, small transactions, current data
- Example: "Insert new order for customer ID 12345"
- Databases: PostgreSQL, MySQL, SQL Server (row-based storage)

**Orchestration**
- Coordinating multiple tasks/services in data pipeline
- Tools: Airflow, Azure Data Factory, AWS Step Functions
- Features: Scheduling, dependencies, retries, monitoring

---

## P

**Pandas**
- Python library for data manipulation and analysis
- Core object: DataFrame (tabular data)
- Operations: Read CSV/SQL, filter, groupby, merge, pivot
- Single-machine (contrasts with Spark's distributed processing)

**Parquet**
- Columnar storage file format (Apache)
- Highly compressed, efficient for analytics
- Schema stored with data
- Widely used: Spark, Snowflake, Redshift Spectrum, Athena

**Partition (Data)**
- Dividing large dataset into smaller chunks
- Benefits: Parallelism, pruning (skip irrelevant partitions)
- Spark: Distributed across workers
- Parquet: Files partitioned by column (e.g., year=2024/month=01/)

**Pipeline**
- See Data Pipeline

**Primary Key**
- Column(s) uniquely identifying each row
- Constraints: Unique, not null
- Example: customer_id in customers table
- Snowflake: Supports PRIMARY KEY but doesn't enforce (informational only)

**Pruning (Snowflake)**
- Skipping micro-partitions that don't contain relevant data
- Based on: WHERE clause predicates, clustering keys
- Dramatically improves query performance
- View in Query Profile: "Partitions Scanned vs. Total"

**PySpark**
- Python API for Apache Spark
- Write Spark jobs in Python (vs. Scala or Java)
- Example: `df = spark.read.parquet("s3://bucket/data"); df.filter(df.amount > 100).show()`

---

## Q

**Query Profile (Snowflake)**
- Visual representation of query execution
- Shows: Execution time breakdown, data scanned, spilling, bottlenecks
- Access: Web UI → History → Click query ID
- Critical for: Performance tuning, troubleshooting

---

## R

**RBAC (Role-Based Access Control)**
- Security model based on roles, not individual users
- Example: Analyst role can read, Admin role can write
- Snowflake: Hierarchical roles (role can inherit from other roles)
- Commands: GRANT, REVOKE

**RDD (Resilient Distributed Dataset)**
- Spark's fundamental data structure (low-level)
- Immutable, distributed, fault-tolerant
- Mostly replaced by DataFrames (higher-level API)
- Use when: Need fine-grained control

**Result Cache (Snowflake)**
- Cache of query results (exact query text match)
- TTL: 24 hours
- Benefits: Instant results, zero compute cost
- Invalidated when: Base tables change

**Row-Level Security**
- Restricting data access at row level based on user/role
- Example: Sales rep sees only their territory's data
- Snowflake: Implemented via secure views with CURRENT_ROLE()

---

## S

**Schema**
- Logical container for database objects (tables, views)
- Hierarchy: Account → Database → Schema → Table
- Example: `sales_db.public.orders`

**SCD (Slowly Changing Dimension)**
- Technique for handling dimension attribute changes over time
- Type 1: Overwrite (no history) - "Update customer address"
- Type 2: Add new row (track history) - Keep old and new address with effective dates
- Type 3: Add new column (limited history) - "Previous_address" column
- Type 2 most common in data warehouses

**Secure View (Snowflake)**
- View that hides underlying table structure and logic
- Definition not visible to users (even SHOW VIEW returns nothing)
- Used for: Row-level security, column masking
- Example: `CREATE SECURE VIEW customer_view AS SELECT * FROM customers WHERE region = CURRENT_ROLE()`

**Shuffle (Spark)**
- Redistributing data across partitions (expensive operation)
- Triggered by: JOIN, GROUP BY, DISTINCT, repartition()
- Involves: Disk writes, network transfer
- Optimization: Broadcast joins, partitioning, coalesce()

**Snowflake**
- Cloud-native data warehouse platform
- Architecture: Storage + Compute separation
- Key features: Auto-scaling, zero-copy cloning, time travel, data sharing
- Clouds: AWS, Azure, GCP

**Snowpipe (Snowflake)**
- Continuous data ingestion service
- Automatically loads files as they arrive in stage
- Event-driven: S3 event notification triggers load
- Benefits: Near real-time loading, hands-off automation

**Spark**
- See Apache Spark

**SQL (Structured Query Language)**
- Standard language for relational databases
- Categories: DDL (CREATE, ALTER), DML (SELECT, INSERT), DCL (GRANT, REVOKE)
- Dialects: ANSI SQL, T-SQL (SQL Server), PL/SQL (Oracle), Snowflake SQL

**Stage (Snowflake)**
- Storage location for data files
- Internal stage: Snowflake-managed storage
- External stage: Customer-managed (S3, Azure Blob, GCS)
- Example: `CREATE STAGE my_s3_stage URL='s3://mybucket/data/' CREDENTIALS=(...)`

**Star Schema**
- Data warehouse design with central fact table surrounded by dimension tables
- Shape: Fact in center, dimensions radiate like star points
- Benefits: Simple queries, BI tool friendly, fast aggregations
- Alternative: Snowflake schema (normalized dimensions)

**Storage (Snowflake)**
- Persistent data storage in cloud object storage
- Pricing: Per TB per month (~$23-40/TB depending on cloud/region)
- Separate from compute (can store 1PB without running queries)

**Streaming**
- Processing data in real-time as it arrives
- Contrasts with: Batch processing
- Tools: Kafka, Spark Streaming, Flink, Kinesis
- Use cases: Fraud detection, real-time dashboards

---

## T

**Time Travel (Snowflake)**
- Access historical data (previous versions)
- Retention: 1 day (Standard), up to 90 days (Enterprise)
- Query historical data: `SELECT * FROM orders AT(TIMESTAMP => '2024-01-01 00:00:00'::timestamp)`
- Restore dropped tables: `UNDROP TABLE orders`

**Transformation**
- Modifying data structure, format, or values
- Examples: Filtering, aggregating, joining, pivoting, cleaning
- ETL: Transform happens before loading
- ELT: Transform happens after loading

**Type Hint (Python)**
- Optional syntax specifying expected data types
- Example: `def process_data(df: pd.DataFrame) -> int:`
- Benefits: Improved code readability, IDE support, type checking
- Not enforced at runtime (Python still dynamically typed)

---

## U

**UNION**
- SQL operator combining results from multiple queries
- UNION: Removes duplicates (implicit DISTINCT)
- UNION ALL: Keeps duplicates (faster)
- Example: `SELECT * FROM orders_2023 UNION ALL SELECT * FROM orders_2024`

**Upsert**
- Combination of UPDATE and INSERT
- If row exists, update; otherwise, insert
- Snowflake: `MERGE INTO target USING source ON ... WHEN MATCHED THEN UPDATE ... WHEN NOT MATCHED THEN INSERT ...`

---

## V

**VARIANT (Snowflake)**
- Semi-structured data type storing JSON, Avro, XML
- Max size: 16MB per value
- Parsing: GET(), FLATTEN(), dot notation
- Example: `SELECT json_data:customer.name FROM events` where json_data is VARIANT

**Virtual Warehouse (Snowflake)**
- Compute cluster for query processing
- Sizes: XS to 4XL (each size doubles previous)
- Multiple warehouses can run simultaneously (no contention)
- Auto-suspend and auto-resume for cost control

**VRF (Virtual Routing and Forwarding)** *(Note: Networking term, see Network glossary)*

---

## W

**Warehouse (Snowflake)**
- See Virtual Warehouse

**Watermark**
- Timestamp tracking last processed record in incremental ETL
- Example: `last_processed_at = '2024-01-01 23:59:59'`
- Next run: `WHERE created_at > '2024-01-01 23:59:59'`
- Stored in: Control table, state file, Airflow XComs

**WHERE Clause**
- SQL clause filtering rows based on condition
- Example: `SELECT * FROM orders WHERE amount > 100`
- Optimization: Push down predicates (filter early in pipeline)

**Window Function**
- SQL function performing calculation across set of rows related to current row
- Examples: ROW_NUMBER(), RANK(), LAG(), LEAD(), SUM() OVER()
- Syntax: `FUNCTION() OVER (PARTITION BY ... ORDER BY ...)`
- Example: `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date)` = Order number per customer

---

## X

**XCom (Airflow)**
- Cross-communication mechanism between Airflow tasks
- Pass small amounts of data (task1 → task2)
- Stored in: Airflow metadata database
- Example: Task1 pushes `last_processed_id`, Task2 pulls it

---

## Z

**Zero-Copy Clone (Snowflake)**
- Instant copy of database/schema/table
- No data duplication (uses metadata pointers)
- Storage cost: Only for changes made post-clone
- Use cases: Dev/test environments, backups, experimentation
- Example: `CREATE DATABASE dev_db CLONE prod_db`

---

## Quick Reference: Snowflake Virtual Warehouse Sizes

| Size | Credits/Hour | Relative Power | Use Case |
|------|--------------|----------------|----------|
| XS | 1 | 1x | Small queries, testing |
| S | 2 | 2x | Light workloads, dashboards |
| M | 4 | 4x | Standard analytics |
| L | 8 | 8x | Heavy queries, ETL |
| XL | 16 | 16x | Very large queries |
| 2XL | 32 | 32x | Extremely large workloads |
| 3XL | 64 | 64x | Rare, specialized |
| 4XL | 128 | 128x | Rare, specialized |

---

## Quick Reference: ETL Design Patterns

| Pattern | Description | When to Use | Example |
|---------|-------------|-------------|---------|
| Full Load | Load entire dataset every time | Small tables, no tracking | `TRUNCATE; INSERT ALL` |
| Incremental (Timestamp) | Load only new/changed records | Tables with updated_at column | `WHERE updated_at > last_run` |
| Incremental (CDC) | Capture changes from transaction log | Large tables, precise tracking | Database triggers, log mining |
| SCD Type 1 | Overwrite old values | Don't need history | `UPDATE SET address = new_address` |
| SCD Type 2 | Add new row with effective dates | Track history | Insert new row, set end_date on old |
| Upsert | Update if exists, insert if not | Maintain current state | `MERGE INTO ...` |

---

## Quick Reference: Data File Formats

| Format | Type | Compression | Use Case | Schema |
|--------|------|-------------|----------|--------|
| CSV | Text | Low | Simple data exchange | No |
| JSON | Text | Low | APIs, semi-structured | No |
| Avro | Binary | High | Schema evolution, Kafka | Yes (stored with data) |
| Parquet | Binary | Very high | Analytics, data lakes | Yes (stored with data) |
| ORC | Binary | Very high | Hadoop/Hive | Yes |

---

## Quick Reference: SQL Window Functions

| Function | Purpose | Example |
|----------|---------|---------|
| ROW_NUMBER() | Unique sequential number | Assign rank, deduplicate |
| RANK() | Rank with gaps for ties | Leaderboard with ties |
| DENSE_RANK() | Rank without gaps | Compact leaderboard |
| LAG() | Access previous row | Compare to previous value |
| LEAD() | Access next row | Compare to next value |
| SUM() OVER() | Running total | Cumulative sales |
| AVG() OVER() | Moving average | 7-day moving average |

Example:
```sql
SELECT
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total,
    AVG(amount) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7day
FROM orders;
```

---

**Last Updated:** 2025-11-11
**For Role:** Backend Data & Snowflake Engineer (T-Mobile)
**Compensation:** $48-56/hr (~$100-117K/year)

**Usage Tips:**
- Use Ctrl+F to quickly find terms
- Cross-reference with expanded cheat sheets for deeper context
- Review Snowflake features thoroughly (core to role)
- Practice SQL window functions (commonly tested)
- Understand ETL patterns (critical for pipeline design)

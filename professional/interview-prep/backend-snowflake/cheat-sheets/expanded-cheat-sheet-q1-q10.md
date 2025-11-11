# Backend Data & Snowflake Engineer - Expanded Cheat Sheet (Q1-Q10)

## Question 1: Snowflake Architecture

**Question:** Explain how Snowflake's architecture differs from traditional databases and why this matters for performance.

**Feynman Explanation:**
Imagine a library where books (storage) and reading rooms (compute) are separate. In traditional databases, they're the same building - if you need more reading space, you have to build a bigger building with more books. Snowflake separates them: storage is like a warehouse where all books live (cheap, unlimited), and compute is like renting reading rooms by the hour (pay only when reading). You can have 100 people reading different books simultaneously by renting 100 rooms, but the books stay in one place. This separation means you can scale compute and storage independently - exactly what data warehouses need.

**Technical Answer:**

**Snowflake's Three-Layer Architecture:**

**1. Storage Layer (Database Storage)**
- Centralized, cloud-based object storage (S3, Azure Blob, GCS)
- Stores all data in compressed, columnar format
- Data organized into **micro-partitions** (~16MB each, immutable)
- Automatic clustering and compression
- Pay only for data stored (monthly)
- **Key point:** All compute accesses same storage (single source of truth)

**2. Compute Layer (Virtual Warehouses)**
- Independent compute clusters (XS, S, M, L, XL, 2XL, 3XL, 4XL)
- Each warehouse is isolated (no resource contention)
- Can scale up (bigger warehouse) or scale out (more warehouses)
- **Auto-suspend:** Stops after inactivity (saves money)
- **Auto-resume:** Starts automatically when query runs
- Pay per-second when running (no queries = no cost)
- **Key point:** Multiple warehouses can query same data simultaneously

**3. Cloud Services Layer (Brain)**
- Query optimization and compilation
- Metadata management (statistics, schemas, security)
- Authentication and access control
- Result caching (query results cached for 24 hours)
- Transaction management
- **Key point:** Fully managed by Snowflake (no tuning needed)

**Why This Matters:**

**Traditional Database (e.g., Oracle, SQL Server):**
```
[Storage + Compute tied together]
- Upgrade database = More storage AND compute (expensive)
- Heavy queries slow down everything (resource contention)
- Scaling requires downtime or complex clustering
- Fixed capacity (provisioned for peak load, wasted during off-hours)
```

**Snowflake:**
```
[Storage] <---> [Virtual Warehouse 1 (ETL)]
              <---> [Virtual Warehouse 2 (Analytics)]
              <---> [Virtual Warehouse 3 (Data Science)]

- Scale storage independently (add 10TB, no compute change)
- Scale compute independently (bigger warehouse for query, doesn't affect storage)
- No resource contention (each workload gets own warehouse)
- Pay only for what you use (warehouses auto-suspend)
- Zero-copy cloning (copy database in seconds, no storage cost until changes made)
```

**Performance Benefits:**

**1. No Indexes Needed**
- Micro-partitions automatically prune (skip irrelevant data)
- Clustering keys (optional) optimize specific queries
- Traditional databases require manual index design

**2. Automatic Caching**
- **Result cache:** Same query returns instantly (24 hour TTL)
- **Warehouse cache:** Remote disk cache (SSD) survives between queries
- **Metadata cache:** Statistics cached in cloud services layer

**3. Instant Scalability**
- Query slow? Increase warehouse size (S → M → L) in seconds
- Need more concurrency? Add more warehouses
- No database restart or migration

**4. Time Travel & Zero-Copy Clone**
- Time Travel: Query historical data (up to 90 days)
- Clone: Instant copy of database for dev/test (no storage cost)
- Traditional databases: Backup/restore takes hours, full storage cost

**Acronym Glossary:**
- **VW** = Virtual Warehouse (compute cluster in Snowflake)
- **XS, S, M, L, XL** = Warehouse sizes (Extra Small to 4X-Large)
- **S3** = Amazon Simple Storage Service (object storage)
- **GCS** = Google Cloud Storage
- **TTL** = Time To Live (how long cached data is valid)
- **SSD** = Solid State Drive (fast storage for caching)
- **OLAP** = Online Analytical Processing (data warehouse queries)
- **OLTP** = Online Transaction Processing (traditional database transactions)

**Practical Example:**
```
Scenario: E-commerce company with two workloads

Workload 1: Nightly ETL (10 PM - 2 AM)
- Load 500GB of new data from various sources
- Heavy transformations, aggregations
- Needs: Large warehouse (XL or 2XL) for speed

Workload 2: Daytime analytics (8 AM - 6 PM)
- 50 analysts running ad-hoc queries
- Lightweight SELECT queries
- Needs: Medium warehouse (M) with auto-scaling

Traditional Database Approach:
- Provision for peak (ETL + Analytics simultaneously)
- ETL slows down daytime queries (resource contention)
- Expensive hardware (always running, even at 3 AM)
- Cost: ~$10K/month (24/7 server + licenses)

Snowflake Approach:
- Virtual Warehouse "ETL_LOAD" (XL size)
  - Runs 10 PM - 2 AM (4 hours)
  - Auto-suspends after 10 minutes idle
  - Cost: 128 credits × 4 hours = 512 credits (~$1,024/month)

- Virtual Warehouse "ANALYTICS" (M size)
  - Runs 8 AM - 6 PM (10 hours)
  - Auto-suspends during lunch/breaks (actual runtime: 7 hours)
  - Cost: 4 credits × 7 hours × 22 workdays = 616 credits (~$1,232/month)

- Storage: 10TB × $23/TB = $230/month

Total Snowflake Cost: ~$2,500/month (75% cheaper than traditional!)

Benefits:
✅ No resource contention (ETL and analytics isolated)
✅ Pay only for actual usage (auto-suspend during idle)
✅ Scale each workload independently (XL for ETL, M for analytics)
✅ Zero downtime (add/remove warehouses without restart)
```

**Common Pitfalls:**
1. **Forgetting to set auto-suspend:** Warehouse runs 24/7, massive bill
2. **Using one warehouse for everything:** Resource contention defeats Snowflake's purpose
3. **Over-provisioning warehouse size:** Start small (S or M), scale up if needed
4. **Not leveraging result cache:** Running same query repeatedly wastes credits
5. **Ignoring clustering:** Large tables (>1TB) benefit from clustering keys
6. **Not using zero-copy cloning:** Copying data wastes storage and time
7. **Query runs forever:** No query timeout set, warehouse never suspends

**Interview Follow-Up Questions to Expect:**
- "What's a micro-partition in Snowflake?" (16MB immutable chunk of compressed columnar data)
- "How does Snowflake achieve zero-copy cloning?" (Metadata pointers, not actual data copy)
- "What's the difference between result cache and warehouse cache?" (Result = query result, warehouse = data cache on SSD)
- "When would you use a larger warehouse vs more warehouses?" (Larger = faster queries, more = more concurrency)

---

## Question 2: Query Optimization

**Question:** A Snowflake query is taking 10 minutes. Walk me through how you'd optimize it.

**Feynman Explanation:**
Optimizing a slow query is like debugging why your car trip took too long. You check: Did you take the wrong route? (Bad SQL logic) Was there traffic? (Too much data scanned) Did you stop for gas too many times? (Inefficient joins) Was your car too small? (Warehouse undersized) Snowflake's Query Profile is like a trip recorder that shows exactly where time was spent - you just need to read it and fix the bottleneck.

**Technical Answer:**

**Step-by-Step Optimization Process:**

**Step 1: Check Query Profile**
```sql
-- Run your slow query, then check profile
-- In Snowflake Web UI: Click "Query ID" → "Query Profile"

-- Or via SQL:
SELECT *
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE QUERY_ID = '<your-query-id>';
```

**Query Profile shows:**
- **Execution time breakdown** (compilation, execution, result fetch)
- **Nodes** (scan, join, aggregate, sort)
- **Data scanned** (how many micro-partitions pruned?)
- **Spilling** (data too big for memory, spills to disk - BAD)

**Step 2: Identify Bottleneck**

**Common Issues:**

**Issue A: Too Much Data Scanned (Partition Pruning)**
```
Symptom: "Partitions Scanned: 10,000 / Partitions Total: 10,000" (100% scanned)
Problem: No pruning - Snowflake scanned entire table
```

**Fix: Add predicates or clustering key**
```sql
-- Bad: Scans entire table
SELECT * FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31';

-- Good: If clustered by order_date, only scans Jan partitions
-- (same query, but first add clustering key)
ALTER TABLE orders CLUSTER BY (order_date);

-- Check clustering quality
SELECT SYSTEM$CLUSTERING_INFORMATION('orders', '(order_date)');
-- Look for "clustering_depth" (lower is better, <5 ideal)
```

**Issue B: Spilling to Disk**
```
Symptom: "Bytes Spilled to Local Storage: 50GB"
Problem: Query needs more memory than warehouse provides
```

**Fix: Increase warehouse size**
```sql
-- Temporarily increase warehouse
ALTER WAREHOUSE my_warehouse SET WAREHOUSE_SIZE = 'LARGE';

-- Run query again (more memory available)

-- Reset after query
ALTER WAREHOUSE my_warehouse SET WAREHOUSE_SIZE = 'MEDIUM';
```

**Issue C: Inefficient Joins**
```
Symptom: Query Profile shows huge join node with long execution time
Problem: Join order wrong, or joining on non-unique keys
```

**Fix: Rewrite join or add filters**
```sql
-- Bad: Joins two large tables without filtering
SELECT o.*, c.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- Good: Filter before joining
SELECT o.*, c.*
FROM orders o
WHERE o.order_date >= '2024-01-01'  -- Filter first!
JOIN customers c ON o.customer_id = c.customer_id;

-- Even better: Use CTE to materialize filtered result
WITH recent_orders AS (
  SELECT * FROM orders WHERE order_date >= '2024-01-01'
)
SELECT o.*, c.*
FROM recent_orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

**Issue D: Expensive Aggregations**
```
Symptom: Aggregate node takes 80% of query time
Problem: GROUP BY on high-cardinality column
```

**Fix: Limit aggregation scope**
```sql
-- Bad: Aggregate entire history
SELECT customer_id, SUM(amount)
FROM orders
GROUP BY customer_id;

-- Good: Aggregate recent data only (if that's all you need)
SELECT customer_id, SUM(amount)
FROM orders
WHERE order_date >= CURRENT_DATE - 90  -- Last 90 days only
GROUP BY customer_id;
```

**Issue E: Suboptimal SQL Patterns**
```sql
-- Bad: DISTINCT (expensive)
SELECT DISTINCT customer_id FROM orders;

-- Good: Use GROUP BY instead (often faster)
SELECT customer_id FROM orders GROUP BY customer_id;

-- Bad: SELECT * (scans all columns)
SELECT * FROM orders WHERE order_id = 12345;

-- Good: Select only needed columns (columnar storage benefit)
SELECT order_id, customer_id, amount FROM orders WHERE order_id = 12345;

-- Bad: Implicit UNION (has DISTINCT overhead)
SELECT customer_id FROM orders_2023
UNION
SELECT customer_id FROM orders_2024;

-- Good: UNION ALL (no deduplication)
SELECT customer_id FROM orders_2023
UNION ALL
SELECT customer_id FROM orders_2024;
```

**Step 3: Check Statistics**
```sql
-- See query details
SELECT
    query_id,
    query_text,
    total_elapsed_time / 1000 AS seconds,
    bytes_scanned / POWER(1024, 3) AS gb_scanned,
    partitions_scanned,
    partitions_total
FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE query_id = '<your-query-id>';
```

**Step 4: Implement Clustering (if appropriate)**
```sql
-- For large tables (>1TB) with common filter columns
ALTER TABLE orders CLUSTER BY (order_date, customer_id);

-- Monitor clustering depth (want <5)
SELECT SYSTEM$CLUSTERING_INFORMATION('orders', '(order_date, customer_id)');

-- Check clustering ratio
SELECT SYSTEM$CLUSTERING_RATIO('orders', '(order_date, customer_id)');
-- 100 = perfectly clustered, 0 = random
```

**Step 5: Use Materialized Views (for repeated queries)**
```sql
-- If same aggregation runs daily, materialize it
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
    DATE(order_date) AS sale_date,
    SUM(amount) AS total_sales,
    COUNT(*) AS order_count
FROM orders
GROUP BY DATE(order_date);

-- Query is now instant (pre-computed)
SELECT * FROM daily_sales WHERE sale_date = '2024-01-15';
```

**Acronym Glossary:**
- **CTE** = Common Table Expression (WITH clause in SQL)
- **TTL** = Time To Live (cache expiration)
- **GB** = Gigabyte (1024 megabytes)
- **SSD** = Solid State Drive (fast disk for caching)
- **DISTINCT** = SQL keyword to remove duplicates (expensive operation)
- **GROUP BY** = SQL aggregation clause
- **JOIN** = Combine rows from two tables based on related column

**Practical Example:**
```
Scenario: Daily sales report query taking 10 minutes

Original Query:
SELECT
    c.customer_name,
    c.customer_segment,
    c.customer_region,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(o.amount) AS total_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_name, c.customer_segment, c.customer_region
ORDER BY total_sales DESC;

Problem Analysis (Query Profile):
1. Partitions Scanned: 100,000 / 100,000 (100% - BAD!)
2. Bytes Scanned: 500 GB
3. Spilling: 20 GB spilled to disk
4. Join node: 6 minutes
5. Aggregate node: 3 minutes
6. Warehouse: Medium (4 credits/hour)

Optimization Steps:

Step 1: Add date filter (business only needs last 30 days)
WITH recent_orders AS (
  SELECT customer_id, order_id, amount
  FROM orders
  WHERE order_date >= CURRENT_DATE - 30  -- Filter first!
)
SELECT
    c.customer_name,
    c.customer_segment,
    c.customer_region,
    COUNT(DISTINCT ro.order_id) AS order_count,
    SUM(ro.amount) AS total_sales
FROM recent_orders ro
JOIN customers c ON ro.customer_id = c.customer_id
GROUP BY c.customer_name, c.customer_segment, c.customer_region
ORDER BY total_sales DESC;

Result: 10 min → 3 min (70% improvement)
Partitions Scanned: 3,000 / 100,000 (97% pruned!)

Step 2: Add clustering key
ALTER TABLE orders CLUSTER BY (order_date);
-- Wait for clustering to complete (automatic background process)

Result: 3 min → 45 seconds (85% improvement)
Partitions Scanned: 900 / 100,000 (better pruning with clustering)

Step 3: Remove unnecessary DISTINCT (order_id is unique)
COUNT(ro.order_id) instead of COUNT(DISTINCT ro.order_id)

Result: 45 sec → 30 seconds (33% improvement)

Step 4: Create materialized view (if query runs daily)
CREATE MATERIALIZED VIEW daily_customer_sales AS
SELECT
    DATE(o.order_date) AS sale_date,
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.customer_region,
    COUNT(o.order_id) AS order_count,
    SUM(o.amount) AS total_sales
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= CURRENT_DATE - 90  -- Keep last 90 days
GROUP BY sale_date, c.customer_id, c.customer_name, c.customer_segment, c.customer_region;

-- Daily query now instant
SELECT * FROM daily_customer_sales
WHERE sale_date = CURRENT_DATE - 1
ORDER BY total_sales DESC;

Result: 30 sec → <1 second (instant from materialized view)

Final Cost:
- Before: 10 min × Medium warehouse = 0.67 credits
- After: <1 sec × Medium warehouse = 0.0003 credits
- Savings: 99.96% reduction in compute cost!
```

**Common Pitfalls:**
1. **Not checking Query Profile:** Guessing instead of diagnosing
2. **Over-clustering:** Too many clustering keys (max 3-4 columns)
3. **Clustering small tables:** Only useful for tables >1TB
4. **Not filtering:** Scanning entire table when only need recent data
5. **Using DISTINCT unnecessarily:** Expensive deduplication
6. **Warehouse too small for workload:** Spilling to disk kills performance
7. **Not using result cache:** Re-running identical query wastes credits

**Interview Follow-Up Questions to Expect:**
- "What's the difference between clustering and partitioning?" (Snowflake auto-partitions into micro-partitions, clustering optimizes within those)
- "When shouldn't you cluster a table?" (Small tables <1TB, high-churn tables)
- "Explain Snowflake's query result cache" (24-hour cache of exact query results)
- "What causes query spilling?" (Not enough memory - increase warehouse size)

---

## Question 3: Data Modeling - Star Schema

**Question:** Design a data warehouse schema for a retail company with 1 billion transactions per year.

**Feynman Explanation:**
A star schema is like organizing a store's sales records. The "fact" table is the receipt (transaction details), and "dimension" tables are the reference books (customer directory, product catalog, store locations). You don't write customer's full address on every receipt - you write customer ID and look up details in the customer directory. This saves space (don't repeat address 1B times) and makes queries fast (join small dimension to large fact). The "star" name comes from the shape: fact table in the center, dimensions radiating out like star points.

**Technical Answer:**

**Star Schema Design:**

**Fact Table (Center of Star):**
```sql
CREATE TABLE fact_sales (
    -- Surrogate key
    sale_id NUMBER AUTOINCREMENT PRIMARY KEY,

    -- Foreign keys to dimensions (integers for fast joins)
    date_key NUMBER NOT NULL,           -- Link to dim_date
    customer_key NUMBER NOT NULL,       -- Link to dim_customer
    product_key NUMBER NOT NULL,        -- Link to dim_product
    store_key NUMBER NOT NULL,          -- Link to dim_store
    promotion_key NUMBER,               -- Link to dim_promotion (nullable if no promo)

    -- Measures (numeric facts to aggregate)
    quantity NUMBER(10,2) NOT NULL,
    unit_price NUMBER(10,2) NOT NULL,
    discount_amount NUMBER(10,2) DEFAULT 0,
    tax_amount NUMBER(10,2) NOT NULL,
    total_amount NUMBER(10,2) NOT NULL,
    cost_amount NUMBER(10,2) NOT NULL,  -- For profit calculation

    -- Degenerate dimension (fact stored in fact table)
    transaction_number VARCHAR(50) NOT NULL,

    -- Audit columns
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

**Dimension Tables (Points of Star):**

**1. Date Dimension (Time intelligence)**
```sql
CREATE TABLE dim_date (
    date_key NUMBER PRIMARY KEY,        -- 20240115 (YYYYMMDD format)
    full_date DATE NOT NULL,            -- 2024-01-15
    day_of_week NUMBER NOT NULL,        -- 1-7 (Monday=1)
    day_name VARCHAR(10) NOT NULL,      -- 'Monday'
    day_of_month NUMBER NOT NULL,       -- 1-31
    day_of_year NUMBER NOT NULL,        -- 1-366
    week_of_year NUMBER NOT NULL,       -- 1-53
    month_number NUMBER NOT NULL,       -- 1-12
    month_name VARCHAR(10) NOT NULL,    -- 'January'
    quarter NUMBER NOT NULL,            -- 1-4
    year NUMBER NOT NULL,               -- 2024
    is_weekend BOOLEAN NOT NULL,        -- TRUE/FALSE
    is_holiday BOOLEAN NOT NULL,        -- TRUE/FALSE
    fiscal_year NUMBER NOT NULL,        -- For fiscal calendar
    fiscal_quarter NUMBER NOT NULL
);
```

**2. Customer Dimension (SCD Type 2 for history tracking)**
```sql
CREATE TABLE dim_customer (
    customer_key NUMBER AUTOINCREMENT PRIMARY KEY,  -- Surrogate key
    customer_id VARCHAR(50) NOT NULL,               -- Natural key (business key)

    -- Customer attributes
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),

    -- Demographics
    birth_date DATE,
    gender VARCHAR(10),

    -- Address
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),

    -- Segmentation
    customer_segment VARCHAR(50),       -- 'Premium', 'Regular', 'Budget'
    loyalty_tier VARCHAR(50),           -- 'Gold', 'Silver', 'Bronze'

    -- SCD Type 2 tracking (Slowly Changing Dimension)
    effective_date DATE NOT NULL,       -- When this version became active
    end_date DATE,                      -- When this version ended (NULL = current)
    is_current BOOLEAN DEFAULT TRUE,    -- TRUE for active version

    -- Audit
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ
);
```

**3. Product Dimension**
```sql
CREATE TABLE dim_product (
    product_key NUMBER AUTOINCREMENT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,     -- SKU

    -- Product info
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    brand VARCHAR(100),

    -- Product hierarchy
    category_level1 VARCHAR(100),               -- 'Electronics'
    category_level2 VARCHAR(100),               -- 'Computers'
    category_level3 VARCHAR(100),               -- 'Laptops'

    -- Attributes
    color VARCHAR(50),
    size VARCHAR(50),
    weight_kg NUMBER(10,2),

    -- Pricing
    list_price NUMBER(10,2),
    cost_price NUMBER(10,2),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    discontinued_date DATE,

    -- Audit
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

**4. Store Dimension**
```sql
CREATE TABLE dim_store (
    store_key NUMBER AUTOINCREMENT PRIMARY KEY,
    store_id VARCHAR(50) NOT NULL UNIQUE,

    -- Store info
    store_name VARCHAR(255) NOT NULL,
    store_type VARCHAR(50),                 -- 'Flagship', 'Regular', 'Outlet'

    -- Location
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    latitude NUMBER(10,6),
    longitude NUMBER(10,6),

    -- Hierarchy
    region VARCHAR(100),                    -- 'Northeast', 'West', etc.
    district VARCHAR(100),

    -- Attributes
    square_footage NUMBER,
    opened_date DATE,
    manager_name VARCHAR(255),

    -- Status
    is_active BOOLEAN DEFAULT TRUE,

    -- Audit
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

**5. Promotion Dimension**
```sql
CREATE TABLE dim_promotion (
    promotion_key NUMBER AUTOINCREMENT PRIMARY KEY,
    promotion_id VARCHAR(50) NOT NULL,

    -- Promotion details
    promotion_name VARCHAR(255),
    promotion_type VARCHAR(50),             -- 'Percentage', 'Fixed Amount', 'BOGO'
    discount_percent NUMBER(5,2),

    -- Validity
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    -- Audit
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Add "No Promotion" record for sales without promotions
INSERT INTO dim_promotion VALUES
    (0, 'NO_PROMO', 'No Promotion', NULL, 0, '1900-01-01', '2099-12-31', CURRENT_TIMESTAMP());
```

**Why Star Schema for 1B Transactions:**

**Benefits:**
1. **Query Performance:** Simple joins (fact → dimension, no dimension → dimension)
2. **BI Tool Friendly:** Tools like Tableau, Power BI optimized for star schema
3. **Intuitive:** Business users understand "sales by date, product, customer"
4. **Aggregation Friendly:** SUM(total_amount) by any dimension is fast
5. **Denormalized Dimensions:** Redundancy in dims is OK (fast reads)

**Example Queries:**

```sql
-- Daily sales by category
SELECT
    d.full_date,
    p.category_level1,
    SUM(f.total_amount) AS total_sales,
    COUNT(*) AS transaction_count,
    AVG(f.total_amount) AS avg_transaction_value
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
JOIN dim_product p ON f.product_key = p.product_key
WHERE d.year = 2024 AND d.month_number = 1
GROUP BY d.full_date, p.category_level1
ORDER BY d.full_date, total_sales DESC;

-- Customer segmentation analysis
SELECT
    c.customer_segment,
    c.loyalty_tier,
    COUNT(DISTINCT f.customer_key) AS customer_count,
    SUM(f.total_amount) AS total_sales,
    AVG(f.total_amount) AS avg_purchase_value
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
WHERE c.is_current = TRUE  -- SCD Type 2: only current records
GROUP BY c.customer_segment, c.loyalty_tier;

-- Store performance by region
SELECT
    s.region,
    s.store_type,
    COUNT(DISTINCT f.store_key) AS store_count,
    SUM(f.total_amount) AS total_sales,
    SUM(f.total_amount - f.cost_amount) AS total_profit
FROM fact_sales f
JOIN dim_store s ON f.store_key = s.store_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = 2024
GROUP BY s.region, s.store_type
ORDER BY total_sales DESC;
```

**Acronym Glossary:**
- **SCD** = Slowly Changing Dimension (handling changes in dimension data over time)
- **Type 1** = Overwrite (no history)
- **Type 2** = Add new row (track history with effective/end dates)
- **Type 3** = Add column (limited history)
- **BI** = Business Intelligence (reporting/analytics tools)
- **ETL** = Extract, Transform, Load (data pipeline process)
- **PK** = Primary Key (unique identifier)
- **FK** = Foreign Key (reference to another table)
- **BOGO** = Buy One Get One (promotion type)
- **SKU** = Stock Keeping Unit (product identifier)

**Practical Example:**
```
Retail Chain: 500 stores, 100K products, 10M customers, 1B transactions/year

Storage Calculation:

Fact Table (fact_sales):
- Columns: ~15 columns × avg 8 bytes = 120 bytes/row
- Rows: 1B transactions/year
- Size: 1B × 120 bytes = 120 GB/year (uncompressed)
- Snowflake compression: ~5:1 = 24 GB/year (compressed)

Dimension Tables:
- dim_date: 3,650 rows (10 years) × 200 bytes = 730 KB
- dim_customer: 10M rows × 500 bytes = 5 GB (with SCD history)
- dim_product: 100K rows × 400 bytes = 40 MB
- dim_store: 500 rows × 400 bytes = 200 KB
- dim_promotion: 1K rows × 200 bytes = 200 KB
- Total dimensions: ~5 GB

Total Storage: ~29 GB/year (tiny!)

Query Performance:
- Query: "Sales by category last 30 days"
- Fact rows scanned: ~83M rows (1B / 12 months)
- With clustering on date_key: Only scans Jan partitions = ~8M rows
- With date filter: Prunes 97% of partitions
- Query time: <10 seconds on Medium warehouse

Comparison to Normalized Schema:
- Normalized: Need 10+ joins (customer → address → city, product → category → subcategory)
- Star: Need 3-4 joins (fact → dimensions)
- Star is 5-10x faster for analytics queries
```

**Common Pitfalls:**
1. **Too many dimensions:** Keep to 5-10 dimensions (more = complex queries)
2. **Not using surrogate keys:** Natural keys (customer ID) change, surrogate keys don't
3. **Putting measures in dimensions:** Quantity/price belong in fact, not dimension
4. **Not handling SCD:** Customer changes address, old reports show wrong data
5. **Missing "Unknown" records:** What if product_key is NULL? Have "Unknown Product" with key -1
6. **Fact table without date:** Every fact should have date dimension (time-series analysis)
7. **Snowflaking dimensions:** Normalizing dims (customer → address table) defeats purpose

**Interview Follow-Up Questions to Expect:**
- "What's the difference between star and snowflake schema?" (Snowflake = normalized dimensions, star = denormalized)
- "When would you use SCD Type 1 vs Type 2?" (Type 1 = don't care about history, Type 2 = track history)
- "What's a degenerate dimension?" (Dimension stored in fact table, like transaction number)
- "How do you handle many-to-many relationships?" (Bridge table or factless fact table)

---

*[Questions 4-10 continue in same format covering Python ETL, PySpark, ETL Patterns, SQL Advanced, Data Loading, Security, and Orchestration]*

**Next Steps:**
1. Review Q1-Q3 thoroughly with hands-on practice
2. Set up Snowflake trial account and implement sample star schema
3. Load data and run example queries
4. Continue to Q4-Q10 for Python/PySpark/ETL topics

**Last Updated:** 2025-11-11
**Role:** Backend Data & Snowflake Engineer (T-Mobile)
**Compensation:** $48-56/hr (~$100-117K/year)

# Backend Data & Snowflake Engineer - Lab Tracking Sheet

## Purpose
Track your progress through all 12 essential labs for Snowflake and data engineering mastery. Check off labs as completed and collect evidence for your portfolio.

---

## 2-Week Lab Schedule Overview

| Week | Focus Area | Labs | Total Hours |
|------|------------|------|-------------|
| Week 1 | Snowflake & SQL Foundations | Labs 01-05 | 21 hours |
| Week 2 | Python ETL & Big Data | Labs 06-12 | 33 hours |

**Total Lab Time:** 54 hours across 2 weeks (~4 hours/day)

---

## Week 1: Snowflake & SQL Foundations

### ☐ Lab 01: Snowflake Setup & Basics
**Time:** 3 hours
**Priority:** 🔴 CRITICAL (Foundation)
**Difficulty:** Easy

**Objectives:**
- [ ] Sign up for Snowflake free trial (30-day, $400 credit)
- [ ] Create virtual warehouse, database, schema
- [ ] Load Snowflake sample datasets (TPC-H, Weather)
- [ ] Run basic SQL queries (SELECT, JOIN, GROUP BY)

**Prerequisites:**
- Email address for Snowflake trial
- Web browser
- Basic SQL knowledge

**Setup Steps:**
1. Go to https://signup.snowflake.com/
2. Choose cloud provider (AWS recommended for trial)
3. Select region close to you
4. Verify email and set password

**Evidence to Collect:**
- [ ] Snowflake account screenshot (showing username, account locator)
- [ ] Screenshot of Worksheets interface
- [ ] Query results from sample data
- [ ] List of created objects (warehouse, database, schema)

**Initial Configuration:**
```sql
-- Create virtual warehouse
CREATE WAREHOUSE my_warehouse
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 300  -- 5 minutes
  AUTO_RESUME = TRUE;

-- Create database and schema
CREATE DATABASE my_database;
CREATE SCHEMA my_database.my_schema;

-- Use Snowflake sample data
USE DATABASE snowflake_sample_data;
USE SCHEMA tpcds_sf10tcl;

-- Test query
SELECT * FROM customer LIMIT 10;
```

**Validation:**
```sql
SHOW WAREHOUSES;
SHOW DATABASES;
SHOW SCHEMAS;
SELECT CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
```

**Common Pitfalls:**
- Forgetting to select warehouse before running query
- Not setting auto-suspend (wastes credits!)
- Using large warehouse for small queries

---

### ☐ Lab 02: Data Modeling (Star Schema)
**Time:** 5 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Medium

**Objectives:**
- [ ] Design star schema for e-commerce data
- [ ] Create fact table (orders) and dimension tables (customers, products, date)
- [ ] Load sample data into tables
- [ ] Write queries answering business questions

**Prerequisites:**
- Lab 01 completed
- Understanding of star schema concepts

**Dimensional Model:**
```
           dim_date
               |
dim_customer ─ fact_sales ─ dim_product
               |
           dim_store
```

**Evidence to Collect:**
- [ ] ERD diagram (draw.io or hand-drawn)
- [ ] DDL scripts (CREATE TABLE statements)
- [ ] Sample data loading scripts
- [ ] Business query examples with results

**DDL Template:**
```sql
-- Fact table
CREATE TABLE fact_sales (
    sale_id NUMBER AUTOINCREMENT PRIMARY KEY,
    date_key NUMBER NOT NULL,
    customer_key NUMBER NOT NULL,
    product_key NUMBER NOT NULL,
    quantity NUMBER(10,2),
    amount NUMBER(10,2),
    cost NUMBER(10,2)
);

-- Dimension tables
CREATE TABLE dim_date (
    date_key NUMBER PRIMARY KEY,
    full_date DATE NOT NULL,
    day_name VARCHAR(10),
    month_name VARCHAR(10),
    quarter NUMBER,
    year NUMBER,
    is_weekend BOOLEAN
);

CREATE TABLE dim_customer (
    customer_key NUMBER AUTOINCREMENT PRIMARY KEY,
    customer_id VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    customer_segment VARCHAR(50)
);

-- Add dim_product, dim_store similarly
```

**Sample Business Queries:**
```sql
-- 1. Total sales by month
SELECT
    d.year,
    d.month_name,
    SUM(f.amount) AS total_sales,
    COUNT(*) AS transaction_count
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month_name
ORDER BY d.year, d.month_name;

-- 2. Top 10 customers by sales
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    SUM(f.amount) AS total_spent
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, customer_name
ORDER BY total_spent DESC
LIMIT 10;

-- 3. Sales by product category and quarter
SELECT
    p.category_level1,
    d.year,
    d.quarter,
    SUM(f.amount) AS total_sales
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY p.category_level1, d.year, d.quarter
ORDER BY d.year, d.quarter, total_sales DESC;
```

**Validation:**
- [ ] Can explain why star schema chosen over snowflake schema
- [ ] Can describe grain of fact table (what does one row represent?)
- [ ] Can write 5+ business queries without looking at notes

---

### ☐ Lab 03: Advanced SQL
**Time:** 4 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Medium

**Objectives:**
- [ ] Practice window functions (ROW_NUMBER, RANK, LAG/LEAD)
- [ ] Use CTEs for complex queries
- [ ] Pivot and unpivot data
- [ ] Parse JSON data with VARIANT type

**Prerequisites:**
- Lab 02 completed
- Star schema with sample data

**Evidence to Collect:**
- [ ] SQL scripts with comments explaining each query
- [ ] Query results screenshots
- [ ] Performance comparison (window function vs subquery)

**Window Functions Examples:**
```sql
-- ROW_NUMBER: Assign unique sequential number
SELECT
    customer_id,
    order_date,
    amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) AS order_number
FROM orders;

-- RANK: Rank with gaps for ties
SELECT
    product_name,
    sales_amount,
    RANK() OVER (ORDER BY sales_amount DESC) AS sales_rank
FROM product_sales;

-- LAG/LEAD: Access previous/next row
SELECT
    order_date,
    sales,
    LAG(sales, 1) OVER (ORDER BY order_date) AS previous_day_sales,
    sales - LAG(sales, 1) OVER (ORDER BY order_date) AS daily_change
FROM daily_sales;

-- Running total
SELECT
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders;

-- Moving average (7-day)
SELECT
    order_date,
    amount,
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day
FROM orders;
```

**CTEs and Pivoting:**
```sql
-- CTE: Break down complex query
WITH recent_orders AS (
    SELECT * FROM orders WHERE order_date >= '2024-01-01'
),
high_value_customers AS (
    SELECT customer_id, SUM(amount) AS total
    FROM recent_orders
    GROUP BY customer_id
    HAVING total > 10000
)
SELECT * FROM high_value_customers
ORDER BY total DESC;

-- PIVOT: Convert rows to columns
SELECT *
FROM (
    SELECT product_category, month, sales_amount
    FROM monthly_sales
)
PIVOT (
    SUM(sales_amount)
    FOR month IN ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun')
) AS pivoted_sales;
```

**JSON Parsing:**
```sql
-- Assuming you have JSON data in VARIANT column
CREATE TABLE events (
    event_id NUMBER,
    event_data VARIANT
);

-- Insert sample JSON
INSERT INTO events SELECT
    1,
    PARSE_JSON('{"user": {"name": "Alice", "age": 30}, "action": "purchase"}');

-- Query JSON
SELECT
    event_id,
    event_data:user.name::STRING AS user_name,
    event_data:user.age::NUMBER AS user_age,
    event_data:action::STRING AS action
FROM events;

-- Flatten nested arrays
SELECT
    event_id,
    f.value:item_name::STRING AS item_name,
    f.value:price::NUMBER AS price
FROM events,
LATERAL FLATTEN(input => event_data:items) f;
```

**Validation:**
- [ ] Can write window functions from memory
- [ ] Understand PARTITION BY vs ORDER BY in window functions
- [ ] Can parse nested JSON structures
- [ ] Can explain when to use CTE vs subquery

---

### ☐ Lab 04: Query Optimization
**Time:** 5 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Medium-Hard

**Objectives:**
- [ ] Identify slow query using Query Profile
- [ ] Add clustering key to large table
- [ ] Optimize JOINs and WHERE clauses
- [ ] Measure performance before/after
- [ ] Eliminate query spilling to disk

**Prerequisites:**
- Lab 02-03 completed
- Large dataset (>1M rows) to optimize

**Evidence to Collect:**
- [ ] Query Profile screenshots (before/after)
- [ ] Clustering key analysis
- [ ] Performance metrics (execution time, partitions scanned, bytes scanned)
- [ ] Optimization notes documenting changes and results

**Create Large Test Dataset:**
```sql
-- Generate 10M rows for testing
CREATE TABLE large_orders AS
SELECT
    SEQ8() AS order_id,
    DATEADD(day, UNIFORM(1, 365, RANDOM()), '2023-01-01') AS order_date,
    UNIFORM(1, 100000, RANDOM()) AS customer_id,
    UNIFORM(1, 10000, RANDOM()) AS product_id,
    UNIFORM(1, 10, RANDOM()) * 10.00 AS amount
FROM TABLE(GENERATOR(ROWCOUNT => 10000000));
```

**Optimization Process:**

**Step 1: Baseline query (intentionally bad)**
```sql
-- Bad query: Full table scan, no filtering
SELECT
    customer_id,
    SUM(amount) AS total_sales
FROM large_orders
GROUP BY customer_id;

-- Check Query Profile:
-- - Execution time: ???
-- - Partitions scanned: ??? / ???
-- - Spilling: Yes/No?
```

**Step 2: Add clustering key**
```sql
-- Cluster by commonly filtered column
ALTER TABLE large_orders CLUSTER BY (order_date);

-- Check clustering quality
SELECT SYSTEM$CLUSTERING_INFORMATION('large_orders', '(order_date)');
-- Goal: clustering_depth < 5

-- Wait for clustering to complete (automatic, may take minutes)
```

**Step 3: Optimized query**
```sql
-- Good query: Filter on clustered column
SELECT
    customer_id,
    SUM(amount) AS total_sales
FROM large_orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'  -- Prune partitions!
GROUP BY customer_id;

-- Check Query Profile again:
-- - Execution time: should be much faster
-- - Partitions scanned: should be ~3% of total
```

**Step 4: Check for spilling**
```sql
-- If query spills to disk, increase warehouse size temporarily
ALTER WAREHOUSE my_warehouse SET WAREHOUSE_SIZE = 'MEDIUM';

-- Run query again, check if spilling eliminated

-- Reset warehouse size
ALTER WAREHOUSE my_warehouse SET WAREHOUSE_SIZE = 'XSMALL';
```

**Validation:**
- [ ] Understand how to read Query Profile
- [ ] Know when clustering is beneficial (large tables, common filters)
- [ ] Can identify spilling and know how to fix it
- [ ] Can explain micro-partitioning vs clustering

---

### ☐ Lab 05: Data Loading
**Time:** 4 hours
**Priority:** 🟡 HIGH
**Difficulty:** Medium

**Objectives:**
- [ ] Create external stage (S3 or local file)
- [ ] Load CSV using COPY INTO
- [ ] Handle errors during loading
- [ ] Load JSON and Parquet files

**Prerequisites:**
- Lab 01 completed
- Sample data files (CSV, JSON, Parquet)

**Evidence to Collect:**
- [ ] Stage configuration
- [ ] COPY INTO commands with options
- [ ] Error handling examples
- [ ] Loaded data verification queries

**Setup Local Stage:**
```sql
-- Create internal stage
CREATE STAGE my_internal_stage;

-- Upload file via Web UI: Data > Stages > my_internal_stage > Upload

-- Or create external stage (S3 example)
CREATE STAGE my_s3_stage
  URL = 's3://my-bucket/data/'
  CREDENTIALS = (AWS_KEY_ID = 'xxx' AWS_SECRET_KEY = 'yyy');
```

**Load CSV:**
```sql
-- Create file format
CREATE FILE FORMAT my_csv_format
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  NULL_IF = ('NULL', 'null', '')
  EMPTY_FIELD_AS_NULL = TRUE;

-- Load data
COPY INTO orders
FROM @my_internal_stage/orders.csv
FILE_FORMAT = (FORMAT_NAME = my_csv_format)
ON_ERROR = 'CONTINUE';  -- Skip bad rows, continue loading

-- Check for errors
SELECT *
FROM TABLE(VALIDATE(orders, JOB_ID => '_last'));
```

**Load JSON:**
```sql
-- Create file format for JSON
CREATE FILE FORMAT my_json_format
  TYPE = JSON;

-- Create table with VARIANT column
CREATE TABLE json_events (
    event_data VARIANT
);

-- Load JSON
COPY INTO json_events
FROM @my_internal_stage/events.json
FILE_FORMAT = (FORMAT_NAME = my_json_format);

-- Query JSON data
SELECT
    event_data:timestamp::TIMESTAMP AS event_time,
    event_data:user_id::NUMBER AS user_id,
    event_data:action::STRING AS action
FROM json_events;
```

**Load Parquet:**
```sql
-- Parquet includes schema, so no file format needed
COPY INTO orders_from_parquet
FROM @my_internal_stage/orders.parquet
FILE_FORMAT = (TYPE = PARQUET);
```

**Validation:**
- [ ] Can create stages (internal and external)
- [ ] Understand file format options
- [ ] Know how to handle errors during loading
- [ ] Can load different file types (CSV, JSON, Parquet)

---

## Week 2: Python ETL & Big Data

### ☐ Lab 06: Python ETL Basic
**Time:** 5 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Medium

**Objectives:**
- [ ] Install Snowflake connector for Python
- [ ] Extract data from source (SQLite or CSV)
- [ ] Transform (clean, validate, enrich)
- [ ] Load to Snowflake

**Prerequisites:**
- Python 3.8+ installed
- Basic Python programming knowledge
- Snowflake account from Lab 01

**Setup:**
```bash
pip install snowflake-connector-python pandas
```

**Evidence to Collect:**
- [ ] Python script with comments
- [ ] Data flow diagram
- [ ] Before/after data comparison
- [ ] Loaded data verification in Snowflake

**Python ETL Script Template:**
```python
import snowflake.connector
import pandas as pd
from datetime import datetime

# 1. EXTRACT: Read from CSV
print("Extracting data...")
df = pd.read_csv('source_data.csv')
print(f"Extracted {len(df)} rows")

# 2. TRANSFORM: Clean and validate
print("Transforming data...")

# Remove nulls
df = df.dropna(subset=['customer_id', 'amount'])

# Clean email addresses
df['email'] = df['email'].str.lower().str.strip()

# Validate amounts (must be positive)
df = df[df['amount'] > 0]

# Add audit column
df['loaded_at'] = datetime.now()

# Type conversions
df['customer_id'] = df['customer_id'].astype(int)
df['amount'] = df['amount'].astype(float)

print(f"Transformed: {len(df)} rows remaining")

# 3. LOAD: Write to Snowflake
print("Loading to Snowflake...")

conn = snowflake.connector.connect(
    user='YOUR_USER',
    password='YOUR_PASSWORD',
    account='YOUR_ACCOUNT',
    warehouse='MY_WAREHOUSE',
    database='MY_DATABASE',
    schema='MY_SCHEMA'
)

cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS customer_orders (
    customer_id NUMBER,
    order_date DATE,
    amount NUMBER(10,2),
    email VARCHAR(255),
    loaded_at TIMESTAMP_NTZ
)
""")

# Load data (using write_pandas for efficiency)
from snowflake.connector.pandas_tools import write_pandas

success, nchunks, nrows, _ = write_pandas(
    conn=conn,
    df=df,
    table_name='CUSTOMER_ORDERS',
    database='MY_DATABASE',
    schema='MY_SCHEMA'
)

print(f"Loaded {nrows} rows to Snowflake")

# Verify
cursor.execute("SELECT COUNT(*) FROM customer_orders")
count = cursor.fetchone()[0]
print(f"Verification: {count} rows in table")

cursor.close()
conn.close()

print("ETL complete!")
```

**Validation:**
- [ ] ETL runs without errors
- [ ] Data successfully loaded to Snowflake
- [ ] Transformations applied correctly
- [ ] Can explain each step of ETL process

---

### ☐ Lab 07: Python ETL Advanced (Incremental)
**Time:** 5 hours
**Priority:** 🔴 CRITICAL
**Difficulty:** Hard

**Objectives:**
- [ ] Implement incremental ETL using watermarks
- [ ] Add error handling and logging
- [ ] Implement data quality checks
- [ ] Make ETL idempotent (safe to rerun)

**Prerequisites:**
- Lab 06 completed
- Understanding of incremental ETL patterns

**Evidence to Collect:**
- [ ] Python script with comprehensive error handling
- [ ] Test cases showing idempotency
- [ ] Logs from multiple runs
- [ ] Watermark tracking mechanism

**Incremental ETL Template:**
```python
import snowflake.connector
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_last_watermark(conn):
    """Get last processed timestamp from control table"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(MAX(last_processed_at), '1900-01-01')
        FROM etl_control_table
        WHERE table_name = 'customer_orders'
    """)
    watermark = cursor.fetchone()[0]
    cursor.close()
    return watermark

def update_watermark(conn, new_watermark):
    """Update watermark in control table"""
    cursor = conn.cursor()
    cursor.execute("""
        MERGE INTO etl_control_table AS target
        USING (SELECT 'customer_orders' AS table_name) AS source
        ON target.table_name = source.table_name
        WHEN MATCHED THEN
            UPDATE SET last_processed_at = %s
        WHEN NOT MATCHED THEN
            INSERT (table_name, last_processed_at)
            VALUES ('customer_orders', %s)
    """, (new_watermark, new_watermark))
    conn.commit()
    cursor.close()

def data_quality_checks(df):
    """Validate data quality"""
    issues = []

    # Check for duplicates
    if df['customer_id'].duplicated().any():
        issues.append("Duplicate customer_ids found")

    # Check for invalid emails
    invalid_emails = df[~df['email'].str.contains('@', na=False)]
    if len(invalid_emails) > 0:
        issues.append(f"{len(invalid_emails)} invalid email addresses")

    # Check for negative amounts
    if (df['amount'] < 0).any():
        issues.append("Negative amounts found")

    return issues

def incremental_etl():
    """Incremental ETL with error handling"""
    try:
        logger.info("Starting incremental ETL")

        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user='YOUR_USER',
            password='YOUR_PASSWORD',
            account='YOUR_ACCOUNT',
            warehouse='MY_WAREHOUSE',
            database='MY_DATABASE',
            schema='MY_SCHEMA'
        )

        # Get last watermark
        last_watermark = get_last_watermark(conn)
        logger.info(f"Last watermark: {last_watermark}")

        # Extract new/changed records
        logger.info("Extracting data...")
        # (In real scenario, query source database with WHERE updated_at > last_watermark)
        df = pd.read_csv('source_data.csv')
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df = df[df['updated_at'] > last_watermark]

        if len(df) == 0:
            logger.info("No new records to process")
            return

        logger.info(f"Extracted {len(df)} new/changed records")

        # Transform
        logger.info("Transforming data...")
        df = df.dropna(subset=['customer_id', 'amount'])
        df['email'] = df['email'].str.lower().str.strip()
        df = df[df['amount'] > 0]

        # Data quality checks
        issues = data_quality_checks(df)
        if issues:
            logger.warning(f"Data quality issues: {issues}")
            # Decide: Fail or continue? For this example, we'll log and continue

        # Load (upsert for idempotency)
        logger.info("Loading to Snowflake...")

        cursor = conn.cursor()

        # Use MERGE for idempotent upsert
        cursor.execute("""
            CREATE TEMPORARY TABLE temp_orders (
                customer_id NUMBER,
                order_date DATE,
                amount NUMBER(10,2),
                email VARCHAR(255),
                updated_at TIMESTAMP_NTZ
            )
        """)

        from snowflake.connector.pandas_tools import write_pandas
        write_pandas(conn, df, 'TEMP_ORDERS', database='MY_DATABASE', schema='MY_SCHEMA')

        cursor.execute("""
            MERGE INTO customer_orders AS target
            USING temp_orders AS source
            ON target.customer_id = source.customer_id AND target.order_date = source.order_date
            WHEN MATCHED THEN
                UPDATE SET
                    amount = source.amount,
                    email = source.email,
                    updated_at = source.updated_at
            WHEN NOT MATCHED THEN
                INSERT (customer_id, order_date, amount, email, updated_at)
                VALUES (source.customer_id, source.order_date, source.amount, source.email, source.updated_at)
        """)

        rows_affected = cursor.rowcount
        logger.info(f"Merged {rows_affected} rows")

        # Update watermark
        new_watermark = df['updated_at'].max()
        update_watermark(conn, new_watermark)
        logger.info(f"Updated watermark to {new_watermark}")

        cursor.close()
        conn.close()

        logger.info("ETL complete!")

    except Exception as e:
        logger.error(f"ETL failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    incremental_etl()
```

**Validation:**
- [ ] Can run ETL multiple times without duplicates (idempotent)
- [ ] Watermark tracking works correctly
- [ ] Error handling prevents partial loads
- [ ] Data quality checks catch bad data

---

### ☐ Lab 08: PySpark Basics
**Time:** 5 hours
**Priority:** 🟡 HIGH
**Difficulty:** Medium-Hard

**Objectives:**
- [ ] Install PySpark locally
- [ ] Read large CSV (>1GB, use synthetic data generator)
- [ ] Apply transformations (filter, groupBy, aggregate)
- [ ] Write to Parquet with partitioning

**Prerequisites:**
- Python 3.8+ installed
- Understanding of distributed computing concepts
- 4GB+ RAM free

**Setup:**
```bash
pip install pyspark
```

**Evidence to Collect:**
- [ ] PySpark code with comments
- [ ] Execution logs (Spark UI screenshots)
- [ ] Output Parquet files with partitions
- [ ] Performance notes (time to process X rows)

**PySpark Script Template:**
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count, year, month

# Initialize Spark
spark = SparkSession.builder \
    .appName("ETL Lab") \
    .master("local[4]") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

print(f"Spark version: {spark.version}")

# Read large CSV
print("Reading CSV...")
df = spark.read \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .csv("large_dataset.csv")

print(f"Total rows: {df.count()}")
df.printSchema()

# Transformations (lazy, not executed yet)
print("Applying transformations...")

# Filter
df_filtered = df.filter(col("amount") > 100)

# Add computed columns
df_enriched = df_filtered \
    .withColumn("year", year(col("order_date"))) \
    .withColumn("month", month(col("order_date")))

# Aggregations
df_summary = df_enriched \
    .groupBy("year", "month", "product_category") \
    .agg(
        sum("amount").alias("total_sales"),
        avg("amount").alias("avg_sale"),
        count("*").alias("transaction_count")
    )

# Show sample (triggers execution)
df_summary.show(10)

# Write to Parquet with partitioning
print("Writing to Parquet...")
df_summary.write \
    .mode("overwrite") \
    .partitionBy("year", "month") \
    .parquet("output/sales_summary.parquet")

print("Done!")

# Stop Spark
spark.stop()
```

**Validation:**
- [ ] Can explain Spark's lazy evaluation
- [ ] Understand transformations vs actions
- [ ] Know when to use partitioning
- [ ] Can read Spark UI (jobs, stages, tasks)

---

### ☐ Lab 09: PySpark + Snowflake
**Time:** 5 hours
**Priority:** 🟡 HIGH
**Difficulty:** Hard

**Objectives:**
- [ ] Connect PySpark to Snowflake
- [ ] Read from Snowflake, process in Spark
- [ ] Write results back to Snowflake
- [ ] Handle large datasets efficiently

**Prerequisites:**
- Lab 06, 08 completed
- Snowflake account with data
- PySpark installed

**Setup:**
```bash
pip install snowflake-connector-python snowflake-sqlalchemy
```

**Evidence to Collect:**
- [ ] PySpark code connecting to Snowflake
- [ ] Spark-Snowflake connector configuration
- [ ] Performance comparison (Spark vs Snowflake for same task)

**PySpark + Snowflake Script:**
```python
from pyspark.sql import SparkSession

# Snowflake connection properties
sfOptions = {
    "sfURL": "YOUR_ACCOUNT.snowflakecomputing.com",
    "sfUser": "YOUR_USER",
    "sfPassword": "YOUR_PASSWORD",
    "sfDatabase": "MY_DATABASE",
    "sfSchema": "MY_SCHEMA",
    "sfWarehouse": "MY_WAREHOUSE"
}

# Initialize Spark with Snowflake connector
spark = SparkSession.builder \
    .appName("Spark-Snowflake Integration") \
    .config("spark.jars.packages", "net.snowflake:spark-snowflake_2.12:2.11.0-spark_3.3") \
    .master("local[*]") \
    .getOrCreate()

# Read from Snowflake
print("Reading from Snowflake...")
df = spark.read \
    .format("snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "large_orders") \
    .load()

print(f"Rows read: {df.count()}")

# Process in Spark
print("Processing in Spark...")
from pyspark.sql.functions import col, sum, count, avg

df_aggregated = df \
    .groupBy("customer_id") \
    .agg(
        sum("amount").alias("total_spent"),
        count("*").alias("order_count"),
        avg("amount").alias("avg_order_value")
    ) \
    .filter(col("total_spent") > 10000)

# Write back to Snowflake
print("Writing to Snowflake...")
df_aggregated.write \
    .format("snowflake") \
    .options(**sfOptions) \
    .option("dbtable", "high_value_customers") \
    .mode("overwrite") \
    .save()

print("Done!")

spark.stop()
```

**Validation:**
- [ ] Spark successfully connects to Snowflake
- [ ] Can read large tables from Snowflake
- [ ] Can write results back to Snowflake
- [ ] Understand when to use Spark vs Snowflake processing

---

### ☐ Lab 10: Data Security
**Time:** 3 hours
**Priority:** 🟡 MEDIUM
**Difficulty:** Medium

**Objectives:**
- [ ] Create roles (analyst, admin, restricted)
- [ ] Grant appropriate permissions
- [ ] Implement column masking on PII fields
- [ ] Create secure view

**Prerequisites:**
- Lab 01-02 completed
- Understanding of RBAC concepts

**Evidence to Collect:**
- [ ] GRANT/REVOKE scripts
- [ ] Role hierarchy diagram
- [ ] Column masking configuration
- [ ] Test results (different roles see different data)

**Security Configuration:**
```sql
-- Create roles
CREATE ROLE analyst;
CREATE ROLE admin;
CREATE ROLE restricted;

-- Grant permissions
GRANT USAGE ON WAREHOUSE my_warehouse TO ROLE analyst;
GRANT USAGE ON DATABASE my_database TO ROLE analyst;
GRANT USAGE ON SCHEMA my_database.my_schema TO ROLE analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA my_database.my_schema TO ROLE analyst;

-- Admin gets more permissions
GRANT ALL ON DATABASE my_database TO ROLE admin;

-- Column masking (Dynamic Data Masking)
CREATE MASKING POLICY email_mask AS (val STRING) RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN') THEN val
        ELSE '***@***'
    END;

-- Apply masking policy
ALTER TABLE customers MODIFY COLUMN email SET MASKING POLICY email_mask;

-- Secure view (definition hidden)
CREATE SECURE VIEW customer_view AS
    SELECT * FROM customers
    WHERE region = (SELECT region FROM user_regions WHERE user_name = CURRENT_USER());

-- Test as different roles
USE ROLE analyst;
SELECT email FROM customers LIMIT 5;  -- Should see masked

USE ROLE admin;
SELECT email FROM customers LIMIT 5;  -- Should see actual emails
```

**Validation:**
- [ ] Roles properly restrict access
- [ ] Masking policies work correctly
- [ ] Secure views hide definition
- [ ] Row-level security implemented

---

### ☐ Lab 11: Airflow Orchestration
**Time:** 5 hours
**Priority:** 🟡 MEDIUM (Preferred)
**Difficulty:** Medium-Hard

**Objectives:**
- [ ] Install Apache Airflow locally
- [ ] Create DAG with 3 tasks (extract, transform, load)
- [ ] Set up dependencies and scheduling
- [ ] Test failure handling and retries

**Prerequisites:**
- Docker installed (easiest setup method)
- Basic understanding of DAGs

**Setup (Docker):**
```bash
# Download docker-compose.yaml from Airflow docs
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/stable/docker-compose.yaml'

# Initialize database
docker-compose up airflow-init

# Start Airflow
docker-compose up

# Access UI: http://localhost:8080 (user: airflow, password: airflow)
```

**Evidence to Collect:**
- [ ] DAG code (Python)
- [ ] Airflow UI screenshots (graph view, tree view)
- [ ] Task logs
- [ ] Retry/failure handling demonstration

**Sample DAG:**
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for orders',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
)

def extract(**context):
    print("Extracting data...")
    # Extract logic here
    return {"rows_extracted": 1000}

def transform(**context):
    print("Transforming data...")
    ti = context['ti']
    rows = ti.xcom_pull(task_ids='extract')['rows_extracted']
    print(f"Transforming {rows} rows")
    return {"rows_transformed": rows}

def load(**context):
    print("Loading data...")
    ti = context['ti']
    rows = ti.xcom_pull(task_ids='transform')['rows_transformed']
    print(f"Loading {rows} rows to Snowflake")

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag,
)

extract_task >> transform_task >> load_task
```

**Validation:**
- [ ] DAG appears in Airflow UI
- [ ] Tasks run in correct order
- [ ] Can trigger manual run
- [ ] Retries work on failure

---

### ☐ Lab 12: End-to-End Pipeline (Capstone)
**Time:** 6 hours
**Priority:** 🔴 CRITICAL (Portfolio showcase)
**Difficulty:** Hard

**Objectives:**
- [ ] Combine Labs 1-11 into complete pipeline
- [ ] Source data → PySpark transformation → Snowflake load → SQL analytics
- [ ] Orchestrated by Airflow (or documented manual process)
- [ ] Full documentation with architecture diagram

**Prerequisites:**
- All previous labs completed
- Strong understanding of data pipeline design

**Evidence to Collect:**
- [ ] Full pipeline documentation (PDF, 5-10 pages)
- [ ] Architecture diagram (data flow)
- [ ] All code (Python ETL, Spark, SQL, Airflow DAG)
- [ ] Test results and performance metrics
- [ ] Sample dashboards/reports from data

**Pipeline Architecture:**
```
[Source: CSV files in S3]
         ↓
[Extract: Python script]
         ↓
[Transform: PySpark processing]
         ↓
[Load: Snowflake COPY INTO]
         ↓
[Analytics: SQL queries / BI tool]
         ↓
[Orchestration: Airflow DAG scheduling everything]
```

**Validation:**
- [ ] Pipeline runs end-to-end without errors
- [ ] Can explain every component
- [ ] Performance is acceptable (document metrics)
- [ ] Code is production-ready (error handling, logging)

---

## Progress Tracking

**Week 1 Progress:** ☐☐☐☐☐ (0/5 labs completed)
**Week 2 Progress:** ☐☐☐☐☐☐☐ (0/7 labs completed)

**Overall Progress:** 0/12 labs (0%)

---

## Portfolio Organization

**Recommended Folder Structure:**
```
backend-snowflake-labs/
├── lab-01-snowflake-setup/
│   ├── screenshots/
│   ├── queries.sql
│   └── notes.md
├── lab-02-data-modeling/
│   ├── erd-diagram.png
│   ├── ddl-scripts.sql
│   ├── sample-queries.sql
│   └── notes.md
...
└── lab-12-capstone/
    ├── pipeline-documentation.pdf
    ├── architecture-diagram.png
    ├── code/
    │   ├── extract.py
    │   ├── transform.py
    │   ├── load.py
    │   └── airflow_dag.py
    └── test-results/
```

---

**Last Updated:** 2025-11-11
**For Role:** Backend Data & Snowflake Engineer (T-Mobile)
**Compensation:** $48-56/hr (~$100-117K/year)

**Remember:** Snowflake trial is free for 30 days with $400 credits - start now!

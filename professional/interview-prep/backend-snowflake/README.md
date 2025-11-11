# Backend Data & Snowflake Engineer
## T-Mobile Interview Prep (Quick Start Package)

**Company:** T-Mobile
**Compensation:** $48-56/hr (~$100-117K/year equivalent)
**Location:** Redmond, WA (On-site)
**Experience Required:** 3+ years Backend Data & Snowflake Engineering

---

## 🎯 Role Overview

Design, build, and optimize ETL pipelines for data ingestion, transformation, and processing. Primary focus on **Snowflake data warehouse** management, Python/Apache Spark for big data workloads, and scalable data architecture.

**Key Differentiator:** This is **80% Snowflake + 20% ETL/Big Data**—deep Snowflake expertise is critical.

---

## 🔥 Top 10 Topics to Master (Priority Order)

### 1. **Snowflake Architecture & Administration** (🔴 CRITICAL)
**What:** Virtual warehouses, databases, schemas, stages, roles, compute vs storage separation
**Why:** "Oversee the operation and performance of the Snowflake data warehouse"
**Study:** Architecture whitepaper, warehouse sizing, auto-suspend, clustering
**Lab:** Set up Snowflake trial, create warehouse/database/schema, load data

### 2. **Snowflake Query Optimization** (🔴 CRITICAL)
**What:** Query profiling, execution plans, clustering keys, partitioning, caching
**Why:** "Optimize queries, storage, and compute resources to improve efficiency"
**Study:** Query history, result cache, warehouse cache, clustering depth
**Lab:** Identify slow query, add clustering key, measure improvement

### 3. **Data Modeling for Warehouses** (🔴 CRITICAL)
**What:** Star schema, snowflake schema (confusingly different!), dimensional modeling, slowly changing dimensions (SCD)
**Why:** "Design and maintain new tables and data models"
**Study:** Kimball methodology, fact vs dimension tables, normalization trade-offs
**Lab:** Design star schema for e-commerce data (orders, customers, products)

### 4. **Python for ETL** (🔴 CRITICAL)
**What:** Pandas, SQL Alchemy, data validation, error handling, logging
**Why:** "Hands-on expertise with Python and Apache Spark (or equivalent)"
**Study:** Pandas DataFrames, read_sql, to_sql, data type conversions
**Lab:** Python script that extracts from Oracle, transforms, loads to Snowflake

### 5. **Apache Spark / PySpark** (🟡 HIGH)
**What:** RDDs, DataFrames, transformations vs actions, partitioning, broadcast joins
**Why:** "Hands-on expertise with Python and Apache Spark (or equivalent)"
**Study:** Spark architecture, lazy evaluation, DAG, shuffle operations
**Lab:** PySpark job that processes large CSV (>1GB), writes partitioned Parquet

### 6. **ETL Design Patterns** (🟡 HIGH)
**What:** Full load vs incremental, CDC (change data capture), idempotency, error handling, data quality checks
**Why:** "Design, build, and optimize ETL pipelines"
**Study:** Common patterns, when to use each, failure recovery strategies
**Lab:** Incremental ETL using watermarks (track last processed timestamp)

### 7. **SQL Advanced** (🟡 HIGH)
**What:** Window functions, CTEs, recursive queries, JSON functions, lateral joins
**Why:** "Strong proficiency in SQL, data modeling, and warehouse optimization"
**Study:** ROW_NUMBER, RANK, LAG/LEAD, PARTITION BY, complex aggregations
**Lab:** Write SQL to calculate running totals, moving averages, YoY growth

### 8. **Snowflake Data Loading** (🟡 MEDIUM)
**What:** COPY INTO, Snowpipe, external stages (S3, Azure Blob), file formats (CSV, JSON, Parquet, Avro)
**Why:** "Integrate and process data from multiple sources"
**Study:** Stage types (internal/external), COPY options, error handling
**Lab:** Load data from S3 using external stage and COPY INTO command

### 9. **Data Security & Compliance** (🟡 MEDIUM)
**What:** RBAC (role-based access control), column-level security, row-level security, encryption, audit logs
**Why:** "Ensure data integrity, security, and compliance across the environment"
**Study:** Roles vs users, grants, secure views, data masking
**Lab:** Implement column masking (hide PII unless user has specific role)

### 10. **Orchestration Tools** (🟢 LOW - Preferred)
**What:** Apache Airflow DAGs, Azure Data Factory pipelines, scheduling, dependencies
**Why:** "Familiarity with orchestration tools such as Apache Airflow or Azure Data Factory"
**Study:** DAG structure, task dependencies, XComs, sensors
**Lab:** Airflow DAG that orchestrates multi-step ETL (extract → transform → load → validate)

---

## 📚 Quick Reference Cheat Sheet

| Topic | Key Concepts | Interview Question Example |
|-------|-------------|---------------------------|
| **Snowflake Architecture** | Virtual warehouses, micro-partitions, time travel, zero-copy cloning | "Explain how Snowflake's architecture differs from traditional databases." |
| **Query Optimization** | Clustering keys, query profiling, result cache, pruning | "A query is taking 10 minutes. Walk me through how you'd optimize it." |
| **Data Modeling** | Star schema, dimension tables, fact tables, SCD Type 2 | "Design a data warehouse schema for a retail company with 1B transactions/year." |
| **Python ETL** | Pandas, data validation, error handling, incremental loading | "Write Python code to extract data from Oracle and load to Snowflake with error handling." |
| **PySpark** | DataFrames, transformations, actions, partitioning, broadcast joins | "Process a 10GB CSV file with PySpark. What optimizations would you apply?" |
| **ETL Patterns** | Full vs incremental, CDC, idempotency, watermarks | "Design an incremental ETL pipeline that processes only new/changed records." |
| **SQL Advanced** | Window functions, CTEs, pivots, JSON parsing | "Write SQL to calculate a 7-day moving average of sales." |
| **Data Loading** | COPY INTO, Snowpipe, stages, file formats | "How would you load 100K CSV files from S3 into Snowflake efficiently?" |
| **Security** | RBAC, column masking, row-level security, encryption | "How do you protect PII in Snowflake while allowing analytics?" |
| **Orchestration** | Airflow DAGs, scheduling, error handling, retries | "Design an Airflow DAG for a multi-step data pipeline with failure recovery." |

---

## 🧪 12 Essential Labs (2-Week Plan)

### Week 1: Snowflake & SQL Foundations

**Lab 01: Snowflake Setup & Basics (3 hours)**
- Sign up for Snowflake free trial
- Create warehouse, database, schema
- Load sample data (Snowflake sample datasets)
- Run basic queries (SELECT, JOIN, GROUP BY)
**Evidence:** Snowflake account, queries, screenshots

**Lab 02: Data Modeling (5 hours)**
- Design star schema for e-commerce (fact: orders; dimensions: customers, products, time)
- Create tables with appropriate data types
- Load sample data
- Write queries to answer business questions
**Evidence:** ERD diagram, DDL scripts, sample queries

**Lab 03: Advanced SQL (4 hours)**
- Window functions (ROW_NUMBER, RANK, LAG/LEAD)
- CTEs for complex queries
- Pivoting and unpivoting
- JSON data parsing
**Evidence:** SQL scripts with comments explaining each query

**Lab 04: Query Optimization (5 hours)**
- Identify slow query (intentionally write inefficient query)
- Use Query Profile to analyze
- Add clustering key
- Optimize JOINs and WHERE clauses
- Measure before/after performance
**Evidence:** Query Profile screenshots, optimization notes

**Lab 05: Data Loading (4 hours)**
- Create external stage (S3 or local file)
- Load CSV using COPY INTO
- Handle errors (ON_ERROR = 'CONTINUE')
- Load JSON and Parquet files
**Evidence:** COPY INTO commands, loaded data verification

### Week 2: Python ETL & Big Data

**Lab 06: Python ETL Basic (5 hours)**
- Python script using Snowflake connector
- Extract data from source (SQLite or CSV)
- Transform (clean, validate, enrich)
- Load to Snowflake
**Evidence:** Python code, data flow diagram, loaded data

**Lab 07: Python ETL Advanced (5 hours)**
- Incremental ETL using watermarks
- Error handling and logging
- Data quality checks
- Idempotent design
**Evidence:** Python code with error handling, test cases

**Lab 08: PySpark Basics (5 hours)**
- Install PySpark locally
- Read large CSV (>1GB, use synthetic data generator)
- Apply transformations (filter, groupBy, agg)
- Write to Parquet with partitioning
**Evidence:** PySpark code, execution logs, output files

**Lab 09: PySpark + Snowflake (5 hours)**
- Connect PySpark to Snowflake
- Read from Snowflake, process in Spark
- Write results back to Snowflake
- Handle large datasets efficiently
**Evidence:** PySpark code, Snowflake-Spark connector config

**Lab 10: Data Security (3 hours)**
- Create roles (analyst, admin, restricted)
- Grant appropriate permissions
- Implement column masking on PII fields
- Create secure view
**Evidence:** GRANT/REVOKE scripts, masked query results

**Lab 11: Airflow Orchestration (5 hours)**
- Install Apache Airflow locally
- Create DAG with 3 tasks (extract, transform, load)
- Set up dependencies and scheduling
- Test failure handling
**Evidence:** DAG code, Airflow UI screenshots, logs

**Lab 12: End-to-End Pipeline (6 hours)**
- Combine Labs 1-11 into complete pipeline
- Source data → PySpark transformation → Snowflake load → SQL analytics
- Orchestrated by Airflow
- Documented with architecture diagram
**Evidence:** Full pipeline documentation, all code, test results

---

## 📅 2-Week Learning Path (Condensed)

**Week 1: Snowflake Mastery**
Day 1-2: Snowflake setup + data modeling (Labs 01-02)
Day 3: Advanced SQL (Lab 03)
Day 4: Query optimization (Lab 04)
Day 5: Data loading patterns (Lab 05)
Day 6-7: Review Snowflake documentation, certification study guide

**Week 2: ETL & Big Data**
Day 8-9: Python ETL (Labs 06-07)
Day 10: PySpark basics (Lab 08)
Day 11: PySpark + Snowflake (Lab 09)
Day 12: Security + Airflow (Labs 10-11)
Day 13: End-to-end pipeline (Lab 12)
Day 14: Interview practice + review

---

## 🎤 Sample Interview Questions

**Easy:**
1. What is Snowflake and how does it differ from traditional databases?
2. Explain the difference between a fact table and a dimension table.
3. What is ETL and why is it important?

**Medium:**
4. Walk me through optimizing a slow Snowflake query.
5. Design an incremental ETL pipeline that processes only new records.
6. Explain how you'd handle PII data in a data warehouse.

**Hard:**
7. Design a data warehouse for a company with 100M daily transactions across 10 data sources.
8. You need to process 10TB of historical data. What's your approach with PySpark and Snowflake?
9. A critical ETL job failed halfway through. How do you recover without duplicating data?

**Behavioral:**
10. Tell me about a time you optimized a data pipeline. What was the impact?

---

## 📂 Your Relevant Portfolio Projects

- `projects/p12-data-pipeline/` → "I built an end-to-end data pipeline that..."
- `projects/16-advanced-data-lake/` → "I designed a data lake architecture with..."
- `projects/5-real-time-data-streaming/` → "I processed streaming data using..."
- `projects/7-serverless-data-processing/` → "I built serverless ETL with..."

---

## ✅ Pre-Interview Checklist

- [ ] Snowflake trial account active, practiced queries
- [ ] Can write star schema from memory
- [ ] Know SQL window functions cold
- [ ] Completed 2-3 Python ETL scripts
- [ ] Basic PySpark understanding
- [ ] Understand Snowflake security model
- [ ] Portfolio mapped to role requirements
- [ ] 5-7 STAR stories prepared
- [ ] Questions for interviewer ready

---

**Next Steps:**
1. Today: Snowflake trial signup + Lab 01
2. Week 1: Master Snowflake (Labs 01-05)
3. Week 2: ETL & big data (Labs 06-12)

**Good luck! 🚀**

---

**Last Updated:** 2025-11-10
**Status:** Ready to start immediately!

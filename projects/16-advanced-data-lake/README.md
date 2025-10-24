# Project 16: Advanced Data Lake & Analytics

## Overview
Implements a medallion architecture on Databricks with Delta Lake, structured streaming, and dbt transformations.

## Workflow
1. Bronze layer ingests raw JSON from Kafka topics.
2. Silver layer applies cleansing and joins with dimension tables.
3. Gold layer exposes star schema to BI tools with Delta Live Tables.

## Local Testing
```bash
pip install -r requirements.txt
python src/bronze_to_silver.py --input data/bronze.json --output silver.parquet
```

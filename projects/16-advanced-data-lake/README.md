# Project 16: Advanced Data Lake & Analytics

## Overview
Implements a medallion architecture on Databricks with Delta Lake, structured streaming, and dbt transformations.

## Architecture
- **Context:** Streaming and batch feeds must land in a medallion-style Delta Lake that enforces quality checks and produces curated gold datasets for BI and ML consumers.
- **Decision:** Combine Kafka + Auto Loader ingestion with structured streaming into bronze, enforce expectations in silver, and publish gold/star schemas via Delta Live Tables and dbt, backed by a feature store.
- **Consequences:** Provides governed, incremental data products and reusable features, but depends on consistent contract testing across layers to prevent schema drift.

[Mermaid source](assets/diagrams/architecture.mmd) · Diagram: render locally from [Mermaid source](assets/diagrams/architecture.mmd) using `python tools/generate_phase1_diagrams.py` (PNG output is .gitignored).

## Workflow
1. Bronze layer ingests raw JSON from Kafka topics.
2. Silver layer applies cleansing and joins with dimension tables.
3. Gold layer exposes star schema to BI tools with Delta Live Tables.

## Local Testing
```bash
pip install -r requirements.txt
python src/bronze_to_silver.py --input data/bronze.json --output silver.parquet
```

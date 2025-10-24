# Catalog Sync Process

## Overview
Nightly ETL pipeline harmonizes supplier catalogs into the storefront schema while enforcing validation gates before publish.

## Steps
1. **Ingest** supplier CSVs via SFTP to staging bucket.
2. **Normalize** columns to canonical schema using Pandas transformation jobs.
3. **Validate** using Great Expectations suite (`expect_unique_values`, `expect_column_values_to_match_regex`).
4. **Price Adjust** using stored procedures (see `pricing-automation.sql`).
5. **Publish** to WooCommerce via REST API with batch window outside store hours.
6. **Notify** results in Slack with diff summary and anomaly highlights.

## Failure Handling
- Validation failures halt pipeline and open Jira ticket with failing expectation IDs.
- Price anomalies over ±20% trigger manual approval workflow.
- API publish errors automatically retry with exponential backoff.

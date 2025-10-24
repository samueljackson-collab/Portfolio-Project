# Architecture

## Overview
Event-driven ingestion feeds a lakehouse with curated zones, governed by metadata services and served through analytics interfaces.

## Component Breakdown
- **Ingestion Pipelines:** Capture CDC streams and batch extracts from CRM, billing, and support.
- **Lakehouse Storage:** Bronze/Silver/Gold zones with schema evolution and quality checks.
- **Metadata Catalog:** Tracks data lineage, privacy classifications, and stewardship ownership.
- **Serving Layer:** SQL warehouse and API endpoints exposing unified customer profiles.

## Diagrams & Flows
```text
Sources -> CDC/Bulk Ingest -> Bronze -> Quality Checks -> Silver -> Feature Engineering -> Gold -> SQL/API Consumers
            Metadata Catalog spans all zones with governance hooks.
```

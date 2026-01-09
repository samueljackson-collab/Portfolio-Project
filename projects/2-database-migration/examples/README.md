# Migration Examples

This directory contains example migration scenarios demonstrating various use cases for the Database Migration Platform.

## Examples Overview

| Example | Description | Source | Target |
|---------|-------------|--------|--------|
| [Large Orders Table](./migrate_large_orders.py) | Migrating a large orders table with 100k+ rows | MySQL | PostgreSQL |
| [Handle MySQL ENUMs](./handle_mysql_enums.py) | Converting MySQL ENUM types to PostgreSQL | MySQL | PostgreSQL |
| [CDC Sync Demo](./cdc_realtime_sync.py) | Real-time CDC synchronization | MySQL | PostgreSQL |
| [Batch Migration](./batch_migration.py) | Batch processing for large datasets | Any | Any |

## Quick Start

```bash
# Start the demo stack
docker-compose -f docker-compose.mysql-demo.yml up -d

# Wait for services to be ready
./scripts/wait-for-services.sh

# Run an example
python examples/migrate_large_orders.py
```

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Required packages: `pip install -r requirements.txt`

## Example 1: Large Orders Table Migration

This example demonstrates migrating a large `orders` table with:
- 100,000+ rows
- Complex relationships (foreign keys)
- JSON columns
- ENUM types

```bash
python examples/migrate_large_orders.py --batch-size 5000 --parallel-workers 4
```

## Example 2: Handling MySQL ENUMs

MySQL ENUMs require special handling when migrating to PostgreSQL. This example shows:
- Automatic ENUM type creation in PostgreSQL
- Value mapping and validation
- Handling invalid ENUM values

```bash
python examples/handle_mysql_enums.py
```

## Example 3: CDC Real-Time Sync

Demonstrates continuous data synchronization using Change Data Capture:
- Initial full load
- Real-time change streaming
- Conflict resolution
- Lag monitoring

```bash
python examples/cdc_realtime_sync.py --duration 300
```

## Common Issues and Solutions

### Issue: MySQL ENUM to PostgreSQL

**Problem**: MySQL ENUMs don't directly translate to PostgreSQL.

**Solution**: Create PostgreSQL ENUM types before migration:
```sql
-- PostgreSQL
CREATE TYPE order_status AS ENUM ('pending', 'shipped', 'delivered');
```

### Issue: Large Table Performance

**Problem**: Migrating tables with millions of rows is slow.

**Solution**: Use parallel workers and batch processing:
```python
config = MigrationConfig(
    batch_size=10000,
    parallel_workers=8,
    use_copy_command=True  # Uses PostgreSQL COPY for bulk inserts
)
```

### Issue: JSON Column Compatibility

**Problem**: MySQL JSON and PostgreSQL JSONB have different behaviors.

**Solution**: Use JSONB in PostgreSQL and validate JSON structure:
```python
# Validate JSON during migration
def validate_json(data):
    if isinstance(data, str):
        return json.loads(data)
    return data
```

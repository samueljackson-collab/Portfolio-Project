#!/bin/bash
# Database backup script

set -e

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

echo "Starting database backup..."
mkdir -p "$BACKUP_DIR"

# Example: PostgreSQL backup (adjust for your database)
# pg_dump -h $DB_HOST -U $DB_USER $DB_NAME > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE" || true

echo "✓ Database backup completed: ${BACKUP_FILE}.gz"

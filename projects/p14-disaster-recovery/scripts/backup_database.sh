#!/bin/bash
# Database backup script with retention policy
# Supports PostgreSQL and MySQL databases

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DB_TYPE="${DB_TYPE:-postgresql}"
DB_HOST="${DB_HOST:-localhost}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-mydb}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_${DB_NAME}_$TIMESTAMP.sql"

# Validate required environment variables
if [ -z "$DB_HOST" ] || [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
    echo "ERROR: Required environment variables not set (DB_HOST, DB_USER, DB_NAME)"
    exit 1
fi

echo "Starting database backup..."
echo "  Database: $DB_NAME"
echo "  Type: $DB_TYPE"
echo "  Host: $DB_HOST"
mkdir -p "$BACKUP_DIR"

# Perform backup based on database type
case "$DB_TYPE" in
    postgresql|postgres)
        echo "  Using pg_dump for PostgreSQL backup..."
        # PGPASSWORD can be set in environment or use .pgpass file
        pg_dump -h "$DB_HOST" -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
        ;;
    mysql|mariadb)
        echo "  Using mysqldump for MySQL backup..."
        # MYSQL_PWD can be set in environment or use .my.cnf file
        mysqldump -h "$DB_HOST" -u "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
        ;;
    *)
        echo "ERROR: Unsupported database type: $DB_TYPE"
        echo "Supported types: postgresql, mysql, mariadb"
        exit 1
        ;;
esac

# Verify backup file was created and is not empty
if [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file is empty or was not created"
    exit 1
fi

# Compress backup
echo "  Compressing backup..."
gzip "$BACKUP_FILE"

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
echo "✓ Database backup completed: ${BACKUP_FILE}.gz (${BACKUP_SIZE})"

# Cleanup old backups (retention policy)
echo "  Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "db_backup_${DB_NAME}_*.sql.gz" -type f -mtime +"$RETENTION_DAYS" -delete
REMAINING_BACKUPS=$(find "$BACKUP_DIR" -name "db_backup_${DB_NAME}_*.sql.gz" -type f | wc -l)
echo "  Retained backups: $REMAINING_BACKUPS"

echo "✓ Backup operation completed successfully"

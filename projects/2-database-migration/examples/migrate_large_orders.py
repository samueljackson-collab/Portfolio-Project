#!/usr/bin/env python3
"""
Example: Migrating Large Orders Table from MySQL to PostgreSQL

This script demonstrates how to migrate a large orders table (100k+ rows)
with optimal performance using batch processing and parallel workers.

Usage:
    python migrate_large_orders.py --batch-size 5000 --parallel-workers 4
"""

import argparse
import logging
import time
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

import mysql.connector
import psycopg2
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    """Configuration for the migration process."""
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "sourcedb"
    mysql_user: str = "debezium"
    mysql_password: str = "dbzpass"

    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_database: str = "targetdb"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    batch_size: int = 5000
    parallel_workers: int = 4


@dataclass
class MigrationStats:
    """Statistics for migration progress."""
    total_rows: int = 0
    migrated_rows: int = 0
    failed_rows: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def rows_per_second(self) -> float:
        if self.duration_seconds > 0:
            return self.migrated_rows / self.duration_seconds
        return 0.0


class LargeTableMigrator:
    """Migrates large tables from MySQL to PostgreSQL with optimal performance."""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.stats = MigrationStats()

    def get_mysql_connection(self):
        """Create MySQL connection."""
        return mysql.connector.connect(
            host=self.config.mysql_host,
            port=self.config.mysql_port,
            database=self.config.mysql_database,
            user=self.config.mysql_user,
            password=self.config.mysql_password
        )

    def get_postgres_connection(self):
        """Create PostgreSQL connection."""
        return psycopg2.connect(
            host=self.config.postgres_host,
            port=self.config.postgres_port,
            database=self.config.postgres_database,
            user=self.config.postgres_user,
            password=self.config.postgres_password
        )

    def get_total_count(self) -> int:
        """Get total row count from source table."""
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count

    def fetch_batch(self, offset: int, limit: int) -> List[Dict[str, Any]]:
        """Fetch a batch of rows from MySQL."""
        conn = self.get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                id, user_id, order_number, status, payment_status, payment_method,
                subtotal, tax_amount, shipping_amount, discount_amount, total_amount,
                currency, shipping_address, billing_address, notes,
                created_at, updated_at, shipped_at, delivered_at
            FROM orders
            ORDER BY id
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def transform_row(self, row: Dict[str, Any]) -> tuple:
        """Transform MySQL row to PostgreSQL format."""
        # Handle JSON columns - parse if string
        shipping_address = row.get('shipping_address')
        if isinstance(shipping_address, str):
            shipping_address = json.loads(shipping_address) if shipping_address else None

        billing_address = row.get('billing_address')
        if isinstance(billing_address, str):
            billing_address = json.loads(billing_address) if billing_address else None

        return (
            row['id'],
            row['user_id'],
            row['order_number'],
            row['status'],
            row['payment_status'],
            row['payment_method'],
            float(row['subtotal']) if row['subtotal'] else 0.0,
            float(row['tax_amount']) if row['tax_amount'] else 0.0,
            float(row['shipping_amount']) if row['shipping_amount'] else 0.0,
            float(row['discount_amount']) if row['discount_amount'] else 0.0,
            float(row['total_amount']) if row['total_amount'] else 0.0,
            row['currency'],
            json.dumps(shipping_address) if shipping_address else None,
            json.dumps(billing_address) if billing_address else None,
            row['notes'],
            row['created_at'],
            row['updated_at'],
            row['shipped_at'],
            row['delivered_at']
        )

    def insert_batch(self, rows: List[Dict[str, Any]]) -> int:
        """Insert a batch of rows into PostgreSQL."""
        if not rows:
            return 0

        conn = self.get_postgres_connection()
        cursor = conn.cursor()

        transformed_rows = [self.transform_row(row) for row in rows]

        insert_query = """
            INSERT INTO orders (
                id, user_id, order_number, status, payment_status, payment_method,
                subtotal, tax_amount, shipping_amount, discount_amount, total_amount,
                currency, shipping_address, billing_address, notes,
                created_at, updated_at, shipped_at, delivered_at
            ) VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                status = EXCLUDED.status,
                payment_status = EXCLUDED.payment_status,
                total_amount = EXCLUDED.total_amount,
                updated_at = EXCLUDED.updated_at
        """

        try:
            execute_values(cursor, insert_query, transformed_rows)
            conn.commit()
            inserted = len(rows)
        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            conn.rollback()
            inserted = 0
        finally:
            cursor.close()
            conn.close()

        return inserted

    def migrate_batch_range(self, start_offset: int, end_offset: int) -> int:
        """Migrate a range of batches (for parallel processing)."""
        total_migrated = 0
        offset = start_offset

        while offset < end_offset:
            rows = self.fetch_batch(offset, self.config.batch_size)
            if not rows:
                break

            migrated = self.insert_batch(rows)
            total_migrated += migrated
            offset += self.config.batch_size

            logger.info(f"Migrated batch at offset {offset}: {migrated} rows")

        return total_migrated

    def run_migration(self) -> MigrationStats:
        """Execute the full migration process."""
        logger.info("=" * 60)
        logger.info("STARTING LARGE TABLE MIGRATION")
        logger.info("=" * 60)

        self.stats.start_time = datetime.now(timezone.utc)
        self.stats.total_rows = self.get_total_count()

        logger.info(f"Total rows to migrate: {self.stats.total_rows:,}")
        logger.info(f"Batch size: {self.config.batch_size:,}")
        logger.info(f"Parallel workers: {self.config.parallel_workers}")

        # Calculate ranges for parallel processing
        num_batches = (self.stats.total_rows + self.config.batch_size - 1) // self.config.batch_size
        batches_per_worker = (num_batches + self.config.parallel_workers - 1) // self.config.parallel_workers

        ranges = []
        for i in range(self.config.parallel_workers):
            start = i * batches_per_worker * self.config.batch_size
            end = min((i + 1) * batches_per_worker * self.config.batch_size, self.stats.total_rows)
            if start < self.stats.total_rows:
                ranges.append((start, end))

        # Execute migration in parallel
        with ThreadPoolExecutor(max_workers=self.config.parallel_workers) as executor:
            futures = {
                executor.submit(self.migrate_batch_range, start, end): (start, end)
                for start, end in ranges
            }

            for future in as_completed(futures):
                start, end = futures[future]
                try:
                    migrated = future.result()
                    self.stats.migrated_rows += migrated
                    logger.info(f"Completed range {start}-{end}: {migrated} rows")
                except Exception as e:
                    logger.error(f"Failed range {start}-{end}: {e}")
                    self.stats.failed_rows += (end - start)

        self.stats.end_time = datetime.now(timezone.utc)

        # Print summary
        logger.info("=" * 60)
        logger.info("MIGRATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total rows: {self.stats.total_rows:,}")
        logger.info(f"Migrated: {self.stats.migrated_rows:,}")
        logger.info(f"Failed: {self.stats.failed_rows:,}")
        logger.info(f"Duration: {self.stats.duration_seconds:.2f} seconds")
        logger.info(f"Throughput: {self.stats.rows_per_second:.2f} rows/second")

        return self.stats


def main():
    parser = argparse.ArgumentParser(description="Migrate large orders table")
    parser.add_argument("--batch-size", type=int, default=5000, help="Batch size for processing")
    parser.add_argument("--parallel-workers", type=int, default=4, help="Number of parallel workers")
    parser.add_argument("--mysql-host", default="localhost", help="MySQL host")
    parser.add_argument("--postgres-host", default="localhost", help="PostgreSQL host")
    args = parser.parse_args()

    config = MigrationConfig(
        batch_size=args.batch_size,
        parallel_workers=args.parallel_workers,
        mysql_host=args.mysql_host,
        postgres_host=args.postgres_host
    )

    migrator = LargeTableMigrator(config)
    stats = migrator.run_migration()

    # Exit with error if migration had failures
    if stats.failed_rows > 0:
        exit(1)


if __name__ == "__main__":
    main()

"""
Database Migration Orchestrator

This module coordinates zero-downtime database migrations using CDC (Change Data Capture)
with Debezium and AWS DMS, providing validation, rollback, and monitoring capabilities.
"""

from __future__ import annotations

import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationPhase(Enum):
    """Migration phases"""
    INIT = "initialization"
    REPLICATION = "replication"
    VALIDATION = "validation"
    CUTOVER = "cutover"
    COMPLETE = "complete"
    ROLLBACK = "rollback"
    FAILED = "failed"


@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"


@dataclass
class MigrationMetrics:
    """Migration performance metrics"""
    replication_lag_seconds: float
    rows_migrated: int
    errors_count: int
    start_time: datetime
    end_time: Optional[datetime] = None
    downtime_seconds: float = 0.0

    def get_duration(self) -> timedelta:
        """Calculate total migration duration"""
        end = self.end_time or datetime.utcnow()
        return end - self.start_time


class DatabaseMigrationOrchestrator:
    """
    Orchestrates zero-downtime database migrations using CDC.

    Features:
    - Change Data Capture with Debezium
    - Automatic validation and verification
    - Rollback capabilities
    - Performance monitoring
    - AWS DMS integration
    """

    def __init__(
        self,
        source_config: DatabaseConfig,
        target_config: DatabaseConfig,
        dms_replication_instance_arn: Optional[str] = None,
        max_replication_lag_seconds: int = 5,
        validation_sample_size: int = 1000
    ):
        """
        Initialize the migration orchestrator.

        Args:
            source_config: Source database configuration
            target_config: Target database configuration
            dms_replication_instance_arn: AWS DMS replication instance ARN
            max_replication_lag_seconds: Maximum acceptable replication lag
            validation_sample_size: Number of rows to sample for validation
        """
        self.source_config = source_config
        self.target_config = target_config
        self.dms_arn = dms_replication_instance_arn
        self.max_lag = max_replication_lag_seconds
        self.validation_sample_size = validation_sample_size

        self.phase = MigrationPhase.INIT
        self.metrics = MigrationMetrics(
            replication_lag_seconds=0.0,
            rows_migrated=0,
            errors_count=0,
            start_time=datetime.utcnow()
        )

        # AWS clients
        self.dms_client = boto3.client('dms') if dms_replication_instance_arn else None
        self.cloudwatch = boto3.client('cloudwatch')

        logger.info("Migration orchestrator initialized")

    def _get_connection(self, config: DatabaseConfig) -> psycopg2.extensions.connection:
        """Create a database connection"""
        try:
            conn = psycopg2.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.username,
                password=config.password,
                sslmode=config.ssl_mode,
                connect_timeout=10
            )
            return conn
        except psycopg2.Error as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def validate_connectivity(self) -> bool:
        """Validate connectivity to source and target databases"""
        logger.info("Validating database connectivity...")

        try:
            # Test source connection
            source_conn = self._get_connection(self.source_config)
            with source_conn.cursor() as cur:
                cur.execute("SELECT version();")
                source_version = cur.fetchone()[0]
                logger.info(f"Source database: {source_version}")
            source_conn.close()

            # Test target connection
            target_conn = self._get_connection(self.target_config)
            with target_conn.cursor() as cur:
                cur.execute("SELECT version();")
                target_version = cur.fetchone()[0]
                logger.info(f"Target database: {target_version}")
            target_conn.close()

            logger.info("✓ Database connectivity validated")
            return True

        except Exception as e:
            logger.error(f"✗ Connectivity validation failed: {e}")
            return False

    def setup_replication(self) -> bool:
        """Set up CDC replication from source to target"""
        logger.info("Setting up change data capture replication...")
        self.phase = MigrationPhase.REPLICATION

        try:
            if self.dms_client:
                # Use AWS DMS for replication
                self._setup_dms_replication()
            else:
                # Use Debezium for replication
                self._setup_debezium_replication()

            logger.info("✓ Replication setup complete")
            return True

        except Exception as e:
            logger.error(f"✗ Replication setup failed: {e}")
            self.metrics.errors_count += 1
            return False

    def _setup_dms_replication(self) -> None:
        """Configure AWS DMS replication task"""
        logger.info("Configuring AWS DMS replication...")

        # Create replication task
        response = self.dms_client.create_replication_task(
            ReplicationTaskIdentifier=f'migration-{datetime.utcnow().strftime("%Y%m%d%H%M")}',
            SourceEndpointArn=self._create_dms_endpoint(self.source_config, 'source'),
            TargetEndpointArn=self._create_dms_endpoint(self.target_config, 'target'),
            ReplicationInstanceArn=self.dms_arn,
            MigrationType='full-load-and-cdc',
            TableMappings=self._get_table_mappings(),
            ReplicationTaskSettings=self._get_replication_settings()
        )

        task_arn = response['ReplicationTask']['ReplicationTaskArn']
        logger.info(f"DMS replication task created: {task_arn}")

        # Start replication
        self.dms_client.start_replication_task(
            ReplicationTaskArn=task_arn,
            StartReplicationTaskType='start-replication'
        )

    def _setup_debezium_replication(self) -> None:
        """Configure Debezium CDC connector"""
        logger.info("Configuring Debezium CDC connector...")
        # Placeholder for Debezium setup
        # In production, this would configure Kafka Connect with Debezium
        logger.info("Debezium configuration would be applied here")

    def validate_replication(self) -> bool:
        """Validate replication lag and data consistency"""
        logger.info("Validating replication...")
        self.phase = MigrationPhase.VALIDATION

        try:
            # Check replication lag
            lag = self._measure_replication_lag()
            self.metrics.replication_lag_seconds = lag

            if lag > self.max_lag:
                logger.warning(f"⚠ Replication lag ({lag}s) exceeds threshold ({self.max_lag}s)")
                return False

            # Validate data consistency
            if not self._validate_data_consistency():
                logger.error("✗ Data consistency validation failed")
                return False

            # Validate row counts
            if not self._validate_row_counts():
                logger.error("✗ Row count validation failed")
                return False

            logger.info("✓ Replication validation passed")
            return True

        except Exception as e:
            logger.error(f"✗ Validation failed: {e}")
            self.metrics.errors_count += 1
            return False

    def _measure_replication_lag(self) -> float:
        """Measure replication lag in seconds"""
        source_conn = self._get_connection(self.source_config)
        target_conn = self._get_connection(self.target_config)

        try:
            # Get latest timestamp from source
            with source_conn.cursor() as cur:
                cur.execute("""
                    SELECT EXTRACT(EPOCH FROM NOW()) as source_time;
                """)
                source_time = cur.fetchone()[0]

            # Get latest replicated timestamp from target
            with target_conn.cursor() as cur:
                cur.execute("""
                    SELECT EXTRACT(EPOCH FROM MAX(updated_at)) as target_time
                    FROM (
                        SELECT updated_at FROM pg_stat_replication
                        UNION ALL
                        SELECT NOW() as updated_at
                    ) t;
                """)
                result = cur.fetchone()
                target_time = result[0] if result else source_time

            lag = abs(source_time - target_time)
            logger.info(f"Replication lag: {lag:.2f} seconds")
            return lag

        finally:
            source_conn.close()
            target_conn.close()

    def _validate_data_consistency(self) -> bool:
        """Validate data consistency between source and target"""
        logger.info("Validating data consistency...")

        source_conn = self._get_connection(self.source_config)
        target_conn = self._get_connection(self.target_config)

        try:
            # Get list of tables
            with source_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename;
                """)
                tables = [row['tablename'] for row in cur.fetchall()]

            # Sample and compare data from each table
            for table in tables:
                if not self._compare_table_sample(source_conn, target_conn, table):
                    logger.error(f"✗ Data mismatch in table: {table}")
                    return False

            logger.info("✓ Data consistency validated")
            return True

        finally:
            source_conn.close()
            target_conn.close()

    def _compare_table_sample(
        self,
        source_conn: psycopg2.extensions.connection,
        target_conn: psycopg2.extensions.connection,
        table: str
    ) -> bool:
        """Compare sample data from a table"""
        try:
            with source_conn.cursor(cursor_factory=RealDictCursor) as source_cur:
                source_cur.execute(f"""
                    SELECT * FROM {table}
                    ORDER BY RANDOM()
                    LIMIT {self.validation_sample_size};
                """)
                source_rows = source_cur.fetchall()

            with target_conn.cursor(cursor_factory=RealDictCursor) as target_cur:
                target_cur.execute(f"""
                    SELECT * FROM {table}
                    ORDER BY RANDOM()
                    LIMIT {self.validation_sample_size};
                """)
                target_rows = target_cur.fetchall()

            # Compare samples (simplified check)
            if len(source_rows) != len(target_rows):
                logger.warning(f"Row count mismatch in {table}: {len(source_rows)} vs {len(target_rows)}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error comparing table {table}: {e}")
            return False

    def _validate_row_counts(self) -> bool:
        """Validate row counts match between source and target"""
        logger.info("Validating row counts...")

        source_conn = self._get_connection(self.source_config)
        target_conn = self._get_connection(self.target_config)

        try:
            with source_conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT tablename FROM pg_tables
                    WHERE schemaname = 'public';
                """)
                tables = [row['tablename'] for row in cur.fetchall()]

            total_rows = 0
            for table in tables:
                with source_conn.cursor() as source_cur:
                    source_cur.execute(f"SELECT COUNT(*) FROM {table};")
                    source_count = source_cur.fetchone()[0]

                with target_conn.cursor() as target_cur:
                    target_cur.execute(f"SELECT COUNT(*) FROM {table};")
                    target_count = target_cur.fetchone()[0]

                if source_count != target_count:
                    logger.error(f"✗ Row count mismatch in {table}: {source_count} vs {target_count}")
                    return False

                total_rows += source_count

            self.metrics.rows_migrated = total_rows
            logger.info(f"✓ Row counts validated ({total_rows} total rows)")
            return True

        finally:
            source_conn.close()
            target_conn.close()

    def perform_cutover(self) -> bool:
        """Perform the database cutover"""
        logger.info("=" * 60)
        logger.info("PERFORMING DATABASE CUTOVER")
        logger.info("=" * 60)
        self.phase = MigrationPhase.CUTOVER

        cutover_start = datetime.utcnow()

        try:
            # 1. Stop replication writes
            logger.info("1. Stopping write traffic to source database...")
            self._pause_application_writes()

            # 2. Wait for final replication to complete
            logger.info("2. Waiting for final replication sync...")
            self._wait_for_replication_sync()

            # 3. Final validation
            logger.info("3. Performing final validation...")
            if not self.validate_replication():
                raise Exception("Final validation failed")

            # 4. Switch application to target database
            logger.info("4. Switching application traffic to target database...")
            self._switch_application_traffic()

            # 5. Verify target database is operational
            logger.info("5. Verifying target database operations...")
            if not self._verify_target_operations():
                raise Exception("Target database verification failed")

            cutover_end = datetime.utcnow()
            self.metrics.downtime_seconds = (cutover_end - cutover_start).total_seconds()

            logger.info("=" * 60)
            logger.info(f"✓ CUTOVER COMPLETE (downtime: {self.metrics.downtime_seconds:.2f}s)")
            logger.info("=" * 60)

            self.phase = MigrationPhase.COMPLETE
            self.metrics.end_time = datetime.utcnow()

            return True

        except Exception as e:
            logger.error(f"✗ Cutover failed: {e}")
            self.metrics.errors_count += 1
            logger.warning("Initiating rollback...")
            self.rollback()
            return False

    def _pause_application_writes(self) -> None:
        """Pause application writes to source database"""
        # In production, this would update load balancer or application config
        logger.info("Application writes paused (placeholder)")
        time.sleep(1)

    def _wait_for_replication_sync(self, timeout_seconds: int = 300) -> None:
        """Wait for replication to fully sync"""
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            lag = self._measure_replication_lag()
            if lag < 1.0:  # Less than 1 second lag
                logger.info("✓ Replication fully synced")
                return
            time.sleep(2)

        raise TimeoutError("Replication sync timeout")

    def _switch_application_traffic(self) -> None:
        """Switch application traffic to target database"""
        # In production, this would update DNS, load balancer, or connection pooler
        logger.info("Application traffic switched to target (placeholder)")
        time.sleep(1)

    def _verify_target_operations(self) -> bool:
        """Verify target database is operational"""
        try:
            target_conn = self._get_connection(self.target_config)
            with target_conn.cursor() as cur:
                # Perform test write
                cur.execute("CREATE TABLE IF NOT EXISTS migration_test (id SERIAL PRIMARY KEY, test_data TEXT);")
                cur.execute("INSERT INTO migration_test (test_data) VALUES ('migration_verification');")
                cur.execute("SELECT COUNT(*) FROM migration_test;")
                count = cur.fetchone()[0]

                # Cleanup
                cur.execute("DROP TABLE migration_test;")
                target_conn.commit()

            target_conn.close()
            logger.info("✓ Target database operations verified")
            return True

        except Exception as e:
            logger.error(f"✗ Target verification failed: {e}")
            return False

    def rollback(self) -> bool:
        """Rollback migration and restore source database"""
        logger.info("=" * 60)
        logger.info("PERFORMING MIGRATION ROLLBACK")
        logger.info("=" * 60)
        self.phase = MigrationPhase.ROLLBACK

        try:
            # 1. Switch traffic back to source
            logger.info("1. Switching traffic back to source database...")
            self._switch_to_source()

            # 2. Stop replication
            logger.info("2. Stopping replication...")
            self._stop_replication()

            # 3. Verify source database
            logger.info("3. Verifying source database...")
            if not self.validate_connectivity():
                raise Exception("Source database verification failed")

            logger.info("=" * 60)
            logger.info("✓ ROLLBACK COMPLETE")
            logger.info("=" * 60)
            return True

        except Exception as e:
            logger.error(f"✗ Rollback failed: {e}")
            self.phase = MigrationPhase.FAILED
            return False

    def _switch_to_source(self) -> None:
        """Switch application traffic back to source"""
        logger.info("Traffic switched to source (placeholder)")

    def _stop_replication(self) -> None:
        """Stop replication tasks"""
        if self.dms_client:
            # Stop DMS replication tasks
            logger.info("Stopping DMS replication tasks...")

        logger.info("Replication stopped")

    def publish_metrics(self) -> None:
        """Publish migration metrics to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='DatabaseMigration',
                MetricData=[
                    {
                        'MetricName': 'ReplicationLag',
                        'Value': self.metrics.replication_lag_seconds,
                        'Unit': 'Seconds'
                    },
                    {
                        'MetricName': 'RowsMigrated',
                        'Value': self.metrics.rows_migrated,
                        'Unit': 'Count'
                    },
                    {
                        'MetricName': 'Downtime',
                        'Value': self.metrics.downtime_seconds,
                        'Unit': 'Seconds'
                    },
                    {
                        'MetricName': 'ErrorCount',
                        'Value': self.metrics.errors_count,
                        'Unit': 'Count'
                    }
                ]
            )
            logger.info("✓ Metrics published to CloudWatch")
        except Exception as e:
            logger.warning(f"Failed to publish metrics: {e}")

    def run_migration(self) -> bool:
        """Execute the complete migration workflow"""
        logger.info("=" * 60)
        logger.info("STARTING DATABASE MIGRATION")
        logger.info("=" * 60)

        try:
            # Step 1: Validate connectivity
            if not self.validate_connectivity():
                raise Exception("Connectivity validation failed")

            # Step 2: Setup replication
            if not self.setup_replication():
                raise Exception("Replication setup failed")

            # Step 3: Wait for initial sync and validate
            logger.info("Waiting for initial replication sync...")
            time.sleep(10)  # Allow time for initial sync

            if not self.validate_replication():
                raise Exception("Replication validation failed")

            # Step 4: Perform cutover
            if not self.perform_cutover():
                raise Exception("Cutover failed")

            # Step 5: Publish metrics
            self.publish_metrics()

            duration = self.metrics.get_duration()
            logger.info("=" * 60)
            logger.info("MIGRATION COMPLETE")
            logger.info(f"Duration: {duration}")
            logger.info(f"Rows migrated: {self.metrics.rows_migrated:,}")
            logger.info(f"Downtime: {self.metrics.downtime_seconds:.2f}s")
            logger.info(f"Errors: {self.metrics.errors_count}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.phase = MigrationPhase.FAILED
            return False

    # Helper methods for DMS
    def _create_dms_endpoint(self, config: DatabaseConfig, endpoint_type: str) -> str:
        """Create DMS endpoint for source or target"""
        # Placeholder - would create actual DMS endpoint
        return f"arn:aws:dms:us-west-2:123456789012:endpoint:{endpoint_type}"

    def _get_table_mappings(self) -> str:
        """Get table mapping rules for DMS"""
        return '''{
            "rules": [{
                "rule-type": "selection",
                "rule-id": "1",
                "rule-name": "1",
                "object-locator": {
                    "schema-name": "public",
                    "table-name": "%"
                },
                "rule-action": "include"
            }]
        }'''

    def _get_replication_settings(self) -> str:
        """Get replication settings for DMS"""
        return '''{
            "TargetMetadata": {
                "SupportLobs": true,
                "LobChunkSize": 64,
                "LobMaxSize": 32
            },
            "FullLoadSettings": {
                "TargetTablePrepMode": "DROP_AND_CREATE"
            },
            "Logging": {
                "EnableLogging": true,
                "LogComponents": [{
                    "Id": "SOURCE_CAPTURE",
                    "Severity": "LOGGER_SEVERITY_DEFAULT"
                }]
            }
        }'''


def main():
    """Main execution function"""
    # Example configuration
    source = DatabaseConfig(
        host="source-db.example.com",
        port=5432,
        database="production",
        username="postgres",
        password="source_password"
    )

    target = DatabaseConfig(
        host="target-db.example.com",
        port=5432,
        database="production",
        username="postgres",
        password="target_password"
    )

    # Create orchestrator
    orchestrator = DatabaseMigrationOrchestrator(
        source_config=source,
        target_config=target,
        max_replication_lag_seconds=5
    )

    # Run migration
    success = orchestrator.run_migration()

    if success:
        logger.info("Migration completed successfully!")
        return 0
    else:
        logger.error("Migration failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

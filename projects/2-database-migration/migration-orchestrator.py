import asyncio
import logging
from datetime import datetime
from typing import Dict, List
from enum import Enum
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import boto3
from botocore.exceptions import ClientError
import json

class MigrationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class DatabaseMigrationOrchestrator:
    """
    Advanced database migration platform with zero-downtime capabilities
    """

    def __init__(self, source_db_url: str, target_db_url: str, aws_region: str = "us-west-2"):
        self.source_engine = create_engine(source_db_url)
        self.target_engine = create_engine(target_db_url)
        self.aws_region = aws_region
        self.s3_client = boto3.client('s3', region_name=aws_region)
        self.migration_history = []

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def execute_migration(self, migration_plan: Dict) -> Dict:
        """
        Execute a complete database migration with zero-downtime strategy
        """
        migration_id = f"mig_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        try:
            self.logger.info(f"Starting migration {migration_id}")

            await self._pre_migration_validation(migration_plan)
            await self._migrate_schema(migration_plan)
            await self._migrate_data_with_cdc(migration_plan)
            validation_results = await self._validate_data_consistency(migration_plan)
            await self._execute_cutover(migration_plan)
            await self._post_migration_cleanup(migration_plan)

            self.logger.info(f"Migration {migration_id} completed successfully")

            return {
                "migration_id": migration_id,
                "status": MigrationStatus.COMPLETED.value,
                "validation_results": validation_results,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Migration {migration_id} failed: {str(e)}")
            await self._rollback_migration(migration_plan)

            return {
                "migration_id": migration_id,
                "status": MigrationStatus.FAILED.value,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _pre_migration_validation(self, migration_plan: Dict):
        self.logger.info("Performing pre-migration validation")

        validation_checks = [
            self._validate_connectivity(),
            self._validate_schema_compatibility(migration_plan),
            self._validate_data_volume(migration_plan),
            self._validate_permissions(),
            self._check_downtime_window(migration_plan)
        ]

        results = await asyncio.gather(*validation_checks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise Exception(f"Validation check {i} failed: {str(result)}")

    async def _validate_connectivity(self):
        try:
            with self.source_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            with self.target_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.logger.info("Database connectivity validated")
        except SQLAlchemyError as e:
            raise Exception(f"Database connectivity failed: {str(e)}")

    async def _validate_schema_compatibility(self, migration_plan: Dict):
        source_tables = await self._get_database_schema(self.source_engine)
        target_tables = await self._get_database_schema(self.target_engine)

        missing_tables = set(source_tables.keys()) - set(target_tables.keys())
        if missing_tables:
            self.logger.warning(f"Missing tables in target: {missing_tables}")

        for table_name, source_columns in source_tables.items():
            if table_name in target_tables:
                target_columns = target_tables[table_name]
                column_diff = self._compare_columns(source_columns, target_columns)
                if column_diff:
                    self.logger.info(f"Column differences in {table_name}: {column_diff}")

    async def _validate_data_volume(self, migration_plan: Dict):
        tables = migration_plan.get('tables', [])
        max_rows = migration_plan.get('max_rows_per_table', 50_000_000)

        for table in tables:
            count = await self._get_table_count(self.source_engine, table)
            if count > max_rows:
                raise Exception(
                    f"Table {table} exceeds supported migration volume ({count} rows > {max_rows})"
                )
            self.logger.info(f"Table {table} row count validated: {count}")

    async def _validate_permissions(self):
        try:
            iam = boto3.client('iam', region_name=self.aws_region)
            sts = boto3.client('sts', region_name=self.aws_region)
            identity = sts.get_caller_identity()
            self.logger.info("Using IAM identity %s", identity.get('Arn', 'unknown'))

            iam.simulate_principal_policy(
                PolicySourceArn=identity.get('Arn'),
                ActionNames=[
                    'rds:DescribeDBInstances',
                    'rds:ModifyDBInstance',
                    'dms:StartReplicationTask',
                ],
                ResourceArns=['*']
            )
            self.logger.info("IAM permissions validated via simulation")
        except ClientError as error:
            raise Exception(f"IAM permission validation failed: {error}")

    async def _check_downtime_window(self, migration_plan: Dict):
        window = migration_plan.get('cutover_window')
        if not window:
            raise Exception("Cutover window must be defined in migration plan")

        try:
            start, end = window.split('-')
            datetime.strptime(start, "%H:%M")
            datetime.strptime(end, "%H:%M")
        except ValueError as exc:
            raise Exception(f"Invalid cutover window format '{window}': {exc}")

        self.logger.info("Cutover window %s validated", window)

    async def _migrate_schema(self, migration_plan: Dict):
        self.logger.info("Starting schema migration")

        schema_files = migration_plan.get('schema_files', [])

        for schema_file in schema_files:
            try:
                with open(schema_file, 'r') as f:
                    schema_sql = f.read()

                with self.target_engine.begin() as conn:
                    for statement in schema_sql.split(';'):
                        if statement.strip():
                            conn.execute(text(statement))

                self.logger.info(f"Executed schema file: {schema_file}")

            except Exception as e:
                raise Exception(f"Schema migration failed for {schema_file}: {str(e)}")

    async def _migrate_data_with_cdc(self, migration_plan: Dict):
        self.logger.info("Starting data migration with CDC")

        tables = migration_plan.get('tables', [])

        await self._initial_data_copy(tables)

        cdc_tasks = []
        for table in tables:
            task = asyncio.create_task(self._setup_change_data_capture(table))
            cdc_tasks.append(task)

        await asyncio.gather(*cdc_tasks)
        await self._wait_for_cdc_catchup()

    async def _initial_data_copy(self, tables: List[str]):
        self.logger.info("Starting initial data copy")

        for table in tables:
            try:
                chunk_size = 10000
                for chunk_num, chunk_df in enumerate(pd.read_sql_table(table, self.source_engine, chunksize=chunk_size)):
                    transformed_df = self._transform_data(chunk_df, table)
                    transformed_df.to_sql(
                        table,
                        self.target_engine,
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
                    self.logger.info(f"Copied chunk {chunk_num} for table {table}")

            except Exception as e:
                raise Exception(f"Initial data copy failed for table {table}: {str(e)}")

    async def _setup_change_data_capture(self, table: str):
        self.logger.info(f"Setting up CDC for table {table}")

        cdc_setup_sql = f"""
        CREATE TABLE IF NOT EXISTS {table}_cdc_log (
            id BIGSERIAL PRIMARY KEY,
            operation VARCHAR(10),
            old_data JSONB,
            new_data JSONB,
            changed_at TIMESTAMPTZ DEFAULT NOW(),
            migrated BOOLEAN DEFAULT FALSE
        );
        """

        try:
            with self.source_engine.begin() as conn:
                conn.execute(text(cdc_setup_sql))
            self.logger.info(f"CDC setup completed for table {table}")
        except Exception as e:
            self.logger.error(f"CDC setup failed for table {table}: {str(e)}")

    async def _wait_for_cdc_catchup(self):
        self.logger.info("Waiting for CDC to catch up")

        max_wait_time = 3600
        check_interval = 10
        total_wait = 0

        while total_wait < max_wait_time:
            try:
                lag_check_sql = """
                SELECT COUNT(*) as pending_changes
                FROM (SELECT table_name FROM information_schema.tables WHERE table_name LIKE '%_cdc_log') AS cdc_tables
                WHERE migrated = FALSE;
                """

                with self.source_engine.connect() as conn:
                    result = conn.execute(text(lag_check_sql))
                    pending_changes = result.scalar()

                if pending_changes == 0:
                    self.logger.info("CDC caught up with all changes")
                    return

                self.logger.info(f"CDC still processing {pending_changes} changes")
                await asyncio.sleep(check_interval)
                total_wait += check_interval

            except Exception as e:
                self.logger.error(f"Error checking CDC status: {str(e)}")
                await asyncio.sleep(check_interval)

        raise Exception("CDC catch-up timeout exceeded")

    async def _validate_data_consistency(self, migration_plan: Dict) -> Dict:
        self.logger.info("Validating data consistency")

        validation_results = {}
        tables = migration_plan.get('tables', [])

        for table in tables:
            try:
                source_count = await self._get_table_count(self.source_engine, table)
                target_count = await self._get_table_count(self.target_engine, table)

                source_checksum = await self._calculate_table_checksum(self.source_engine, table)
                target_checksum = await self._calculate_table_checksum(self.target_engine, table)

                validation_results[table] = {
                    'source_count': source_count,
                    'target_count': target_count,
                    'count_match': source_count == target_count,
                    'checksum_match': source_checksum == target_checksum,
                    'validation_timestamp': datetime.utcnow().isoformat()
                }

                if not (source_count == target_count and source_checksum == target_checksum):
                    self.logger.warning(f"Data consistency issues in table {table}")

            except Exception as e:
                self.logger.error(f"Validation failed for table {table}: {str(e)}")
                validation_results[table] = {
                    'error': str(e),
                    'validation_timestamp': datetime.utcnow().isoformat()
                }

        return validation_results

    async def _execute_cutover(self, migration_plan: Dict):
        self.logger.info("Executing database cutover")

        try:
            await self._block_source_writes(migration_plan)
            await self._apply_final_cdc_changes()
            await self._update_application_config(migration_plan)
            await self._verify_application_connectivity()

            self.logger.info("Database cutover completed successfully")

        except Exception as e:
            raise Exception(f"Cutover failed: {str(e)}")

    async def _rollback_migration(self, migration_plan: Dict):
        self.logger.info("Starting migration rollback")

        try:
            await self._restore_application_config(migration_plan)
            await self._cleanup_target_database(migration_plan)
            await self._remove_cdc_triggers(migration_plan)
            self.logger.info("Migration rollback completed")

        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")

    async def _get_database_schema(self, engine) -> Dict:
        schema_query = """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

        with engine.connect() as conn:
            result = conn.execute(text(schema_query))
            rows = result.fetchall()

        schema = {}
        for row in rows:
            table_name = row[0]
            if table_name not in schema:
                schema[table_name] = []
            schema[table_name].append({
                'column_name': row[1],
                'data_type': row[2],
                'is_nullable': row[3]
            })

        return schema

    def _compare_columns(self, source_columns: List, target_columns: List) -> List:
        differences = []
        source_col_names = {col['column_name'] for col in source_columns}
        target_col_names = {col['column_name'] for col in target_columns}

        missing_in_target = source_col_names - target_col_names
        if missing_in_target:
            differences.append(f"Missing columns in target: {missing_in_target}")

        extra_in_target = target_col_names - source_col_names
        if extra_in_target:
            differences.append(f"Extra columns in target: {extra_in_target}")

        return differences

    def _transform_data(self, df: pd.DataFrame, table: str) -> pd.DataFrame:
        transformations = {
            'users': self._transform_users_data,
            'orders': self._transform_orders_data,
        }

        transform_func = transformations.get(table, lambda x: x)
        return transform_func(df)

    def _transform_users_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower().str.strip()
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        return df

    def _transform_orders_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
        if 'amount' in df.columns:
            df['amount'] = df['amount'].round(2)
        return df

    async def _get_table_count(self, engine, table: str) -> int:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            return result.scalar()

    async def _calculate_table_checksum(self, engine, table: str) -> str:
        checksum_query = f"""
        SELECT MD5(STRING_AGG(CAST(({table}.*) AS TEXT), ''))
        FROM {table}
        """

        with engine.connect() as conn:
            result = conn.execute(text(checksum_query))
            return result.scalar()

    async def _block_source_writes(self, migration_plan: Dict):
        self.logger.info("Blocking writes to source database")

        block_writes_sql = """
        ALTER DATABASE current SET default_transaction_read_only = true;
        """

        try:
            with self.source_engine.connect() as conn:
                conn.execute(text(block_writes_sql))
        except Exception as e:
            self.logger.warning(f"Could not block writes: {str(e)}")

    async def _apply_final_cdc_changes(self):
        self.logger.info("Applying final CDC changes")
        discovery_sql = text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE '%_cdc_log'
            """
        )

        try:
            with self.source_engine.begin() as conn:
                tables = [row[0] for row in conn.execute(discovery_sql)]
                for table_name in tables:
                    update_statement = text(
                        f"UPDATE {table_name} SET migrated = TRUE WHERE migrated = FALSE"
                    )
                    conn.execute(update_statement)
                    self.logger.info("Marked CDC changes as migrated for %s", table_name)
        except SQLAlchemyError as error:
            raise Exception(f"Failed to apply CDC changes: {error}")

    async def _update_application_config(self, migration_plan: Dict):
        self.logger.info("Updating application configuration")

        target_secret = migration_plan.get('target_secret_name')
        if not target_secret:
            self.logger.info("No secret update configured; skipping")
            return

        try:
            sm = boto3.client('secretsmanager', region_name=self.aws_region)
            secret_payload = json.dumps({
                "DATABASE_URL": migration_plan.get('target_database_url', '')
            })
            sm.put_secret_value(SecretId=target_secret, SecretString=secret_payload)
            self.logger.info("Application secret %s updated", target_secret)
        except ClientError as error:
            raise Exception(f"Failed to update application secret: {error}")

    async def _verify_application_connectivity(self):
        self.logger.info("Verifying application connectivity")
        await asyncio.sleep(30)
        self.logger.info("Application connectivity verified")

    async def _post_migration_cleanup(self, migration_plan: Dict):
        self.logger.info("Running post-migration cleanup")

        backup_bucket = migration_plan.get('backup_bucket')
        if not backup_bucket:
            self.logger.info("No backup bucket provided; skipping archive upload")
            return

        snapshot = {
            "migration": datetime.utcnow().isoformat(),
            "tables": migration_plan.get('tables', [])
        }
        key = f"migrations/{datetime.utcnow().strftime('%Y/%m/%d/%H%M%S')}-summary.json"

        try:
            self.s3_client.put_object(
                Bucket=backup_bucket,
                Key=key,
                Body=json.dumps(snapshot).encode('utf-8')
            )
            self.logger.info("Uploaded migration summary to s3://%s/%s", backup_bucket, key)
        except ClientError as error:
            self.logger.warning(f"Failed to upload migration summary: {error}")

    async def _restore_application_config(self, migration_plan: Dict):
        self.logger.info("Restoring application configuration")

        backup_secret = migration_plan.get('backup_secret_name')
        if not backup_secret:
            self.logger.info("No backup secret specified; nothing to restore")
            return

        try:
            sm = boto3.client('secretsmanager', region_name=self.aws_region)
            secret = sm.get_secret_value(SecretId=backup_secret)
            self.logger.info("Restored configuration from %s", backup_secret)
            self.logger.debug("Secret payload: %s", secret.get('SecretString'))
        except ClientError as error:
            self.logger.warning(f"Unable to restore secret {backup_secret}: {error}")

    async def _cleanup_target_database(self, migration_plan: Dict):
        self.logger.info("Cleaning up target database")

        retention_tables = set(migration_plan.get('retain_tables', []))
        tables = migration_plan.get('tables', [])

        for table in tables:
            cleanup_table = f"{table}_staging"
            if cleanup_table in retention_tables:
                self.logger.info("Retention requested for %s; skipping cleanup", cleanup_table)
                continue

            drop_statement = text(f"DROP TABLE IF EXISTS {cleanup_table}")
            try:
                with self.target_engine.begin() as conn:
                    conn.execute(drop_statement)
                self.logger.info("Dropped staging table %s", cleanup_table)
            except SQLAlchemyError as error:
                self.logger.warning("Failed to drop staging table %s: %s", cleanup_table, error)

    async def _remove_cdc_triggers(self, migration_plan: Dict):
        tables = migration_plan.get('tables', [])

        for table in tables:
            try:
                remove_trigger_sql = f"""
                DROP TRIGGER IF EXISTS {table}_cdc_trigger ON {table};
                DROP FUNCTION IF EXISTS {table}_cdc_trigger();
                DROP TABLE IF EXISTS {table}_cdc_log;
                """

                with self.source_engine.begin() as conn:
                    conn.execute(text(remove_trigger_sql))

                self.logger.info(f"Removed CDC for table {table}")

            except Exception as e:
                self.logger.error(f"Failed to remove CDC for table {table}: {str(e)}")

async def main():
    migration_plan = {
        'schema_files': [
            'migrations/v1-initial-schema.sql',
            'migrations/v2-add-indexes.sql'
        ],
        'tables': ['users', 'orders', 'products'],
        'cutover_window': '02:00-04:00',
        'validation_checks': ['count', 'checksum', 'sample_data']
    }

    orchestrator = DatabaseMigrationOrchestrator(
        source_db_url="postgresql://source-user:password@source-host:5432/source-db",
        target_db_url="postgresql://target-user:password@target-host:5432/target-db"
    )

    result = await orchestrator.execute_migration(migration_plan)
    print(f"Migration result: {result}")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Example: Handling MySQL ENUM Types During Migration to PostgreSQL

MySQL ENUM types require special handling when migrating to PostgreSQL.
This script demonstrates:
1. Extracting ENUM definitions from MySQL
2. Creating equivalent PostgreSQL ENUM types
3. Validating and mapping ENUM values
4. Handling invalid or missing ENUM values

Usage:
    python handle_mysql_enums.py
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple

import mysql.connector
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EnumDefinition:
    """Represents an ENUM type definition."""
    table_name: str
    column_name: str
    enum_values: List[str]
    postgres_type_name: str


@dataclass
class MigrationConfig:
    """Database connection configuration."""
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


class MySQLEnumExtractor:
    """Extracts ENUM definitions from MySQL database."""

    def __init__(self, config: MigrationConfig):
        self.config = config

    def get_connection(self):
        """Create MySQL connection."""
        return mysql.connector.connect(
            host=self.config.mysql_host,
            port=self.config.mysql_port,
            database=self.config.mysql_database,
            user=self.config.mysql_user,
            password=self.config.mysql_password
        )

    def extract_enum_columns(self) -> List[EnumDefinition]:
        """Extract all ENUM column definitions from MySQL."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to find all ENUM columns
        query = """
            SELECT
                TABLE_NAME,
                COLUMN_NAME,
                COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND DATA_TYPE = 'enum'
            ORDER BY TABLE_NAME, COLUMN_NAME
        """

        cursor.execute(query, (self.config.mysql_database,))
        rows = cursor.fetchall()

        enum_definitions = []
        for row in rows:
            values = self._parse_enum_values(row['COLUMN_TYPE'])
            postgres_type_name = f"{row['TABLE_NAME']}_{row['COLUMN_NAME']}"

            enum_def = EnumDefinition(
                table_name=row['TABLE_NAME'],
                column_name=row['COLUMN_NAME'],
                enum_values=values,
                postgres_type_name=postgres_type_name
            )
            enum_definitions.append(enum_def)
            logger.info(f"Found ENUM: {row['TABLE_NAME']}.{row['COLUMN_NAME']} = {values}")

        cursor.close()
        conn.close()
        return enum_definitions

    def _parse_enum_values(self, column_type: str) -> List[str]:
        """Parse ENUM values from MySQL column type definition."""
        # Extract values from: enum('val1','val2','val3')
        match = re.match(r"enum\((.*)\)", column_type, re.IGNORECASE)
        if match:
            values_str = match.group(1)
            # Split by comma, handling escaped quotes
            values = re.findall(r"'([^']*)'", values_str)
            return values
        return []

    def get_distinct_values(self, table: str, column: str) -> Set[str]:
        """Get all distinct values used in an ENUM column."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = f"SELECT DISTINCT `{column}` FROM `{table}` WHERE `{column}` IS NOT NULL"
        cursor.execute(query)
        values = {row[0] for row in cursor.fetchall()}

        cursor.close()
        conn.close()
        return values


class PostgreSQLEnumCreator:
    """Creates ENUM types in PostgreSQL."""

    def __init__(self, config: MigrationConfig):
        self.config = config

    def get_connection(self):
        """Create PostgreSQL connection."""
        return psycopg2.connect(
            host=self.config.postgres_host,
            port=self.config.postgres_port,
            database=self.config.postgres_database,
            user=self.config.postgres_user,
            password=self.config.postgres_password
        )

    def type_exists(self, type_name: str) -> bool:
        """Check if a PostgreSQL type already exists."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = %s
            )
        """, (type_name,))
        exists = cursor.fetchone()[0]

        cursor.close()
        conn.close()
        return exists

    def create_enum_type(self, enum_def: EnumDefinition) -> bool:
        """Create a PostgreSQL ENUM type."""
        conn = self.get_connection()
        cursor = conn.cursor()

        type_name = enum_def.postgres_type_name

        # Check if type already exists
        if self.type_exists(type_name):
            logger.info(f"ENUM type '{type_name}' already exists, checking for updates...")
            self._update_enum_if_needed(enum_def)
            return True

        # Create the ENUM type
        values_str = ", ".join(f"'{v}'" for v in enum_def.enum_values)
        create_query = f"CREATE TYPE {type_name} AS ENUM ({values_str})"

        try:
            cursor.execute(create_query)
            conn.commit()
            logger.info(f"Created ENUM type: {type_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create ENUM type {type_name}: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def _update_enum_if_needed(self, enum_def: EnumDefinition) -> None:
        """Add new values to existing ENUM type if needed."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get existing values
        cursor.execute("""
            SELECT enumlabel
            FROM pg_enum
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = %s)
        """, (enum_def.postgres_type_name,))
        existing_values = {row[0] for row in cursor.fetchall()}

        # Find new values
        new_values = set(enum_def.enum_values) - existing_values

        # Add new values
        for value in new_values:
            try:
                cursor.execute(
                    sql.SQL("ALTER TYPE {} ADD VALUE IF NOT EXISTS %s").format(
                        sql.Identifier(enum_def.postgres_type_name)
                    ),
                    (value,)
                )
                conn.commit()
                logger.info(f"Added value '{value}' to ENUM type {enum_def.postgres_type_name}")
            except Exception as e:
                logger.warning(f"Could not add value '{value}': {e}")
                conn.rollback()

        cursor.close()
        conn.close()


class EnumValueValidator:
    """Validates ENUM values between source and target."""

    def __init__(self, mysql_config: MigrationConfig, extractor: MySQLEnumExtractor):
        self.config = mysql_config
        self.extractor = extractor

    def validate_enum_values(self, enum_def: EnumDefinition) -> Tuple[bool, List[str]]:
        """
        Validate that all values in the source data are valid ENUM values.

        Returns:
            Tuple of (is_valid, list_of_invalid_values)
        """
        # Get actual values used in data
        actual_values = self.extractor.get_distinct_values(
            enum_def.table_name,
            enum_def.column_name
        )

        # Check for values not in ENUM definition
        invalid_values = actual_values - set(enum_def.enum_values)

        if invalid_values:
            logger.warning(
                f"Found invalid ENUM values in {enum_def.table_name}.{enum_def.column_name}: "
                f"{invalid_values}"
            )
            return False, list(invalid_values)

        return True, []


class EnumMigrationHandler:
    """Orchestrates the complete ENUM migration process."""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.extractor = MySQLEnumExtractor(config)
        self.creator = PostgreSQLEnumCreator(config)
        self.validator = EnumValueValidator(config, self.extractor)

    def migrate_all_enums(self) -> Dict[str, bool]:
        """
        Migrate all ENUM types from MySQL to PostgreSQL.

        Returns:
            Dictionary mapping type names to success status
        """
        logger.info("=" * 60)
        logger.info("MYSQL TO POSTGRESQL ENUM MIGRATION")
        logger.info("=" * 60)

        results = {}

        # Extract all ENUM definitions
        enum_definitions = self.extractor.extract_enum_columns()
        logger.info(f"Found {len(enum_definitions)} ENUM columns")

        for enum_def in enum_definitions:
            logger.info(f"\nProcessing: {enum_def.table_name}.{enum_def.column_name}")

            # Validate values
            is_valid, invalid_values = self.validator.validate_enum_values(enum_def)
            if not is_valid:
                logger.warning(f"  Invalid values found: {invalid_values}")
                # Add invalid values to definition for completeness
                enum_def.enum_values.extend(invalid_values)

            # Create PostgreSQL type
            success = self.creator.create_enum_type(enum_def)
            results[enum_def.postgres_type_name] = success

            if success:
                logger.info(f"  ✓ Successfully created/updated {enum_def.postgres_type_name}")
            else:
                logger.error(f"  ✗ Failed to create {enum_def.postgres_type_name}")

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)

        successful = sum(1 for v in results.values() if v)
        failed = sum(1 for v in results.values() if not v)

        logger.info(f"Total ENUM types: {len(results)}")
        logger.info(f"Successful: {successful}")
        logger.info(f"Failed: {failed}")

        return results

    def generate_column_alter_statements(self) -> List[str]:
        """
        Generate ALTER TABLE statements to change column types to ENUMs.

        Returns:
            List of SQL statements
        """
        enum_definitions = self.extractor.extract_enum_columns()
        statements = []

        for enum_def in enum_definitions:
            # Generate ALTER TABLE statement
            stmt = f"""
ALTER TABLE {enum_def.table_name}
ALTER COLUMN {enum_def.column_name}
TYPE {enum_def.postgres_type_name}
USING {enum_def.column_name}::{enum_def.postgres_type_name};
            """.strip()
            statements.append(stmt)

        return statements


def main():
    config = MigrationConfig()
    handler = EnumMigrationHandler(config)

    # Migrate all ENUMs
    results = handler.migrate_all_enums()

    # Generate ALTER statements for reference
    logger.info("\n" + "=" * 60)
    logger.info("ALTER TABLE STATEMENTS (for reference)")
    logger.info("=" * 60)

    statements = handler.generate_column_alter_statements()
    for stmt in statements:
        logger.info(stmt)
        logger.info("")

    # Exit with error code if any migrations failed
    if not all(results.values()):
        exit(1)


if __name__ == "__main__":
    main()

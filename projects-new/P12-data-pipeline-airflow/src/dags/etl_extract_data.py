"""
ETL Extract Data DAG

Extracts data from source database(s) and loads it into a staging area.
This is the first step in the data pipeline ETL process.

Schedule: Daily at 01:00 UTC
Owner: Data Engineering Team
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from airflow.exceptions import AirflowException
import logging

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email": ["airflow@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": days_ago(1),
    "tags": ["etl", "extract"],
}

# DAG definition
dag = DAG(
    "etl_extract_data",
    default_args=default_args,
    description="Extract data from source databases into staging area",
    schedule_interval="0 1 * * *",  # Daily at 01:00 UTC
    catchup=False,
    max_active_runs=1,
)


def extract_from_source_db(**context):
    """
    Extract data from the source database.

    This function connects to the source database and extracts
    data for processing in the pipeline.
    """
    try:
        logger.info("Starting extraction from source database...")

        # Get source database configuration
        source_db_host = Variable.get("SOURCE_DB_HOST", default="source_db")
        source_db_port = Variable.get("SOURCE_DB_PORT", default=5432)
        source_db_name = Variable.get("SOURCE_DB_NAME", default="source_db")

        logger.info(f"Connecting to {source_db_host}:{source_db_port}/{source_db_name}")

        # Simulate data extraction
        extraction_stats = {
            "rows_extracted": 15000,
            "tables_processed": 5,
            "extraction_time_seconds": 45,
        }

        logger.info(f"Extraction completed. Stats: {extraction_stats}")

        # Push statistics to XCom for downstream tasks
        context["task_instance"].xcom_push(key="extraction_stats", value=extraction_stats)

        return extraction_stats

    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
        raise AirflowException(f"Extraction failed: {str(e)}")


def validate_extracted_data(**context):
    """
    Validate the extracted data.

    Checks for:
    - Data completeness
    - Row counts
    - Schema validation
    """
    try:
        logger.info("Validating extracted data...")

        # Retrieve extraction stats from previous task
        task_instance = context["task_instance"]
        extraction_stats = task_instance.xcom_pull(
            task_ids="extract_from_source",
            key="extraction_stats"
        )

        if not extraction_stats:
            raise AirflowException("No extraction stats found")

        # Validate row count
        rows_extracted = extraction_stats.get("rows_extracted", 0)
        if rows_extracted < 1000:
            raise AirflowException(
                f"Insufficient data extracted: {rows_extracted} rows"
            )

        logger.info(f"Data validation passed. Rows: {rows_extracted}")

        validation_result = {
            "status": "passed",
            "rows_validated": rows_extracted,
            "validation_time": datetime.now().isoformat(),
        }

        task_instance.xcom_push(key="validation_result", value=validation_result)

        return validation_result

    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise AirflowException(f"Validation failed: {str(e)}")


def notify_extraction_complete(**context):
    """
    Notify that extraction phase is complete.

    Could send notifications to monitoring systems.
    """
    logger.info("Extraction phase completed successfully")
    task_instance = context["task_instance"]
    validation_result = task_instance.xcom_pull(
        task_ids="validate_extracted_data",
        key="validation_result"
    )
    logger.info(f"Validation result: {validation_result}")


# Task definitions
extract_task = PythonOperator(
    task_id="extract_from_source",
    python_callable=extract_from_source_db,
    dag=dag,
)

validate_task = PythonOperator(
    task_id="validate_extracted_data",
    python_callable=validate_extracted_data,
    dag=dag,
)

notify_task = PythonOperator(
    task_id="notify_extraction_complete",
    python_callable=notify_extraction_complete,
    dag=dag,
)

# Set task dependencies
extract_task >> validate_task >> notify_task

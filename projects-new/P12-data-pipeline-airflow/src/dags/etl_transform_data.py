"""
ETL Transform Data DAG

Applies data transformations including cleaning, validation, and enrichment.
This is the second step in the data pipeline ETL process.

Schedule: Daily at 02:00 UTC
Owner: Data Engineering Team
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.branch_python import BranchPythonOperator
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
    "tags": ["etl", "transform"],
}

# DAG definition
dag = DAG(
    "etl_transform_data",
    default_args=default_args,
    description="Clean, validate, and transform staging data",
    schedule_interval="0 2 * * *",  # Daily at 02:00 UTC
    catchup=False,
    max_active_runs=1,
)


def clean_data(**context):
    """
    Clean the extracted data.

    Operations include:
    - Remove duplicates
    - Handle missing values
    - Standardize formats
    - Remove outliers
    """
    try:
        logger.info("Starting data cleaning...")

        # Simulate data cleaning
        cleaning_stats = {
            "rows_input": 15000,
            "rows_output": 14850,
            "duplicates_removed": 150,
            "nulls_handled": 45,
            "format_standardized": True,
        }

        logger.info(f"Data cleaning completed. Stats: {cleaning_stats}")
        context["task_instance"].xcom_push(key="cleaning_stats", value=cleaning_stats)

        return cleaning_stats

    except Exception as e:
        logger.error(f"Error during data cleaning: {str(e)}")
        raise AirflowException(f"Cleaning failed: {str(e)}")


def apply_transformations(**context):
    """
    Apply business logic transformations to the data.

    Transformations include:
    - Field calculations
    - Aggregations
    - Data enrichment
    - Derived field creation
    """
    try:
        logger.info("Applying data transformations...")

        task_instance = context["task_instance"]
        cleaning_stats = task_instance.xcom_pull(
            task_ids="clean_data",
            key="cleaning_stats"
        )

        rows_to_transform = cleaning_stats.get("rows_output", 0)

        # Simulate transformations
        transform_stats = {
            "rows_processed": rows_to_transform,
            "new_fields_created": 8,
            "aggregations_applied": 3,
            "enrichment_sources": 2,
            "transform_time_seconds": 120,
        }

        logger.info(f"Data transformations completed. Stats: {transform_stats}")
        task_instance.xcom_push(key="transform_stats", value=transform_stats)

        return transform_stats

    except Exception as e:
        logger.error(f"Error during transformation: {str(e)}")
        raise AirflowException(f"Transformation failed: {str(e)}")


def check_data_quality(**context):
    """
    Perform data quality checks.

    Checks include:
    - Null value rates
    - Value distribution analysis
    - Referential integrity
    - Business rule validation
    """
    try:
        logger.info("Running data quality checks...")

        task_instance = context["task_instance"]
        transform_stats = task_instance.xcom_pull(
            task_ids="apply_transformations",
            key="transform_stats"
        )

        # Simulate quality checks
        quality_metrics = {
            "null_rate": 0.002,
            "duplicate_rate": 0.0,
            "valid_range_check": True,
            "business_rule_pass_rate": 0.998,
            "overall_quality_score": 98.5,
        }

        logger.info(f"Quality checks completed. Score: {quality_metrics['overall_quality_score']}%")
        task_instance.xcom_push(key="quality_metrics", value=quality_metrics)

        return quality_metrics

    except Exception as e:
        logger.error(f"Error during quality checks: {str(e)}")
        raise AirflowException(f"Quality checks failed: {str(e)}")


def decide_quality_branch(**context):
    """
    Branch logic based on data quality score.

    Returns task_id to execute next based on quality metrics.
    """
    task_instance = context["task_instance"]
    quality_metrics = task_instance.xcom_pull(
        task_ids="check_data_quality",
        key="quality_metrics"
    )

    quality_score = quality_metrics.get("overall_quality_score", 0)

    if quality_score >= 95:
        logger.info(f"Quality score {quality_score} is acceptable. Proceeding to load.")
        return "notify_transform_complete"
    else:
        logger.warning(f"Quality score {quality_score} is below threshold. Manual review needed.")
        return "quality_alert"


def trigger_quality_alert(**context):
    """
    Trigger alert for manual review when quality score is low.
    """
    task_instance = context["task_instance"]
    quality_metrics = task_instance.xcom_pull(
        task_ids="check_data_quality",
        key="quality_metrics"
    )

    logger.error(f"Data quality alert triggered. Metrics: {quality_metrics}")
    raise AirflowException(
        f"Data quality threshold not met: {quality_metrics['overall_quality_score']}%"
    )


def notify_transform_complete(**context):
    """
    Notify that transform phase is complete.
    """
    logger.info("Transform phase completed successfully")
    task_instance = context["task_instance"]
    quality_metrics = task_instance.xcom_pull(
        task_ids="check_data_quality",
        key="quality_metrics"
    )
    logger.info(f"Final quality score: {quality_metrics['overall_quality_score']}%")


# Task definitions
clean_task = PythonOperator(
    task_id="clean_data",
    python_callable=clean_data,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="apply_transformations",
    python_callable=apply_transformations,
    dag=dag,
)

quality_task = PythonOperator(
    task_id="check_data_quality",
    python_callable=check_data_quality,
    dag=dag,
)

branch_task = BranchPythonOperator(
    task_id="decide_quality_branch",
    python_callable=decide_quality_branch,
    dag=dag,
)

alert_task = PythonOperator(
    task_id="quality_alert",
    python_callable=trigger_quality_alert,
    dag=dag,
)

notify_task = PythonOperator(
    task_id="notify_transform_complete",
    python_callable=notify_transform_complete,
    dag=dag,
)

# Set task dependencies
clean_task >> transform_task >> quality_task >> branch_task
branch_task >> [alert_task, notify_task]

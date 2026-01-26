"""
ETL Load Warehouse DAG

Loads transformed data into the data warehouse.
This is the final step in the data pipeline ETL process.

Schedule: Daily at 03:00 UTC
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
    "tags": ["etl", "load"],
}

# DAG definition
dag = DAG(
    "etl_load_warehouse",
    default_args=default_args,
    description="Load transformed data into data warehouse",
    schedule_interval="0 3 * * *",  # Daily at 03:00 UTC
    catchup=False,
    max_active_runs=1,
)


def prepare_for_load(**context):
    """
    Prepare data for loading into warehouse.

    Operations include:
    - Data format conversion
    - Schema mapping
    - Surrogate key generation
    - Partition preparation
    """
    try:
        logger.info("Preparing data for warehouse load...")

        # Simulate preparation
        prep_stats = {
            "rows_prepared": 14850,
            "partitions_created": 12,
            "surrogate_keys_generated": 14850,
            "format_conversion_successful": True,
            "prep_time_seconds": 30,
        }

        logger.info(f"Data preparation completed. Stats: {prep_stats}")
        context["task_instance"].xcom_push(key="prep_stats", value=prep_stats)

        return prep_stats

    except Exception as e:
        logger.error(f"Error during data preparation: {str(e)}")
        raise AirflowException(f"Preparation failed: {str(e)}")


def load_facts_table(**context):
    """
    Load fact table data into the warehouse.

    Loads the main fact table with:
    - Transactional data
    - Measures and metrics
    - Foreign key references
    """
    try:
        logger.info("Loading facts table into warehouse...")

        task_instance = context["task_instance"]
        prep_stats = task_instance.xcom_pull(
            task_ids="prepare_for_load", key="prep_stats"
        )

        rows_to_load = prep_stats.get("rows_prepared", 0)

        # Get warehouse configuration
        wh_host = Variable.get("WAREHOUSE_DB_HOST", default="warehouse_db")
        wh_db = Variable.get("WAREHOUSE_DB_NAME", default="warehouse")

        logger.info(f"Connecting to warehouse at {wh_host}/{wh_db}")

        # Simulate fact table load
        load_stats = {
            "rows_loaded": rows_to_load,
            "table_name": "fact_transactions",
            "load_method": "append",
            "load_time_seconds": 45,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Fact table load completed. Rows: {rows_to_load}")
        task_instance.xcom_push(key="facts_load_stats", value=load_stats)

        return load_stats

    except Exception as e:
        logger.error(f"Error loading facts table: {str(e)}")
        raise AirflowException(f"Facts load failed: {str(e)}")


def load_dimensions_table(**context):
    """
    Load dimension table data into the warehouse.

    Loads dimension tables with:
    - Reference data
    - Slowly changing dimensions (SCD)
    - Attribute hierarchies
    """
    try:
        logger.info("Loading dimensions table into warehouse...")

        task_instance = context["task_instance"]

        # Simulate dimension table load
        load_stats = {
            "tables_loaded": 5,
            "total_rows_loaded": 2500,
            "scd_type": "Type 2",
            "load_time_seconds": 15,
            "tables": [
                "dim_customer",
                "dim_product",
                "dim_date",
                "dim_location",
                "dim_channel",
            ],
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Dimensions load completed. Tables: {load_stats['tables_loaded']}")
        task_instance.xcom_push(key="dimensions_load_stats", value=load_stats)

        return load_stats

    except Exception as e:
        logger.error(f"Error loading dimensions table: {str(e)}")
        raise AirflowException(f"Dimensions load failed: {str(e)}")


def refresh_warehouse_views(**context):
    """
    Refresh materialized views and aggregations in warehouse.

    Refreshes:
    - Mart views
    - Aggregated tables
    - Summary tables
    """
    try:
        logger.info("Refreshing warehouse views...")

        # Simulate view refresh
        refresh_stats = {
            "views_refreshed": 8,
            "aggregations_refreshed": 5,
            "refresh_time_seconds": 60,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"View refresh completed. Views: {refresh_stats['views_refreshed']}"
        )
        context["task_instance"].xcom_push(key="refresh_stats", value=refresh_stats)

        return refresh_stats

    except Exception as e:
        logger.error(f"Error refreshing views: {str(e)}")
        raise AirflowException(f"View refresh failed: {str(e)}")


def validate_warehouse_load(**context):
    """
    Validate the loaded data in the warehouse.

    Validates:
    - Row counts match source
    - Foreign key integrity
    - Aggregations accuracy
    - Business rule compliance
    """
    try:
        logger.info("Validating warehouse load...")

        task_instance = context["task_instance"]
        facts_stats = task_instance.xcom_pull(
            task_ids="load_facts_table", key="facts_load_stats"
        )
        dimensions_stats = task_instance.xcom_pull(
            task_ids="load_dimensions_table", key="dimensions_load_stats"
        )

        # Simulate validation
        validation_result = {
            "facts_row_count": facts_stats.get("rows_loaded", 0),
            "dimensions_total_rows": dimensions_stats.get("total_rows_loaded", 0),
            "foreign_key_check": "passed",
            "aggregation_check": "passed",
            "business_rules_check": "passed",
            "overall_status": "success",
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"Warehouse validation completed. Status: {validation_result['overall_status']}"
        )
        task_instance.xcom_push(key="validation_result", value=validation_result)

        return validation_result

    except Exception as e:
        logger.error(f"Error validating warehouse load: {str(e)}")
        raise AirflowException(f"Validation failed: {str(e)}")


def notify_load_complete(**context):
    """
    Notify that load phase is complete.

    Could send notifications to monitoring systems or trigger
    downstream analytics pipelines.
    """
    logger.info("Load phase completed successfully")
    task_instance = context["task_instance"]
    validation_result = task_instance.xcom_pull(
        task_ids="validate_warehouse_load", key="validation_result"
    )
    logger.info(f"Load validation result: {validation_result}")


# Task definitions
prepare_task = PythonOperator(
    task_id="prepare_for_load",
    python_callable=prepare_for_load,
    dag=dag,
)

load_facts_task = PythonOperator(
    task_id="load_facts_table",
    python_callable=load_facts_table,
    dag=dag,
)

load_dims_task = PythonOperator(
    task_id="load_dimensions_table",
    python_callable=load_dimensions_table,
    dag=dag,
)

refresh_views_task = PythonOperator(
    task_id="refresh_warehouse_views",
    python_callable=refresh_warehouse_views,
    dag=dag,
)

validate_task = PythonOperator(
    task_id="validate_warehouse_load",
    python_callable=validate_warehouse_load,
    dag=dag,
)

notify_task = PythonOperator(
    task_id="notify_load_complete",
    python_callable=notify_load_complete,
    dag=dag,
)

# Set task dependencies
prepare_task >> [load_facts_task, load_dims_task]
[load_facts_task, load_dims_task] >> refresh_views_task >> validate_task >> notify_task

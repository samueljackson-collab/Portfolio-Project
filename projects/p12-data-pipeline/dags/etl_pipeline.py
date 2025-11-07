#!/usr/bin/env python3
"""ETL pipeline DAG."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def extract_data():
    """Extract data from source."""
    print("Extracting data...")
    return {'records': 100}

def transform_data(**context):
    """Transform extracted data."""
    print("Transforming data...")
    ti = context['ti']
    data = ti.xcom_pull(task_ids='extract')
    return {'transformed': data['records'] * 2}

def load_data(**context):
    """Load data to destination."""
    print("Loading data...")
    ti = context['ti']
    data = ti.xcom_pull(task_ids='transform')
    print(f"Loaded {data['transformed']} records")

with DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL pipeline example',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    extract = PythonOperator(
        task_id='extract',
        python_callable=extract_data,
    )

    transform = PythonOperator(
        task_id='transform',
        python_callable=transform_data,
    )

    load = PythonOperator(
        task_id='load',
        python_callable=load_data,
    )

    extract >> transform >> load

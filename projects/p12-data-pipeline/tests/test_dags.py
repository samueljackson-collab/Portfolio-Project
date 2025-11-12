"""Test DAG integrity."""
import pytest
from airflow.models import DagBag

def test_dag_loaded():
    """Test that DAGs are loaded correctly."""
    dagbag = DagBag(dag_folder='dags/', include_examples=False)
    assert len(dagbag.import_errors) == 0, f"DAG import errors: {dagbag.import_errors}"
    assert len(dagbag.dags) > 0, "No DAGs found"

def test_etl_pipeline_exists():
    """Test ETL pipeline DAG exists."""
    dagbag = DagBag(dag_folder='dags/', include_examples=False)
    assert 'etl_pipeline' in dagbag.dags

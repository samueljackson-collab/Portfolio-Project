"""
Test suite for DAG validation.

Tests that all DAGs are properly configured, have correct schedules,
owners, and basic structure.
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import DAGs
from src.dags.etl_extract_data import dag as extract_dag
from src.dags.etl_transform_data import dag as transform_dag
from src.dags.etl_load_warehouse import dag as load_dag
from src.dags.daily_analytics import dag as analytics_dag


class TestDAGValidation(unittest.TestCase):
    """Test cases for DAG validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.dags = {
            "etl_extract_data": extract_dag,
            "etl_transform_data": transform_dag,
            "etl_load_warehouse": load_dag,
            "daily_analytics": analytics_dag,
        }

    def test_dags_exist(self):
        """Test that all DAGs are properly instantiated."""
        for dag_name, dag in self.dags.items():
            self.assertIsNotNone(dag, f"DAG {dag_name} is None")

    def test_dag_names(self):
        """Test that DAGs have correct names."""
        expected_names = [
            "etl_extract_data",
            "etl_transform_data",
            "etl_load_warehouse",
            "daily_analytics",
        ]

        for dag_name, dag in self.dags.items():
            self.assertEqual(dag.dag_id, dag_name, f"DAG ID mismatch for {dag_name}")

    def test_dag_owners(self):
        """Test that DAGs have owners defined."""
        for dag_name, dag in self.dags.items():
            self.assertIsNotNone(dag.owner, f"DAG {dag_name} has no owner")
            self.assertNotEqual(dag.owner, "", f"DAG {dag_name} has empty owner")

    def test_dag_schedules(self):
        """Test that DAGs have schedule intervals defined."""
        expected_schedules = {
            "etl_extract_data": "0 1 * * *",
            "etl_transform_data": "0 2 * * *",
            "etl_load_warehouse": "0 3 * * *",
            "daily_analytics": "0 4 * * *",
        }

        for dag_name, dag in self.dags.items():
            if dag_name in expected_schedules:
                self.assertEqual(
                    str(dag.schedule_interval),
                    expected_schedules[dag_name],
                    f"Schedule interval mismatch for {dag_name}",
                )

    def test_dag_descriptions(self):
        """Test that DAGs have descriptions."""
        for dag_name, dag in self.dags.items():
            self.assertIsNotNone(dag.description, f"DAG {dag_name} has no description")
            self.assertGreater(
                len(dag.description), 0, f"DAG {dag_name} has empty description"
            )

    def test_dag_catchup_disabled(self):
        """Test that catchup is disabled for all DAGs."""
        for dag_name, dag in self.dags.items():
            self.assertFalse(dag.catchup, f"DAG {dag_name} has catchup enabled")

    def test_dag_max_active_runs(self):
        """Test that max_active_runs is set to prevent overlaps."""
        for dag_name, dag in self.dags.items():
            self.assertEqual(
                dag.max_active_runs, 1, f"DAG {dag_name} max_active_runs is not 1"
            )

    def test_dag_start_date_valid(self):
        """Test that DAGs have valid start dates."""
        for dag_name, dag in self.dags.items():
            self.assertIsNotNone(dag.start_date, f"DAG {dag_name} has no start_date")
            self.assertIsInstance(
                dag.start_date, datetime, f"DAG {dag_name} start_date is not a datetime"
            )

    def test_dag_default_view(self):
        """Test that DAGs have default_view set."""
        for dag_name, dag in self.dags.items():
            # default_view should be either not set or valid
            if hasattr(dag, "default_view"):
                valid_views = ["tree", "graph", "calendar"]
                if dag.default_view is not None:
                    self.assertIn(
                        dag.default_view,
                        valid_views,
                        f"DAG {dag_name} has invalid default_view",
                    )

    def test_extract_dag_structure(self):
        """Test etl_extract_data DAG structure."""
        dag = self.dags["etl_extract_data"]
        expected_tasks = [
            "extract_from_source",
            "validate_extracted_data",
            "notify_extraction_complete",
        ]

        task_ids = [task.task_id for task in dag.tasks]
        for task_id in expected_tasks:
            self.assertIn(
                task_id, task_ids, f"Expected task {task_id} not found in extract DAG"
            )

    def test_transform_dag_structure(self):
        """Test etl_transform_data DAG structure."""
        dag = self.dags["etl_transform_data"]
        expected_tasks = [
            "clean_data",
            "apply_transformations",
            "check_data_quality",
            "decide_quality_branch",
            "quality_alert",
            "notify_transform_complete",
        ]

        task_ids = [task.task_id for task in dag.tasks]
        for task_id in expected_tasks:
            self.assertIn(
                task_id, task_ids, f"Expected task {task_id} not found in transform DAG"
            )

    def test_load_dag_structure(self):
        """Test etl_load_warehouse DAG structure."""
        dag = self.dags["etl_load_warehouse"]
        expected_tasks = [
            "prepare_for_load",
            "load_facts_table",
            "load_dimensions_table",
            "refresh_warehouse_views",
            "validate_warehouse_load",
            "notify_load_complete",
        ]

        task_ids = [task.task_id for task in dag.tasks]
        for task_id in expected_tasks:
            self.assertIn(
                task_id, task_ids, f"Expected task {task_id} not found in load DAG"
            )

    def test_analytics_dag_structure(self):
        """Test daily_analytics DAG structure."""
        dag = self.dags["daily_analytics"]
        expected_tasks = [
            "calculate_kpis",
            "generate_customer_analytics",
            "generate_product_analytics",
            "generate_trend_analysis",
            "generate_report",
            "publish_report",
            "send_completion_notification",
        ]

        task_ids = [task.task_id for task in dag.tasks]
        for task_id in expected_tasks:
            self.assertIn(
                task_id, task_ids, f"Expected task {task_id} not found in analytics DAG"
            )


class TestDAGImports(unittest.TestCase):
    """Test that DAGs can be imported without errors."""

    def test_extract_dag_imports(self):
        """Test that extract DAG imports successfully."""
        try:
            from src.dags.etl_extract_data import dag

            self.assertIsNotNone(dag)
        except ImportError as e:
            self.fail(f"Failed to import etl_extract_data: {str(e)}")

    def test_transform_dag_imports(self):
        """Test that transform DAG imports successfully."""
        try:
            from src.dags.etl_transform_data import dag

            self.assertIsNotNone(dag)
        except ImportError as e:
            self.fail(f"Failed to import etl_transform_data: {str(e)}")

    def test_load_dag_imports(self):
        """Test that load DAG imports successfully."""
        try:
            from src.dags.etl_load_warehouse import dag

            self.assertIsNotNone(dag)
        except ImportError as e:
            self.fail(f"Failed to import etl_load_warehouse: {str(e)}")

    def test_analytics_dag_imports(self):
        """Test that analytics DAG imports successfully."""
        try:
            from src.dags.daily_analytics import dag

            self.assertIsNotNone(dag)
        except ImportError as e:
            self.fail(f"Failed to import daily_analytics: {str(e)}")


if __name__ == "__main__":
    unittest.main()

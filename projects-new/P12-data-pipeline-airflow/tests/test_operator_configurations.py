"""
Test suite for operator configurations.

Tests that operators are properly configured with correct parameters,
retry policies, and resource allocations.
"""

import unittest
from datetime import timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import DAGs
from src.dags.etl_extract_data import dag as extract_dag
from src.dags.etl_transform_data import dag as transform_dag
from src.dags.etl_load_warehouse import dag as load_dag
from src.dags.daily_analytics import dag as analytics_dag


class TestOperatorConfiguration(unittest.TestCase):
    """Test operator configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.dags = {
            "extract": extract_dag,
            "transform": transform_dag,
            "load": load_dag,
            "analytics": analytics_dag,
        }

    def test_all_operators_are_initialized(self):
        """Test that all operators are properly initialized."""
        for dag_name, dag in self.dags.items():
            self.assertGreater(len(dag.tasks), 0, f"DAG {dag_name} has no tasks")

            for task in dag.tasks:
                self.assertIsNotNone(task)
                self.assertIsNotNone(task.task_id)

    def test_python_operators_have_callables(self):
        """Test that PythonOperators have callable python_callable."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                # Check if it's a PythonOperator
                task_type = type(task).__name__
                if task_type == "PythonOperator":
                    self.assertIsNotNone(
                        task.python_callable,
                        f"PythonOperator {task.task_id} has no python_callable",
                    )
                    self.assertTrue(
                        callable(task.python_callable),
                        f"python_callable for {task.task_id} is not callable",
                    )

    def test_all_tasks_have_retry_configuration(self):
        """Test that all tasks have retry configuration."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                self.assertIsNotNone(
                    task.retries, f"Task {task.task_id} has no retries configuration"
                )
                self.assertGreaterEqual(
                    task.retries, 0, f"Task {task.task_id} has negative retries"
                )

    def test_all_tasks_have_retry_delay(self):
        """Test that all tasks have retry delay configured."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                if task.retries > 0:
                    self.assertIsNotNone(
                        task.retry_delay,
                        f"Task {task.task_id} has retries but no retry_delay",
                    )
                    self.assertIsInstance(
                        task.retry_delay,
                        timedelta,
                        f"Task {task.task_id} retry_delay is not a timedelta",
                    )

    def test_all_tasks_have_pool_set(self):
        """Test pool slot management for resource control."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                # pool_slots should be at least 1
                self.assertGreaterEqual(
                    task.pool_slots, 1, f"Task {task.task_id} has invalid pool_slots"
                )


class TestPythonOperatorDefaults(unittest.TestCase):
    """Test default configurations for PythonOperators."""

    def setUp(self):
        """Set up test fixtures."""
        self.extract_dag = extract_dag
        self.transform_dag = transform_dag
        self.load_dag = load_dag
        self.analytics_dag = analytics_dag

    def test_extract_dag_python_operators(self):
        """Test PythonOperator configurations in extract DAG."""
        expected_python_tasks = {
            "extract_from_source",
            "validate_extracted_data",
            "notify_extraction_complete",
        }

        for task in self.extract_dag.tasks:
            if task.task_id in expected_python_tasks:
                self.assertEqual(
                    type(task).__name__,
                    "PythonOperator",
                    f"Task {task.task_id} should be a PythonOperator",
                )
                self.assertIsNotNone(task.python_callable)

    def test_transform_dag_python_operators(self):
        """Test PythonOperator configurations in transform DAG."""
        expected_python_tasks = {
            "clean_data",
            "apply_transformations",
            "check_data_quality",
            "quality_alert",
            "notify_transform_complete",
        }

        for task in self.transform_dag.tasks:
            if task.task_id in expected_python_tasks:
                task_type = type(task).__name__
                self.assertIn(
                    task_type,
                    ["PythonOperator", "BranchPythonOperator"],
                    f"Task {task.task_id} should be a PythonOperator variant",
                )

    def test_load_dag_python_operators(self):
        """Test PythonOperator configurations in load DAG."""
        expected_python_tasks = {
            "prepare_for_load",
            "load_facts_table",
            "load_dimensions_table",
            "refresh_warehouse_views",
            "validate_warehouse_load",
            "notify_load_complete",
        }

        for task in self.load_dag.tasks:
            if task.task_id in expected_python_tasks:
                self.assertEqual(
                    type(task).__name__,
                    "PythonOperator",
                    f"Task {task.task_id} should be a PythonOperator",
                )
                self.assertIsNotNone(task.python_callable)

    def test_analytics_dag_python_operators(self):
        """Test PythonOperator configurations in analytics DAG."""
        expected_python_tasks = {
            "calculate_kpis",
            "generate_customer_analytics",
            "generate_product_analytics",
            "generate_trend_analysis",
            "generate_report",
            "publish_report",
            "send_completion_notification",
        }

        for task in self.analytics_dag.tasks:
            if task.task_id in expected_python_tasks:
                self.assertEqual(
                    type(task).__name__,
                    "PythonOperator",
                    f"Task {task.task_id} should be a PythonOperator",
                )
                self.assertIsNotNone(task.python_callable)


class TestRetryPolicies(unittest.TestCase):
    """Test retry policies for tasks."""

    def setUp(self):
        """Set up test fixtures."""
        self.dags = {
            "extract": extract_dag,
            "transform": transform_dag,
            "load": load_dag,
            "analytics": analytics_dag,
        }

    def test_extract_dag_retry_policy(self):
        """Test retry policy for extract DAG."""
        for task in self.extract_dag.tasks:
            self.assertEqual(
                task.retries,
                2,
                f"Extract DAG task {task.task_id} should have 2 retries",
            )

    def test_transform_dag_retry_policy(self):
        """Test retry policy for transform DAG."""
        for task in self.transform_dag.tasks:
            self.assertEqual(
                task.retries,
                2,
                f"Transform DAG task {task.task_id} should have 2 retries",
            )

    def test_load_dag_retry_policy(self):
        """Test retry policy for load DAG."""
        for task in self.load_dag.tasks:
            self.assertEqual(
                task.retries, 2, f"Load DAG task {task.task_id} should have 2 retries"
            )

    def test_analytics_dag_retry_policy(self):
        """Test retry policy for analytics DAG."""
        for task in self.analytics_dag.tasks:
            expected_retries = 1
            self.assertEqual(
                task.retries,
                expected_retries,
                f"Analytics DAG task {task.task_id} should have {expected_retries} retries",
            )

    def test_retry_delay_consistency(self):
        """Test that retry delays are reasonable."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                if task.retries > 0:
                    # Retry delay should be between 1 minute and 1 hour
                    min_delay = timedelta(minutes=1)
                    max_delay = timedelta(hours=1)

                    self.assertGreaterEqual(
                        task.retry_delay,
                        min_delay,
                        f"Task {task.task_id} retry_delay is too small",
                    )
                    self.assertLessEqual(
                        task.retry_delay,
                        max_delay,
                        f"Task {task.task_id} retry_delay is too large",
                    )


class TestEmailNotifications(unittest.TestCase):
    """Test email notification configurations."""

    def setUp(self):
        """Set up test fixtures."""
        self.dags = {
            "extract": extract_dag,
            "transform": transform_dag,
            "load": load_dag,
            "analytics": analytics_dag,
        }

    def test_email_on_failure_configured(self):
        """Test that email_on_failure is configured for tasks."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                # Check if email_on_failure is set (could be True or False)
                self.assertIsNotNone(
                    task.email_on_failure,
                    f"Task {task.task_id} has no email_on_failure configuration",
                )

    def test_email_on_retry_configured(self):
        """Test that email_on_retry is configured for tasks."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                # Check if email_on_retry is set (could be True or False)
                self.assertIsNotNone(
                    task.email_on_retry,
                    f"Task {task.task_id} has no email_on_retry configuration",
                )


class TestTaskTags(unittest.TestCase):
    """Test task tagging for organization."""

    def setUp(self):
        """Set up test fixtures."""
        self.dags = {
            "extract": extract_dag,
            "transform": transform_dag,
            "load": load_dag,
            "analytics": analytics_dag,
        }

    def test_dags_have_tags(self):
        """Test that DAGs have tags defined."""
        for dag_name, dag in self.dags.items():
            self.assertIsNotNone(dag.tags, f"DAG {dag_name} has no tags")
            self.assertGreater(len(dag.tags), 0, f"DAG {dag_name} has empty tags")

    def test_extract_dag_tags(self):
        """Test tags for extract DAG."""
        expected_tags = {"etl", "extract"}
        actual_tags = set(self.dags["extract"].tags)
        self.assertTrue(
            expected_tags.issubset(actual_tags),
            f"Extract DAG should have tags {expected_tags}",
        )

    def test_transform_dag_tags(self):
        """Test tags for transform DAG."""
        expected_tags = {"etl", "transform"}
        actual_tags = set(self.dags["transform"].tags)
        self.assertTrue(
            expected_tags.issubset(actual_tags),
            f"Transform DAG should have tags {expected_tags}",
        )

    def test_load_dag_tags(self):
        """Test tags for load DAG."""
        expected_tags = {"etl", "load"}
        actual_tags = set(self.dags["load"].tags)
        self.assertTrue(
            expected_tags.issubset(actual_tags),
            f"Load DAG should have tags {expected_tags}",
        )

    def test_analytics_dag_tags(self):
        """Test tags for analytics DAG."""
        expected_tags = {"analytics", "reporting"}
        actual_tags = set(self.dags["analytics"].tags)
        self.assertTrue(
            expected_tags.issubset(actual_tags),
            f"Analytics DAG should have tags {expected_tags}",
        )


if __name__ == "__main__":
    unittest.main()

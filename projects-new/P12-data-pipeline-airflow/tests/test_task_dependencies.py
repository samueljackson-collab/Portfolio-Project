"""
Test suite for task dependencies.

Tests that task dependencies are properly configured and that
the DAG execution flow is correct.
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import DAGs
from src.dags.etl_extract_data import dag as extract_dag
from src.dags.etl_transform_data import dag as transform_dag
from src.dags.etl_load_warehouse import dag as load_dag
from src.dags.daily_analytics import dag as analytics_dag


class TestExtractDAGDependencies(unittest.TestCase):
    """Test task dependencies for etl_extract_data DAG."""

    def setUp(self):
        """Set up test fixtures."""
        self.dag = extract_dag
        self.tasks = {task.task_id: task for task in self.dag.tasks}

    def test_extract_task_exists(self):
        """Test that extract_from_source task exists."""
        self.assertIn("extract_from_source", self.tasks)

    def test_validate_task_depends_on_extract(self):
        """Test that validate task depends on extract task."""
        validate_task = self.tasks["validate_extracted_data"]
        upstream_ids = {task.task_id for task in validate_task.upstream_list}

        self.assertIn(
            "extract_from_source",
            upstream_ids,
            "validate_extracted_data should depend on extract_from_source"
        )

    def test_notify_task_depends_on_validate(self):
        """Test that notify task depends on validate task."""
        notify_task = self.tasks["notify_extraction_complete"]
        upstream_ids = {task.task_id for task in notify_task.upstream_list}

        self.assertIn(
            "validate_extracted_data",
            upstream_ids,
            "notify_extraction_complete should depend on validate_extracted_data"
        )

    def test_linear_dependency_chain(self):
        """Test that extract DAG has linear dependency chain."""
        extract_task = self.tasks["extract_from_source"]
        validate_task = self.tasks["validate_extracted_data"]
        notify_task = self.tasks["notify_extraction_complete"]

        # Extract has no upstream
        self.assertEqual(len(extract_task.upstream_list), 0)

        # Validate depends only on extract
        self.assertEqual(len(validate_task.upstream_list), 1)
        self.assertIn(extract_task, validate_task.upstream_list)

        # Notify depends only on validate
        self.assertEqual(len(notify_task.upstream_list), 1)
        self.assertIn(validate_task, notify_task.upstream_list)


class TestTransformDAGDependencies(unittest.TestCase):
    """Test task dependencies for etl_transform_data DAG."""

    def setUp(self):
        """Set up test fixtures."""
        self.dag = transform_dag
        self.tasks = {task.task_id: task for task in self.dag.tasks}

    def test_clean_task_has_no_dependencies(self):
        """Test that clean_data task has no upstream dependencies."""
        clean_task = self.tasks["clean_data"]
        self.assertEqual(len(clean_task.upstream_list), 0)

    def test_transform_depends_on_clean(self):
        """Test that apply_transformations depends on clean_data."""
        transform_task = self.tasks["apply_transformations"]
        upstream_ids = {task.task_id for task in transform_task.upstream_list}

        self.assertIn(
            "clean_data",
            upstream_ids,
            "apply_transformations should depend on clean_data"
        )

    def test_quality_check_depends_on_transform(self):
        """Test that quality check depends on transform task."""
        quality_task = self.tasks["check_data_quality"]
        upstream_ids = {task.task_id for task in quality_task.upstream_list}

        self.assertIn(
            "apply_transformations",
            upstream_ids,
            "check_data_quality should depend on apply_transformations"
        )

    def test_branch_depends_on_quality_check(self):
        """Test that branch task depends on quality check."""
        branch_task = self.tasks["decide_quality_branch"]
        upstream_ids = {task.task_id for task in branch_task.upstream_list}

        self.assertIn(
            "check_data_quality",
            upstream_ids,
            "decide_quality_branch should depend on check_data_quality"
        )

    def test_branch_leads_to_two_paths(self):
        """Test that branch task has two downstream paths."""
        branch_task = self.tasks["decide_quality_branch"]
        downstream_ids = {task.task_id for task in branch_task.downstream_list}

        expected_downstream = {"quality_alert", "notify_transform_complete"}
        self.assertEqual(
            downstream_ids,
            expected_downstream,
            "Branch task should lead to quality_alert and notify_transform_complete"
        )

    def test_sequential_chain(self):
        """Test the sequential chain from clean to branch."""
        clean_task = self.tasks["clean_data"]
        transform_task = self.tasks["apply_transformations"]
        quality_task = self.tasks["check_data_quality"]
        branch_task = self.tasks["decide_quality_branch"]

        # Verify the chain
        self.assertIn(clean_task, transform_task.upstream_list)
        self.assertIn(transform_task, quality_task.upstream_list)
        self.assertIn(quality_task, branch_task.upstream_list)


class TestLoadDAGDependencies(unittest.TestCase):
    """Test task dependencies for etl_load_warehouse DAG."""

    def setUp(self):
        """Set up test fixtures."""
        self.dag = load_dag
        self.tasks = {task.task_id: task for task in self.dag.tasks}

    def test_prepare_task_has_no_dependencies(self):
        """Test that prepare_for_load has no upstream dependencies."""
        prepare_task = self.tasks["prepare_for_load"]
        self.assertEqual(len(prepare_task.upstream_list), 0)

    def test_load_tasks_depend_on_prepare(self):
        """Test that load tasks depend on prepare task."""
        prepare_task = self.tasks["prepare_for_load"]
        facts_task = self.tasks["load_facts_table"]
        dims_task = self.tasks["load_dimensions_table"]

        self.assertIn(prepare_task, facts_task.upstream_list)
        self.assertIn(prepare_task, dims_task.upstream_list)

    def test_refresh_views_depends_on_load_tasks(self):
        """Test that refresh_views depends on both load tasks."""
        refresh_task = self.tasks["refresh_warehouse_views"]
        upstream_ids = {task.task_id for task in refresh_task.upstream_list}

        expected_upstream = {"load_facts_table", "load_dimensions_table"}
        self.assertEqual(
            upstream_ids,
            expected_upstream,
            "refresh_warehouse_views should depend on both load tasks"
        )

    def test_validate_depends_on_refresh(self):
        """Test that validate depends on refresh_views."""
        validate_task = self.tasks["validate_warehouse_load"]
        upstream_ids = {task.task_id for task in validate_task.upstream_list}

        self.assertIn(
            "refresh_warehouse_views",
            upstream_ids,
            "validate_warehouse_load should depend on refresh_warehouse_views"
        )

    def test_notify_depends_on_validate(self):
        """Test that notify depends on validate."""
        notify_task = self.tasks["notify_load_complete"]
        upstream_ids = {task.task_id for task in notify_task.upstream_list}

        self.assertIn(
            "validate_warehouse_load",
            upstream_ids,
            "notify_load_complete should depend on validate_warehouse_load"
        )

    def test_fan_in_pattern(self):
        """Test the fan-in pattern where two tasks converge."""
        facts_task = self.tasks["load_facts_table"]
        dims_task = self.tasks["load_dimensions_table"]
        refresh_task = self.tasks["refresh_warehouse_views"]

        # Both load tasks should have refresh_task as downstream
        self.assertIn(refresh_task, facts_task.downstream_list)
        self.assertIn(refresh_task, dims_task.downstream_list)


class TestAnalyticsDAGDependencies(unittest.TestCase):
    """Test task dependencies for daily_analytics DAG."""

    def setUp(self):
        """Set up test fixtures."""
        self.dag = analytics_dag
        self.tasks = {task.task_id: task for task in self.dag.tasks}

    def test_analytics_tasks_have_no_dependencies(self):
        """Test that analytics generation tasks have no dependencies."""
        analytics_tasks = [
            "calculate_kpis",
            "generate_customer_analytics",
            "generate_product_analytics",
        ]

        for task_id in analytics_tasks:
            task = self.tasks[task_id]
            self.assertEqual(
                len(task.upstream_list),
                0,
                f"{task_id} should have no upstream dependencies"
            )

    def test_trend_analysis_depends_on_kpis(self):
        """Test that trend analysis depends on KPI calculation."""
        trend_task = self.tasks["generate_trend_analysis"]
        upstream_ids = {task.task_id for task in trend_task.upstream_list}

        self.assertIn(
            "calculate_kpis",
            upstream_ids,
            "generate_trend_analysis should depend on calculate_kpis"
        )

    def test_trend_analysis_depends_on_other_analytics(self):
        """Test that trend analysis waits for all analytics to complete."""
        trend_task = self.tasks["generate_trend_analysis"]
        upstream_ids = {task.task_id for task in trend_task.upstream_list}

        # Trend should depend on KPIs and other analytics
        expected_upstream = {
            "calculate_kpis",
            "generate_customer_analytics",
            "generate_product_analytics",
        }
        self.assertEqual(
            upstream_ids,
            expected_upstream,
            "generate_trend_analysis should depend on all analytics tasks"
        )

    def test_report_depends_on_trend_analysis(self):
        """Test that report generation depends on trend analysis."""
        report_task = self.tasks["generate_report"]
        upstream_ids = {task.task_id for task in report_task.upstream_list}

        self.assertIn(
            "generate_trend_analysis",
            upstream_ids,
            "generate_report should depend on generate_trend_analysis"
        )

    def test_publish_depends_on_report(self):
        """Test that publish depends on report generation."""
        publish_task = self.tasks["publish_report"]
        upstream_ids = {task.task_id for task in publish_task.upstream_list}

        self.assertIn(
            "generate_report",
            upstream_ids,
            "publish_report should depend on generate_report"
        )

    def test_notify_depends_on_publish(self):
        """Test that notification depends on publish."""
        notify_task = self.tasks["send_completion_notification"]
        upstream_ids = {task.task_id for task in notify_task.upstream_list}

        self.assertIn(
            "publish_report",
            upstream_ids,
            "send_completion_notification should depend on publish_report"
        )

    def test_fan_out_to_fan_in_pattern(self):
        """Test the fan-out to fan-in pattern in analytics DAG."""
        # Three tasks start in parallel
        kpi_task = self.tasks["calculate_kpis"]
        customer_task = self.tasks["generate_customer_analytics"]
        product_task = self.tasks["generate_product_analytics"]

        # Trend task waits for all three
        trend_task = self.tasks["generate_trend_analysis"]

        self.assertIn(kpi_task, trend_task.upstream_list)
        self.assertIn(customer_task, trend_task.upstream_list)
        self.assertIn(product_task, trend_task.upstream_list)


class TestDependencyConsistency(unittest.TestCase):
    """Test overall consistency of DAG dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.dags = {
            "extract": extract_dag,
            "transform": transform_dag,
            "load": load_dag,
            "analytics": analytics_dag,
        }

    def test_no_circular_dependencies(self):
        """Test that no DAG has circular dependencies."""
        for dag_name, dag in self.dags.items():
            try:
                # This will raise an exception if there are circular dependencies
                _ = dag.topological_sort()
            except Exception as e:
                self.fail(f"DAG {dag_name} has circular dependencies: {str(e)}")

    def test_all_tasks_have_owners(self):
        """Test that all tasks have owners defined."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                self.assertIsNotNone(
                    task.owner,
                    f"Task {task.task_id} in {dag_name} has no owner"
                )

    def test_all_tasks_have_retries_configured(self):
        """Test that all tasks have retry configuration."""
        for dag_name, dag in self.dags.items():
            for task in dag.tasks:
                # Check that retries is at least 0
                self.assertGreaterEqual(
                    task.retries,
                    0,
                    f"Task {task.task_id} in {dag_name} has invalid retries"
                )


if __name__ == "__main__":
    unittest.main()

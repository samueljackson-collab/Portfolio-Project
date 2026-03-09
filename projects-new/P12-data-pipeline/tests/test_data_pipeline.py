"""
Tests for P12 Data Pipeline (Airflow DAG simulation).

Covers:
- Individual ETL step functions (extract, transform, load)
- Full DAG run orchestration
- Artifact log generation
- Step ordering and content validation
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import extract, transform, load, run_dag, main


class TestExtract:
    """Unit tests for the extract step."""

    def test_returns_string(self):
        """Extract must return a string filename."""
        result = extract()
        assert isinstance(result, str)

    def test_returns_csv_filename(self):
        """Extract output must be a CSV file reference."""
        result = extract()
        assert result.endswith(".csv")

    def test_filename_not_empty(self):
        """Extract must return a non-empty filename."""
        result = extract()
        assert len(result) > 0


class TestTransform:
    """Unit tests for the transform step."""

    def test_returns_string(self):
        """Transform must return a string filename."""
        result = transform("sales_data.csv")
        assert isinstance(result, str)

    def test_output_is_parquet(self):
        """Transform output must reference a Parquet file."""
        result = transform("raw_events.csv")
        assert result.endswith(".parquet")

    def test_removes_csv_extension(self):
        """Transform must not retain the .csv extension."""
        result = transform("dataset.csv")
        assert ".csv" not in result

    def test_includes_clean_prefix(self):
        """Transform must prefix output with 'clean_'."""
        result = transform("transactions.csv")
        assert result.startswith("clean_")

    def test_preserves_base_name(self):
        """Transform must preserve the base file name."""
        result = transform("monthly_report.csv")
        assert "monthly_report" in result


class TestLoad:
    """Unit tests for the load step."""

    def test_returns_string(self):
        """Load must return a string result."""
        result = load("clean_sales.parquet")
        assert isinstance(result, str)

    def test_result_starts_with_loaded(self):
        """Load result must start with 'loaded:' prefix."""
        result = load("clean_data.parquet")
        assert result.startswith("loaded:")

    def test_dataset_name_in_result(self):
        """Load result must include the dataset name."""
        result = load("clean_transactions.parquet")
        assert "clean_transactions.parquet" in result


class TestRunDag:
    """Integration tests for the full DAG orchestration."""

    def test_returns_list(self):
        """run_dag must return a list of log steps."""
        result = run_dag()
        assert isinstance(result, list)

    def test_returns_non_empty_list(self):
        """DAG run must produce at least one log entry."""
        result = run_dag()
        assert len(result) > 0

    def test_starts_with_starting_message(self):
        """First step must indicate DAG start."""
        result = run_dag()
        assert any("Starting DAG run" in step for step in result)

    def test_extract_step_logged(self):
        """Extract step must appear in DAG log."""
        result = run_dag()
        assert any("extract" in step.lower() for step in result)

    def test_transform_step_logged(self):
        """Transform step must appear in DAG log."""
        result = run_dag()
        assert any("transform" in step.lower() for step in result)

    def test_load_step_logged(self):
        """Load step must appear in DAG log."""
        result = run_dag()
        assert any("load" in step.lower() for step in result)

    def test_ends_with_success_message(self):
        """Last step must indicate successful completion."""
        result = run_dag()
        assert any("completed" in step.lower() for step in result[-3:])

    def test_extract_before_transform(self):
        """Extract step must appear before transform step in log."""
        result = run_dag()
        extract_idx = next(
            (i for i, s in enumerate(result) if "extract" in s.lower()), None
        )
        transform_idx = next(
            (i for i, s in enumerate(result) if "transform" in s.lower()), None
        )
        assert extract_idx is not None
        assert transform_idx is not None
        assert extract_idx < transform_idx, "Extract must run before transform"

    def test_transform_before_load(self):
        """Transform step must appear before load step in log."""
        result = run_dag()
        transform_idx = next(
            (i for i, s in enumerate(result) if "transform" in s.lower()), None
        )
        load_idx = next(
            (i for i, s in enumerate(result) if "load ->" in s.lower()), None
        )
        assert transform_idx is not None
        assert load_idx is not None
        assert transform_idx < load_idx, "Transform must run before load"

    def test_timestamps_in_log(self):
        """Log entries with timestamps must use UTC ISO-8601 format."""
        result = run_dag()
        timestamped = [s for s in result if s.startswith("[")]
        assert len(timestamped) > 0
        for entry in timestamped:
            assert "Z]" in entry, f"Timestamp entry missing UTC 'Z': {entry}"

    def test_parquet_file_produced(self):
        """Transform step must reference a parquet output file."""
        result = run_dag()
        parquet_entries = [s for s in result if ".parquet" in s]
        assert len(parquet_entries) > 0, "No parquet file reference found in DAG log"


class TestArtifactGeneration:
    """Tests for artifact log file creation."""

    def test_main_creates_artifact(self, tmp_path, monkeypatch):
        """Running main() must produce a log artifact file."""
        import app as app_module

        original_artifact = app_module.ARTIFACT
        artifact_path = tmp_path / "airflow_dag_run.log"
        monkeypatch.setattr(app_module, "ARTIFACT", artifact_path)

        app_module.main()

        assert artifact_path.exists(), "Artifact log file was not created"
        assert artifact_path.stat().st_size > 0, "Artifact log file is empty"

        app_module.ARTIFACT = original_artifact

    def test_artifact_contains_dag_steps(self, tmp_path, monkeypatch):
        """Artifact log must contain DAG step entries."""
        import app as app_module

        artifact_path = tmp_path / "airflow_dag_run.log"
        monkeypatch.setattr(app_module, "ARTIFACT", artifact_path)

        app_module.main()

        content = artifact_path.read_text()
        assert "extract" in content.lower()
        assert "transform" in content.lower()
        assert "load" in content.lower()

        app_module.ARTIFACT = Path("artifacts/airflow_dag_run.log")

    def test_artifact_records_completion(self, tmp_path, monkeypatch):
        """Artifact log must record successful DAG completion."""
        import app as app_module

        artifact_path = tmp_path / "airflow_dag_run.log"
        monkeypatch.setattr(app_module, "ARTIFACT", artifact_path)

        app_module.main()

        content = artifact_path.read_text()
        assert "completed" in content.lower()

        app_module.ARTIFACT = Path("artifacts/airflow_dag_run.log")

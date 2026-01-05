"""Enhanced experiment tracking and model registry management."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import mlflow
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperimentTracker:
    """Enhanced experiment tracking with MLflow."""

    def __init__(self, tracking_uri: str = "http://localhost:5000"):
        """
        Initialize experiment tracker.

        Args:
            tracking_uri: MLflow tracking server URI
        """
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient(tracking_uri=tracking_uri)
        logger.info(f"Connected to MLflow at {tracking_uri}")

    def list_experiments(self) -> List[Dict[str, Any]]:
        """
        List all experiments.

        Returns:
            List of experiment information
        """
        experiments = self.client.search_experiments()

        results = []
        for exp in experiments:
            results.append(
                {
                    "experiment_id": exp.experiment_id,
                    "name": exp.name,
                    "artifact_location": exp.artifact_location,
                    "lifecycle_stage": exp.lifecycle_stage,
                }
            )

        return results

    def get_experiment_runs(
        self,
        experiment_name: str,
        max_results: int = 100,
        order_by: str = "metrics.accuracy DESC",
    ) -> List[Dict[str, Any]]:
        """
        Get runs for an experiment.

        Args:
            experiment_name: Name of experiment
            max_results: Maximum number of runs to return
            order_by: Ordering criteria

        Returns:
            List of run information
        """
        experiment = self.client.get_experiment_by_name(experiment_name)

        if not experiment:
            logger.warning(f"Experiment '{experiment_name}' not found")
            return []

        runs = self.client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=max_results,
            order_by=[order_by],
        )

        results = []
        for run in runs:
            results.append(
                {
                    "run_id": run.info.run_id,
                    "start_time": datetime.fromtimestamp(run.info.start_time / 1000),
                    "end_time": (
                        datetime.fromtimestamp(run.info.end_time / 1000)
                        if run.info.end_time
                        else None
                    ),
                    "status": run.info.status,
                    "params": run.data.params,
                    "metrics": run.data.metrics,
                    "tags": run.data.tags,
                }
            )

        return results

    def get_best_run(
        self, experiment_name: str, metric: str = "accuracy", maximize: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get best run from an experiment.

        Args:
            experiment_name: Name of experiment
            metric: Metric to optimize
            maximize: Whether to maximize (True) or minimize (False) metric

        Returns:
            Best run information
        """
        order_direction = "DESC" if maximize else "ASC"
        runs = self.get_experiment_runs(
            experiment_name,
            max_results=1,
            order_by=f"metrics.{metric} {order_direction}",
        )

        return runs[0] if runs else None

    def compare_runs(
        self, run_ids: List[str], metrics: List[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple runs.

        Args:
            run_ids: List of run IDs to compare
            metrics: List of metrics to compare (None for all)

        Returns:
            Comparison results
        """
        comparison = {}

        for run_id in run_ids:
            run = self.client.get_run(run_id)

            run_data = {
                "params": run.data.params,
                "metrics": (
                    run.data.metrics
                    if metrics is None
                    else {k: v for k, v in run.data.metrics.items() if k in metrics}
                ),
                "start_time": datetime.fromtimestamp(run.info.start_time / 1000),
                "duration_seconds": (
                    (run.info.end_time - run.info.start_time) / 1000
                    if run.info.end_time
                    else None
                ),
            }

            comparison[run_id] = run_data

        return comparison

    def tag_run(self, run_id: str, tags: Dict[str, str]):
        """
        Add tags to a run.

        Args:
            run_id: Run ID
            tags: Dictionary of tags
        """
        for key, value in tags.items():
            self.client.set_tag(run_id, key, value)

        logger.info(f"Added tags to run {run_id}: {tags}")

    def delete_run(self, run_id: str):
        """
        Delete a run.

        Args:
            run_id: Run ID to delete
        """
        self.client.delete_run(run_id)
        logger.info(f"Deleted run: {run_id}")

    def export_run(self, run_id: str, output_path: str):
        """
        Export run data to JSON.

        Args:
            run_id: Run ID
            output_path: Output file path
        """
        run = self.client.get_run(run_id)

        data = {
            "run_id": run.info.run_id,
            "experiment_id": run.info.experiment_id,
            "status": run.info.status,
            "start_time": datetime.fromtimestamp(
                run.info.start_time / 1000
            ).isoformat(),
            "end_time": (
                datetime.fromtimestamp(run.info.end_time / 1000).isoformat()
                if run.info.end_time
                else None
            ),
            "params": run.data.params,
            "metrics": run.data.metrics,
            "tags": run.data.tags,
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported run to {output_path}")


class ModelRegistry:
    """Model registry management."""

    def __init__(self, tracking_uri: str = "http://localhost:5000"):
        """
        Initialize model registry.

        Args:
            tracking_uri: MLflow tracking server URI
        """
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient(tracking_uri=tracking_uri)
        logger.info("Model registry initialized")

    def list_registered_models(self) -> List[Dict[str, Any]]:
        """
        List all registered models.

        Returns:
            List of registered models
        """
        models = self.client.search_registered_models()

        results = []
        for model in models:
            latest_versions = self.client.get_latest_versions(model.name)

            results.append(
                {
                    "name": model.name,
                    "creation_time": datetime.fromtimestamp(
                        model.creation_timestamp / 1000
                    ),
                    "last_updated": datetime.fromtimestamp(
                        model.last_updated_timestamp / 1000
                    ),
                    "description": model.description,
                    "latest_versions": [
                        {
                            "version": v.version,
                            "stage": v.current_stage,
                            "run_id": v.run_id,
                        }
                        for v in latest_versions
                    ],
                }
            )

        return results

    def get_model_versions(self, model_name: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a model.

        Args:
            model_name: Name of registered model

        Returns:
            List of model versions
        """
        versions = self.client.search_model_versions(f"name='{model_name}'")

        results = []
        for v in versions:
            results.append(
                {
                    "version": v.version,
                    "stage": v.current_stage,
                    "run_id": v.run_id,
                    "creation_time": datetime.fromtimestamp(
                        v.creation_timestamp / 1000
                    ),
                    "last_updated": datetime.fromtimestamp(
                        v.last_updated_timestamp / 1000
                    ),
                    "description": v.description,
                    "status": v.status,
                }
            )

        return results

    def transition_model_stage(
        self, model_name: str, version: int, stage: str, archive_existing: bool = True
    ):
        """
        Transition model version to a new stage.

        Args:
            model_name: Name of registered model
            version: Model version
            stage: Target stage (Staging, Production, Archived)
            archive_existing: Whether to archive existing versions in target stage
        """
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage,
            archive_existing_versions=archive_existing,
        )

        logger.info(f"Transitioned {model_name} v{version} to {stage}")

    def promote_to_production(self, model_name: str, version: int):
        """
        Promote model version to production.

        Args:
            model_name: Name of registered model
            version: Model version
        """
        self.transition_model_stage(model_name, version, "Production")
        logger.info(f"Promoted {model_name} v{version} to Production")

    def delete_model_version(self, model_name: str, version: int):
        """
        Delete a model version.

        Args:
            model_name: Name of registered model
            version: Model version
        """
        self.client.delete_model_version(model_name, version)
        logger.info(f"Deleted {model_name} v{version}")

    def add_model_description(self, model_name: str, version: int, description: str):
        """
        Add description to model version.

        Args:
            model_name: Name of registered model
            version: Model version
            description: Description text
        """
        self.client.update_model_version(
            name=model_name, version=version, description=description
        )

        logger.info(f"Updated description for {model_name} v{version}")

    def get_production_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current production model version.

        Args:
            model_name: Name of registered model

        Returns:
            Production model information
        """
        versions = self.client.get_latest_versions(model_name, stages=["Production"])

        if not versions:
            logger.warning(f"No production version for {model_name}")
            return None

        v = versions[0]
        return {
            "version": v.version,
            "run_id": v.run_id,
            "creation_time": datetime.fromtimestamp(v.creation_timestamp / 1000),
            "description": v.description,
        }


def main():
    """Example usage of experiment tracker and model registry."""
    # Initialize tracker
    tracker = ExperimentTracker()

    # List experiments
    print("\n=== Experiments ===")
    experiments = tracker.list_experiments()
    for exp in experiments:
        print(f"- {exp['name']} (ID: {exp['experiment_id']})")

    # Get best run from an experiment
    print("\n=== Best Run ===")
    if experiments:
        exp_name = experiments[0]["name"]
        best_run = tracker.get_best_run(exp_name, metric="accuracy")
        if best_run:
            print(f"Run ID: {best_run['run_id']}")
            print(f"Accuracy: {best_run['metrics'].get('accuracy', 'N/A')}")

    # Initialize model registry
    registry = ModelRegistry()

    # List registered models
    print("\n=== Registered Models ===")
    models = registry.list_registered_models()
    for model in models:
        print(f"- {model['name']}")
        for v in model["latest_versions"]:
            print(f"  v{v['version']} ({v['stage']})")

    # Get production model
    print("\n=== Production Models ===")
    for model in models:
        prod = registry.get_production_model(model["name"])
        if prod:
            print(f"{model['name']}: v{prod['version']}")


if __name__ == "__main__":
    main()

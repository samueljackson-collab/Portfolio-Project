"""Machine learning pipeline with experiment tracking, hyperparameter tuning, and deployment utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import mlflow
import numpy as np
import optuna
import pandas as pd
from mlflow.tracking import MlflowClient
from optuna.integration.mlflow import MLflowCallback
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class DatasetConfig:
    """Configuration describing where the dataset lives and how it should be parsed."""

    path: Path
    target_column: str
    categorical_features: List[str]
    numeric_features: List[str]


@dataclass
class ExperimentConfig:
    """Parameters for running an automated training experiment."""

    name: str
    dataset: DatasetConfig
    test_size: float = 0.2
    random_state: int = 42
    n_trials: int = 30


class ExperimentRunner:
    """Coordinates data preparation, hyperparameter tuning, and model registration."""

    def __init__(self, tracking_uri: str = "sqlite:///mlruns.db") -> None:
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()

    def run(self, config: ExperimentConfig) -> str:
        dataset = self._load_dataset(config.dataset)
        X_train, X_test, y_train, y_test = train_test_split(
            dataset.drop(columns=config.dataset.target_column),
            dataset[config.dataset.target_column],
            test_size=config.test_size,
            random_state=config.random_state,
            stratify=dataset[config.dataset.target_column],
        )

        transformer = ColumnTransformer(
            transformers=[
                ("categorical", OneHotEncoder(handle_unknown="ignore"), config.dataset.categorical_features),
                ("numeric", Pipeline([("scaler", StandardScaler())]), config.dataset.numeric_features),
            ],
        )

        def objective(trial: optuna.Trial) -> float:
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 400),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 4),
            }

            model = Pipeline(
                steps=[
                    ("features", transformer),
                    ("classifier", RandomForestClassifier(**params, random_state=config.random_state)),
                ]
            )

            model.fit(X_train, y_train)
            probabilities = model.predict_proba(X_test)[:, 1]
            return float(roc_auc_score(y_test, probabilities))

        study = optuna.create_study(direction="maximize")
        study.optimize(
            objective,
            n_trials=config.n_trials,
            callbacks=[MLflowCallback(tracking_uri=mlflow.get_tracking_uri(), metric_name="validation_auc")],
        )

        best_model = Pipeline(
            steps=[
                ("features", transformer),
                (
                    "classifier",
                    RandomForestClassifier(**study.best_params, random_state=config.random_state),
                ),
            ]
        )
        best_model.fit(X_train, y_train)

        with mlflow.start_run(run_name=f"{config.name}-final-model") as run:
            mlflow.log_params(study.best_params)
            y_pred = best_model.predict(X_test)
            metrics = classification_report(y_test, y_pred, output_dict=True)
            mlflow.log_metric("validation_auc", roc_auc_score(y_test, best_model.predict_proba(X_test)[:, 1]))
            mlflow.log_dict(metrics, "classification_report.json")
            mlflow.sklearn.log_model(best_model, artifact_path="model")

            registered = mlflow.register_model(f"runs:/{run.info.run_id}/model", config.name)
            self.client.set_model_version_tag(registered.name, registered.version, "registered_at", datetime.now(timezone.utc).isoformat())
            return registered.name

    def promote_model(self, name: str, stage: str) -> None:
        versions = self.client.get_latest_versions(name)
        if not versions:
            raise ValueError(f"No versions found for model {name}")
        newest = max(versions, key=lambda version: int(version.version))
        self.client.transition_model_version_stage(name, newest.version, stage)

    def build_kubernetes_deployment(self, name: str, image: str) -> Dict[str, object]:
        version = self.client.get_latest_versions(name, stages=["Production"])
        if not version:
            raise ValueError("Model must be in Production to generate deployment manifest")
        version_info = version[0]
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": f"{name}-inference", "namespace": "ml-services"},
            "spec": {
                "replicas": 2,
                "selector": {"matchLabels": {"app": f"{name}-inference"}},
                "template": {
                    "metadata": {"labels": {"app": f"{name}-inference"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "model-server",
                                "image": image,
                                "env": [
                                    {"name": "MLFLOW_MODEL_URI", "value": version_info.source},
                                    {"name": "MODEL_NAME", "value": name},
                                ],
                                "ports": [{"containerPort": 8080}],
                            }
                        ]
                    },
                },
            },
        }

    def _load_dataset(self, config: DatasetConfig) -> pd.DataFrame:
        df = pd.read_csv(config.path)
        missing_columns = set([config.target_column, *config.categorical_features, *config.numeric_features]) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Dataset missing columns: {sorted(missing_columns)}")
        return df


def load_experiment_config(path: Path) -> ExperimentConfig:
    data = json.loads(Path(path).read_text()) if path.suffix == ".json" else yaml_load(path)
    dataset = DatasetConfig(
        path=Path(data["dataset"]["path"]),
        target_column=data["dataset"]["target_column"],
        categorical_features=data["dataset"].get("categorical_features", []),
        numeric_features=data["dataset"].get("numeric_features", []),
    )
    return ExperimentConfig(
        name=data["name"],
        dataset=dataset,
        test_size=data.get("test_size", 0.2),
        random_state=data.get("random_state", 42),
        n_trials=data.get("n_trials", 30),
    )


def yaml_load(path: Path) -> Dict[str, object]:
    import yaml

    return yaml.safe_load(Path(path).read_text())


__all__ = ["DatasetConfig", "ExperimentConfig", "ExperimentRunner", "load_experiment_config"]

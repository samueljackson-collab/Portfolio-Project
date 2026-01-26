"""Model training pipeline with MLflow tracking and experiment management."""

from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
)
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainingPipeline:
    """Complete model training pipeline with MLflow tracking."""

    def __init__(
        self,
        experiment_name: str = "mlops-model-training",
        tracking_uri: str = "http://localhost:5000",
        artifact_location: str = "./mlruns",
    ):
        """
        Initialize training pipeline.

        Args:
            experiment_name: MLflow experiment name
            tracking_uri: MLflow tracking server URI
            artifact_location: Directory for artifacts
        """
        self.experiment_name = experiment_name

        # Configure MLflow
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

        self.artifact_location = Path(artifact_location)
        self.artifact_location.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized training pipeline: {experiment_name}")

    def load_data(self, data_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load training data from file.

        Args:
            data_path: Path to training data (CSV or NPY)

        Returns:
            Tuple of (features, labels)
        """
        logger.info(f"Loading data from {data_path}")

        if data_path.endswith(".csv"):
            df = pd.read_csv(data_path)
            X = df.drop("target", axis=1).values
            y = df["target"].values
        elif data_path.endswith(".npy"):
            data = np.load(data_path)
            X = data[:, :-1]
            y = data[:, -1]
        else:
            raise ValueError(f"Unsupported file format: {data_path}")

        logger.info(f"Loaded {X.shape[0]} samples with {X.shape[1]} features")
        return X, y

    def preprocess_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
        """
        Preprocess and split data.

        Args:
            X: Feature matrix
            y: Target labels
            test_size: Test set proportion
            random_state: Random seed

        Returns:
            X_train, X_test, y_train, y_test, scaler
        """
        logger.info("Preprocessing data...")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Scale features
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        logger.info(f"Train set: {X_train.shape[0]} samples")
        logger.info(f"Test set: {X_test.shape[0]} samples")

        return X_train, X_test, y_train, y_test, scaler

    def train_model(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        model_type: str = "random_forest",
        hyperparameters: Dict[str, Any] = None,
    ) -> Any:
        """
        Train a model with specified configuration.

        Args:
            X_train: Training features
            y_train: Training labels
            model_type: Model type (random_forest, gradient_boosting, logistic_regression)
            hyperparameters: Model hyperparameters

        Returns:
            Trained model
        """
        logger.info(f"Training {model_type} model...")

        if hyperparameters is None:
            hyperparameters = {}

        # Select model
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=hyperparameters.get("n_estimators", 100),
                max_depth=hyperparameters.get("max_depth", 10),
                min_samples_split=hyperparameters.get("min_samples_split", 2),
                random_state=42,
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=hyperparameters.get("n_estimators", 100),
                max_depth=hyperparameters.get("max_depth", 5),
                learning_rate=hyperparameters.get("learning_rate", 0.1),
                random_state=42,
            )
        elif model_type == "logistic_regression":
            model = LogisticRegression(
                C=hyperparameters.get("C", 1.0),
                max_iter=hyperparameters.get("max_iter", 1000),
                random_state=42,
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train
        model.fit(X_train, y_train)
        logger.info("Training complete")

        return model

    def evaluate_model(
        self, model: Any, X_test: np.ndarray, y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate model performance.

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels

        Returns:
            Dictionary of metrics
        """
        logger.info("Evaluating model...")

        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average="weighted"),
            "recall": recall_score(y_test, y_pred, average="weighted"),
            "f1_score": f1_score(y_test, y_pred, average="weighted"),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }

        # Log metrics
        for metric_name, metric_value in metrics.items():
            logger.info(f"{metric_name}: {metric_value:.4f}")

        return metrics

    def hyperparameter_tuning(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        model_type: str = "random_forest",
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Perform hyperparameter tuning with grid search.

        Args:
            X_train: Training features
            y_train: Training labels
            model_type: Model type

        Returns:
            Tuple of (best_model, best_params)
        """
        logger.info("Starting hyperparameter tuning...")

        # Define parameter grids
        if model_type == "random_forest":
            param_grid = {
                "n_estimators": [50, 100, 200],
                "max_depth": [5, 10, 15],
                "min_samples_split": [2, 5, 10],
            }
            model = RandomForestClassifier(random_state=42)
        elif model_type == "gradient_boosting":
            param_grid = {
                "n_estimators": [50, 100, 150],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.01, 0.1, 0.2],
            }
            model = GradientBoostingClassifier(random_state=42)
        else:
            raise ValueError(f"Tuning not supported for {model_type}")

        # Grid search
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring="f1_weighted", n_jobs=-1, verbose=1
        )
        grid_search.fit(X_train, y_train)

        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best score: {grid_search.best_score_:.4f}")

        return grid_search.best_estimator_, grid_search.best_params_

    def run_training_experiment(
        self,
        data_path: str,
        model_type: str = "random_forest",
        tune_hyperparameters: bool = False,
        register_model: bool = True,
    ) -> str:
        """
        Run complete training experiment with MLflow tracking.

        Args:
            data_path: Path to training data
            model_type: Model type to train
            tune_hyperparameters: Whether to perform hyperparameter tuning
            register_model: Whether to register model in MLflow

        Returns:
            Run ID
        """
        with mlflow.start_run() as run:
            # Log parameters
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("data_path", data_path)
            mlflow.log_param("tune_hyperparameters", tune_hyperparameters)
            mlflow.log_param("timestamp", datetime.now().isoformat())

            # Load and preprocess data
            X, y = self.load_data(data_path)
            X_train, X_test, y_train, y_test, scaler = self.preprocess_data(X, y)

            # Log data info
            mlflow.log_param("n_samples", X.shape[0])
            mlflow.log_param("n_features", X.shape[1])
            mlflow.log_param("n_train", X_train.shape[0])
            mlflow.log_param("n_test", X_test.shape[0])

            # Train model
            if tune_hyperparameters:
                model, best_params = self.hyperparameter_tuning(
                    X_train, y_train, model_type
                )
                mlflow.log_params(best_params)
            else:
                model = self.train_model(X_train, y_train, model_type)

            # Evaluate
            metrics = self.evaluate_model(model, X_test, y_test)
            mlflow.log_metrics(metrics)

            # Log model
            mlflow.sklearn.log_model(
                model,
                "model",
                registered_model_name=(
                    f"{model_type}_classifier" if register_model else None
                ),
            )

            # Log scaler
            mlflow.sklearn.log_model(scaler, "scaler")

            # Log confusion matrix as artifact
            y_pred = model.predict(X_test)
            cm = confusion_matrix(y_test, y_pred)

            cm_path = self.artifact_location / f"confusion_matrix_{run.info.run_id}.txt"
            with open(cm_path, "w") as f:
                f.write(f"Confusion Matrix:\n{cm}\n\n")
                f.write(classification_report(y_test, y_pred))

            mlflow.log_artifact(str(cm_path))

            logger.info(f"Experiment complete. Run ID: {run.info.run_id}")

            return run.info.run_id


def main():
    """CLI for training pipeline."""
    parser = argparse.ArgumentParser(description="MLOps Training Pipeline")
    parser.add_argument(
        "--data", required=True, help="Path to training data (CSV or NPY)"
    )
    parser.add_argument(
        "--model-type",
        choices=["random_forest", "gradient_boosting", "logistic_regression"],
        default="random_forest",
        help="Model type to train",
    )
    parser.add_argument(
        "--tune", action="store_true", help="Perform hyperparameter tuning"
    )
    parser.add_argument(
        "--no-register", action="store_true", help="Don't register model in MLflow"
    )
    parser.add_argument(
        "--experiment-name",
        default="mlops-model-training",
        help="MLflow experiment name",
    )

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = ModelTrainingPipeline(experiment_name=args.experiment_name)

    # Run training
    run_id = pipeline.run_training_experiment(
        data_path=args.data,
        model_type=args.model_type,
        tune_hyperparameters=args.tune,
        register_model=not args.no_register,
    )

    print(f"\n✅ Training complete! Run ID: {run_id}")
    print(f"View results: http://localhost:5000/#/experiments")


if __name__ == "__main__":
    main()

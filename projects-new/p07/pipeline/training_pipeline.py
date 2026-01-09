"""Kubeflow Pipeline for demand forecasting model training.
Usage:
    python training_pipeline.py --experiment-name demand-forecast --run-name run-001 \
      --data-path s3://bucket/data.parquet --mlflow-uri http://mlflow-server:5000
"""

from __future__ import annotations
import argparse
from typing import NamedTuple

from kfp import dsl, compiler
from kfp.dsl import Dataset, Model, Metrics, Output, Input


@dsl.component(
    base_image="python:3.10",
    packages_to_install=[
        "pandas==2.0.3",
        "pyarrow==13.0.0",
        "great-expectations==0.17.15",
        "boto3==1.28.0",
    ],
)
def data_ingestion(
    data_path: str,
    output_dataset: Output[Dataset],
) -> None:
    """Ingest data from S3 and validate schema."""
    import pandas as pd
    import great_expectations as gx

    df = pd.read_parquet(data_path)

    # Basic validation
    context = gx.get_context()
    suite = context.add_expectation_suite("demand_data")
    validator = context.sources.pandas_default.read_dataframe(df).get_validator(
        expectation_suite=suite
    )
    validator.expect_table_row_count_to_be_between(min_value=1000)
    validator.expect_column_to_exist("store_id")
    validator.expect_column_to_exist("date")
    validator.expect_column_to_exist("sales")
    validator.expect_column_values_to_not_be_null("sales")

    result = validator.validate()
    assert result.success, f"Data validation failed: {result}"

    df.to_parquet(output_dataset.path, index=False)
    print(f"Ingested {len(df)} rows to {output_dataset.path}")


@dsl.component(
    base_image="python:3.10",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.0", "feast==0.34.1"],
)
def feature_engineering(
    input_dataset: Input[Dataset],
    output_features: Output[Dataset],
) -> None:
    """Compute features for training."""
    import pandas as pd
    from sklearn.preprocessing import StandardScaler

    df = pd.read_parquet(input_dataset.path)
    df["date"] = pd.to_datetime(df["date"])
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # Rolling features
    df = df.sort_values(["store_id", "date"])
    df["sales_lag_7"] = df.groupby("store_id")["sales"].shift(7)
    df["sales_rolling_mean_7"] = df.groupby("store_id")["sales"].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )

    df = df.dropna()
    df.to_parquet(output_features.path, index=False)
    print(f"Engineered {len(df)} rows with features to {output_features.path}")


@dsl.component(
    base_image="pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.0",
        "mlflow==2.8.1",
        "boto3==1.28.0",
    ],
)
def training(
    input_features: Input[Dataset],
    mlflow_tracking_uri: str,
    experiment_name: str,
    run_name: str,
    model_output: Output[Model],
    metrics_output: Output[Metrics],
) -> NamedTuple("Outputs", [("mae", float), ("rmse", float)]):
    """Train demand forecasting model and log to MLflow."""
    import pandas as pd
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import math
    import joblib

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)

    df = pd.read_parquet(input_features.path)
    feature_cols = [
        "day_of_week",
        "month",
        "is_weekend",
        "sales_lag_7",
        "sales_rolling_mean_7",
    ]
    X = df[feature_cols]
    y = df["sales"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run(run_name=run_name) as run:
        params = {"n_estimators": 100, "max_depth": 10, "random_state": 42}
        mlflow.log_params(params)

        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = math.sqrt(mean_squared_error(y_test, y_pred))

        mlflow.log_metrics({"mae": mae, "rmse": rmse})
        mlflow.sklearn.log_model(model, "model")

        joblib.dump(model, model_output.path)
        metrics_output.log_metric("mae", mae)
        metrics_output.log_metric("rmse", rmse)

        print(f"Training complete. MAE: {mae:.2f}, RMSE: {rmse:.2f}")

        from collections import namedtuple

        outputs = namedtuple("Outputs", ["mae", "rmse"])
        return outputs(mae, rmse)


@dsl.component(
    base_image="python:3.10", packages_to_install=["mlflow==2.8.1", "boto3==1.28.0"]
)
def evaluation(
    model_input: Input[Model],
    mae: float,
    rmse: float,
    mlflow_tracking_uri: str,
    baseline_mae_threshold: float = 100.0,
) -> str:
    """Evaluate model and gate promotion."""
    import mlflow

    mlflow.set_tracking_uri(mlflow_tracking_uri)

    if mae > baseline_mae_threshold:
        raise ValueError(
            f"Model MAE {mae:.2f} exceeds threshold {baseline_mae_threshold:.2f}. Failing pipeline."
        )

    print(
        f"Model passed evaluation gate. MAE: {mae:.2f} <= {baseline_mae_threshold:.2f}"
    )
    return "PASS"


@dsl.component(
    base_image="python:3.10", packages_to_install=["mlflow==2.8.1", "boto3==1.28.0"]
)
def register_model(
    model_input: Input[Model],
    mlflow_tracking_uri: str,
    model_name: str = "demand-forecast",
    stage: str = "Staging",
) -> str:
    """Register model to MLflow Model Registry."""
    import mlflow
    from mlflow.tracking import MlflowClient

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    client = MlflowClient()

    # Find the latest run and register model
    experiment = mlflow.get_experiment_by_name("demand-forecast")
    runs = client.search_runs(
        experiment.experiment_id, order_by=["start_time DESC"], max_results=1
    )
    run_id = runs[0].info.run_id
    model_uri = f"runs:/{run_id}/model"

    result = mlflow.register_model(model_uri, model_name)
    version = result.version

    # Transition to Staging
    client.transition_model_version_stage(model_name, version, stage)

    print(f"Registered model {model_name} version {version} to stage {stage}")
    return f"{model_name}:{version}"


@dsl.pipeline(
    name="Demand Forecasting Training Pipeline",
    description="End-to-end ML pipeline for retail demand forecasting",
)
def training_pipeline(
    data_path: str,
    mlflow_tracking_uri: str,
    experiment_name: str = "demand-forecast",
    run_name: str = "run-001",
    baseline_mae_threshold: float = 100.0,
):
    """Orchestrate training pipeline."""
    ingest_task = data_ingestion(data_path=data_path)

    feature_task = feature_engineering(
        input_dataset=ingest_task.outputs["output_dataset"]
    )

    train_task = training(
        input_features=feature_task.outputs["output_features"],
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name,
        run_name=run_name,
    )

    eval_task = evaluation(
        model_input=train_task.outputs["model_output"],
        mae=train_task.outputs["mae"],
        rmse=train_task.outputs["rmse"],
        mlflow_tracking_uri=mlflow_tracking_uri,
        baseline_mae_threshold=baseline_mae_threshold,
    )

    register_task = register_model(
        model_input=train_task.outputs["model_output"],
        mlflow_tracking_uri=mlflow_tracking_uri,
    )
    register_task.after(eval_task)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-name", default="demand-forecast")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--data-path", required=True)
    parser.add_argument("--mlflow-uri", required=True)
    parser.add_argument("--output-file", default="pipeline.yaml")
    args = parser.parse_args()

    compiler.Compiler().compile(
        pipeline_func=training_pipeline,
        package_path=args.output_file,
    )
    print(f"Pipeline compiled to {args.output_file}")

    # Optionally submit to Kubeflow
    # from kfp import Client
    # client = Client()
    # client.create_run_from_pipeline_func(
    #     training_pipeline,
    #     arguments={
    #         "data_path": args.data_path,
    #         "mlflow_tracking_uri": args.mlflow_uri,
    #         "experiment_name": args.experiment_name,
    #         "run_name": args.run_name,
    #     }
    # )


if __name__ == "__main__":
    main()

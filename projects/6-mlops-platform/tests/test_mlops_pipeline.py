from importlib import util
from pathlib import Path
from types import SimpleNamespace

import pytest


def load_module():
    path = Path(__file__).resolve().parents[1] / "src" / "mlops_pipeline.py"
    spec = util.spec_from_file_location("mlops_pipeline", path)
    module = util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


mlops_pipeline = load_module()


def test_load_experiment_config_reads_yaml(tmp_path: Path):
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(
        """
name: churn-model
dataset:
  path: data/churn.csv
  target_column: churn
  categorical_features: [country]
  numeric_features: [age]
random_state: 1
n_trials: 2
"""
    )

    config = mlops_pipeline.load_experiment_config(config_path)
    assert config.name == "churn-model"
    assert config.dataset.target_column == "churn"
    assert config.n_trials == 2


def test_build_kubernetes_deployment_uses_production_version(monkeypatch):
    runner = mlops_pipeline.ExperimentRunner()

    fake_version = SimpleNamespace(version="2", source="s3://mlflow/model")
    monkeypatch.setattr(runner.client, "get_latest_versions", lambda name, stages=None: [fake_version])

    deployment = runner.build_kubernetes_deployment(name="fraud", image="ghcr.io/example/fraud:1.0")
    container = deployment["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "ghcr.io/example/fraud:1.0"
    assert container["env"][0]["value"] == "s3://mlflow/model"


def test_yaml_load_handles_yaml(tmp_path: Path):
    path = tmp_path / "config.yaml"
    path.write_text("name: demo")
    data = mlops_pipeline.yaml_load(path)
    assert data["name"] == "demo"

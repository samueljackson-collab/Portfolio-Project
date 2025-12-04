import importlib.util
import json
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


def _stub_mlops_dependencies(monkeypatch):
    mlflow = ModuleType("mlflow")

    class DummyRunInfo:
        def __init__(self) -> None:
            self.run_id = "run-123"

    @contextmanager
    def start_run(run_name=None):
        yield SimpleNamespace(info=DummyRunInfo())

    def _noop(*_args, **_kwargs):
        return None

    def register_model(uri, name):
        return SimpleNamespace(name=name, version="1", source=uri)

    class DummyClient:
        def __init__(self) -> None:
            self.latest_versions = []

        def get_latest_versions(self, name, stages=None):
            return getattr(self, "_versions", self.latest_versions)

        def set_model_version_tag(self, name, version, key, value):
            self.tag = (name, version, key, value)

        def transition_model_version_stage(self, name, version, stage):
            self.transition = (name, version, stage)

    mlflow.set_tracking_uri = _noop
    mlflow.start_run = start_run
    mlflow.log_params = _noop
    mlflow.log_metric = _noop
    mlflow.log_dict = _noop
    mlflow.register_model = register_model
    mlflow.tracking = SimpleNamespace(MlflowClient=DummyClient)
    mlflow.sklearn = SimpleNamespace(log_model=_noop)

    optuna = ModuleType("optuna")

    class DummyStudy:
        def __init__(self) -> None:
            self.best_params = {}

        def optimize(self, *_args, **_kwargs):
            return None

    optuna.create_study = lambda direction=None: DummyStudy()
    optuna.integration = SimpleNamespace(mlflow=SimpleNamespace(MLflowCallback=_noop))
    optuna.Trial = object

    pandas = ModuleType("pandas")

    class DummyFrame:
        def __init__(self, columns):
            self.columns = columns

    def fake_read_csv(path):
        header = Path(path).read_text().splitlines()[0].split(",")
        return DummyFrame(header)

    pandas.read_csv = fake_read_csv

    numpy = ModuleType("numpy")

    sklearn = ModuleType("sklearn")
    compose = ModuleType("sklearn.compose")
    ensemble = ModuleType("sklearn.ensemble")
    metrics = ModuleType("sklearn.metrics")
    model_selection = ModuleType("sklearn.model_selection")
    pipeline = ModuleType("sklearn.pipeline")
    preprocessing = ModuleType("sklearn.preprocessing")

    class Dummy:
        def __init__(self, *_args, **_kwargs):
            pass

        def fit(self, *_args, **_kwargs):
            return self

        def predict(self, *_args, **_kwargs):
            return []

        def predict_proba(self, *_args, **_kwargs):
            return [[0.5, 0.5]]

    def train_test_split(*_args, **_kwargs):
        return [], [], [], []

    def classification_report(*_args, **_kwargs):
        return {}

    def roc_auc_score(*_args, **_kwargs):
        return 0.5

    compose.ColumnTransformer = Dummy
    ensemble.RandomForestClassifier = Dummy
    metrics.classification_report = classification_report
    metrics.roc_auc_score = roc_auc_score
    model_selection.train_test_split = train_test_split
    pipeline.Pipeline = Dummy
    preprocessing.OneHotEncoder = Dummy
    preprocessing.StandardScaler = Dummy

    monkeypatch.setitem(sys.modules, "mlflow", mlflow)
    monkeypatch.setitem(sys.modules, "mlflow.tracking", mlflow.tracking)
    monkeypatch.setitem(sys.modules, "mlflow.sklearn", mlflow.sklearn)
    monkeypatch.setitem(sys.modules, "optuna", optuna)
    monkeypatch.setitem(sys.modules, "optuna.integration", optuna.integration)
    monkeypatch.setitem(sys.modules, "optuna.integration.mlflow", optuna.integration.mlflow)
    monkeypatch.setitem(sys.modules, "pandas", pandas)
    monkeypatch.setitem(sys.modules, "numpy", numpy)
    monkeypatch.setitem(sys.modules, "sklearn", sklearn)
    monkeypatch.setitem(sys.modules, "sklearn.compose", compose)
    monkeypatch.setitem(sys.modules, "sklearn.ensemble", ensemble)
    monkeypatch.setitem(sys.modules, "sklearn.metrics", metrics)
    monkeypatch.setitem(sys.modules, "sklearn.model_selection", model_selection)
    monkeypatch.setitem(sys.modules, "sklearn.pipeline", pipeline)
    monkeypatch.setitem(sys.modules, "sklearn.preprocessing", preprocessing)


def _load_module(monkeypatch):
    _stub_mlops_dependencies(monkeypatch)
    module_path = Path(__file__).resolve().parents[1] / "src" / "mlops_pipeline.py"
    spec = importlib.util.spec_from_file_location("mlops_pipeline", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["mlops_pipeline"] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_load_experiment_config_from_json(monkeypatch, tmp_path):
    module = _load_module(monkeypatch)
    config_path = tmp_path / "experiment.json"
    config_path.write_text(
        json.dumps(
            {
                "name": "fraud-detector",
                "dataset": {
                    "path": "data/train.csv",
                    "target_column": "label",
                    "categorical_features": ["country"],
                    "numeric_features": ["amount"],
                },
                "test_size": 0.3,
                "random_state": 7,
                "n_trials": 5,
            }
        )
    )

    config = module.load_experiment_config(config_path)

    assert config.name == "fraud-detector"
    assert config.dataset.path == Path("data/train.csv")
    assert config.dataset.target_column == "label"
    assert config.test_size == 0.3
    assert config.random_state == 7
    assert config.n_trials == 5


def test_load_experiment_config_from_yaml(monkeypatch, tmp_path):
    module = _load_module(monkeypatch)
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(
        """
name: recommender
dataset:
  path: data/interactions.csv
  target_column: clicked
  categorical_features: [country]
  numeric_features: [dwell_time]
"""
    )

    config = module.load_experiment_config(config_path)

    assert config.name == "recommender"
    assert config.dataset.categorical_features == ["country"]
    assert config.dataset.numeric_features == ["dwell_time"]
    assert config.n_trials == 30  # default


def test_load_dataset_validates_missing_columns(monkeypatch, tmp_path):
    module = _load_module(monkeypatch)
    data_path = tmp_path / "data.csv"
    data_path.write_text("label,country,amount\n1,us,9.5\n")

    config = module.DatasetConfig(
        path=data_path,
        target_column="label",
        categorical_features=["country"],
        numeric_features=["amount"],
    )

    dataframe = module.ExperimentRunner()._load_dataset(config)
    assert dataframe.columns == ["label", "country", "amount"]


def test_load_dataset_raises_for_missing_columns(monkeypatch, tmp_path):
    module = _load_module(monkeypatch)
    data_path = tmp_path / "data.csv"
    data_path.write_text("label,country\n1,us\n")

    config = module.DatasetConfig(
        path=data_path,
        target_column="label",
        categorical_features=["country"],
        numeric_features=["amount"],
    )

    with pytest.raises(ValueError):
        module.ExperimentRunner()._load_dataset(config)


def test_build_kubernetes_deployment_uses_latest_production(monkeypatch):
    module = _load_module(monkeypatch)
    runner = module.ExperimentRunner()
    runner.client.get_latest_versions = lambda name, stages=None: [
        SimpleNamespace(name=name, version="3", source="s3://models/fraud"),
        SimpleNamespace(name=name, version="2", source="s3://models/old"),
    ]

    manifest = runner.build_kubernetes_deployment("fraud", "ghcr.io/model:1.0")

    assert manifest["metadata"]["name"] == "fraud-inference"
    container = manifest["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == "ghcr.io/model:1.0"
    assert {env["name"]: env["value"] for env in container["env"]}["MLFLOW_MODEL_URI"] == "s3://models/fraud"

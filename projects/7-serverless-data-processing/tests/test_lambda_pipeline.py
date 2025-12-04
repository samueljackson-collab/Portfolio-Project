import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_module(monkeypatch, s3_payload=None):
    stub_boto3(monkeypatch, s3_payload)
    module_path = Path(__file__).resolve().parents[1] / "src" / "lambda_pipeline.py"
    spec = importlib.util.spec_from_file_location("lambda_pipeline", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def stub_boto3(monkeypatch, s3_payload=None):
    class DummyBody:
        def __init__(self, data: bytes) -> None:
            self._data = data

        def read(self) -> bytes:
            return self._data

    class DummyS3:
        def __init__(self) -> None:
            self.objects = {}
            if s3_payload is not None:
                self.objects["bucket/key.json"] = DummyBody(json.dumps(s3_payload).encode())

        def get_object(self, Bucket, Key):  # noqa: N802
            return {"Body": self.objects[f"{Bucket}/{Key}"]}

    class DummyTable:
        def __init__(self) -> None:
            self.items = []

        def put_item(self, Item):  # noqa: N802
            self.items.append(Item)

    class DummyDynamo:
        def __init__(self) -> None:
            self.tables = {}

        def Table(self, name):  # noqa: N802
            return self.tables.setdefault(name, DummyTable())

    class DummyStepFunctions:
        def __init__(self) -> None:
            self.executions = []

        def start_execution(self, stateMachineArn, input):  # noqa: N802
            self.executions.append({"arn": stateMachineArn, "input": json.loads(input)})

    def resource(service_name):
        if service_name == "dynamodb":
            return DummyDynamo()
        raise ValueError(service_name)

    def client(service_name):
        if service_name == "s3":
            return DummyS3()
        if service_name == "stepfunctions":
            return DummyStepFunctions()
        raise ValueError(service_name)

    boto3 = SimpleNamespace(resource=resource, client=client)
    monkeypatch.setitem(sys.modules, "boto3", boto3)


@pytest.fixture(autouse=True)
def _env(monkeypatch):
    monkeypatch.setenv("CURATED_TABLE", "curated")
    monkeypatch.setenv("WORKFLOW_ARN", "arn:aws:states:demo")


def test_ingestion_handler_processes_api_payload(monkeypatch):
    module = _load_module(monkeypatch)
    event = {
        "body": json.dumps({"id": "1", "user_id": "u-1", "timestamp": "2024-01-01", "event_type": "click", "amount": 9.5}),
    }

    response = module.ingestion_handler(event, None)

    assert response == {"statusCode": 202, "body": json.dumps({"records": 1})}
    table = module.dynamodb.Table("curated")
    assert table.items[0]["amount"] == Decimal("9.5")
    assert module.step_functions.executions  # executions stored on client


def test_ingestion_handler_validates_required_fields(monkeypatch):
    module = _load_module(monkeypatch)
    event = {"body": json.dumps({"id": "1", "timestamp": "2024-01-01"})}

    with pytest.raises(ValueError):
        module.ingestion_handler(event, None)


def test_ingestion_handler_reads_from_s3(monkeypatch):
    payload = {"id": "2", "user_id": "u-2", "timestamp": "2024-01-02", "event_type": "purchase"}
    module = _load_module(monkeypatch, s3_payload=payload)
    s3_event = {
        "Records": [
            {
                "s3": {"bucket": {"name": "bucket"}, "object": {"key": "key.json"}},
            }
        ]
    }

    response = module.ingestion_handler(s3_event, None)

    assert json.loads(response["body"]) == {"records": 1}
    table = module.dynamodb.Table("curated")
    assert table.items[0]["id"] == payload["id"]


def test_analytics_handler_returns_rollup(monkeypatch):
    module = _load_module(monkeypatch)
    event = {
        "records": [
            {"user_id": "a", "amount": 5.0},
            {"user_id": "b", "amount": 7.0},
            {"user_id": "a", "amount": 2.0},
        ]
    }

    response = module.analytics_handler(event, None)
    body = json.loads(response["body"])

    assert body["total_records"] == 3
    assert body["total_amount"] == pytest.approx(14.0)
    assert body["unique_users"] == 2

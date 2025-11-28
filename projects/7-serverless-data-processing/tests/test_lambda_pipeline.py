import json
from importlib import util
from pathlib import Path
from types import SimpleNamespace

import pytest


def load_module():
    path = Path(__file__).resolve().parents[1] / "src" / "lambda_pipeline.py"
    spec = util.spec_from_file_location("lambda_pipeline", path)
    module = util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


lambda_pipeline = load_module()


def test_ingestion_handler_validates_and_enriches(monkeypatch):
    captured = {}

    class FakeTable:
        def put_item(self, Item):
            captured["item"] = Item

    monkeypatch.setattr(lambda_pipeline, "dynamodb", SimpleNamespace(Table=lambda _: FakeTable()))
    monkeypatch.setattr(lambda_pipeline, "_start_workflow", lambda payload: captured.setdefault("workflow", payload))
    monkeypatch.setenv("CURATED_TABLE", "table")

    event = {"body": json.dumps({"id": "1", "user_id": "u1", "timestamp": "now", "event_type": "click"})}
    response = lambda_pipeline.ingestion_handler(event, None)

    assert response["statusCode"] == 202
    assert captured["item"]["channel"] == "api"
    assert captured["workflow"]["id"] == "1"


def test_analytics_handler_summarizes_records():
    records = [
        {"user_id": "a", "amount": 5.0},
        {"user_id": "b", "amount": 7.5},
        {"user_id": "a", "amount": 2.5},
    ]
    event = {"records": records}
    response = lambda_pipeline.analytics_handler(event, None)
    payload = json.loads(response["body"])

    assert payload["total_records"] == 3
    assert payload["unique_users"] == 2
    assert pytest.approx(payload["total_amount"], rel=0.01) == 15.0

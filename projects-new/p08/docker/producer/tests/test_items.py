import os
import requests

BASE_URL = os.getenv("BASE_URL", "http://mock-api:8080")

def test_create_item_success():
    resp = requests.post(f"{BASE_URL}/items", json={"id": "1", "name": "demo", "value": 5})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_create_item_validation_error():
    resp = requests.post(f"{BASE_URL}/items", json={"id": "2", "name": "bad", "value": -1})
    assert resp.status_code == 422

import json
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from Twisted_Monk_Suite_v1.backend import main


class MockResponse:
    def __init__(self, data: Dict[str, Any], status_code: int = 200):
        self._data = data
        self.status_code = status_code
        self.text = json.dumps(data)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("HTTP error")

    def json(self) -> Dict[str, Any]:
        return self._data


class MockAsyncClient:
    def __init__(self, responses):
        self._responses = responses
        self._index = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def get(self, *args, **kwargs):
        response = self._responses[self._index]
        self._index = min(self._index + 1, len(self._responses) - 1)
        return response

    async def post(self, *args, **kwargs):
        return self._responses[self._index]


@pytest.fixture(autouse=True)
def reset_cache(monkeypatch):
    cache = main.InMemoryCache()
    monkeypatch.setattr(main, "cache", cache)
    return cache


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("SHOPIFY_STORE_DOMAIN", "example.myshopify.com")
    monkeypatch.setenv("SHOPIFY_ACCESS_TOKEN", "test-token")
    main.get_settings.cache_clear()
    main.settings = main.get_settings()
    return TestClient(main.app)


def test_health_check(monkeypatch, client):
    mock_responses = [MockResponse({"count": 1})]

    async def _mock_get(*args, **kwargs):
        return mock_responses[0]

    class HealthClient(MockAsyncClient):
        async def get(self, *args, **kwargs):
            return mock_responses[0]

    monkeypatch.setattr(main.httpx, "AsyncClient", lambda *args, **kwargs: HealthClient(mock_responses))

    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["redis"] == "connected"


def test_get_inventory(monkeypatch, client):
    product_payload = {
        "product": {
            "id": 123,
            "title": "Test Product",
            "variants": [
                {"id": 1, "inventory_quantity": 10, "price": "20.00"},
                {"id": 2, "inventory_quantity": 5, "price": "22.00"},
            ],
        }
    }

    async def _mock_get(url, *args, **kwargs):
        if "products/123" in url:
            return MockResponse(product_payload)
        raise AssertionError("Unexpected URL")

    class InventoryClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, *args, **kwargs):
            return await _mock_get(url)

    async def _mock_client():
        return InventoryClient()

    monkeypatch.setattr(main, "get_shopify_client", _mock_client)

    response = client.get("/inventory/123", headers={"Authorization": "Bearer test"})
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == "123"
    assert data["total_quantity"] == 15
    assert len(data["variants"]) == 2


def test_bundle_recommendations(monkeypatch, client):
    current_product = {
        "product": {
            "id": 1,
            "title": "Rope",
            "product_type": "Bondage Gear",
            "tags": "rope, silk",
            "variants": [{"price": "20.00", "inventory_quantity": 5}],
        }
    }
    other_products = {
        "products": [
            {
                "id": 2,
                "title": "Handcuffs",
                "product_type": "Bondage Gear",
                "tags": "metal, rope",
                "handle": "handcuffs",
                "variants": [{"price": "18.00", "inventory_quantity": 6}],
                "images": [{"src": "https://example.com/image.jpg"}],
            }
        ]
    }

    class RecommendationClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, *args, **kwargs):
            if url.endswith("products/1.json"):
                return MockResponse(current_product)
            if url.endswith("products.json"):
                return MockResponse(other_products)
            raise AssertionError(f"Unexpected URL {url}")

    async def _mock_client():
        return RecommendationClient()

    monkeypatch.setattr(main, "get_shopify_client", _mock_client)

    response = client.post(
        "/recommendations/bundle",
        headers={"Authorization": "Bearer test"},
        json={"product_id": "1", "limit": 4},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == "2"

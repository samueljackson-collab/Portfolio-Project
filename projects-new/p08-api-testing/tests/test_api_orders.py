"""
API Tests for Orders Endpoints

Tests CRUD operations on the Orders API including:
- Creating, reading, updating, and deleting orders
- Error handling and validation
- Response format and data type validation
"""

import pytest
import requests
from datetime import datetime
from typing import Dict, Any, Optional


class TestOrdersCRUD:
    """Test suite for Orders CRUD operations"""

    @pytest.fixture
    def api_client(self, base_url, auth_token):
        """Create API client with authentication"""
        return APIClient(base_url, auth_token)

    @pytest.fixture
    def sample_order(self):
        """Sample order payload for testing"""
        return {
            "customer_id": "CUST001",
            "items": [
                {
                    "product_id": "PROD001",
                    "quantity": 2,
                    "price": 29.99
                }
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }

    def test_create_order_success(self, api_client, sample_order):
        """Test successful order creation"""
        response = api_client.post("/orders", json=sample_order)

        assert response.status_code == 201, "Order creation should return 201"
        data = response.json()

        # Validate response structure
        assert "id" in data, "Response must contain order ID"
        assert "status" in data, "Response must contain status"
        assert data["status"] == "pending", "New orders should be in pending status"
        assert data["customer_id"] == sample_order["customer_id"]
        assert len(data["items"]) == 1

    def test_create_order_with_multiple_items(self, api_client):
        """Test order creation with multiple items"""
        order = {
            "customer_id": "CUST002",
            "items": [
                {"product_id": "PROD001", "quantity": 1, "price": 29.99},
                {"product_id": "PROD002", "quantity": 2, "price": 49.99},
                {"product_id": "PROD003", "quantity": 3, "price": 19.99}
            ],
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Capital City",
                "state": "CA",
                "zip": "90210"
            }
        }

        response = api_client.post("/orders", json=order)
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 3

    def test_get_order_by_id(self, api_client, sample_order):
        """Test retrieving an order by ID"""
        # Create an order first
        create_resp = api_client.post("/orders", json=sample_order)
        order_id = create_resp.json()["id"]

        # Retrieve the order
        get_resp = api_client.get(f"/orders/{order_id}")

        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["id"] == order_id
        assert data["customer_id"] == sample_order["customer_id"]

    def test_list_orders_with_pagination(self, api_client):
        """Test listing orders with pagination parameters"""
        params = {
            "page": 1,
            "pageSize": 5
        }

        response = api_client.get("/orders", params=params)

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "items" in data, "Response must contain items array"
        assert "total" in data, "Response must contain total count"
        assert "page" in data, "Response must contain page number"

        # Validate data types
        assert isinstance(data["items"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["page"], int)

        # Validate pagination
        assert len(data["items"]) <= 5, "Page size should not exceed requested size"

    def test_list_orders_empty(self, api_client):
        """Test listing orders when no orders exist"""
        response = api_client.get("/orders", params={"page": 999, "pageSize": 5})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)

    def test_update_order_status(self, api_client, sample_order):
        """Test updating order status"""
        # Create an order
        create_resp = api_client.post("/orders", json=sample_order)
        order_id = create_resp.json()["id"]

        # Update order status
        update_data = {
            "status": "confirmed"
        }
        update_resp = api_client.put(f"/orders/{order_id}", json=update_data)

        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["status"] == "confirmed"

    def test_update_order_items(self, api_client, sample_order):
        """Test updating order items"""
        # Create an order
        create_resp = api_client.post("/orders", json=sample_order)
        order_id = create_resp.json()["id"]

        # Update order items
        new_items = [
            {"product_id": "PROD001", "quantity": 1, "price": 29.99},
            {"product_id": "PROD002", "quantity": 1, "price": 49.99}
        ]
        update_data = {
            "items": new_items
        }
        update_resp = api_client.put(f"/orders/{order_id}", json=update_data)

        assert update_resp.status_code == 200
        data = update_resp.json()
        assert len(data["items"]) == 2

    def test_delete_order(self, api_client, sample_order):
        """Test deleting an order"""
        # Create an order
        create_resp = api_client.post("/orders", json=sample_order)
        order_id = create_resp.json()["id"]

        # Delete the order
        delete_resp = api_client.delete(f"/orders/{order_id}")

        assert delete_resp.status_code in [200, 204]

        # Verify order is deleted
        get_resp = api_client.get(f"/orders/{order_id}")
        assert get_resp.status_code == 404


class TestOrdersErrorHandling:
    """Test suite for error handling"""

    @pytest.fixture
    def api_client(self, base_url, auth_token):
        return APIClient(base_url, auth_token)

    def test_get_nonexistent_order(self, api_client):
        """Test retrieving a non-existent order"""
        response = api_client.get("/orders/invalid-order-id-12345")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data, "Error response should contain error message"

    def test_create_order_with_invalid_payload(self, api_client):
        """Test order creation with invalid payload"""
        invalid_orders = [
            {},  # Empty payload
            {"customer_id": "CUST001"},  # Missing items
            {"items": []},  # Missing customer_id
            {"customer_id": None, "items": []},  # Null customer_id
        ]

        for invalid_order in invalid_orders:
            response = api_client.post("/orders", json=invalid_order)
            assert response.status_code in [400, 422], \
                f"Invalid payload should return 400 or 422, got {response.status_code}"

    def test_update_nonexistent_order(self, api_client):
        """Test updating a non-existent order"""
        response = api_client.put("/orders/invalid-id", json={"status": "confirmed"})

        assert response.status_code == 404

    def test_delete_nonexistent_order(self, api_client):
        """Test deleting a non-existent order"""
        response = api_client.delete("/orders/invalid-id")

        assert response.status_code == 404

    def test_create_order_with_invalid_items(self, api_client):
        """Test creating order with invalid item structure"""
        invalid_order = {
            "customer_id": "CUST001",
            "items": [
                {
                    "product_id": "PROD001",
                    "quantity": -1,  # Invalid negative quantity
                    "price": 29.99
                }
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }

        response = api_client.post("/orders", json=invalid_order)
        assert response.status_code in [400, 422]

    def test_invalid_http_method(self, api_client):
        """Test invalid HTTP method"""
        response = api_client.patch("/orders/123", json={})

        assert response.status_code == 405  # Method Not Allowed


class TestOrdersDataValidation:
    """Test suite for data validation"""

    @pytest.fixture
    def api_client(self, base_url, auth_token):
        return APIClient(base_url, auth_token)

    @pytest.fixture
    def sample_order(self):
        return {
            "customer_id": "CUST001",
            "items": [{"product_id": "PROD001", "quantity": 2, "price": 29.99}],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }

    def test_response_content_type(self, api_client, sample_order):
        """Test that response Content-Type is application/json"""
        response = api_client.post("/orders", json=sample_order)

        assert response.status_code == 201
        assert "application/json" in response.headers.get("Content-Type", "")

    def test_response_is_valid_json(self, api_client, sample_order):
        """Test that response is valid JSON"""
        response = api_client.post("/orders", json=sample_order)

        assert response.status_code == 201
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("Response is not valid JSON")

    def test_order_response_structure(self, api_client, sample_order):
        """Test order response has expected structure"""
        response = api_client.post("/orders", json=sample_order)
        assert response.status_code == 201

        data = response.json()

        # Required fields
        required_fields = ["id", "customer_id", "status", "items", "created_at"]
        for field in required_fields:
            assert field in data, f"Response missing required field: {field}"

    def test_order_id_format(self, api_client, sample_order):
        """Test order ID is a valid string"""
        response = api_client.post("/orders", json=sample_order)
        assert response.status_code == 201

        data = response.json()
        assert isinstance(data["id"], str)
        assert len(data["id"]) > 0

    def test_order_timestamps(self, api_client, sample_order):
        """Test order timestamps are valid"""
        response = api_client.post("/orders", json=sample_order)
        assert response.status_code == 201

        data = response.json()

        # Validate timestamp format
        if "created_at" in data:
            # Should be ISO 8601 format
            try:
                datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {data['created_at']}")

    def test_order_total_calculation(self, api_client):
        """Test order total is calculated correctly"""
        order = {
            "customer_id": "CUST001",
            "items": [
                {"product_id": "PROD001", "quantity": 2, "price": 10.00},
                {"product_id": "PROD002", "quantity": 3, "price": 5.00}
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }

        response = api_client.post("/orders", json=order)
        assert response.status_code == 201

        data = response.json()
        expected_total = (2 * 10.00) + (3 * 5.00)  # 35.00
        assert data["total"] == expected_total


class TestOrdersResponseTime:
    """Test suite for response time validation"""

    @pytest.fixture
    def api_client(self, base_url, auth_token):
        return APIClient(base_url, auth_token)

    def test_list_orders_response_time(self, api_client):
        """Test list orders response time is acceptable"""
        response = api_client.get("/orders", params={"page": 1, "pageSize": 5})

        assert response.status_code == 200
        response_time_ms = response.elapsed.total_seconds() * 1000
        assert response_time_ms < 1000, f"Response took {response_time_ms}ms, should be < 1000ms"

    def test_create_order_response_time(self, api_client):
        """Test create order response time is acceptable"""
        order = {
            "customer_id": "CUST001",
            "items": [{"product_id": "PROD001", "quantity": 1, "price": 29.99}],
            "shipping_address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip": "62701"
            }
        }

        response = api_client.post("/orders", json=order)

        assert response.status_code == 201
        response_time_ms = response.elapsed.total_seconds() * 1000
        assert response_time_ms < 2000, f"Response took {response_time_ms}ms, should be < 2000ms"


class APIClient:
    """Helper class for making API requests"""

    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        })

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None):
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, params=params)

    def post(self, endpoint: str, json: Dict[str, Any]):
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, json=json)

    def put(self, endpoint: str, json: Dict[str, Any]):
        url = f"{self.base_url}{endpoint}"
        return self.session.put(url, json=json)

    def patch(self, endpoint: str, json: Dict[str, Any]):
        url = f"{self.base_url}{endpoint}"
        return self.session.patch(url, json=json)

    def delete(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"
        return self.session.delete(url)

    def close(self):
        self.session.close()

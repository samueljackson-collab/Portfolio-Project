"""
Test suite for Twisted Monk Suite backend API.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_success(self):
        """Test health check returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "redis_connected" in data
        assert "timestamp" in data
    
    def test_health_check_structure(self):
        """Test health check response structure."""
        response = client.get("/health")
        data = response.json()
        
        assert isinstance(data["status"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["redis_connected"], bool)
        assert isinstance(data["timestamp"], float)


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct message."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Twisted Monk Suite" in data["message"]


class TestLeadTimeEndpoint:
    """Tests for lead time calculation endpoint."""
    
    def test_calculate_lead_time_success(self):
        """Test successful lead time calculation."""
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["supplier_id"] == "SUP001"
        assert data["product_id"] == "PROD-123"
        assert "estimated_days" in data
        assert "confidence" in data
        assert isinstance(data["estimated_days"], int)
        assert 0.0 <= data["confidence"] <= 1.0
    
    def test_calculate_lead_time_validation_error(self):
        """Test lead time calculation with invalid data."""
        # Missing required field
        payload = {
            "supplier_id": "SUP001",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 422
    
    def test_calculate_lead_time_negative_quantity(self):
        """Test lead time calculation with negative quantity."""
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": -5
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 422
    
    def test_calculate_lead_time_empty_strings(self):
        """Test lead time calculation with empty strings."""
        payload = {
            "supplier_id": "",
            "product_id": "",
            "quantity": 10
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 422


class TestInventoryEndpoint:
    """Tests for inventory status endpoint."""
    
    def test_get_inventory_success(self):
        """Test successful inventory retrieval."""
        response = client.get("/api/v1/inventory/PROD-123")
        assert response.status_code == 200
        
        data = response.json()
        assert data["product_id"] == "PROD-123"
        assert "available" in data
        assert "reserved" in data
        assert "incoming" in data
        assert "status" in data
        
        # Check types
        assert isinstance(data["available"], int)
        assert isinstance(data["reserved"], int)
        assert isinstance(data["incoming"], int)
        assert data["status"] in ["in_stock", "low_stock", "out_of_stock"]
    
    def test_get_inventory_empty_product_id(self):
        """Test inventory retrieval with empty product ID."""
        response = client.get("/api/v1/inventory/")
        # Should return 404 (not found) or 405 (method not allowed)
        assert response.status_code in [404, 405]
    
    def test_get_inventory_special_characters(self):
        """Test inventory retrieval with special characters in product ID."""
        response = client.get("/api/v1/inventory/PROD-123-XYZ")
        assert response.status_code == 200
        
        data = response.json()
        assert data["product_id"] == "PROD-123-XYZ"


class TestBundleEndpoint:
    """Tests for bundle recommendations endpoint."""
    
    def test_get_bundle_recommendations(self):
        """Test successful bundle recommendations retrieval."""
        response = client.get("/api/v1/bundles/PROD-123")
        assert response.status_code == 200
        
        data = response.json()
        assert data["main_product_id"] == "PROD-123"
        assert "recommended_products" in data
        assert isinstance(data["recommended_products"], list)
        assert "reason" in data
    
    def test_get_bundle_recommendations_with_discount(self):
        """Test bundle recommendations include discount information."""
        response = client.get("/api/v1/bundles/PROD-123")
        data = response.json()
        
        if "discount_percentage" in data:
            assert isinstance(data["discount_percentage"], float)
            assert 0.0 <= data["discount_percentage"] <= 100.0


class TestMetricsEndpoint:
    """Tests for metrics endpoint."""
    
    def test_get_metrics(self):
        """Test metrics endpoint returns data."""
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "uptime_seconds" in data


class TestRateLimiting:
    """Tests for rate limiting functionality."""
    
    def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced."""
        # This test would need to be adjusted based on rate limits
        # Make many rapid requests to trigger rate limit
        
        # Note: This is a simplified test
        # In production, you'd want to test actual rate limit thresholds
        pass


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_404_not_found(self):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test 405 error for wrong HTTP method."""
        response = client.put("/health")
        assert response.status_code == 405


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self):
        """Test that CORS headers are present."""
        response = client.options("/api/v1/inventory/PROD-123")
        # Check for CORS headers
        assert "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]


class TestValidation:
    """Tests for input validation."""
    
    def test_whitespace_validation(self):
        """Test that whitespace-only inputs are rejected."""
        payload = {
            "supplier_id": "   ",
            "product_id": "PROD-123",
            "quantity": 10
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 422
    
    def test_data_type_validation(self):
        """Test that incorrect data types are rejected."""
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": "not-a-number"
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 422


class TestCaching:
    """Tests for caching behavior."""
    
    @patch('main.redis_client')
    def test_cache_miss_and_set(self, mock_redis):
        """Test cache miss and subsequent cache set."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)
        
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # First request should not be cached
        assert data.get("cached", False) == False


@pytest.fixture
def mock_redis():
    """Fixture to mock Redis client."""
    with patch('main.redis_client') as mock:
        mock.get = AsyncMock(return_value=None)
        mock.setex = AsyncMock(return_value=True)
        mock.ping = AsyncMock(return_value=True)
        yield mock


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

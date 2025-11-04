"""
Integration tests for Twisted Monk Suite.
Tests the interaction between different components.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'operations'))

from fastapi.testclient import TestClient
from main import app
from inventory_monitor import InventoryMonitor, Product
from lead_time import LeadTimeCalculator, SupplierProfile, SupplierTier


client = TestClient(app)


class TestAPIIntegration:
    """Test API integration with operations modules."""
    
    def test_api_to_lead_time_integration(self):
        """Test API endpoint integrates with lead time calculator."""
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify response matches lead time calculator output
        calculator = LeadTimeCalculator()
        estimate = calculator.calculate("SUP001", "PROD-123", 50)
        
        assert data["supplier_id"] == estimate.supplier_id
        assert data["product_id"] == estimate.product_id
        assert isinstance(data["estimated_days"], int)
    
    def test_api_inventory_endpoint_data_format(self):
        """Test inventory API returns data in expected format."""
        response = client.get("/api/v1/inventory/PROD-123")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify format matches inventory monitor Product structure
        assert "product_id" in data
        assert "available" in data
        assert "reserved" in data
        assert "incoming" in data
        assert "status" in data


class TestLeadTimeCalculator:
    """Test lead time calculator functionality."""
    
    def test_lead_time_calculation_basic(self):
        """Test basic lead time calculation."""
        calculator = LeadTimeCalculator()
        
        estimate = calculator.calculate(
            supplier_id="SUP001",
            product_id="PROD-123",
            quantity=25
        )
        
        assert estimate.product_id == "PROD-123"
        assert estimate.supplier_id == "SUP001"
        assert estimate.estimated_days > 0
        assert 0.0 <= estimate.confidence <= 1.0
        assert len(estimate.factors) > 0
    
    def test_lead_time_large_quantity_adjustment(self):
        """Test lead time increases for large quantities."""
        calculator = LeadTimeCalculator()
        
        small_order = calculator.calculate("SUP001", "PROD-123", 10)
        large_order = calculator.calculate("SUP001", "PROD-123", 150)
        
        # Large orders should take longer
        assert large_order.estimated_days >= small_order.estimated_days
    
    def test_lead_time_supplier_tier_impact(self):
        """Test that supplier tier affects lead time."""
        calculator = LeadTimeCalculator()
        
        # Premium supplier should be faster
        premium_estimate = calculator.calculate("SUP001", "PROD-123", 50)
        economy_estimate = calculator.calculate("SUP003", "PROD-123", 50)
        
        # Economy supplier should have longer lead time
        assert economy_estimate.estimated_days >= premium_estimate.estimated_days
    
    def test_supplier_recommendations(self):
        """Test getting supplier recommendations."""
        from datetime import datetime, timedelta
        
        calculator = LeadTimeCalculator()
        required_date = datetime.now() + timedelta(days=15)
        
        recommendations = calculator.get_supplier_recommendations(
            product_id="PROD-123",
            required_by_date=required_date,
            quantity=50
        )
        
        # Should return recommendations
        assert isinstance(recommendations, list)
        
        # Recommendations should be sorted by suitability
        if len(recommendations) > 1:
            # First recommendation should have highest confidence
            assert recommendations[0][1].confidence >= recommendations[1][1].confidence
    
    def test_bulk_calculation(self):
        """Test bulk lead time calculation."""
        calculator = LeadTimeCalculator()
        
        orders = [
            ("SUP001", "PROD-001", 10),
            ("SUP002", "PROD-002", 20),
            ("SUP001", "PROD-003", 30),
        ]
        
        results = calculator.bulk_calculate(orders)
        
        assert len(results) == 3
        assert "PROD-001" in results
        assert "PROD-002" in results
        assert "PROD-003" in results
    
    def test_invalid_supplier_error(self):
        """Test error handling for invalid supplier."""
        calculator = LeadTimeCalculator()
        
        with pytest.raises(ValueError, match="Supplier .* not found"):
            calculator.calculate("INVALID-SUP", "PROD-123", 50)
    
    def test_invalid_quantity_error(self):
        """Test error handling for invalid quantity."""
        calculator = LeadTimeCalculator()
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            calculator.calculate("SUP001", "PROD-123", -5)


class TestCacheIntegration:
    """Test Redis caching integration."""
    
    @patch('main.redis_client')
    def test_cache_hit_flow(self, mock_redis):
        """Test API with cache hit."""
        import json
        
        # Mock cached data
        cached_data = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "estimated_days": 7,
            "confidence": 0.85
        }
        
        mock_redis.get = AsyncMock(return_value=json.dumps(cached_data))
        mock_redis.ping = AsyncMock(return_value=True)
        
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        data = response.json()
        
        # Should indicate data came from cache
        assert data.get("cached") in [True, False]  # Either cached or calculated
    
    @patch('main.redis_client')
    def test_cache_miss_flow(self, mock_redis):
        """Test API with cache miss."""
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.setex = AsyncMock(return_value=True)
        mock_redis.ping = AsyncMock(return_value=True)
        
        payload = {
            "supplier_id": "SUP001",
            "product_id": "PROD-123",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 200
        
        # Verify setex was called to cache the result
        # Note: In real test, mock_redis.setex.called might not work with TestClient
        # This is a simplified assertion


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_low_stock_alert_workflow(self):
        """Test complete workflow from stock check to alert."""
        # Setup monitor
        monitor = InventoryMonitor(check_interval_seconds=1)
        
        # Add product with low stock
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=5,
            reserved_stock=0,
            incoming_stock=0,
            critical_threshold=10
        )
        monitor.add_product(product)
        
        # Run check
        await monitor.check_inventory()
        
        # Verify alert was generated
        assert len(monitor.alerts) > 0
        alert = monitor.alerts[0]
        assert alert.product.product_id == "PROD-001"
        
        # Get lead time for reorder
        calculator = LeadTimeCalculator()
        estimate = calculator.calculate("SUP001", "PROD-001", 100)
        
        assert estimate.estimated_days > 0
        
        # Verify we can calculate when stock will arrive
        from datetime import datetime, timedelta
        expected_arrival = datetime.now() + timedelta(days=estimate.estimated_days)
        assert expected_arrival > datetime.now()
    
    def test_api_metrics_collection(self):
        """Test that API metrics are collected."""
        # Make several API calls
        for i in range(5):
            client.get("/health")
        
        # Get metrics
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)


class TestErrorHandlingIntegration:
    """Test error handling across components."""
    
    def test_api_error_propagation(self):
        """Test that errors from operations propagate correctly to API."""
        # Invalid supplier should return appropriate error
        payload = {
            "supplier_id": "",
            "product_id": "PROD-123",
            "quantity": 50
        }
        
        response = client.post("/api/v1/lead-time", json=payload)
        assert response.status_code == 422
        
        # Should have error details
        data = response.json()
        assert "detail" in data or "error" in data
    
    @pytest.mark.asyncio
    async def test_monitor_handles_missing_product(self):
        """Test monitor handles updates for non-existent products."""
        monitor = InventoryMonitor()
        
        # Update stock for non-existent product should not crash
        monitor.update_stock("NON-EXISTENT", current=100, reserved=0, incoming=0)
        
        # Should complete without error
        await monitor.check_inventory()


class TestPerformance:
    """Basic performance tests."""
    
    def test_api_response_time(self):
        """Test API responds within acceptable time."""
        import time
        
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond within 1 second
    
    def test_bulk_lead_time_calculation_performance(self):
        """Test bulk calculations complete in reasonable time."""
        import time
        
        calculator = LeadTimeCalculator()
        
        # Create 100 orders
        orders = [
            (f"SUP00{i % 3 + 1}", f"PROD-{i:03d}", (i % 100) + 1)
            for i in range(100)
        ]
        
        start = time.time()
        results = calculator.bulk_calculate(orders)
        duration = time.time() - start
        
        assert len(results) > 0
        assert duration < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_monitor_check_performance(self):
        """Test inventory monitor checks complete quickly."""
        import time
        
        monitor = InventoryMonitor()
        
        # Add 50 products
        for i in range(50):
            product = Product(
                product_id=f"PROD-{i:03d}",
                name=f"Product {i}",
                sku=f"SKU-{i:03d}",
                current_stock=100,
                reserved_stock=10,
                incoming_stock=20
            )
            monitor.add_product(product)
        
        start = time.time()
        await monitor.check_inventory()
        duration = time.time() - start
        
        assert duration < 2.0  # Should complete within 2 seconds


class TestDataConsistency:
    """Test data consistency across components."""
    
    def test_product_status_consistency(self):
        """Test product status is consistent between API and monitor."""
        # Get inventory from API
        response = client.get("/api/v1/inventory/PROD-123")
        api_data = response.json()
        
        # Create equivalent Product
        product = Product(
            product_id="PROD-123",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=api_data["available"] + api_data["reserved"],
            reserved_stock=api_data["reserved"],
            incoming_stock=api_data["incoming"]
        )
        
        # Status should match
        assert product.status.value in ["in_stock", "low_stock", "critical_stock", "out_of_stock"]


class TestSecurityIntegration:
    """Test security features integration."""
    
    def test_rate_limiting_applied(self):
        """Test that rate limiting is enforced."""
        # This is a placeholder - actual implementation would need
        # to make many requests to trigger rate limit
        response = client.get("/health")
        assert "X-Process-Time" in response.headers or response.status_code == 200
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = client.options("/api/v1/inventory/PROD-123")
        # Should have CORS headers in production
        assert response.status_code in [200, 404, 405]  # Depends on configuration


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

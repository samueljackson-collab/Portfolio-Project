"""
Test suite for inventory monitor module.
"""

import pytest
import asyncio
from datetime import datetime
import sys
import os

# Add operations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'operations'))

from inventory_monitor import (
    InventoryMonitor,
    Product,
    Alert,
    AlertLevel,
    StockStatus,
    SlackNotifier,
    EmailNotifier
)


class TestProduct:
    """Tests for Product dataclass."""
    
    def test_product_creation(self):
        """Test creating a product instance."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=100,
            reserved_stock=20,
            incoming_stock=50
        )
        
        assert product.product_id == "PROD-001"
        assert product.name == "Test Product"
        assert product.current_stock == 100
    
    def test_available_stock_calculation(self):
        """Test available stock calculation."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=100,
            reserved_stock=20,
            incoming_stock=50
        )
        
        assert product.available_stock == 80  # 100 - 20
    
    def test_available_stock_negative_handling(self):
        """Test that available stock doesn't go negative."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=10,
            reserved_stock=20,
            incoming_stock=0
        )
        
        assert product.available_stock == 0  # Should be 0, not negative
    
    def test_stock_status_in_stock(self):
        """Test stock status when product is in stock."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=100,
            reserved_stock=0,
            incoming_stock=0,
            low_threshold=50,
            critical_threshold=10
        )
        
        assert product.status == StockStatus.IN_STOCK
    
    def test_stock_status_low_stock(self):
        """Test stock status when product is low stock."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=30,
            reserved_stock=0,
            incoming_stock=0,
            low_threshold=50,
            critical_threshold=10
        )
        
        assert product.status == StockStatus.LOW_STOCK
    
    def test_stock_status_critical(self):
        """Test stock status when product is critically low."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=5,
            reserved_stock=0,
            incoming_stock=0,
            low_threshold=50,
            critical_threshold=10
        )
        
        assert product.status == StockStatus.CRITICAL_STOCK
    
    def test_stock_status_out_of_stock(self):
        """Test stock status when product is out of stock."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=0,
            reserved_stock=0,
            incoming_stock=0
        )
        
        assert product.status == StockStatus.OUT_OF_STOCK


class TestAlert:
    """Tests for Alert dataclass."""
    
    def test_alert_creation(self):
        """Test creating an alert."""
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=5,
            reserved_stock=0,
            incoming_stock=0
        )
        
        alert = Alert(
            alert_id="alert-001",
            product=product,
            level=AlertLevel.CRITICAL,
            message="Critical stock level"
        )
        
        assert alert.alert_id == "alert-001"
        assert alert.level == AlertLevel.CRITICAL
        assert alert.acknowledged == False


class TestInventoryMonitor:
    """Tests for InventoryMonitor class."""
    
    def test_monitor_creation(self):
        """Test creating an inventory monitor."""
        monitor = InventoryMonitor(check_interval_seconds=60)
        
        assert monitor.check_interval == 60
        assert len(monitor.products) == 0
        assert len(monitor.alerts) == 0
        assert monitor.running == False
    
    def test_add_product(self):
        """Test adding a product to monitor."""
        monitor = InventoryMonitor()
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=100,
            reserved_stock=0,
            incoming_stock=0
        )
        
        monitor.add_product(product)
        
        assert "PROD-001" in monitor.products
        assert monitor.products["PROD-001"] == product
    
    def test_update_stock(self):
        """Test updating stock levels."""
        monitor = InventoryMonitor()
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=100,
            reserved_stock=0,
            incoming_stock=0
        )
        monitor.add_product(product)
        
        # Update stock
        monitor.update_stock("PROD-001", current=50, reserved=10, incoming=25)
        
        updated_product = monitor.products["PROD-001"]
        assert updated_product.current_stock == 50
        assert updated_product.reserved_stock == 10
        assert updated_product.incoming_stock == 25
    
    @pytest.mark.asyncio
    async def test_check_inventory_critical(self):
        """Test inventory check generates critical alert."""
        monitor = InventoryMonitor()
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
        
        # Check inventory
        await monitor.check_inventory()
        
        # Should have generated an alert
        assert len(monitor.alerts) > 0
        assert "PROD-001" in monitor.alerted_products
        
        # Check alert level
        alert = monitor.alerts[0]
        assert alert.level == AlertLevel.CRITICAL
    
    @pytest.mark.asyncio
    async def test_check_inventory_low_stock(self):
        """Test inventory check generates low stock warning."""
        monitor = InventoryMonitor()
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=30,
            reserved_stock=0,
            incoming_stock=0,
            low_threshold=50,
            critical_threshold=10
        )
        monitor.add_product(product)
        
        await monitor.check_inventory()
        
        assert len(monitor.alerts) > 0
        alert = monitor.alerts[0]
        assert alert.level == AlertLevel.WARNING
    
    @pytest.mark.asyncio
    async def test_check_inventory_no_alert_when_in_stock(self):
        """Test no alert generated when stock is sufficient."""
        monitor = InventoryMonitor()
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=100,
            reserved_stock=0,
            incoming_stock=0,
            low_threshold=50
        )
        monitor.add_product(product)
        
        await monitor.check_inventory()
        
        # Should not generate any alerts
        assert len(monitor.alerts) == 0
        assert "PROD-001" not in monitor.alerted_products
    
    @pytest.mark.asyncio
    async def test_alert_deduplication(self):
        """Test that alerts are not duplicated for same product."""
        monitor = InventoryMonitor()
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
        
        # Check inventory multiple times
        await monitor.check_inventory()
        alert_count_1 = len(monitor.alerts)
        
        await monitor.check_inventory()
        alert_count_2 = len(monitor.alerts)
        
        # Should not create duplicate alerts
        assert alert_count_1 == alert_count_2
    
    @pytest.mark.asyncio
    async def test_alert_clearing(self):
        """Test that alerts are cleared when stock recovers."""
        monitor = InventoryMonitor()
        product = Product(
            product_id="PROD-001",
            name="Test Product",
            sku="TEST-SKU",
            current_stock=5,
            reserved_stock=0,
            incoming_stock=0,
            critical_threshold=10,
            low_threshold=50
        )
        monitor.add_product(product)
        
        # Generate alert
        await monitor.check_inventory()
        assert "PROD-001" in monitor.alerted_products
        
        # Update stock to normal levels
        monitor.update_stock("PROD-001", current=100, reserved=0, incoming=0)
        
        # Check inventory again
        await monitor.check_inventory()
        
        # Alert should be cleared
        assert "PROD-001" not in monitor.alerted_products
    
    def test_get_summary(self):
        """Test getting inventory summary."""
        monitor = InventoryMonitor()
        
        # Add various products
        products = [
            Product("P1", "Product 1", "SKU1", 100, 0, 0, 50, 10),  # In stock
            Product("P2", "Product 2", "SKU2", 30, 0, 0, 50, 10),   # Low stock
            Product("P3", "Product 3", "SKU3", 5, 0, 0, 50, 10),    # Critical
            Product("P4", "Product 4", "SKU4", 0, 0, 0, 50, 10),    # Out of stock
        ]
        
        for product in products:
            monitor.add_product(product)
        
        summary = monitor.get_summary()
        
        assert summary["total_products"] == 4
        assert summary["in_stock"] == 1
        assert summary["low_stock"] == 1
        assert summary["critical_stock"] == 1
        assert summary["out_of_stock"] == 1
        assert len(summary["products"]) == 4


class TestNotifiers:
    """Tests for notification channels."""
    
    @pytest.mark.asyncio
    async def test_slack_notifier_creation(self):
        """Test creating a Slack notifier."""
        notifier = SlackNotifier(webhook_url="https://hooks.slack.com/test")
        assert notifier.webhook_url == "https://hooks.slack.com/test"
    
    def test_email_notifier_creation(self):
        """Test creating an email notifier."""
        notifier = EmailNotifier(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="test@example.com",
            password="password",
            from_addr="from@example.com",
            to_addrs=["to@example.com"]
        )
        
        assert notifier.smtp_host == "smtp.gmail.com"
        assert notifier.smtp_port == 587
        assert len(notifier.to_addrs) == 1


class TestIntegration:
    """Integration tests for full workflow."""
    
    @pytest.mark.asyncio
    async def test_monitor_with_notifier(self):
        """Test monitor with notification system."""
        monitor = InventoryMonitor()
        
        # Add a mock notifier
        notifier = SlackNotifier(webhook_url="https://test.webhook.url")
        monitor.add_notifier(notifier)
        
        # Add critical stock product
        product = Product(
            product_id="PROD-001",
            name="Critical Product",
            sku="CRIT-SKU",
            current_stock=5,
            reserved_stock=0,
            incoming_stock=0,
            critical_threshold=10
        )
        monitor.add_product(product)
        
        # Note: This won't actually send notification without mocking HTTP
        # In real tests, you'd mock the HTTP client
        await monitor.check_inventory()
        
        assert len(monitor.alerts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

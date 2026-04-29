import asyncio
import pytest

from Twisted_Monk_Suite_v1.operations.inventory_monitor import InventoryMonitor


@pytest.mark.asyncio
async def test_inventory_monitor_creates_alert(monkeypatch):
    monitor = InventoryMonitor()

    async def _mock_get_products(*args, **kwargs):
        return [
            {
                "id": 1,
                "title": "Limited Edition",
                "handle": "limited-edition",
                "variants": [
                    {"inventory_quantity": 1},
                ],
            }
        ]

    async def _mock_send_alert(alert):
        monitor._last_alert = alert

    monkeypatch.setattr(monitor, "get_shopify_products", _mock_get_products)
    monkeypatch.setattr(monitor, "send_alert", _mock_send_alert)

    alerts = await monitor.check_inventory_levels()
    assert alerts, "Expected at least one alert"
    assert alerts[0]["alert_type"] in {"low_stock", "critical_stock", "out_of_stock"}


def test_alert_message_content():
    message = InventoryMonitor.generate_alert_message("low_stock", "Sample", 3)
    assert "LOW STOCK" in message.upper()

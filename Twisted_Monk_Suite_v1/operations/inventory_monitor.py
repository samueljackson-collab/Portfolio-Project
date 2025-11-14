#!/usr/bin/env python3
"""
Twisted Monk Inventory Monitor
Continuous monitoring and alerting for inventory levels
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from redis import Redis
from redis.exceptions import RedisError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventory_monitor")


class SimpleCache:
    def __init__(self) -> None:
        self._store: Dict[str, str] = {}
        self._expiry: Dict[str, datetime] = {}

    def _cleanup(self) -> None:
        now = datetime.utcnow()
        expired = [key for key, value in self._expiry.items() if value <= now]
        for key in expired:
            self._store.pop(key, None)
            self._expiry.pop(key, None)

    def get(self, key: str) -> Optional[str]:
        self._cleanup()
        return self._store.get(key)

    def setex(self, key: str, seconds: int, value: str) -> None:
        self._store[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=seconds)

    def lpush(self, key: str, value: str) -> None:
        existing = json.loads(self._store.get(key, "[]"))
        existing.insert(0, value)
        self._store[key] = json.dumps(existing)

    def ltrim(self, key: str, start: int, end: int) -> None:  # noqa: D401
        existing = json.loads(self._store.get(key, "[]"))
        self._store[key] = json.dumps(existing[start : end + 1])

    def exists(self, key: str) -> bool:
        self._cleanup()
        return key in self._store

    def set(self, key: str, value: str) -> None:
        self._store[key] = value

    def expire(self, key: str, seconds: int) -> None:
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=seconds)


def get_cache() -> object:
    try:
        client = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD") or None,
            decode_responses=True,
        )
        client.ping()
        logger.info("Connected to Redis for inventory monitoring")
        return client
    except (RedisError, OSError) as exc:
        logger.warning("Redis unavailable, using SimpleCache: %s", exc)
        return SimpleCache()


cache = get_cache()


class InventoryMonitor:
    def __init__(self) -> None:
        self.cache = cache
        self.shopify_store = os.getenv("SHOPIFY_STORE_DOMAIN")
        self.shopify_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.thresholds = {
            "low_stock": 10,
            "critical_stock": 3,
            "out_of_stock": 0,
        }
        self.alert_cooldown = int(os.getenv("ALERT_COOLDOWN_MINUTES", "60"))

    async def check_inventory_levels(self) -> List[Dict]:
        products = await self.get_shopify_products()
        alerts: List[Dict] = []
        for product in products:
            alerts.extend(await self.analyze_product_inventory(product))
        await self.process_alerts(alerts)
        logger.info("Inventory check completed: %s alerts", len(alerts))
        return alerts

    async def get_shopify_products(self) -> List[Dict]:
        if not self.shopify_store or not self.shopify_token:
            raise RuntimeError("Shopify credentials are not configured")

        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "X-Shopify-Access-Token": self.shopify_token,
                "Content-Type": "application/json",
            }
            response = await client.get(
                f"https://{self.shopify_store}/admin/api/2023-10/products.json",
                headers=headers,
                params={
                    "limit": 250,
                    "fields": "id,title,variants,inventory_quantity,vendor,handle",
                },
            )
            response.raise_for_status()
            return response.json().get("products", [])

    async def analyze_product_inventory(self, product: Dict) -> List[Dict]:
        alerts: List[Dict] = []
        total_quantity = sum(
            variant.get("inventory_quantity", 0) for variant in product.get("variants", [])
        )

        if total_quantity <= self.thresholds["out_of_stock"]:
            alerts.append(await self.create_alert(product, "out_of_stock", total_quantity))
        elif total_quantity <= self.thresholds["critical_stock"]:
            alerts.append(await self.create_alert(product, "critical_stock", total_quantity))
        elif total_quantity <= self.thresholds["low_stock"]:
            alerts.append(await self.create_alert(product, "low_stock", total_quantity))

        drop_alert = await self.check_inventory_drop(product, total_quantity)
        if drop_alert:
            alerts.append(drop_alert)

        return alerts

    async def create_alert(self, product: Dict, alert_type: str, quantity: int) -> Dict:
        return {
            "product_id": str(product.get("id")),
            "product_title": product.get("title"),
            "product_handle": product.get("handle"),
            "alert_type": alert_type,
            "current_quantity": quantity,
            "threshold": self.thresholds.get(alert_type, 0),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": self.get_alert_severity(alert_type),
            "message": self.generate_alert_message(alert_type, product.get("title"), quantity),
        }

    @staticmethod
    def get_alert_severity(alert_type: str) -> str:
        severity_map = {
            "out_of_stock": "critical",
            "critical_stock": "high",
            "low_stock": "medium",
            "inventory_drop": "medium",
        }
        return severity_map.get(alert_type, "low")

    @staticmethod
    def generate_alert_message(alert_type: str, product_title: str, quantity: int) -> str:
        messages = {
            "out_of_stock": f"🚨 OUT OF STOCK: {product_title} has 0 inventory",
            "critical_stock": f"⚠️ CRITICAL STOCK: {product_title} has only {quantity} units left",
            "low_stock": f"📉 LOW STOCK: {product_title} has {quantity} units left",
            "inventory_drop": f"📊 INVENTORY DROP: {product_title} had a significant inventory decrease",
        }
        return messages.get(alert_type, f"Inventory alert for {product_title}")

    async def check_inventory_drop(self, product: Dict, current_quantity: int) -> Optional[Dict]:
        product_id = str(product.get("id"))
        previous_key = f"previous_inventory:{product_id}"
        previous_quantity = self.cache.get(previous_key)
        if previous_quantity is not None:
            previous_quantity = int(previous_quantity)
            drop_amount = previous_quantity - current_quantity
            if previous_quantity > 0 and drop_amount >= 5 and drop_amount / previous_quantity > 0.5:
                return await self.create_alert(product, "inventory_drop", current_quantity)
        self.cache.set(previous_key, str(current_quantity))
        self.cache.expire(previous_key, 86400)
        return None

    async def process_alerts(self, alerts: List[Dict]) -> None:
        for alert in alerts:
            cooldown_key = f"alert_cooldown:{alert['product_id']}:{alert['alert_type']}"
            if self.cache.exists(cooldown_key):
                continue
            await self.send_alert(alert)
            self.cache.setex(cooldown_key, self.alert_cooldown * 60, "1")

    async def send_alert(self, alert: Dict) -> None:
        logger.warning("INVENTORY ALERT: %s", alert["message"])
        await self.send_slack_alert(alert)
        self.store_alert(alert)

    async def send_slack_alert(self, alert: Dict) -> None:
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return

        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "📦 Inventory Alert"},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Product:*\n{alert['product_title']}"},
                        {"type": "mrkdwn", "text": f"*Quantity:*\n{alert['current_quantity']} units"},
                        {"type": "mrkdwn", "text": f"*Severity:*\n{alert['severity'].upper()}"},
                        {"type": "mrkdwn", "text": f"*Type:*\n{alert['alert_type'].replace('_', ' ').title()}"},
                    ],
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Product"},
                            "url": f"https://{self.shopify_store}/admin/products/{alert['product_id']}",
                        }
                    ],
                },
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(webhook_url, json=payload)
        except httpx.HTTPError as exc:
            logger.error("Failed to send Slack alert: %s", exc)

    def store_alert(self, alert: Dict) -> None:
        alert_key = f"inventory_alerts:{datetime.utcnow():%Y%m%d}"
        self.cache.lpush(alert_key, json.dumps(alert))
        self.cache.ltrim(alert_key, 0, 999)

    async def run_continuous_monitoring(self) -> None:
        logger.info("Starting continuous inventory monitoring loop")
        while True:
            try:
                await self.check_inventory_levels()
            except Exception as exc:  # noqa: BLE001
                logger.error("Monitoring loop error: %s", exc)
            await asyncio.sleep(int(os.getenv("MONITOR_INTERVAL_SECONDS", "300")))


async def main() -> None:
    monitor = InventoryMonitor()
    await monitor.check_inventory_levels()


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())

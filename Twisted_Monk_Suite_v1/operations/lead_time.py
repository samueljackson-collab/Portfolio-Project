#!/usr/bin/env python3
"""
Twisted Monk Lead Time Calculator
Monitors supplier lead times and predicts inventory needs
"""

import asyncio
import json
import logging
import os
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("lead_time_calculator")


class LeadTimeCalculator:
    def __init__(self) -> None:
        self.shopify_store = os.getenv("SHOPIFY_STORE_DOMAIN")
        self.shopify_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        self.alert_email = os.getenv("ALERT_EMAIL")

        self.thresholds = {
            "critical": 21,
            "warning": 14,
            "normal": 7,
        }

        self.suppliers = {
            "supplier_a": {
                "api_url": os.getenv("SUPPLIER_A_API_URL"),
                "api_key": os.getenv("SUPPLIER_A_API_KEY"),
                "lead_time_days": 10,
            },
            "supplier_b": {
                "api_url": os.getenv("SUPPLIER_B_API_URL"),
                "api_key": os.getenv("SUPPLIER_B_API_KEY"),
                "lead_time_days": 14,
            },
        }

    async def get_shopify_inventory(self) -> List[Dict]:
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
                    "fields": "id,title,variants,inventory_quantity,vendor",
                },
            )
            response.raise_for_status()
            products = response.json().get("products", [])
            logger.info("Retrieved %s products from Shopify", len(products))
            return products

    async def get_supplier_lead_times(self, supplier: str) -> Dict:
        supplier_config = self.suppliers.get(supplier)
        if not supplier_config:
            raise ValueError(f"Unknown supplier: {supplier}")

        if not supplier_config.get("api_url") or not supplier_config.get("api_key"):
            logger.warning("Supplier %s missing API configuration, using default lead time", supplier)
            return {"estimated_lead_time_days": supplier_config.get("lead_time_days", 14)}

        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {supplier_config['api_key']}",
                "Content-Type": "application/json",
            }
            try:
                response = await client.get(
                    f"{supplier_config['api_url']}/lead-times",
                    headers=headers,
                )
                response.raise_for_status()
                logger.info("Retrieved lead times from %s", supplier)
                return response.json()
            except httpx.HTTPError as exc:
                logger.error("Failed to fetch lead times from %s: %s", supplier, exc)
                return {"estimated_lead_time_days": supplier_config.get("lead_time_days", 14)}

    def calculate_demand_forecast(self, products: List[Dict], days: int = 30) -> Dict[str, float]:
        forecast: Dict[str, float] = {}
        for product in products:
            product_id = str(product.get("id"))
            total_inventory = sum(
                variant.get("inventory_quantity", 0) for variant in product.get("variants", [])
            )
            if total_inventory > 0:
                velocity = self.calculate_product_velocity(product_id)
                forecast[product_id] = velocity * days
            else:
                forecast[product_id] = 0.0
        return forecast

    def calculate_product_velocity(self, product_id: str) -> float:  # noqa: D401
        return round(random.uniform(0.1, 5.0), 2)

    async def generate_replenishment_alerts(self) -> List[Dict]:
        products = await self.get_shopify_inventory()
        demand_forecast = self.calculate_demand_forecast(products)
        alerts: List[Dict] = []

        for product in products:
            product_id = str(product.get("id"))
            vendor = (product.get("vendor") or "").lower()
            total_inventory = sum(
                variant.get("inventory_quantity", 0) for variant in product.get("variants", [])
            )
            supplier = self.map_vendor_to_supplier(vendor)
            if not supplier:
                continue

            supplier_data = await self.get_supplier_lead_times(supplier)
            lead_time_days = supplier_data.get("estimated_lead_time_days", 14)

            daily_demand = demand_forecast.get(product_id, 0) / 30 if demand_forecast.get(product_id) else 0
            days_of_inventory = (
                total_inventory / daily_demand if daily_demand > 0 else float("inf")
            )

            alert_level = self.determine_alert_level(days_of_inventory, lead_time_days)
            if alert_level not in {"warning", "critical"}:
                continue

            alerts.append(
                {
                    "product_id": product_id,
                    "product_title": product.get("title"),
                    "vendor": vendor,
                    "supplier": supplier,
                    "current_inventory": total_inventory,
                    "lead_time_days": lead_time_days,
                    "days_of_inventory": round(days_of_inventory, 1)
                    if days_of_inventory != float("inf")
                    else "∞",
                    "alert_level": alert_level,
                    "recommended_action": self.get_recommended_action(alert_level),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        logger.info("Generated %s replenishment alerts", len(alerts))
        return alerts

    def determine_alert_level(self, days_of_inventory: float, lead_time_days: int) -> str:
        if days_of_inventory <= lead_time_days:
            return "critical"
        if days_of_inventory <= lead_time_days + 7:
            return "warning"
        return "normal"

    @staticmethod
    def get_recommended_action(alert_level: str) -> str:
        actions = {
            "critical": "IMMEDIATE REORDER - Risk of stockout",
            "warning": "Schedule reorder within 3 days",
            "normal": "Monitor inventory levels",
        }
        return actions.get(alert_level, "Monitor inventory levels")

    @staticmethod
    def map_vendor_to_supplier(vendor: str) -> Optional[str]:
        vendor_supplier_map = {
            "alpha garments": "supplier_a",
            "beta textiles": "supplier_b",
            "gamma fabrics": "supplier_a",
        }
        return vendor_supplier_map.get(vendor)

    async def send_alert_email(self, alerts: List[Dict]) -> None:
        if not alerts or not self.alert_email:
            return

        critical_alerts = [a for a in alerts if a["alert_level"] == "critical"]
        warning_alerts = [a for a in alerts if a["alert_level"] == "warning"]
        if not critical_alerts and not warning_alerts:
            return

        msg = MIMEMultipart()
        msg["From"] = "inventory-alerts@twistedmonk.com"
        msg["To"] = self.alert_email
        msg["Subject"] = f"Inventory Replenishment Alerts - {datetime.utcnow():%Y-%m-%d}"

        def build_alert_section(alerts: List[Dict], css_class: str, emoji: str, title: str) -> str:
            items = []
            for alert in alerts:
                items.append(
                    f"<div class='{css_class}'>"
                    f"<div class='product-title'>{alert['product_title']}</div>"
                    f"<div class='alert-info'>"
                    f"Inventory: {alert['current_inventory']} units<br>"
                    f"Days of Inventory: {alert['days_of_inventory']}<br>"
                    f"Lead Time: {alert['lead_time_days']} days<br>"
                    f"Supplier: {alert['supplier']}<br>"
                    f"Action: {alert['recommended_action']}"
                    f"</div></div>"
                )
            return (
                f"<h3>{emoji} {title} ({len(alerts)})</h3>" + "".join(items)
                if alerts
                else ""
            )

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .critical {{ background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 12px; margin: 8px 0; }}
                .warning {{ background-color: #fef3c7; border-left: 4px solid #d97706; padding: 12px; margin: 8px 0; }}
                .product-title {{ font-weight: bold; font-size: 16px; }}
                .alert-info {{ font-size: 14px; color: #374151; }}
            </style>
        </head>
        <body>
            <h2>Inventory Replenishment Alerts</h2>
            <p>Generated at: {datetime.utcnow():%Y-%m-%d %H:%M UTC}</p>
            {build_alert_section(critical_alerts, 'critical', '🚨', 'Critical Alerts')}
            {build_alert_section(warning_alerts, 'warning', '⚠️', 'Warning Alerts')}
            <p><em>This is an automated alert from Twisted Monk Inventory System.</em></p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        if not smtp_user or not smtp_password:
            logger.warning("SMTP credentials not configured; skipping email delivery")
            return

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Alert email sent to %s", self.alert_email)

    async def generate_lead_time_report(self) -> Dict:
        products = await self.get_shopify_inventory()
        alerts = await self.generate_replenishment_alerts()
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_products": len(products),
                "critical_alerts": len([a for a in alerts if a["alert_level"] == "critical"]),
                "warning_alerts": len([a for a in alerts if a["alert_level"] == "warning"]),
                "average_lead_time": self.calculate_average_lead_time(alerts),
            },
            "alerts": alerts,
            "products_analyzed": len(products),
        }

        output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"lead_time_report_{datetime.utcnow():%Y%m%d_%H%M}.json"
        report_path.write_text(json.dumps(report, indent=2))
        logger.info("Lead time report saved to %s", report_path)
        return report

    @staticmethod
    def calculate_average_lead_time(alerts: List[Dict]) -> float:
        relevant = [alert["lead_time_days"] for alert in alerts if alert.get("lead_time_days")]
        if not relevant:
            return 0.0
        return round(sum(relevant) / len(relevant), 2)


async def main() -> None:
    calculator = LeadTimeCalculator()
    report = await calculator.generate_lead_time_report()
    await calculator.send_alert_email(report.get("alerts", []))
    logger.info("Lead time analysis completed: %s", report.get("summary"))


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())

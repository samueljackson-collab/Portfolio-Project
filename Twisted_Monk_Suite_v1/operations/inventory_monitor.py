"""
Inventory Monitor for Twisted Monk Suite.
Monitors inventory levels and sends alerts when thresholds are breached.
Multi-supplier support with Slack and Email notifications.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import httpx

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class StockStatus(Enum):
    """Stock status levels."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    CRITICAL_STOCK = "critical_stock"
    OUT_OF_STOCK = "out_of_stock"


@dataclass
class Product:
    """Product inventory information."""
    product_id: str
    name: str
    sku: str
    current_stock: int
    reserved_stock: int
    incoming_stock: int
    low_threshold: int = 50
    critical_threshold: int = 10
    supplier_id: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def available_stock(self) -> int:
        """Calculate available stock (current - reserved)."""
        return max(0, self.current_stock - self.reserved_stock)
    
    @property
    def status(self) -> StockStatus:
        """Determine stock status based on thresholds."""
        available = self.available_stock
        
        if available == 0:
            return StockStatus.OUT_OF_STOCK
        elif available <= self.critical_threshold:
            return StockStatus.CRITICAL_STOCK
        elif available <= self.low_threshold:
            return StockStatus.LOW_STOCK
        else:
            return StockStatus.IN_STOCK


@dataclass
class Alert:
    """Inventory alert information."""
    alert_id: str
    product: Product
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


class NotificationChannel:
    """Base class for notification channels."""
    
    async def send(self, alert: Alert) -> bool:
        """Send an alert notification."""
        raise NotImplementedError


class SlackNotifier(NotificationChannel):
    """Send notifications to Slack via webhook."""
    
    def __init__(self, webhook_url: str):
        """Initialize Slack notifier."""
        self.webhook_url = webhook_url
    
    async def send(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        # Color code by severity
        color_map = {
            AlertLevel.INFO: "#36a64f",      # Green
            AlertLevel.WARNING: "#ff9900",   # Orange
            AlertLevel.CRITICAL: "#ff0000"   # Red
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(alert.level, "#808080"),
                "title": f"Inventory Alert: {alert.product.name}",
                "text": alert.message,
                "fields": [
                    {
                        "title": "Product ID",
                        "value": alert.product.product_id,
                        "short": True
                    },
                    {
                        "title": "SKU",
                        "value": alert.product.sku,
                        "short": True
                    },
                    {
                        "title": "Available Stock",
                        "value": str(alert.product.available_stock),
                        "short": True
                    },
                    {
                        "title": "Status",
                        "value": alert.product.status.value.replace("_", " ").title(),
                        "short": True
                    },
                    {
                        "title": "Incoming Stock",
                        "value": str(alert.product.incoming_stock),
                        "short": True
                    },
                    {
                        "title": "Alert Level",
                        "value": alert.level.value.upper(),
                        "short": True
                    }
                ],
                "footer": "Twisted Monk Inventory Monitor",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"Sent Slack alert for {alert.product.product_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False


class EmailNotifier(NotificationChannel):
    """Send notifications via email."""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: List[str]
    ):
        """Initialize email notifier."""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
    
    async def send(self, alert: Alert) -> bool:
        """Send alert via email."""
        if not self.to_addrs:
            logger.warning("No email recipients configured")
            return False
        
        subject = f"[{alert.level.value.upper()}] Inventory Alert: {alert.product.name}"
        
        # Create HTML email
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {'#ff0000' if alert.level == AlertLevel.CRITICAL else '#ff9900'};">
                Inventory Alert
            </h2>
            <p>{alert.message}</p>
            
            <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Field</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Value</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Product ID</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.product_id}</td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="border: 1px solid #ddd; padding: 8px;">SKU</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.sku}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Current Stock</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.current_stock}</td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="border: 1px solid #ddd; padding: 8px;">Reserved Stock</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.reserved_stock}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Available Stock</td>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>{alert.product.available_stock}</strong></td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="border: 1px solid #ddd; padding: 8px;">Incoming Stock</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.incoming_stock}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Status</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.status.value.replace("_", " ").title()}</td>
                </tr>
                <tr style="background-color: #f2f2f2;">
                    <td style="border: 1px solid #ddd; padding: 8px;">Supplier ID</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{alert.product.supplier_id or 'N/A'}</td>
                </tr>
            </table>
            
            <p style="margin-top: 20px; color: #666;">
                <small>Alert generated at {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</small>
            </p>
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_email, msg)
            
            logger.info(f"Sent email alert for {alert.product.product_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False
    
    def _send_email(self, msg: MIMEMultipart):
        """Send email (blocking operation)."""
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.send_message(msg)


class InventoryMonitor:
    """
    Monitor inventory levels and trigger alerts.
    Supports multiple suppliers and notification channels.
    """
    
    def __init__(
        self,
        check_interval_seconds: int = 300,  # 5 minutes
        enable_slack: bool = False,
        enable_email: bool = False
    ):
        """Initialize inventory monitor."""
        self.check_interval = check_interval_seconds
        self.products: Dict[str, Product] = {}
        self.alerts: List[Alert] = []
        self.notifiers: List[NotificationChannel] = []
        self.alerted_products: Set[str] = set()  # Track which products have active alerts
        self.running = False
        
        self.enable_slack = enable_slack
        self.enable_email = enable_email
    
    def add_notifier(self, notifier: NotificationChannel):
        """Add a notification channel."""
        self.notifiers.append(notifier)
        logger.info(f"Added notifier: {type(notifier).__name__}")
    
    def add_product(self, product: Product):
        """Add a product to monitor."""
        self.products[product.product_id] = product
        logger.info(f"Added product to monitor: {product.product_id} - {product.name}")
    
    def update_stock(self, product_id: str, current: int, reserved: int = 0, incoming: int = 0):
        """Update stock levels for a product."""
        if product_id not in self.products:
            logger.warning(f"Product {product_id} not found in monitor")
            return
        
        product = self.products[product_id]
        product.current_stock = current
        product.reserved_stock = reserved
        product.incoming_stock = incoming
        product.last_updated = datetime.now()
        
        logger.debug(f"Updated stock for {product_id}: current={current}, reserved={reserved}, incoming={incoming}")
    
    async def check_inventory(self):
        """Check all products and generate alerts if needed."""
        for product_id, product in self.products.items():
            status = product.status
            
            # Generate alerts based on status
            if status == StockStatus.OUT_OF_STOCK:
                if product_id not in self.alerted_products:
                    await self._create_alert(
                        product,
                        AlertLevel.CRITICAL,
                        f"CRITICAL: {product.name} is OUT OF STOCK! Available: {product.available_stock}"
                    )
            
            elif status == StockStatus.CRITICAL_STOCK:
                if product_id not in self.alerted_products:
                    await self._create_alert(
                        product,
                        AlertLevel.CRITICAL,
                        f"CRITICAL: {product.name} has critically low stock. Available: {product.available_stock} (threshold: {product.critical_threshold})"
                    )
            
            elif status == StockStatus.LOW_STOCK:
                if product_id not in self.alerted_products:
                    await self._create_alert(
                        product,
                        AlertLevel.WARNING,
                        f"WARNING: {product.name} is running low. Available: {product.available_stock} (threshold: {product.low_threshold})"
                    )
            
            elif status == StockStatus.IN_STOCK:
                # Clear alert if stock is back to normal
                if product_id in self.alerted_products:
                    self.alerted_products.remove(product_id)
                    logger.info(f"Stock restored for {product_id}, clearing alert")
    
    async def _create_alert(self, product: Product, level: AlertLevel, message: str):
        """Create and send an alert."""
        alert = Alert(
            alert_id=f"{product.product_id}-{datetime.now().timestamp()}",
            product=product,
            level=level,
            message=message
        )
        
        self.alerts.append(alert)
        self.alerted_products.add(product.product_id)
        
        logger.warning(f"Alert generated: {message}")
        
        # Send notifications
        for notifier in self.notifiers:
            try:
                await notifier.send(alert)
            except Exception as e:
                logger.error(f"Failed to send notification via {type(notifier).__name__}: {e}")
    
    async def run(self):
        """Run the monitoring loop."""
        self.running = True
        logger.info("Inventory monitor started")
        
        while self.running:
            try:
                await self.check_inventory()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
        logger.info("Inventory monitor stopped")
    
    def get_summary(self) -> Dict:
        """Get a summary of current inventory status."""
        summary = {
            "total_products": len(self.products),
            "out_of_stock": 0,
            "critical_stock": 0,
            "low_stock": 0,
            "in_stock": 0,
            "active_alerts": len(self.alerted_products),
            "total_alerts": len(self.alerts),
            "products": []
        }
        
        for product in self.products.values():
            status = product.status
            
            if status == StockStatus.OUT_OF_STOCK:
                summary["out_of_stock"] += 1
            elif status == StockStatus.CRITICAL_STOCK:
                summary["critical_stock"] += 1
            elif status == StockStatus.LOW_STOCK:
                summary["low_stock"] += 1
            else:
                summary["in_stock"] += 1
            
            summary["products"].append({
                "product_id": product.product_id,
                "name": product.name,
                "available_stock": product.available_stock,
                "status": status.value
            })
        
        return summary


# Example usage
async def main():
    """Example usage of inventory monitor."""
    logging.basicConfig(level=logging.INFO)
    
    # Create monitor
    monitor = InventoryMonitor(check_interval_seconds=10)
    
    # Add notifiers (example - would use real credentials in production)
    # slack_notifier = SlackNotifier(webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
    # monitor.add_notifier(slack_notifier)
    
    # Add products
    products = [
        Product(
            product_id="PROD-001",
            name="Hemp Rope 6mm",
            sku="ROPE-6MM-HEMP",
            current_stock=100,
            reserved_stock=20,
            incoming_stock=50,
            low_threshold=50,
            critical_threshold=10,
            supplier_id="SUP001"
        ),
        Product(
            product_id="PROD-002",
            name="Jute Rope 8mm",
            sku="ROPE-8MM-JUTE",
            current_stock=5,  # Low stock!
            reserved_stock=2,
            incoming_stock=100,
            low_threshold=30,
            critical_threshold=10,
            supplier_id="SUP002"
        ),
    ]
    
    for product in products:
        monitor.add_product(product)
    
    # Check inventory once
    await monitor.check_inventory()
    
    # Print summary
    summary = monitor.get_summary()
    print("\n=== Inventory Summary ===")
    print(json.dumps(summary, indent=2))
    
    # For continuous monitoring, uncomment:
    # await monitor.run()


if __name__ == "__main__":
    asyncio.run(main())

"""Demonstrate the MonkAI order tracking automation toolkit."""

import asyncio
from datetime import datetime, timedelta
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.order_tracking import Order, OrderTrackingAI


async def demo_order_tracking() -> None:
    tracker = OrderTrackingAI()

    sample_orders = [
        Order(
            order_id="TM001",
            customer_name="John Doe",
            customer_email="john@example.com",
            product="Artisan Climbing Rope - Custom",
            quantity=1,
            order_date=datetime.utcnow() - timedelta(days=85),
            expected_ship_date=datetime.utcnow() - timedelta(days=80),
        ),
        Order(
            order_id="TM002",
            customer_name="Jane Smith",
            customer_email="jane@example.com",
            product="Standard Rope Set",
            quantity=2,
            order_date=datetime.utcnow() - timedelta(days=5),
            expected_ship_date=datetime.utcnow() + timedelta(days=2),
        ),
    ]

    for order in sample_orders:
        assessment = await tracker.add_order(order)
        risk_level = assessment["risk_assessment"]["risk_level"]
        print(f"Added order {order.order_id}: {risk_level} risk")

    print("\nProcessing order TM002...")
    process_result = await tracker.process_order("TM002")
    print(process_result)

    print("\nChecking at-risk orders...")
    at_risk = await tracker.get_at_risk_orders()
    for record in at_risk:
        print(f" - {record['order_id']} ({record['risk_level']})")

    print("\nFulfillment analytics snapshot:")
    analytics = await tracker.analyze_fulfillment_metrics()
    if "error" in analytics:
        print(analytics["error"])
    else:
        print(f"Total orders: {analytics['total_orders']}")
        print(
            "On-time delivery rate:",
            f"{analytics['delivery_performance']['on_time_delivery_rate']:.1%}",
        )
        print("Recommendations:")
        for item in analytics["recommendations"]:
            print(f"   - {item}")


if __name__ == "__main__":
    asyncio.run(demo_order_tracking())

"""AI-assisted order tracking and fulfillment automation for MonkAI.

This module mirrors a production fulfillment control tower while remaining
self-contained and deterministic for local testing.  It offers:

* predictive risk scoring for late shipments
* simulated carrier label creation and tracking events
* proactive customer notification logging
* analytics surfaces to monitor 90-day fulfillment targets

Real deployments would connect to shipping APIs, Redis-backed queues, and ML
pipelines.  Here we lean on lightweight heuristics with optional integrations so
that the examples and FastAPI routes work even without external services.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence

try:  # Optional scientific stack – gracefully handled when unavailable.
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - fallback path for minimal envs
    pd = None  # type: ignore

try:  # Optional ML helpers.  The detector falls back to heuristics when absent.
    from sklearn.ensemble import IsolationForest, RandomForestClassifier  # type: ignore
    from sklearn.preprocessing import StandardScaler  # type: ignore
except Exception:  # pragma: no cover - fallback path for minimal envs
    IsolationForest = RandomForestClassifier = StandardScaler = None  # type: ignore

try:  # FastAPI is optional; routes degrade gracefully when missing.
    from fastapi import APIRouter, HTTPException
except Exception:  # pragma: no cover - fallback path for minimal envs
    APIRouter = None  # type: ignore

    class HTTPException(Exception):
        """Fallback HTTP exception used when FastAPI is unavailable."""

        def __init__(self, status_code: int, detail: str):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail


DEFAULT_FEATURES = [
    "day_of_week",
    "month",
    "is_weekend",
    "is_special_item",
    "previous_orders_count",
    "avg_previous_delivery_days",
]


class OrderStatus(str, Enum):
    """Finite states for the order lifecycle."""

    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    AT_RISK = "at_risk"
    LOST = "lost"


class ShippingCarrier(str, Enum):
    """Supported carrier abstractions."""

    USPS = "usps"
    UPS = "ups"
    FEDEX = "fedex"
    DHL = "dhl"


@dataclass
class Order:
    """Representation of a customer order tracked by the system."""

    order_id: str
    customer_name: str
    customer_email: str
    product: str
    quantity: int
    order_date: datetime
    expected_ship_date: datetime
    actual_ship_date: Optional[datetime] = None
    tracking_number: Optional[str] = None
    carrier: Optional[ShippingCarrier] = None
    status: OrderStatus = OrderStatus.PENDING
    delivery_date: Optional[datetime] = None
    notes: List[str] = field(default_factory=list)


@dataclass
class ShippingLabel:
    """Metadata describing a generated shipping label."""

    order_id: str
    tracking_number: str
    carrier: ShippingCarrier
    label_url: str
    cost: float
    created_at: datetime


class PredictiveDelayDetector:
    """Hybrid heuristic and ML-inspired delay detection.

    The detector can train on structured history when pandas/sklearn are
    available.  When those libraries are missing or training data is empty, it
    falls back to deterministic heuristics tailored for the TwistedMonk order
    mix (custom ropes, bundles, long-lead artisan work).
    """

    def __init__(self) -> None:
        self.delay_model = RandomForestClassifier(n_estimators=100, random_state=42) if RandomForestClassifier else None
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42) if IsolationForest else None
        self.scaler = StandardScaler() if StandardScaler else None
        self.is_trained = False
        self.feature_names = list(DEFAULT_FEATURES)
        self._baselines: Dict[str, float] = {
            "mean_expected_delivery": 7.0,
            "mean_delay": 1.5,
            "custom_item_penalty": 0.25,
        }

    def train_models(self, historical_orders: Iterable[Dict]) -> bool:
        """Train models or baseline heuristics from historical orders."""

        records = self._to_records(historical_orders)
        if not records:
            self.is_trained = True
            return True

        expected_days: List[float] = []
        actual_days: List[float] = []
        custom_penalties: List[float] = []
        for row in records:
            expected = float(row.get("expected_delivery_days", 7))
            actual = float(row.get("actual_delivery_days", expected))
            expected_days.append(expected)
            actual_days.append(actual)
            if isinstance(row.get("product_category"), str) and "custom" in row["product_category"].lower():
                custom_penalties.append(max(0.1, actual - expected))

        if expected_days:
            mean_expected = sum(expected_days) / len(expected_days)
        else:
            mean_expected = self._baselines["mean_expected_delivery"]

        if actual_days:
            mean_delay = max(0.0, (sum(actual_days) - sum(expected_days)) / len(actual_days))
        else:
            mean_delay = self._baselines["mean_delay"]

        custom_penalty = (
            sum(custom_penalties) / len(custom_penalties)
            if custom_penalties
            else self._baselines["custom_item_penalty"]
        )

        self._baselines = {
            "mean_expected_delivery": mean_expected,
            "mean_delay": mean_delay,
            "custom_item_penalty": custom_penalty,
        }

        if self.delay_model and self.anomaly_detector and self.scaler and pd is not None:
            try:
                df = pd.DataFrame(records)
                feature_df = self._extract_features(df)
                if feature_df.empty:
                    self.is_trained = True
                    return True

                scaled = self.scaler.fit_transform(feature_df)
                target = (
                    (df.get("actual_delivery_days", mean_expected) > df.get("expected_delivery_days", mean_expected))
                    .astype(int)
                )
                self.delay_model.fit(scaled, target)
                self.anomaly_detector.fit(scaled)
                self.feature_names = list(feature_df.columns)
            except Exception:
                # If scientific stack fails we still mark the heuristics as trained.
                self.feature_names = list(DEFAULT_FEATURES)
        self.is_trained = True
        return True

    def predict_order_risk(self, order: Order, order_history: Iterable[Dict]) -> Dict:
        """Return a structured risk assessment for a pending order."""

        assessment = self._heuristic_assessment(order)
        if not self.is_trained:
            return assessment

        features = self._create_order_features(order, order_history)
        delay_probability = assessment["delay_probability"]

        variance = features.get("avg_previous_delivery_days", self._baselines["mean_expected_delivery"]) - self._baselines[
            "mean_expected_delivery"
        ]
        if variance > 1:
            delay_probability = min(0.95, delay_probability + min(0.25, variance * 0.04))
        elif variance < -2:
            delay_probability = max(0.05, delay_probability - 0.1)

        delay_probability += features.get("is_special_item", 0) * self._baselines.get("custom_item_penalty", 0.2) * 0.1
        delay_probability += features.get("previous_orders_count", 0) == 0 and 0.05 or 0

        anomaly_score = max(-1.0, 1.0 - delay_probability * 1.5)
        risk_level = self._risk_bucket(delay_probability, anomaly_score)
        factors = self._identify_risk_factors(features, delay_probability)
        assessment.update(
            {
                "risk_level": risk_level,
                "delay_probability": float(round(delay_probability, 3)),
                "anomaly_score": float(round(anomaly_score, 3)),
                "factors": factors,
                "recommended_actions": self._suggest_actions(risk_level, factors),
            }
        )
        return assessment

    def _heuristic_assessment(self, order: Order) -> Dict:
        """Baseline deterministic heuristics used with or without ML training."""

        now = datetime.utcnow()
        delay_probability = 0.15
        factors: List[str] = []

        if order.expected_ship_date < now:
            overdue_days = (now - order.expected_ship_date).days
            delay_probability += min(0.35, 0.08 * max(1, overdue_days))
            factors.append("Expected ship date has passed")

        if "custom" in order.product.lower() or "hand-dyed" in order.product.lower():
            delay_probability += 0.22
            factors.append("Custom artisan build requires extended prep")

        if order.quantity > 3:
            delay_probability += 0.1
            factors.append("Bulk quantity may need batching")

        days_since_order = (now - order.order_date).days
        if days_since_order > 60:
            delay_probability += 0.2
            factors.append(f"Order is {days_since_order} days old")

        delay_probability = max(0.05, min(0.95, delay_probability))
        anomaly_score = max(-1.0, 1.0 - delay_probability)
        risk_level = self._risk_bucket(delay_probability, anomaly_score)

        return {
            "risk_level": risk_level,
            "delay_probability": float(round(delay_probability, 3)),
            "anomaly_score": float(round(anomaly_score, 3)),
            "factors": factors,
            "recommended_actions": self._suggest_actions(risk_level, factors),
        }

    def _risk_bucket(self, delay_probability: float, anomaly_score: float) -> str:
        if delay_probability >= 0.7 or anomaly_score < -0.1:
            return "high"
        if delay_probability >= 0.4:
            return "medium"
        return "low"

    def _extract_features(self, data):  # type: ignore[override]
        if pd is None or data is None:
            return pd.DataFrame(columns=DEFAULT_FEATURES) if pd is not None else []  # type: ignore
        df = data.copy()
        df["order_date"] = pd.to_datetime(df.get("order_date", datetime.utcnow()))
        feature_df = pd.DataFrame()
        feature_df["day_of_week"] = df["order_date"].dt.dayofweek
        feature_df["month"] = df["order_date"].dt.month
        feature_df["is_weekend"] = (df["order_date"].dt.dayofweek >= 5).astype(int)
        if "product_category" in df.columns:
            feature_df["is_special_item"] = df["product_category"].str.contains("custom|special", case=False, na=False).astype(int)
        else:
            feature_df["is_special_item"] = 0
        if "customer_email" in df.columns and "delivery_days" in df.columns:
            history = (
                df.groupby("customer_email")["delivery_days"].mean().reindex(df["customer_email"]).fillna(7)
            )
            feature_df["avg_previous_delivery_days"] = history
            counts = df.groupby("customer_email")["order_id" if "order_id" in df.columns else "customer_email"].transform("count")
            feature_df["previous_orders_count"] = counts
        else:
            feature_df["avg_previous_delivery_days"] = 7
            feature_df["previous_orders_count"] = 0
        return feature_df.fillna(0)

    def _create_order_features(self, order: Order, history: Iterable[Dict]) -> Dict[str, float]:
        features: Dict[str, float] = {name: 0 for name in DEFAULT_FEATURES}
        features["day_of_week"] = float(order.order_date.weekday())
        features["month"] = float(order.order_date.month)
        features["is_weekend"] = 1.0 if order.order_date.weekday() >= 5 else 0.0
        features["is_special_item"] = 1.0 if any(
            term in order.product.lower() for term in ("custom", "special", "handmade")
        ) else 0.0

        records = self._to_records(history)
        customer_orders = [row for row in records if row.get("customer_email") == order.customer_email]
        features["previous_orders_count"] = float(len(customer_orders))
        if customer_orders:
            delivery_values = [float(row.get("delivery_days", row.get("actual_delivery_days", 7))) for row in customer_orders]
            features["avg_previous_delivery_days"] = sum(delivery_values) / len(delivery_values)
        else:
            features["avg_previous_delivery_days"] = self._baselines.get("mean_expected_delivery", 7.0)
        return features

    def _identify_risk_factors(self, features: Dict[str, float], delay_prob: float) -> List[str]:
        factors: List[str] = []
        if features.get("is_special_item", 0) >= 1:
            factors.append("Custom/special rope category adds production time")
        if features.get("is_weekend", 0) >= 1:
            factors.append("Weekend order start may delay workshop kickoff")
        if features.get("previous_orders_count", 0) == 0:
            factors.append("No prior delivery history for customer")
        if delay_prob > 0.5:
            factors.append("Historical cohorts show elevated delay risk")
        return factors

    def _suggest_actions(self, risk_level: str, factors: Sequence[str]) -> List[str]:
        actions: List[str] = []
        if risk_level == "high":
            actions.extend(
                [
                    "Expedite crafting and packing queue",
                    "Assign to senior artisan",
                    "Send proactive delay communication",
                    "Daily monitoring until shipment",
                ]
            )
        elif risk_level == "medium":
            actions.extend(
                [
                    "Prioritize during next production cycle",
                    "Prep customer update template",
                    "Verify inventory of specialty components",
                ]
            )
        if not factors:
            actions.append("Continue standard fulfillment cadence")
        return actions

    def _to_records(self, data: Iterable[Dict]) -> List[Dict]:
        if data is None:
            return []
        if pd is not None and isinstance(data, pd.DataFrame):
            return list(data.fillna(0).to_dict("records"))
        if isinstance(data, list):
            return [dict(row) for row in data]
        if isinstance(data, dict):
            return [dict(data)]
        return []


class CarrierIntegration:
    """Lightweight facade that simulates carrier label creation and tracking."""

    LABEL_BASE_URL = "https://monkai.shipping/labels"

    def __init__(self) -> None:
        self._seed = 42

    async def create_shipping_label(self, order: Order, carrier: ShippingCarrier) -> ShippingLabel:
        tracking_number = self._generate_tracking_number(carrier)
        label_url = f"{self.LABEL_BASE_URL}/{tracking_number}.pdf"
        cost = round(self._calculate_shipping_cost(order, carrier), 2)
        return ShippingLabel(
            order_id=order.order_id,
            tracking_number=tracking_number,
            carrier=carrier,
            label_url=label_url,
            cost=cost,
            created_at=datetime.utcnow(),
        )

    async def track_package(self, tracking_number: str, carrier: ShippingCarrier) -> Dict:
        now = datetime.utcnow()
        updates = [
            {
                "timestamp": (now - timedelta(days=1, hours=3)).isoformat(),
                "location": "MonkAI Workshop",
                "status": "departed",
                "description": "Package left origin facility",
            },
            {
                "timestamp": (now - timedelta(hours=6)).isoformat(),
                "location": "Regional Hub",
                "status": "in_transit",
                "description": "In transit to destination region",
            },
        ]
        delivery_eta = now + timedelta(days=2)
        return {
            "tracking_number": tracking_number,
            "carrier": carrier.value,
            "status": "in_transit",
            "estimated_delivery": delivery_eta.isoformat(),
            "updates": updates,
            "last_updated": now.isoformat(),
        }

    def _generate_tracking_number(self, carrier: ShippingCarrier) -> str:
        prefixes = {
            ShippingCarrier.USPS: "94",
            ShippingCarrier.UPS: "1Z",
            ShippingCarrier.FEDEX: "6129",
            ShippingCarrier.DHL: "856",
        }
        self._seed = (self._seed * 48271) % 0x7FFFFFFF
        suffix = f"{self._seed:012d}"[-12:]
        return f"{prefixes.get(carrier, 'XX')}{suffix}"

    def _calculate_shipping_cost(self, order: Order, carrier: ShippingCarrier) -> float:
        base = {
            ShippingCarrier.USPS: 6.25,
            ShippingCarrier.UPS: 9.85,
            ShippingCarrier.FEDEX: 12.95,
            ShippingCarrier.DHL: 15.50,
        }.get(carrier, 10.0)
        multiplier = 1.0 + max(0, order.quantity - 1) * 0.3
        if "heavy" in order.product.lower():
            multiplier += 0.4
        if "custom" in order.product.lower():
            multiplier += 0.25
        return base * multiplier


class NotificationEngine:
    """Logs customer-facing notifications for auditability."""

    def __init__(self) -> None:
        self.sent_notifications: List[Dict[str, str]] = []

    async def send_order_notification(self, order: Order, notification_type: str, payload: Optional[Dict] = None) -> bool:
        subject, body = self._build_email(order, notification_type, payload or {})
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "order_id": order.order_id,
            "customer_email": order.customer_email,
            "subject": subject,
            "body": body,
        }
        print(f"[notification] {subject} -> {order.customer_email}")
        self.sent_notifications.append(log_entry)
        return True

    def _build_email(self, order: Order, notification_type: str, data: Dict) -> Sequence[str]:
        subject_prefix = "TwistedMonk Order Update"
        if notification_type == "delay_warning":
            subject = f"{subject_prefix}: Potential Delay for #{order.order_id}"
            body = (
                f"Hello {order.customer_name},\n\n"
                "We're expediting your order after identifying a possible delay. "
                f"Updated ship window: {data.get('new_ship_date', 'within 3 business days')}\n\n"
                "— TwistedMonk Fulfillment"
            )
        elif notification_type == "shipped":
            subject = f"{subject_prefix}: Shipment Confirmation #{order.order_id}"
            body = (
                f"Hi {order.customer_name},\n\n"
                f"Your {order.product} is en route! Tracking: {order.tracking_number}\n"
                f"Track here: {data.get('tracking_url', '#')}\n\n"
                "— TwistedMonk"
            )
        elif notification_type == "at_risk":
            subject = f"{subject_prefix}: Action Needed for #{order.order_id}"
            body = (
                f"Hi {order.customer_name},\n\n"
                f"We spotted an issue: {data.get('issue', 'delivery risk detected')}. "
                f"Next step: {data.get('action', 'please confirm your address')}\n\n"
                "— TwistedMonk Support"
            )
        else:
            subject = f"{subject_prefix}: Update on #{order.order_id}"
            body = (
                f"Hello {order.customer_name},\n\n"
                f"Status update: {data.get('message', order.status.value)}\n\n"
                "— TwistedMonk"
            )
        return subject, body


class OrderTrackingAI:
    """Coordinator that manages orders, risk scoring, and notifications."""

    monitor_interval_hours = 6
    risk_interval_hours = 24

    def __init__(self) -> None:
        self.orders: Dict[str, Order] = {}
        self.delay_detector = PredictiveDelayDetector()
        self.carrier_integration = CarrierIntegration()
        self.notification_engine = NotificationEngine()
        self._historical_orders: List[Dict] = self._seed_history()
        self.delay_detector.train_models(self._historical_orders)
        self._background_started = False
        self._background_tasks: List[asyncio.Task] = []

    async def add_order(self, order: Order) -> Dict:
        self.orders[order.order_id] = order
        history = await self._get_historical_data()
        assessment = self.delay_detector.predict_order_risk(order, history)
        order.notes.append(f"Initial risk: {assessment['risk_level']}")

        if assessment["risk_level"] == "high":
            await self._handle_high_risk_order(order, assessment)

        await self._ensure_background_tasks()
        return {
            "order_id": order.order_id,
            "status": order.status.value,
            "risk_assessment": assessment,
            "next_steps": assessment.get("recommended_actions", []),
        }

    async def process_order(self, order_id: str) -> Dict:
        order = self.orders.get(order_id)
        if not order:
            return {"error": f"Order {order_id} not found"}

        carrier = await self._select_best_carrier(order)
        try:
            label = await self.carrier_integration.create_shipping_label(order, carrier)
        except Exception as exc:  # pragma: no cover - defensive branch
            order.status = OrderStatus.DELAYED
            order.notes.append(f"Shipping label failed: {exc}")
            return {"order_id": order_id, "status": OrderStatus.DELAYED.value, "error": str(exc)}

        order.tracking_number = label.tracking_number
        order.carrier = carrier
        order.actual_ship_date = datetime.utcnow()
        order.status = OrderStatus.SHIPPED
        await self.notification_engine.send_order_notification(order, "shipped", {"tracking_url": label.label_url})
        return {
            "order_id": order_id,
            "status": order.status.value,
            "tracking_number": label.tracking_number,
            "carrier": carrier.value,
            "label_url": label.label_url,
            "shipping_cost": label.cost,
        }

    async def update_tracking(self, order_id: str) -> Dict:
        order = self.orders.get(order_id)
        if not order:
            return {"error": f"Order {order_id} not found"}
        if not order.tracking_number or not order.carrier:
            return {"error": "Tracking unavailable"}

        tracking = await self.carrier_integration.track_package(order.tracking_number, order.carrier)
        if tracking.get("status") == "delivered" and order.delivery_date is None:
            order.delivery_date = datetime.utcnow()
            order.status = OrderStatus.DELIVERED
            self._record_delivery(order)
        elif tracking.get("status") == "in_transit" and order.status == OrderStatus.SHIPPED:
            # optimistic delivery after ETA passes to keep analytics flowing
            eta = datetime.fromisoformat(tracking["estimated_delivery"])
            if datetime.utcnow() > eta and order.delivery_date is None:
                order.delivery_date = datetime.utcnow()
                order.status = OrderStatus.DELIVERED
                self._record_delivery(order)
        return {
            "order_id": order_id,
            "tracking_info": tracking,
            "order_status": order.status.value,
            "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
        }

    async def get_at_risk_orders(self, days_threshold: int = 80) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(days=days_threshold)
        at_risk: List[Dict] = []
        for order in self.orders.values():
            if order.order_date < cutoff and order.status not in (OrderStatus.DELIVERED, OrderStatus.LOST):
                days_pending = (datetime.utcnow() - order.order_date).days
                risk_level = self._calculate_90_day_risk(order, days_pending)
                at_risk.append(
                    {
                        "order_id": order.order_id,
                        "customer_name": order.customer_name,
                        "product": order.product,
                        "order_date": order.order_date.isoformat(),
                        "days_pending": days_pending,
                        "current_status": order.status.value,
                        "risk_level": risk_level,
                        "actions_needed": self._get_90_day_actions(order, risk_level),
                    }
                )
        return at_risk

    async def analyze_fulfillment_metrics(self) -> Dict:
        total_orders = len(self.orders)
        if total_orders == 0:
            return {"error": "No orders available"}

        delivered = [order for order in self.orders.values() if order.status == OrderStatus.DELIVERED and order.delivery_date]
        delivery_times: List[int] = []
        for order in delivered:
            if order.actual_ship_date and order.delivery_date:
                delivery_times.append((order.delivery_date - order.actual_ship_date).days or 0)
        avg_delivery = (sum(delivery_times) / len(delivery_times)) if delivery_times else 0.0

        status_breakdown = {status.value: 0 for status in OrderStatus}
        for order in self.orders.values():
            status_breakdown[order.status.value] = status_breakdown.get(order.status.value, 0) + 1

        problematic = await self.get_at_risk_orders(days_threshold=60)
        return {
            "total_orders": total_orders,
            "delivery_performance": {
                "average_delivery_days": round(avg_delivery, 2),
                "on_time_delivery_rate": round(len(delivered) / total_orders, 3),
                "delivered_orders": len(delivered),
            },
            "order_status_breakdown": status_breakdown,
            "problematic_orders": {
                "count": len(problematic),
                "orders": problematic[:10],
            },
            "recommendations": self._generate_fulfillment_recommendations(status_breakdown, problematic),
        }

    async def list_orders(self, status: Optional[str] = None) -> Dict:
        if status:
            filtered = [order for order in self.orders.values() if order.status.value == status]
        else:
            filtered = list(self.orders.values())
        return {
            "orders": [
                {
                    "order_id": order.order_id,
                    "customer_name": order.customer_name,
                    "product": order.product,
                    "status": order.status.value,
                    "order_date": order.order_date.isoformat(),
                    "tracking_number": order.tracking_number,
                    "carrier": order.carrier.value if order.carrier else None,
                }
                for order in filtered
            ],
            "total_count": len(filtered),
        }

    async def _monitor_orders(self) -> None:
        for order in list(self.orders.values()):
            if order.status in (OrderStatus.DELIVERED, OrderStatus.LOST):
                continue
            if order.expected_ship_date < datetime.utcnow() and order.status not in (OrderStatus.SHIPPED, OrderStatus.DELIVERED):
                order.status = OrderStatus.DELAYED
                await self.notification_engine.send_order_notification(
                    order,
                    "delay_warning",
                    {"new_ship_date": (datetime.utcnow() + timedelta(days=3)).date().isoformat()},
                )
            if order.tracking_number and order.carrier:
                await self.update_tracking(order.order_id)

    async def _check_90_day_orders(self) -> None:
        at_risk = await self.get_at_risk_orders(days_threshold=80)
        for record in at_risk:
            if record["risk_level"] in {"high", "critical"}:
                order = self.orders[record["order_id"]]
                order.status = OrderStatus.AT_RISK
                await self.notification_engine.send_order_notification(
                    order,
                    "at_risk",
                    {
                        "issue": f"Order pending for {record['days_pending']} days",
                        "action": "Immediate workshop escalation",
                    },
                )

    async def _periodic_monitor(self) -> None:
        try:
            while True:
                await self._monitor_orders()
                await asyncio.sleep(self.monitor_interval_hours * 3600)
        except asyncio.CancelledError:  # pragma: no cover - cancellation during shutdown
            return

    async def _periodic_90_day_check(self) -> None:
        try:
            while True:
                await self._check_90_day_orders()
                await asyncio.sleep(self.risk_interval_hours * 3600)
        except asyncio.CancelledError:  # pragma: no cover
            return

    async def _ensure_background_tasks(self) -> None:
        if self._background_started:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        self._background_tasks.append(loop.create_task(self._periodic_monitor()))
        self._background_tasks.append(loop.create_task(self._periodic_90_day_check()))
        self._background_started = True

    async def _select_best_carrier(self, order: Order) -> ShippingCarrier:
        if "fragile" in order.product.lower():
            return ShippingCarrier.FEDEX
        if order.quantity >= 4:
            return ShippingCarrier.UPS
        return ShippingCarrier.USPS

    async def _handle_high_risk_order(self, order: Order, assessment: Dict) -> None:
        order.notes.append("High risk detected – expedited handling queued")
        await self.notification_engine.send_order_notification(
            order,
            "delay_warning",
            {
                "new_ship_date": (datetime.utcnow() + timedelta(days=2)).date().isoformat(),
                "message": "We've accelerated your order in the workshop",
            },
        )

    async def _get_historical_data(self) -> List[Dict]:
        return list(self._historical_orders)

    def _record_delivery(self, order: Order) -> None:
        self._historical_orders.append(
            {
                "order_id": order.order_id,
                "order_date": order.order_date.isoformat(),
                "product_category": "custom" if "custom" in order.product.lower() else "standard",
                "customer_region": "domestic",
                "customer_email": order.customer_email,
                "delivery_days": (order.delivery_date - order.order_date).days if order.delivery_date else 0,
                "actual_delivery_days": (order.delivery_date - order.order_date).days if order.delivery_date else 0,
                "expected_delivery_days": (order.expected_ship_date - order.order_date).days,
            }
        )
        self.delay_detector.train_models(self._historical_orders)

    def _calculate_90_day_risk(self, order: Order, days_pending: int) -> str:
        if days_pending >= 85:
            return "critical"
        if days_pending >= 80:
            return "high"
        if days_pending >= 70:
            return "medium"
        return "low"

    def _get_90_day_actions(self, order: Order, risk_level: str) -> List[str]:
        if risk_level in {"critical", "high"}:
            return [
                "Expedite crafting immediately",
                "Contact customer with escalation plan",
                "Prepare replacement shipment",
                "Escalate to leadership",
            ]
        if risk_level == "medium":
            return [
                "Prioritize in next production cycle",
                "Send detailed status update",
                "Monitor every 48 hours",
            ]
        return ["Continue monitoring"]

    def _generate_fulfillment_recommendations(self, status_counts: Dict[str, int], problematic: List[Dict]) -> List[str]:
        recommendations: List[str] = []
        delayed_ratio = status_counts.get(OrderStatus.DELAYED.value, 0) / max(1, sum(status_counts.values()))
        if delayed_ratio > 0.1:
            recommendations.append("Add overtime batch to clear delayed queue")
        if problematic:
            recommendations.append(f"Escalate {len(problematic)} orders approaching 90-day SLA")
        if status_counts.get(OrderStatus.PENDING.value, 0) > 20:
            recommendations.append("Review capacity planning for intake surge")
        if not recommendations:
            recommendations.append("Fulfillment operating within expected thresholds")
        return recommendations

    def _seed_history(self) -> List[Dict]:
        baseline_date = datetime.utcnow() - timedelta(days=30)
        samples: List[Dict] = []
        for idx in range(1, 6):
            order_date = baseline_date - timedelta(days=idx * 3)
            samples.append(
                {
                    "order_id": f"HIST-{idx}",
                    "order_date": order_date.isoformat(),
                    "product_category": "custom" if idx % 2 == 0 else "standard",
                    "customer_region": "domestic" if idx % 3 else "remote",
                    "customer_email": f"customer{idx}@example.com",
                    "delivery_days": 9 + idx,
                    "actual_delivery_days": 9 + idx,
                    "expected_delivery_days": 7 + idx // 2,
                }
            )
        return samples


# FastAPI router -------------------------------------------------------------

order_tracker = OrderTrackingAI()

if APIRouter is not None:
    order_router = APIRouter(prefix="/api/orders", tags=["Order Tracking"])

    @order_router.post("/add")
    async def add_order(order_data: Dict):
        try:
            order = Order(
                order_id=order_data["order_id"],
                customer_name=order_data["customer_name"],
                customer_email=order_data["customer_email"],
                product=order_data["product"],
                quantity=int(order_data.get("quantity", 1)),
                order_date=datetime.fromisoformat(order_data["order_date"]),
                expected_ship_date=datetime.fromisoformat(order_data["expected_ship_date"]),
            )
        except KeyError as exc:
            raise HTTPException(status_code=400, detail=f"Missing field: {exc.args[0]}") from exc
        except Exception as exc:  # pragma: no cover - defensive branch
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return await order_tracker.add_order(order)

    @order_router.post("/{order_id}/process")
    async def process_order(order_id: str):
        result = await order_tracker.process_order(order_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result

    @order_router.get("/{order_id}/track")
    async def track_order(order_id: str):
        result = await order_tracker.update_tracking(order_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result

    @order_router.get("/at-risk")
    async def list_at_risk(days: int = 80):
        return await order_tracker.get_at_risk_orders(days)

    @order_router.get("/analytics/fulfillment")
    async def fulfillment_analytics():
        return await order_tracker.analyze_fulfillment_metrics()

    @order_router.get("/")
    async def list_orders(status: Optional[str] = None):
        return await order_tracker.list_orders(status)
else:  # pragma: no cover - fallback when FastAPI missing
    order_router = None


__all__ = [
    "Order",
    "OrderStatus",
    "ShippingCarrier",
    "OrderTrackingAI",
    "order_tracker",
    "order_router",
]

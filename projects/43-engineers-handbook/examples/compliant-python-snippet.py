"""
Example: Compliant Python Service — Order Processing Module

This snippet demonstrates all code standards from the Engineer's Handbook:
  ✅ Python 3.11+ with full type hints
  ✅ Pydantic v2 for input validation
  ✅ Parameterised SQL (no injection risk)
  ✅ Secrets from environment (no hardcoding)
  ✅ Structured logging
  ✅ Custom exception types
  ✅ clear function signatures with docstrings on non-obvious logic
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator

# ── Structured logger ─────────────────────────────────────────────────────────
log = logging.getLogger(__name__)


# ── Domain types ──────────────────────────────────────────────────────────────

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentDeclinedError(Exception):
    """Raised when the payment processor rejects a charge."""

    def __init__(self, reason: str, decline_code: str) -> None:
        super().__init__(f"Payment declined ({decline_code}): {reason}")
        self.decline_code = decline_code


class InsufficientStockError(Exception):
    """Raised when requested quantity exceeds available inventory."""


# ── Request / Response models (Pydantic v2) ───────────────────────────────────

class OrderLineItem(BaseModel):
    product_id: int = Field(gt=0, description="Product catalogue ID")
    quantity: int = Field(gt=0, le=100, description="Must be between 1 and 100")
    unit_price: Decimal = Field(gt=Decimal("0"), decimal_places=2)

    @field_validator("unit_price")
    @classmethod
    def price_has_two_decimal_places(cls, v: Decimal) -> Decimal:
        # Enforce exactly 2 decimal places to prevent rounding errors in totals
        return v.quantize(Decimal("0.01"))


class CreateOrderRequest(BaseModel):
    customer_id: int = Field(gt=0)
    items: list[OrderLineItem] = Field(min_length=1, max_length=50)
    shipping_address_id: int = Field(gt=0)

    @property
    def total_amount(self) -> Decimal:
        return sum(item.unit_price * item.quantity for item in self.items)


@dataclass
class OrderResult:
    order_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ── Service layer ─────────────────────────────────────────────────────────────

class OrderService:
    """
    Handles order creation with inventory validation and payment processing.
    All database queries use parameterised statements to prevent SQL injection.
    """

    def __init__(self, db_conn, payment_client) -> None:
        self._db = db_conn
        self._payment = payment_client

    def create_order(self, request: CreateOrderRequest) -> OrderResult:
        """
        Create a confirmed order if stock is available and payment succeeds.

        Raises:
            InsufficientStockError: If any item exceeds available stock.
            PaymentDeclinedError: If the payment processor rejects the charge.
        """
        log.info("Creating order", extra={"customer_id": request.customer_id,
                                           "item_count": len(request.items)})

        self._validate_stock(request.items)

        order_id = self._insert_order(request)
        self._charge_customer(request.customer_id, request.total_amount, order_id)
        self._deduct_stock(request.items)

        log.info("Order created successfully", extra={"order_id": order_id,
                                                       "total": str(request.total_amount)})

        return OrderResult(
            order_id=order_id,
            status=OrderStatus.CONFIRMED,
            total_amount=request.total_amount,
        )

    def _validate_stock(self, items: list[OrderLineItem]) -> None:
        for item in items:
            # Parameterised query — NEVER use f-string interpolation here
            row = self._db.execute(
                "SELECT available_qty FROM inventory WHERE product_id = %s FOR UPDATE",
                (item.product_id,)
            ).fetchone()

            if row is None or row[0] < item.quantity:
                available = row[0] if row else 0
                raise InsufficientStockError(
                    f"Product {item.product_id}: requested {item.quantity}, available {available}"
                )

    def _insert_order(self, request: CreateOrderRequest) -> int:
        cursor = self._db.execute(
            """
            INSERT INTO orders (customer_id, shipping_address_id, total_amount, status)
            VALUES (%s, %s, %s, %s)
            RETURNING order_id
            """,
            (request.customer_id, request.shipping_address_id,
             str(request.total_amount), OrderStatus.PENDING.value)
        )
        return cursor.fetchone()[0]

    def _charge_customer(self, customer_id: int, amount: Decimal, order_id: int) -> None:
        result = self._payment.charge(
            customer_id=customer_id,
            amount_cents=int(amount * 100),
            idempotency_key=f"order-{order_id}",
        )
        if not result.success:
            log.warning("Payment declined",
                        extra={"customer_id": customer_id, "decline_code": result.decline_code})
            raise PaymentDeclinedError(result.message, result.decline_code)

    def _deduct_stock(self, items: list[OrderLineItem]) -> None:
        for item in items:
            self._db.execute(
                "UPDATE inventory SET available_qty = available_qty - %s WHERE product_id = %s",
                (item.quantity, item.product_id)
            )


# ── Configuration (from environment — never hardcoded) ────────────────────────

def get_db_url() -> str:
    """Read database URL from environment. Raises if not set."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is required")
    return url

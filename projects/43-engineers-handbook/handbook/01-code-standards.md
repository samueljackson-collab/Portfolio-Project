# Code Standards

**Version:** 2.1 | **Owner:** Platform Engineering | **Last Updated:** 2026-01-10

These standards define how we write code across all languages used in our systems. They are not suggestions — every PR must comply before merge. The goal is consistent, readable, maintainable code that any engineer on the team can understand and modify safely.

---

## Table of Contents

1. [Python Standards](#python-standards)
2. [TypeScript Standards](#typescript-standards)
3. [Bash Standards](#bash-standards)
4. [Go Standards](#go-standards)
5. [Language-Agnostic Rules](#language-agnostic-rules)

---

## Python Standards

Python is the primary language for data pipelines, backend services, and automation scripts. All Python code must target **Python 3.11+**.

### 1.1 Type Hints

Type hints are **required** on all function signatures, including private methods. Use `from __future__ import annotations` at the top of every file to enable PEP 604 union syntax (`X | Y` instead of `Optional[X]`).

```python
# GOOD — fully annotated, clear intent
from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal

@dataclass
class User:
    user_id: int
    email: str
    is_active: bool

@dataclass
class OrderResult:
    order_id: int
    status: str
    total: Decimal
    error: str | None = None

def process_order(order_id: int, user: User) -> OrderResult:
    ...
```

```python
# BAD — no types, impossible to understand without reading body
def process_order(order_id, user):
    ...
```

**Rules:**
- Return types are always annotated, including `-> None`
- Use `list[str]` not `List[str]` (Python 3.9+ built-in generics)
- Use `dict[str, int]` not `Dict[str, int]`
- Use `X | None` not `Optional[X]`
- Use `X | Y` not `Union[X, Y]`
- `Any` is banned except when interfacing with untyped third-party code — add a `# type: ignore[...]` comment with explanation

### 1.2 Docstrings — Google Style

All public classes, methods, and module-level functions must have Google-style docstrings. Private methods (`_method`) should have docstrings when the logic is non-trivial.

```python
def calculate_shipping_cost(
    weight_kg: float,
    destination_country: str,
    express: bool = False,
) -> Decimal:
    """Calculate the shipping cost for an order.

    Uses weight-based tiered pricing with a country surcharge applied
    to non-domestic shipments. Express surcharge doubles base cost.

    Args:
        weight_kg: Package weight in kilograms. Must be positive.
        destination_country: ISO 3166-1 alpha-2 country code (e.g. "US", "DE").
        express: If True, apply 2x express surcharge. Defaults to False.

    Returns:
        Shipping cost in USD as a Decimal, rounded to 2 decimal places.

    Raises:
        ValueError: If weight_kg is not positive.
        LookupError: If destination_country is not in the supported countries list.

    Example:
        >>> calculate_shipping_cost(2.5, "DE", express=True)
        Decimal('18.40')
    """
    if weight_kg <= 0:
        raise ValueError(f"weight_kg must be positive, got {weight_kg}")
    ...
```

**Do not** write docstrings that merely restate the function name:

```python
# BAD — adds no value
def get_user(user_id: int) -> User:
    """Get user by user ID."""
    ...

# GOOD — explains what matters
def get_user(user_id: int) -> User:
    """Fetch an active user record by primary key.

    Args:
        user_id: Database primary key of the user record.

    Returns:
        User dataclass populated from the database row.

    Raises:
        UserNotFoundError: If no active user with user_id exists.
    """
    ...
```

### 1.3 Naming Conventions

| Construct | Convention | Example |
|-----------|-----------|---------|
| Variables | `snake_case` | `order_total`, `user_email` |
| Functions | `snake_case` | `process_order()`, `get_user()` |
| Methods | `snake_case` | `self._validate_stock()` |
| Classes | `PascalCase` | `OrderProcessor`, `UserService` |
| Constants | `UPPER_CASE` | `MAX_RETRY_COUNT = 3` |
| Modules | `snake_case` | `order_processor.py` |
| Packages | `snake_case` | `payment_gateway/` |
| Type aliases | `PascalCase` | `UserId = int` |

```python
# GOOD
MAX_RETRY_COUNT: int = 3
DEFAULT_TIMEOUT_SECONDS: float = 30.0

class PaymentProcessor:
    BASE_FEE_PERCENT: Decimal = Decimal("0.029")

    def process_payment(self, amount: Decimal, currency: str) -> PaymentResult:
        retry_count = 0
        ...

# BAD — inconsistent, meaningless names, magic numbers
class payment_processor:
    def ProcessPayment(self, amt, cur):
        n = 0
        while n < 3:  # magic number
            ...
```

### 1.4 Error Handling

**Never** use bare `except:` or `except Exception:` without re-raising or specific logging. Always:
1. Catch the most specific exception type possible
2. Log with full context (what was happening, what inputs caused it)
3. Either handle and recover, or re-raise with context

```python
# GOOD — specific exception, logged with context, re-raised with context
import structlog
log = structlog.get_logger()

def fetch_product_price(product_id: str) -> Decimal:
    try:
        response = catalog_client.get_price(product_id)
        return Decimal(str(response["price"]))
    except catalog_client.ProductNotFoundError:
        log.warning("product_not_found", product_id=product_id)
        raise
    except (KeyError, ValueError) as exc:
        log.error(
            "invalid_price_response",
            product_id=product_id,
            error=str(exc),
        )
        raise ValueError(f"Malformed price response for product {product_id}") from exc
```

```python
# BAD — swallows errors, no context, bare except
def fetch_product_price(product_id):
    try:
        response = catalog_client.get_price(product_id)
        return response["price"]
    except:
        return 0  # silently returns wrong value
```

### 1.5 Async Standards

Use `asyncio` for **I/O-bound** operations: HTTP calls, database queries, file reads. Never use `asyncio` for CPU-bound work — use `concurrent.futures.ProcessPoolExecutor` instead.

```python
# GOOD — async for I/O, proper context manager usage
import asyncio
import httpx

async def fetch_inventory_levels(product_ids: list[str]) -> dict[str, int]:
    """Fetch inventory for multiple products concurrently."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [
            client.get(f"/inventory/{pid}")
            for pid in product_ids
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

    result: dict[str, int] = {}
    for pid, response in zip(product_ids, responses):
        if isinstance(response, Exception):
            log.warning("inventory_fetch_failed", product_id=pid, error=str(response))
            result[pid] = 0
        else:
            result[pid] = response.json()["quantity"]
    return result
```

```python
# BAD — blocking I/O in async context, blocks the event loop
async def fetch_inventory_levels(product_ids):
    import requests  # synchronous — blocks event loop!
    result = {}
    for pid in product_ids:
        r = requests.get(f"/inventory/{pid}")
        result[pid] = r.json()["quantity"]
    return result
```

### 1.6 Complete Compliant Class Example: OrderProcessor

The following 55-line class demonstrates every Python standard in this section simultaneously.

```python
#!/usr/bin/env python3
"""
Order Processing Service

Processes customer orders through inventory validation,
payment charging, and status management.
"""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, UTC
from decimal import Decimal
from enum import Enum
from typing import Protocol

log = structlog.get_logger()

# Constants — UPPER_CASE
MAX_ITEMS_PER_ORDER: int = 100
PAYMENT_TIMEOUT_SECONDS: float = 30.0


class OrderStatus(Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class InsufficientStockError(Exception):
    """Raised when requested quantity exceeds available stock."""


class PaymentDeclinedError(Exception):
    """Raised when the payment gateway declines the charge."""


@dataclass
class OrderItem:
    product_id: str
    quantity:   int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    order_id:   str
    user_id:    str
    items:      list[OrderItem] = field(default_factory=list)
    status:     OrderStatus    = OrderStatus.PENDING
    created_at: datetime       = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total(self) -> Decimal:
        return sum(item.subtotal for item in self.items)


class InventoryClient(Protocol):
    def get_stock(self, product_id: str) -> int: ...


class PaymentClient(Protocol):
    def charge(self, user_id: str, amount: Decimal, reference: str) -> None: ...


class OrderProcessor:
    """Processes customer orders through inventory check and payment.

    Validates stock availability for every line item, charges the customer,
    and transitions the order to CONFIRMED status. Any failure leaves the
    order in PENDING so callers can retry or cancel.

    Args:
        inventory_client: Client implementing InventoryClient protocol.
        payment_client:   Client implementing PaymentClient protocol.
    """

    def __init__(
        self,
        inventory_client: InventoryClient,
        payment_client:   PaymentClient,
    ) -> None:
        self._inventory = inventory_client
        self._payment   = payment_client

    def process_order(self, order: Order) -> Order:
        """Process an order through validation, payment, and confirmation.

        Args:
            order: The Order to process. Must have at least one item.

        Returns:
            The same Order object with status set to CONFIRMED.

        Raises:
            ValueError:             If the order contains no items or exceeds
                                    MAX_ITEMS_PER_ORDER.
            InsufficientStockError: If any item has insufficient stock.
            PaymentDeclinedError:   If the payment gateway rejects the charge.
        """
        if not order.items:
            raise ValueError(f"Order {order.order_id} has no items")

        if len(order.items) > MAX_ITEMS_PER_ORDER:
            raise ValueError(
                f"Order {order.order_id} has {len(order.items)} items; "
                f"maximum is {MAX_ITEMS_PER_ORDER}"
            )

        log.info(
            "order_processing_started",
            order_id=order.order_id,
            user_id=order.user_id,
            item_count=len(order.items),
            total=str(order.total),
        )

        self._validate_stock(order)
        self._charge_payment(order)

        order.status = OrderStatus.CONFIRMED
        log.info(
            "order_confirmed",
            order_id=order.order_id,
            total=str(order.total),
        )
        return order

    def _validate_stock(self, order: Order) -> None:
        """Check all items have sufficient stock.

        Args:
            order: Order whose items to validate.

        Raises:
            InsufficientStockError: On first item found with insufficient stock.
        """
        for item in order.items:
            available = self._inventory.get_stock(item.product_id)
            if available < item.quantity:
                raise InsufficientStockError(
                    f"Product {item.product_id}: "
                    f"requested {item.quantity}, available {available}"
                )

    def _charge_payment(self, order: Order) -> None:
        """Charge the customer for the order total.

        Args:
            order: Order to charge. Uses order_id as payment reference.

        Raises:
            PaymentDeclinedError: If the payment gateway rejects the charge.
        """
        try:
            self._payment.charge(
                order.user_id,
                order.total,
                order.order_id,
            )
        except PaymentDeclinedError:
            log.warning(
                "payment_declined",
                order_id=order.order_id,
                user_id=order.user_id,
                total=str(order.total),
            )
            raise
```

---

## TypeScript Standards

TypeScript is used for all frontend code and Node.js backend services. All TypeScript must compile with `strict: true`.

### 2.1 tsconfig Requirements

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "esModuleInterop": true,
    "skipLibCheck": false
  }
}
```

### 2.2 Interfaces over Type Aliases

Use `interface` for object shapes — they produce better error messages and support declaration merging.

```typescript
// GOOD — interface for object shapes
interface User {
  readonly userId: string;
  email: string;
  role: UserRole;
  createdAt: Date;
}

interface CreateUserRequest {
  email: string;
  role?: UserRole;
}

// Type aliases are fine for unions, primitives, and mapped types
type UserId = string;
type UserRole = "admin" | "editor" | "viewer";
type UserMap = Record<UserId, User>;
```

```typescript
// BAD — type alias where interface is clearer
type User = {
  userId: string;
  email: string;
};
```

### 2.3 unknown over any

```typescript
// GOOD — parse unknown API response safely
function parseApiResponse(raw: unknown): ApiResponse {
  if (
    typeof raw !== "object" ||
    raw === null ||
    !("status" in raw) ||
    typeof (raw as Record<string, unknown>).status !== "string"
  ) {
    throw new Error("Invalid API response shape");
  }
  return raw as ApiResponse;
}
```

```typescript
// BAD — any bypasses all type checking
function parseApiResponse(raw: any): ApiResponse {
  return raw; // no validation, runtime errors waiting to happen
}
```

### 2.4 Async/Await over Callbacks and .then()

```typescript
// GOOD
async function getUserWithOrders(userId: string): Promise<UserWithOrders> {
  const user = await userRepository.findById(userId);
  if (user === null) {
    throw new UserNotFoundError(userId);
  }
  const orders = await orderRepository.findByUserId(userId);
  return { ...user, orders };
}
```

```typescript
// BAD — callback pyramid
function getUserWithOrders(userId: string, callback: (err: Error | null, result?: UserWithOrders) => void): void {
  userRepository.findById(userId, (err, user) => {
    if (err) { callback(err); return; }
    orderRepository.findByUserId(userId, (err, orders) => {
      if (err) { callback(err); return; }
      callback(null, { ...user, orders });
    });
  });
}
```

### 2.5 Complete Example: UserService

```typescript
import { createHash } from "crypto";

type UserId = string;
type UserRole = "admin" | "editor" | "viewer";

interface User {
  readonly userId: UserId;
  email: string;
  role: UserRole;
  passwordHash: string;
  createdAt: Date;
  updatedAt: Date;
}

interface CreateUserRequest {
  email: string;
  password: string;
  role?: UserRole;
}

interface UpdateUserRequest {
  email?: string;
  role?: UserRole;
}

interface UserRepository {
  findById(id: UserId): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  create(user: Omit<User, "userId" | "createdAt" | "updatedAt">): Promise<User>;
  update(id: UserId, changes: Partial<User>): Promise<User>;
  delete(id: UserId): Promise<void>;
}

class UserNotFoundError extends Error {
  constructor(userId: UserId) {
    super(`User not found: ${userId}`);
    this.name = "UserNotFoundError";
  }
}

class EmailAlreadyTakenError extends Error {
  constructor(email: string) {
    super(`Email already in use: ${email}`);
    this.name = "EmailAlreadyTakenError";
  }
}

export class UserService {
  constructor(private readonly repo: UserRepository) {}

  async createUser(request: CreateUserRequest): Promise<User> {
    const existing = await this.repo.findByEmail(request.email);
    if (existing !== null) {
      throw new EmailAlreadyTakenError(request.email);
    }

    const passwordHash = this.hashPassword(request.password);

    return this.repo.create({
      email: request.email,
      role: request.role ?? "viewer",
      passwordHash,
    });
  }

  async getUserById(userId: UserId): Promise<User> {
    const user = await this.repo.findById(userId);
    if (user === null) {
      throw new UserNotFoundError(userId);
    }
    return user;
  }

  async updateUser(userId: UserId, changes: UpdateUserRequest): Promise<User> {
    // Verify user exists before updating
    await this.getUserById(userId);

    if (changes.email !== undefined) {
      const conflict = await this.repo.findByEmail(changes.email);
      if (conflict !== null && conflict.userId !== userId) {
        throw new EmailAlreadyTakenError(changes.email);
      }
    }

    return this.repo.update(userId, {
      ...changes,
      updatedAt: new Date(),
    });
  }

  async deleteUser(userId: UserId): Promise<void> {
    await this.getUserById(userId);
    await this.repo.delete(userId);
  }

  private hashPassword(password: string): string {
    return createHash("sha256").update(password).digest("hex");
  }
}
```

---

## Bash Standards

Bash is used for deployment scripts, CI helpers, and operational automation. All scripts must be POSIX-compatible except where bash-specific features are explicitly needed.

### 3.1 Script Header

Every script must start with:

```bash
#!/usr/bin/env bash
set -euo pipefail
```

- `set -e`: Exit immediately on error
- `set -u`: Treat unset variables as errors
- `set -o pipefail`: Fail if any command in a pipeline fails

### 3.2 Functions and Reusability

Extract logic into named functions. Scripts should have a `main()` function called at the bottom.

### 3.3 Logging with Timestamps

```bash
log() {
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [${1:-INFO}] ${*:2}" >&2
}
```

Usage: `log INFO "Deploying version ${VERSION}"` or `log ERROR "Migration failed"`

### 3.4 Argument Validation

```bash
# GOOD — validate early, fail with helpful message
if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <environment> <version>" >&2
    exit 1
fi
ENVIRONMENT="$1"
VERSION="$2"

# Validate environment is a known value
case "${ENVIRONMENT}" in
    dev|staging|prod) ;;
    *)
        log ERROR "Unknown environment: ${ENVIRONMENT}. Must be dev, staging, or prod."
        exit 1
        ;;
esac
```

### 3.5 Complete Deployment Script Example

```bash
#!/usr/bin/env bash
set -euo pipefail

# deploy.sh — Deploy application to ECS service
# Usage: ./deploy.sh <environment> <image_tag>
# Example: ./deploy.sh staging v1.42.0

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly AWS_REGION="${AWS_REGION:-us-east-1}"

log() {
    echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') [${1:-INFO}] ${*:2}" >&2
}

die() {
    log ERROR "$*"
    exit 1
}

validate_args() {
    if [[ $# -lt 2 ]]; then
        die "Usage: $0 <environment> <image_tag>"
    fi

    local env="$1"
    case "${env}" in
        dev|staging|prod) ;;
        *) die "Unknown environment '${env}'. Must be dev, staging, or prod." ;;
    esac
}

get_cluster_name() {
    local environment="$1"
    echo "myapp-${environment}-ecs-cluster"
}

get_service_name() {
    local environment="$1"
    echo "myapp-${environment}-api-service"
}

update_ecs_service() {
    local cluster="$1"
    local service="$2"
    local image_tag="$3"

    log INFO "Updating ECS service: cluster=${cluster} service=${service} tag=${image_tag}"

    aws ecs update-service \
        --cluster "${cluster}" \
        --service "${service}" \
        --force-new-deployment \
        --region "${AWS_REGION}" \
        --query "service.serviceArn" \
        --output text

    log INFO "Waiting for service stability..."
    aws ecs wait services-stable \
        --cluster "${cluster}" \
        --services "${service}" \
        --region "${AWS_REGION}"
}

wait_for_health() {
    local environment="$1"
    local max_attempts=20
    local attempt=0
    local endpoint="https://api-${environment}.example.com/health"

    log INFO "Polling health endpoint: ${endpoint}"
    until curl --silent --fail "${endpoint}" > /dev/null 2>&1; do
        attempt=$(( attempt + 1 ))
        if [[ "${attempt}" -ge "${max_attempts}" ]]; then
            die "Health check failed after ${max_attempts} attempts"
        fi
        log INFO "Health check attempt ${attempt}/${max_attempts} — sleeping 15s"
        sleep 15
    done
    log INFO "Health check passed"
}

main() {
    validate_args "$@"

    local environment="$1"
    local image_tag="$2"
    local cluster
    local service
    cluster="$(get_cluster_name "${environment}")"
    service="$(get_service_name "${environment}")"

    log INFO "Starting deployment: env=${environment} tag=${image_tag}"
    update_ecs_service "${cluster}" "${service}" "${image_tag}"
    wait_for_health "${environment}"
    log INFO "Deployment complete: env=${environment} tag=${image_tag}"
}

main "$@"
```

---

## Go Standards

Go is used for high-throughput microservices and CLI tools.

### 4.1 Error Wrapping

Always wrap errors with context using `fmt.Errorf` and `%w`. This preserves the error chain for `errors.Is()` and `errors.As()`.

```go
// GOOD — wrapped error with context
func processOrder(ctx context.Context, orderID string) (*Order, error) {
    order, err := db.GetOrder(ctx, orderID)
    if err != nil {
        return nil, fmt.Errorf("fetching order %s: %w", orderID, err)
    }

    if err := validateOrder(order); err != nil {
        return nil, fmt.Errorf("validating order %s: %w", orderID, err)
    }

    return order, nil
}
```

```go
// BAD — loses original error type, no context
func processOrder(ctx context.Context, orderID string) (*Order, error) {
    order, err := db.GetOrder(ctx, orderID)
    if err != nil {
        return nil, errors.New("failed to get order") // drops context + original error
    }
    return order, nil
}
```

### 4.2 Table-Driven Tests

```go
func TestCalculateShippingCost(t *testing.T) {
    tests := []struct {
        name        string
        weightKg    float64
        destCountry string
        express     bool
        wantCost    float64
        wantErr     bool
    }{
        {
            name:        "domestic standard under 1kg",
            weightKg:    0.5,
            destCountry: "US",
            express:     false,
            wantCost:    4.99,
        },
        {
            name:        "international express over 5kg",
            weightKg:    6.0,
            destCountry: "DE",
            express:     true,
            wantCost:    42.80,
        },
        {
            name:        "zero weight returns error",
            weightKg:    0,
            destCountry: "US",
            wantErr:     true,
        },
    }

    for _, tc := range tests {
        t.Run(tc.name, func(t *testing.T) {
            got, err := CalculateShippingCost(tc.weightKg, tc.destCountry, tc.express)
            if tc.wantErr {
                require.Error(t, err)
                return
            }
            require.NoError(t, err)
            assert.InDelta(t, tc.wantCost, got, 0.01)
        })
    }
}
```

### 4.3 Interface Design — Small and Focused

Interfaces should describe behavior, not data. Prefer one-method interfaces where possible.

```go
// GOOD — small, focused, testable
type OrderReader interface {
    GetOrder(ctx context.Context, orderID string) (*Order, error)
}

type OrderWriter interface {
    SaveOrder(ctx context.Context, order *Order) error
}

type OrderStore interface {
    OrderReader
    OrderWriter
}

// Handler only needs to read — inject minimal interface
type OrderHandler struct {
    store OrderReader
}
```

```go
// BAD — massive interface, hard to mock, breaks ISP
type Database interface {
    GetOrder(ctx context.Context, id string) (*Order, error)
    SaveOrder(ctx context.Context, o *Order) error
    GetUser(ctx context.Context, id string) (*User, error)
    SaveUser(ctx context.Context, u *User) error
    GetProduct(ctx context.Context, id string) (*Product, error)
    DeleteProduct(ctx context.Context, id string) error
    ListOrders(ctx context.Context, userID string) ([]*Order, error)
    // ... 20 more methods
}
```

### 4.4 Complete HTTP Handler Example

```go
package orders

import (
    "encoding/json"
    "errors"
    "fmt"
    "log/slog"
    "net/http"
)

// OrderNotFoundError is returned when an order ID does not exist.
type OrderNotFoundError struct {
    OrderID string
}

func (e *OrderNotFoundError) Error() string {
    return fmt.Sprintf("order not found: %s", e.OrderID)
}

// GetOrderHandler handles GET /orders/{id}
type GetOrderHandler struct {
    store  OrderReader
    logger *slog.Logger
}

func NewGetOrderHandler(store OrderReader, logger *slog.Logger) *GetOrderHandler {
    return &GetOrderHandler{store: store, logger: logger}
}

func (h *GetOrderHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    orderID := r.PathValue("id")
    if orderID == "" {
        http.Error(w, "order id is required", http.StatusBadRequest)
        return
    }

    order, err := h.store.GetOrder(r.Context(), orderID)
    if err != nil {
        var notFound *OrderNotFoundError
        if errors.As(err, &notFound) {
            http.Error(w, notFound.Error(), http.StatusNotFound)
            return
        }
        h.logger.ErrorContext(r.Context(), "failed to fetch order",
            slog.String("order_id", orderID),
            slog.Any("error", err),
        )
        http.Error(w, "internal server error", http.StatusInternalServerError)
        return
    }

    w.Header().Set("Content-Type", "application/json")
    if err := json.NewEncoder(w).Encode(order); err != nil {
        h.logger.ErrorContext(r.Context(), "failed to encode response",
            slog.String("order_id", orderID),
            slog.Any("error", err),
        )
    }
}
```

---

## Language-Agnostic Rules

These rules apply regardless of language.

### 5.1 Magic Numbers and Strings

All magic literals must be named constants.

```python
# BAD
if status_code == 429:
    time.sleep(60)

# GOOD
HTTP_TOO_MANY_REQUESTS: int = 429
RATE_LIMIT_BACKOFF_SECONDS: int = 60

if status_code == HTTP_TOO_MANY_REQUESTS:
    time.sleep(RATE_LIMIT_BACKOFF_SECONDS)
```

### 5.2 Function Length

Functions longer than 40 lines are a code smell. Extract sub-steps into well-named helper functions.

### 5.3 Commit Size

One logical change per commit. PRs touching more than 500 lines need a justification comment in the PR description.

### 5.4 No Debug Code in Main Branch

No `print()` / `console.log()` / `fmt.Println()` debug statements, no commented-out code blocks, no `TODO` or `FIXME` comments without a linked issue.

### 5.5 Self-Documenting Names

```python
# BAD
def proc(d, f=False):
    res = []
    for i in d:
        if i["s"] == 1 or f:
            res.append(i)
    return res

# GOOD
def filter_active_orders(orders: list[Order], include_all: bool = False) -> list[Order]:
    return [
        order for order in orders
        if order.status == OrderStatus.ACTIVE or include_all
    ]
```

---

*Standards maintained by Platform Engineering. Exceptions require a written justification in the PR and sign-off from a Staff Engineer.*

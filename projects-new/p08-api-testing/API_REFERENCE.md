# API Reference

Complete reference for all tested API endpoints.

## Base URL

```
http://localhost:8080
```

## Authentication

All endpoints (except `/auth/token`) require Bearer token authentication:

```bash
Authorization: Bearer <token>
Content-Type: application/json
```

## Endpoints

### Authentication

#### Get Token

Generate OAuth2 access token.

```http
POST /auth/token
Content-Type: application/json

{
  "client_id": "string",
  "client_secret": "string"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

**Test Coverage:**
- `test_api_authentication.py::TestAuthentication::test_get_auth_token_success`
- `test_api_authentication.py::TestAuthentication::test_invalid_client_id`

---

### Orders

#### List Orders

Get paginated list of orders.

```http
GET /orders?page=1&pageSize=5
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| pageSize | integer | No | Items per page (default: 10) |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "ORDER001",
      "customer_id": "CUST001",
      "status": "pending",
      "items": [
        {
          "product_id": "PROD001",
          "quantity": 2,
          "price": 29.99
        }
      ],
      "total": 59.98,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "pageSize": 5
}
```

**Test Coverage:**
- `test_api_orders.py::TestOrdersCRUD::test_list_orders_with_pagination`
- `test_api_orders.py::TestOrdersCRUD::test_list_orders_empty`

---

#### Create Order

Create a new order.

```http
POST /orders
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_id": "string",
  "items": [
    {
      "product_id": "string",
      "quantity": integer,
      "price": number
    }
  ],
  "shipping_address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip": "string"
  }
}
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| customer_id | string | Yes | Customer identifier |
| items | array | Yes | Array of order items |
| items[].product_id | string | Yes | Product identifier |
| items[].quantity | integer | Yes | Item quantity |
| items[].price | number | Yes | Item price |
| shipping_address | object | Yes | Delivery address |

**Response (201 Created):**
```json
{
  "id": "ORDER_ABC123",
  "customer_id": "CUST001",
  "status": "pending",
  "items": [
    {
      "product_id": "PROD001",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "total": 59.98,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response (400):**
```json
{
  "error": "Missing required field: customer_id"
}
```

**Test Coverage:**
- `test_api_orders.py::TestOrdersCRUD::test_create_order_success`
- `test_api_orders.py::TestOrdersCRUD::test_create_order_with_multiple_items`

---

#### Get Order

Retrieve a specific order by ID.

```http
GET /orders/{id}
Authorization: Bearer <token>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Order ID |

**Response (200 OK):**
```json
{
  "id": "ORDER001",
  "customer_id": "CUST001",
  "status": "pending",
  "items": [
    {
      "product_id": "PROD001",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "total": 59.98,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response (404):**
```json
{
  "error": "Order not found"
}
```

**Test Coverage:**
- `test_api_orders.py::TestOrdersCRUD::test_get_order_by_id`
- `test_api_orders.py::TestOrdersErrorHandling::test_get_nonexistent_order`

---

#### Update Order

Update an existing order.

```http
PUT /orders/{id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "string",
  "items": [
    {
      "product_id": "string",
      "quantity": integer,
      "price": number
    }
  ]
}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Order ID |

**Request Body (at least one required):**
| Field | Type | Description |
|-------|------|-------------|
| status | string | Order status (pending, confirmed, shipped, etc.) |
| items | array | Updated order items |

**Response (200 OK):**
```json
{
  "id": "ORDER001",
  "customer_id": "CUST001",
  "status": "confirmed",
  "items": [
    {
      "product_id": "PROD001",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "total": 59.98,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Test Coverage:**
- `test_api_orders.py::TestOrdersCRUD::test_update_order_status`
- `test_api_orders.py::TestOrdersCRUD::test_update_order_items`

---

#### Delete Order

Delete an order.

```http
DELETE /orders/{id}
Authorization: Bearer <token>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Order ID |

**Response (204 No Content):**
```
(empty response body)
```

**Alternative Response (200 OK):**
```json
{
  "message": "Order deleted successfully"
}
```

**Error Response (404):**
```json
{
  "error": "Order not found"
}
```

**Test Coverage:**
- `test_api_orders.py::TestOrdersCRUD::test_delete_order`

---

### Products

#### List Products

Get list of products with optional filtering.

```http
GET /products?category=electronics&limit=10
Authorization: Bearer <token>
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| category | string | No | Product category filter |
| limit | integer | No | Max items to return |

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": "PROD001",
      "name": "Product Name",
      "category": "electronics",
      "price": 29.99,
      "description": "Product description"
    }
  ]
}
```

**Test Coverage:**
- `test_api_orders.py::TestProducts::test_list_products`

---

#### Get Product

Retrieve a specific product by ID.

```http
GET /products/{id}
Authorization: Bearer <token>
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Product ID |

**Response (200 OK):**
```json
{
  "id": "PROD001",
  "name": "Product Name",
  "category": "electronics",
  "price": 29.99,
  "description": "Product description"
}
```

**Test Coverage:**
- `test_api_orders.py::TestProducts::test_get_product_by_id`

---

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created |
| 204 | No Content | Request succeeded, no response body |
| 400 | Bad Request | Invalid request payload |
| 401 | Unauthorized | Missing or invalid auth token |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not allowed |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 502 | Bad Gateway | Gateway error |
| 503 | Service Unavailable | Service unavailable |

## Order Statuses

| Status | Description | Transition |
|--------|-------------|-----------|
| pending | Order created, awaiting confirmation | -> confirmed |
| confirmed | Order confirmed, ready for shipping | -> shipped |
| shipped | Order shipped to customer | -> delivered |
| delivered | Order delivered | (final) |
| cancelled | Order cancelled | (final) |

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Description of error for field"
  }
}
```

## Examples

### Example: Create and Retrieve Order

1. **Get Token:**
```bash
curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "demo",
    "client_secret": "secret"
  }'
```

Response:
```json
{
  "access_token": "token_value",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

2. **Create Order:**
```bash
curl -X POST http://localhost:8080/orders \
  -H "Authorization: Bearer token_value" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST001",
    "items": [
      {
        "product_id": "PROD001",
        "quantity": 2,
        "price": 29.99
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Springfield",
      "state": "IL",
      "zip": "62701"
    }
  }'
```

Response:
```json
{
  "id": "ORDER_ABC123",
  "customer_id": "CUST001",
  "status": "pending",
  "items": [
    {
      "product_id": "PROD001",
      "quantity": 2,
      "price": 29.99
    }
  ],
  "total": 59.98,
  "created_at": "2024-01-15T10:30:00Z"
}
```

3. **Retrieve Order:**
```bash
curl -X GET http://localhost:8080/orders/ORDER_ABC123 \
  -H "Authorization: Bearer token_value"
```

## Rate Limiting

Currently not implemented. Future versions may include rate limits.

## API Versioning

Current API version: v1
Future versions will be available at `/api/v2/`, etc.

## Pagination

Implemented using offset-based pagination:

```
GET /orders?page=1&pageSize=10
```

- `page`: 1-based page number
- `pageSize`: Items per page (max: 100)
- Default pageSize: 10

# 🛒 Cart Service

Shopping cart management service for the e-commerce platform.

## Overview

The Cart Service manages user shopping carts with real-time product validation, stock checking, and checkout preparation. It communicates with the Product Service to ensure data consistency and availability.

## Features

### Core Functionality
- ✅ **Cart Management**: Get, create, and manage user carts
- ✅ **Item Operations**: Add, update, remove cart items
- ✅ **Bulk Operations**: Add multiple items at once
- ✅ **Product Validation**: Real-time validation with Product Service
- ✅ **Stock Checking**: Ensures sufficient stock before adding items
- ✅ **Price Synchronization**: Keeps cart prices in sync with Product Service
- ✅ **Checkout Preparation**: Validates all items before checkout

### Security & Performance
- ✅ **JWT Authentication**: Validates tokens from Auth Service
- ✅ **Rate Limiting**: Prevents abuse
- ✅ **Input Validation**: Pydantic schemas
- ✅ **Async HTTP**: Non-blocking Product Service calls

## API Endpoints

### Cart Operations

#### Get Cart
```http
GET /cart
Authorization: Bearer {token}
```

Returns full cart with enriched product data (titles, images, stock status).

#### Get Cart Summary
```http
GET /cart/summary
Authorization: Bearer {token}
```

Returns lightweight summary (total items, subtotal).

### Item Operations

#### Add Item
```http
POST /cart/items
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": "uuid",
  "quantity": 2
}
```

Validates product and stock, adds to cart or increases quantity.

#### Bulk Add Items
```http
POST /cart/items/bulk
Authorization: Bearer {token}
Content-Type: application/json

{
  "items": [
    {"product_id": "uuid1", "quantity": 2},
    {"product_id": "uuid2", "quantity": 1}
  ]
}
```

Add up to 50 items at once. Returns success/failure counts.

#### Update Item Quantity
```http
PUT /cart/items/{product_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 5
}
```

Updates item quantity with stock validation.

#### Remove Item
```http
DELETE /cart/items/{product_id}
Authorization: Bearer {token}
```

Removes item from cart.

#### Clear Cart
```http
DELETE /cart
Authorization: Bearer {token}
```

Removes all items from cart.

### Checkout Operations

#### Prepare Checkout
```http
POST /cart/checkout/prepare
Authorization: Bearer {token}
Content-Type: application/json

{
  "shipping_address": "123 Main St, City, Country",
  "billing_address": "Optional, defaults to shipping",
  "notes": "Optional delivery instructions"
}
```

Validates all cart items for checkout:
- Checks product availability
- Verifies stock levels
- Returns list of unavailable items if any

#### Sync Prices
```http
POST /cart/sync-prices
Authorization: Bearer {token}
```

Updates all cart item prices to current Product Service prices.

## Database Schema

### Carts Table
```sql
CREATE TABLE carts (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Cart Items Table
```sql
CREATE TABLE cart_items (
    id UUID PRIMARY KEY,
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    quantity INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(cart_id, product_id)
);
```

**Note:** One product can only be in cart once (quantity tracks amount).

## Product Service Integration

The Cart Service makes HTTP requests to Product Service:

### Endpoints Called:
- `GET /products/{id}` - Get product details
- Validates: existence, active status, stock, price

### Batch Operations:
- Fetches multiple products concurrently
- Optimized for bulk cart operations

### Validation Logic:
```
1. Check product exists
2. Check product is active
3. Check sufficient stock
4. Get current price
5. Add/update cart item
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/cart_db

# Redis (for rate limiting)
REDIS_URL=redis://localhost:6379/3

# JWT (must match Auth Service)
JWT_SECRET_KEY=secret-key
JWT_ALGORITHM=HS256

# External Services
PRODUCT_SERVICE_URL=http://localhost:8002

# Application
APP_NAME=CartService
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## Running the Service

### With Docker Compose
```bash
docker-compose up -d cart-service
```

### Standalone
```bash
cd services/cart-service
cp .env.example .env
# Edit .env with your settings

pip install -r requirements.txt
uvicorn src.main:app --reload --port 8003
```

## Rate Limits

| Endpoint | Limit | Purpose |
|----------|-------|---------|
| Get cart | 100/min | Frequent UI updates |
| Add item | 50/min | Normal shopping |
| Bulk add | 10/min | Prevent abuse |
| Update item | 50/min | Normal adjustments |
| Checkout prepare | 10/min | Intensive validation |
| Sync prices | 10/min | Expensive operation |
| Clear cart | 20/min | Moderate usage |

## Error Handling

### Common Errors:

**400 Bad Request:**
- Product not found
- Product not active
- Insufficient stock
- Invalid quantity (must be 1-100)

**401 Unauthorized:**
- Missing or invalid JWT token

**404 Not Found:**
- Cart item not found
- Cart not found (when empty)

**429 Too Many Requests:**
- Rate limit exceeded

## Architecture

```
Cart Service
├── Domain Layer
│   └── Models (Cart, CartItem)
├── Application Layer
│   ├── Services (Business Logic)
│   └── DTOs (Pydantic Schemas)
├── Infrastructure Layer
│   ├── Database (Repository)
│   └── External (Product Service Client)
└── Presentation Layer
    ├── Routes (API Endpoints)
    └── Middlewares (Auth, Rate Limiting)
```

## Testing

### Example Flow:

```bash
# 1. Login to get token
TOKEN=$(curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"Pass123!"}' \
  | jq -r '.access_token')

# 2. Get empty cart
curl http://localhost:8003/cart \
  -H "Authorization: Bearer $TOKEN"

# 3. Add item to cart
curl -X POST http://localhost:8003/cart/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":"PRODUCT_UUID","quantity":2}'

# 4. Update quantity
curl -X PUT http://localhost:8003/cart/items/PRODUCT_UUID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'

# 5. Prepare checkout
curl -X POST http://localhost:8003/cart/checkout/prepare \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"shipping_address":"123 Main St, City"}'

# 6. Clear cart
curl -X DELETE http://localhost:8003/cart \
  -H "Authorization: Bearer $TOKEN"
```

## Dependencies

- **Auth Service**: JWT token validation
- **Product Service**: Product data, stock, pricing
- **PostgreSQL**: Cart data storage
- **Redis**: Rate limiting

## Port

Default: **8003**

## Health Check

```http
GET /health
```

Returns service status and Product Service URL.

## API Documentation

Interactive docs available at:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

---

**Built with Clean Architecture principles for the DEPI E-Commerce Platform** 🛒

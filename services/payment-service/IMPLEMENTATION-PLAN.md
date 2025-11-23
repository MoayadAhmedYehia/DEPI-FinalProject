# 💳 Payment Service - Implementation Plan

## 📋 **Service Overview**

**Purpose:** Handle payment processing, order creation, transaction management, and payment gateway integration for the e-commerce platform.

**Port:** 8005

**Key Features:**
- Payment processing (Stripe/PayPal integration)
- Order management
- Transaction history
- Refunds & cancellations
- Payment method management
- Webhook handling
- Invoice generation

---

## 📂 **Folder Structure**

```
services/payment-service/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                     # Configuration (API keys, webhooks)
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── order.py                   # Order model
│   │   │   ├── payment.py                 # Payment model
│   │   │   ├── transaction.py             # Transaction log
│   │   │   ├── refund.py                  # Refund model
│   │   │   └── payment_method.py          # Saved payment methods
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       └── payment_gateway.py         # Abstract payment provider
│   │
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── order_service.py           # Order business logic
│   │   │   ├── payment_service.py         # Payment processing
│   │   │   ├── transaction_service.py     # Transaction management
│   │   │   ├── refund_service.py          # Refund handling
│   │   │   └── invoice_service.py         # Invoice generation
│   │   └── dtos/
│   │       ├── __init__.py
│   │       ├── order_schemas.py           # Order DTOs
│   │       ├── payment_schemas.py         # Payment DTOs
│   │       ├── transaction_schemas.py     # Transaction DTOs
│   │       └── refund_schemas.py          # Refund DTOs
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py              # PostgreSQL connection
│   │   │   ├── order_repository.py        # Order CRUD
│   │   │   ├── payment_repository.py      # Payment CRUD
│   │   │   └── transaction_repository.py  # Transaction logs
│   │   ├── payment_gateways/
│   │   │   ├── __init__.py
│   │   │   ├── stripe_gateway.py          # Stripe integration
│   │   │   ├── paypal_gateway.py          # PayPal integration (optional)
│   │   │   └── mock_gateway.py            # Testing/development
│   │   ├── external/
│   │   │   ├── __init__.py
│   │   │   ├── cart_client.py             # Cart Service API client
│   │   │   ├── product_client.py          # Product Service client
│   │   │   └── user_client.py             # Auth Service client
│   │   └── notifications/
│   │       ├── __init__.py
│   │       ├── email_service.py           # Email notifications
│   │       └── webhook_service.py         # Webhook sender
│   │
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── order_routes.py            # Order endpoints
│   │   │   ├── payment_routes.py          # Payment endpoints
│   │   │   ├── webhook_routes.py          # Payment gateway webhooks
│   │   │   └── admin_routes.py            # Admin endpoints
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       ├── auth_middleware.py         # JWT validation
│   │       ├── rate_limit.py              # Rate limiting
│   │       └── webhook_verify.py          # Webhook signature verification
│   │
│   └── main.py                             # FastAPI application
│
├── templates/
│   ├── invoice.html                        # Invoice template
│   ├── order_confirmation.html             # Order confirmation email
│   └── refund_notification.html            # Refund notification
│
├── scripts/
│   ├── migrate_orders.py                   # Data migration
│   ├── reconcile_payments.py               # Payment reconciliation
│   └── generate_reports.py                 # Financial reports
│
├── tests/
│   ├── unit/
│   │   ├── test_order_service.py
│   │   ├── test_payment_service.py
│   │   └── test_refund_service.py
│   └── integration/
│       ├── test_payment_flow.py
│       └── test_webhook_handling.py
│
├── requirements.txt                        # Python dependencies
├── Dockerfile                              # Container definition
├── .env.example                            # Environment template
└── README.md                               # Documentation
```

---

## 🎯 **Core Features to Implement**

### **1. Order Management**
- Create orders from cart
- Order status tracking (pending, paid, processing, shipped, delivered, cancelled)
- Order history
- Order details & invoice
- Cancel orders
- Update shipping info

### **2. Payment Processing**
- Charge payments via Stripe
- Payment intent creation
- 3D Secure (SCA) support
- Payment confirmation
- Idempotency (prevent double charges)
- Currency support

### **3. Transaction Management**
- Transaction logging
- Payment status tracking
- Failed payment handling
- Retry logic
- Audit trail

### **4. Refunds**
- Full & partial refunds
- Refund to original payment method
- Refund status tracking
- Automatic stock restoration

### **5. Webhook Handling**
- Stripe webhook events
- Payment success/failure
- Dispute notifications
- Signature verification
- Event deduplication

### **6. Payment Methods**
- Save payment methods (tokenization)
- List saved methods
- Set default method
- Delete payment methods
- PCI compliance (no card storage)

---

## 🗄️ **Database Schema**

### **orders** (PostgreSQL)
```sql
CREATE TYPE order_status AS ENUM (
    'pending', 'payment_pending', 'paid', 'processing',
    'shipped', 'delivered', 'cancelled', 'refunded'
);

CREATE TABLE orders (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    order_number VARCHAR(20) UNIQUE NOT NULL,  -- ORD-2024-001234
    
    -- Amounts
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) DEFAULT 0,
    shipping_cost DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Status
    status order_status DEFAULT 'pending',
    
    -- Addresses
    shipping_address JSONB NOT NULL,
    billing_address JSONB,
    
    -- Items (denormalized for history)
    items JSONB NOT NULL,                      -- Cart items snapshot
    
    -- Metadata
    notes TEXT,
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_number ON orders(order_number);
```

### **payments** (PostgreSQL)
```sql
CREATE TYPE payment_status AS ENUM (
    'pending', 'processing', 'succeeded',
    'failed', 'cancelled', 'refunded'
);

CREATE TYPE payment_method_type AS ENUM (
    'card', 'paypal', 'bank_transfer', 'other'
);

CREATE TABLE payments (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    user_id UUID NOT NULL,
    
    -- Amounts
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Payment details
    payment_method_type payment_method_type,
    payment_method_id VARCHAR(255),            -- Stripe payment method ID
    
    -- Gateway info
    gateway VARCHAR(50) DEFAULT 'stripe',      -- 'stripe', 'paypal', 'mock'
    gateway_payment_id VARCHAR(255) UNIQUE,    -- Stripe payment intent ID
    gateway_response JSONB,                    -- Full gateway response
    
    -- Status
    status payment_status DEFAULT 'pending',
    failure_reason TEXT,
    
    -- Metadata
    metadata JSONB,
    idempotency_key VARCHAR(255) UNIQUE,       -- Prevent duplicates
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_gateway_id ON payments(gateway_payment_id);
```

### **transactions** (PostgreSQL - Audit Log)
```sql
CREATE TYPE transaction_type AS ENUM (
    'charge', 'refund', 'chargeback', 'fee'
);

CREATE TABLE transactions (
    id UUID PRIMARY KEY,
    order_id UUID REFERENCES orders(id),
    payment_id UUID REFERENCES payments(id),
    
    -- Transaction details
    type transaction_type,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Gateway
    gateway_transaction_id VARCHAR(255),
    gateway VARCHAR(50),
    
    -- Status
    status VARCHAR(50),
    description TEXT,
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_order ON transactions(order_id);
CREATE INDEX idx_transactions_payment ON transactions(payment_id);
```

### **refunds** (PostgreSQL)
```sql
CREATE TYPE refund_status AS ENUM (
    'pending', 'processing', 'succeeded', 'failed', 'cancelled'
);

CREATE TABLE refunds (
    id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES orders(id),
    payment_id UUID NOT NULL REFERENCES payments(id),
    user_id UUID NOT NULL,
    
    -- Refund details
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    reason TEXT,
    
    -- Gateway
    gateway VARCHAR(50),
    gateway_refund_id VARCHAR(255) UNIQUE,
    
    -- Status
    status refund_status DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);

CREATE INDEX idx_refunds_order ON refunds(order_id);
CREATE INDEX idx_refunds_payment ON refunds(payment_id);
```

### **saved_payment_methods** (PostgreSQL)
```sql
CREATE TABLE saved_payment_methods (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    
    -- Payment method (tokenized, NO raw card data)
    gateway VARCHAR(50) DEFAULT 'stripe',
    gateway_method_id VARCHAR(255) NOT NULL,   -- Stripe payment method ID
    
    -- Display info
    type VARCHAR(50),                          -- 'card', 'paypal'
    last4 VARCHAR(4),                          -- Last 4 digits
    brand VARCHAR(50),                         -- 'visa', 'mastercard'
    exp_month INTEGER,
    exp_year INTEGER,
    
    -- Defaults
    is_default BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_saved_methods_user ON saved_payment_methods(user_id);
```

---

## 🔧 **Technology Stack**

### **Core:**
- **FastAPI** - Web framework
- **PostgreSQL** - Main database
- **Redis** - Caching, idempotency keys
- **SQLAlchemy** - ORM

### **Payment Gateways:**
- **Stripe** - Primary payment processor
- **stripe-python** - Official Python SDK

### **Optional:**
- **PayPal SDK** - Alternative payment method
- **Celery** - Background jobs (invoice generation)
- **RabbitMQ** - Task queue

### **Utilities:**
- **Jinja2** - HTML templates (invoices, emails)
- **WeasyPrint** - PDF generation
- **cryptography** - Webhook signature verification

---

## 🚀 **Implementation Plan**

### **Phase 1: Foundation (Week 1)**
1. ✅ Set up service structure
2. ✅ Configure FastAPI application
3. ✅ Set up PostgreSQL database
4. ✅ Create domain models (Order, Payment, Transaction)
5. ✅ Implement repositories
6. ✅ Set up Stripe test account

### **Phase 2: Order Management (Week 2)**
1. ✅ Implement Order creation from Cart
2. ✅ Order status management
3. ✅ Order history endpoints
4. ✅ Order cancellation logic
5. ✅ Integration with Cart Service
6. ✅ Integration with Product Service (stock updates)

### **Phase 3: Payment Processing (Week 3)**
1. ✅ Stripe integration
2. ✅ Payment Intent creation
3. ✅ Payment confirmation
4. ✅ Handle payment failures
5. ✅ Idempotency implementation
6. ✅ 3D Secure support

### **Phase 4: Webhooks (Week 4)**
1. ✅ Webhook endpoint setup
2. ✅ Signature verification
3. ✅ Event handling (payment succeeded/failed)
4. ✅ Event deduplication
5. ✅ Retry logic
6. ✅ Webhook testing

### **Phase 5: Refunds & Payment Methods (Week 5)**
1. ✅ Refund creation
2. ✅ Partial & full refunds
3. ✅ Stock restoration
4. ✅ Save payment methods (tokenization)
5. ✅ List/delete methods
6. ✅ Default method management

### **Phase 6: Notifications & Admin (Week 6)**
1. ✅ Email notifications (order confirmation, refunds)
2. ✅ Invoice generation (PDF)
3. ✅ Admin endpoints (reports, statistics)
4. ✅ Transaction logs & audit trail
5. ✅ Testing & deployment
6. ✅ Documentation

---

## 📡 **API Endpoints**

### **Order Endpoints:**
```
POST   /api/orders                   # Create order from cart
GET    /api/orders                   # List user orders
GET    /api/orders/{id}              # Get order details
PATCH  /api/orders/{id}/status       # Update order status
DELETE /api/orders/{id}              # Cancel order (if not paid)
GET    /api/orders/{id}/invoice      # Download invoice PDF
```

### **Payment Endpoints:**
```
POST   /api/payments/intent          # Create payment intent
POST   /api/payments/confirm         # Confirm payment
GET    /api/payments/{id}            # Get payment details
GET    /api/payments?order_id={id}   # Get order payments
```

### **Refund Endpoints:**
```
POST   /api/refunds                  # Create refund
GET    /api/refunds/{id}             # Get refund details
GET    /api/refunds?order_id={id}    # Order refunds
```

### **Payment Methods:**
```
POST   /api/payment-methods          # Save payment method
GET    /api/payment-methods          # List saved methods
DELETE /api/payment-methods/{id}     # Delete method
PATCH  /api/payment-methods/{id}/default  # Set default
```

### **Webhooks (Public):**
```
POST   /webhooks/stripe              # Stripe webhook receiver
POST   /webhooks/paypal              # PayPal webhook (optional)
```

### **Admin Endpoints:**
```
GET    /api/admin/orders             # All orders (paginated)
GET    /api/admin/transactions       # Transaction log
GET    /api/admin/reports            # Financial reports
POST   /api/admin/refunds/{id}/approve  # Approve refund
```

---

## 🔗 **External Service Integration**

### **Cart Service Integration:**
```python
# Get cart for checkout
GET /api/cart

# Clear cart after order creation
DELETE /api/cart

# Prepare checkout (validate items, stock)
POST /api/cart/checkout/prepare
{
  "shipping_address": "...",
  "billing_address": "..."
}
```

### **Product Service Integration:**
```python
# Update stock after order
PATCH /api/products/{id}/stock
{
  "decrement": 2
}

# Restore stock after refund
PATCH /api/products/{id}/stock
{
  "increment": 2
}
```

### **Auth Service Integration:**
```python
# Get user details
GET /api/auth/users/{id}

# Validate JWT token
# (via middleware)
```

---

## 💳 **Stripe Integration Details**

### **Payment Flow:**
```python
1. Frontend: User initiates checkout
2. Backend: Create PaymentIntent
   - POST /api/payments/intent
   - Stripe creates payment intent
   - Return client_secret to frontend

3. Frontend: Use Stripe.js to confirm payment
   - Collect card details securely
   - stripe.confirmCardPayment(client_secret)

4. Stripe: Processes payment
   - Returns success/failure
   - Sends webhook to backend

5. Backend: Webhook handler
   - Verify signature
   - Update order status to "paid"
   - Send confirmation email
   - Update stock

6. Frontend: Show confirmation page
```

### **Stripe Webhooks to Handle:**
```python
payment_intent.succeeded       → Mark order as paid
payment_intent.payment_failed  → Mark payment as failed
charge.refunded                → Update refund status
charge.dispute.created         → Notify admin
payment_method.attached        → Save payment method
```

---

## ⚙️ **Configuration**

### **Environment Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/payment_db

# Redis
REDIS_URL=redis://localhost:6379/5

# JWT
JWT_SECRET_KEY=same-as-auth-service

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# External Services
CART_SERVICE_URL=http://localhost:8003
PRODUCT_SERVICE_URL=http://localhost:8002
AUTH_SERVICE_URL=http://localhost:8001

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
APP_NAME=PaymentService
DEFAULT_CURRENCY=USD
TAX_RATE=0.1               # 10% tax
SHIPPING_COST=5.99
```

---

## 🔒 **Security & Compliance**

### **PCI DSS Compliance:**
✅ **Never store raw card data**  
✅ Use Stripe tokenization  
✅ Use Stripe.js for card collection (client-side)  
✅ Only store Stripe payment method IDs  
✅ Webhook signature verification  
✅ HTTPS only in production  

### **Security Measures:**
- Idempotency keys (prevent double charges)
- Rate limiting on payment endpoints
- Webhook signature verification
- Transaction logging
- Fraud detection (Stripe Radar)
- 3D Secure (SCA) support

---

## 📊 **Order Flow Diagram**

```
User → Frontend → Payment Service
                      ↓
                  Cart Service (get cart)
                      ↓
                  Create Order (pending)
                      ↓
                  Stripe (create payment intent)
                      ↓
Frontend ← Return client_secret
    ↓
Stripe.js confirms payment
    ↓
Stripe processes
    ↓
Webhook → Payment Service
            ↓
        Update order (paid)
            ↓
        Update stock (Product Service)
            ↓
        Clear cart (Cart Service)
            ↓
        Send email
            ↓
Frontend ← Success response
```

---

## 🧪 **Testing Strategy**

### **Unit Tests:**
- Order creation logic
- Payment processing
- Refund calculations
- Webhook signature verification
- Stock update logic

### **Integration Tests:**
- Full checkout flow
- Stripe API integration
- Service-to-service calls
- Webhook handling
- Email sending

### **E2E Tests:**
- Complete purchase flow (cart → order → payment → confirmation)
- Refund flow
- Failed payment handling
- Concurrent payment prevention

### **Stripe Testing:**
- Use Stripe test mode
- Test cards: `4242 4242 4242 4242` (success)
- Test cards: `4000 0000 0000 0002` (declined)
- Test 3D Secure: `4000 0027 6000 3184`

---

## 📊 **Key Metrics**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Payment Success Rate | > 95% | Successful / Total payments |
| Order Processing Time | < 2s | Creation to confirmation |
| Webhook Processing | < 500ms | Handle and respond |
| Refund Processing | < 1 day | Initiate to complete |
| Failed Payment Rate | < 5% | Failed / Total attempts |
| Duplicate Prevention | 100% | Via idempotency keys |

---

## 🚨 **Error Handling**

### **Payment Failures:**
```python
# Insufficient funds
→ Notify user, suggest retry or alternate method

# Card declined
→ Show error, allow retry with different card

# 3D Secure required
→ Redirect to authentication, retry after verification

# Network timeout
→ Check payment status via Stripe API, don't double charge
```

### **Stock Issues:**
```python
# Product out of stock during checkout
→ Remove from order, notify user, offer alternatives

# Stock update fails after payment
→ Log error, queue retry, notify admin (critical!)
```

---

## 📚 **Dependencies**

```txt
# Core
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9

# Payment
stripe>=7.0.0

# Email & PDFs
jinja2>=3.1.2
weasyprint>=60.0           # PDF generation
python-multipart>=0.0.6

# HTTP clients
httpx>=0.25.0

# Utilities
redis>=5.0.0
python-dotenv>=1.0.0
python-jose[cryptography]>=3.3.0
```

---

## 🎯 **Success Criteria**

✅ **Functional:**
- Orders created from cart successfully
- Stripe payments processed
- Webhooks handled correctly
- Refunds processed
- Emails sent

✅ **Technical:**
- < 100ms payment intent creation
- < 500ms webhook processing
- 100% idempotency (no double charges)
- PCI compliant (no card storage)

✅ **Business:**
- > 95% payment success rate
- < 5% dispute rate
- Complete audit trail
- Ready for production traffic

---

## 📝 **Post-Implementation**

### **Monitoring:**
- Payment success/failure rates
- Webhook processing times
- Failed payment reasons
- Revenue tracking
- Chargeback monitoring

### **Optimizations:**
- Cache payment methods
- Batch stock updates
- Async email sending
- Payment retry logic

### **Enhancements:**
- Multi-currency support
- Subscription payments
- Split payments
- Gift cards
- Loyalty points

---

**This service handles the critical payment flow - security and reliability are paramount!** 💳🔒

---

**Estimated Development Time:** 6 weeks  
**Team Size:** 2 developers  
**Priority:** HIGH (core business functionality)

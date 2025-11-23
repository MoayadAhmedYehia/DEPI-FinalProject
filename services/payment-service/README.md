# Payment Service

Secure payment processing service supporting multiple payment gateways for the e-commerce platform.

## Features

- **Multiple Payment Gateways**: Stripe, PayPal support
- **Secure Transactions**: PCI-DSS compliant payment processing
- **Webhook Handling**: Real-time payment status updates
- **Refunds & Cancellations**: Full refund management
- **Payment History**: Transaction tracking and reporting
- **Email Receipts**: Automatic receipt generation
- **Async Processing**: Background job processing with Celery

## Tech Stack

- **Framework**: FastAPI
- **Payment Gateways**: Stripe, PayPal
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Email**: SMTP with Jinja2 templates
- **Authentication**: JWT validation

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Stripe Account
- SMTP Server (Gmail, SendGrid, etc.)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Update .env with your credentials

# Run database migrations
python -m src.infrastructure.database.migrate

# Start Celery worker (in separate terminal)
celery -A src.infrastructure.tasks.celery_app worker --loglevel=info

# Start the service
uvicorn src.main:app --reload --port 8005
```

## API Endpoints

### Payments
- `POST /payments/create-intent` - Create payment intent
- `POST /payments/confirm` - Confirm payment
- `GET /payments/{payment_id}` - Get payment details
- `GET /payments/user/{user_id}` - Get user payment history

### Refunds
- `POST /refunds/create` - Create refund
- `GET /refunds/{refund_id}` - Get refund status

### Webhooks
- `POST /webhooks/stripe` - Stripe webhook handler
- `POST /webhooks/paypal` - PayPal webhook handler

### Admin
- `GET /admin/transactions` - Get all transactions
- `GET /admin/analytics` - Payment analytics

## Architecture

```
payment-service/
├── src/
│   ├── application/          # Use cases and business logic
│   │   ├── dtos/            # Data transfer objects
│   │   └── use_cases/       # Payment processing logic
│   ├── domain/              # Domain models and entities
│   │   ├── entities/        # Payment, Transaction, Refund entities
│   │   └── repositories/    # Repository interfaces
│   ├── infrastructure/      # External integrations
│   │   ├── payment/         # Stripe, PayPal integrations
│   │   ├── database/        # PostgreSQL
│   │   ├── cache/           # Redis
│   │   ├── tasks/           # Celery tasks
│   │   └── email/           # Email service
│   ├── presentation/        # API layer
│   │   ├── api/            # Route handlers
│   │   └── middleware/     # Auth, rate limiting
│   ├── config/             # Configuration
│   └── main.py            # Application entry point
```

## Security

- All sensitive data is encrypted at rest
- PCI-DSS Level 1 compliance through Stripe/PayPal
- JWT authentication for all endpoints
- Rate limiting to prevent abuse
- Webhook signature verification

## Environment Variables

See `.env.example` for all configuration options.

## Docker

```bash
# Build
docker build -t payment-service .

# Run
docker run -p 8005:8005 --env-file .env payment-service
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src
```

## License

Proprietary - DEPI Final Project

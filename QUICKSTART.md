# 🚀 Quick Start Guide

## Prerequisites

- **Docker** & **Docker Compose** installed
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend)
- **Git**

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd DEPI-FinalProject

# Copy environment files
cp services/auth-service/.env.example services/auth-service/.env
cp services/product-service/.env.example services/product-service/.env
# ... repeat for other services
```

## Step 2: Start All Services with Docker Compose

```bash
# Start all services (databases + microservices)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f auth-service
```

## Step 3: Verify Services

Once all containers are running, verify each service:

### Auth Service
```bash
curl http://localhost:8001/health
# Or visit: http://localhost:8001/docs
```

### Product Service
```bash
curl http://localhost:8002/health
# Or visit: http://localhost:8002/docs
```

### Cart Service
```bash
curl http://localhost:8003/health
```

### Payment Service
```bash
curl http://localhost:8004/health
```

### Analytics Service
```bash
curl http://localhost:8005/health
```

### AI Search Service
```bash
curl http://localhost:8006/health
```

## Step 4: Test Authentication Flow

### Register a User

```bash
curl -X POST "http://localhost:8001/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from the response!

### Get Current User

```bash
curl -X GET "http://localhost:8001/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Step 5: Test Product Operations

### Create a Product (requires auth token)

```bash
curl -X POST "http://localhost:8002/products" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Laptop Pro 2024",
    "description": "High-performance laptop",
    "price": 1299.99,
    "stock": 50,
    "category_id": null,
    "metadata": {"brand": "TechCorp", "warranty": "2 years"}
  }'
```

### List Products (no auth required)

```bash
curl "http://localhost:8002/products?page=1&limit=10"
```

### Search Products

```bash
curl "http://localhost:8002/products/search?query=laptop&min_price=1000&max_price=2000"
```

## Step 6: Access API Documentation

Each service provides interactive API documentation:

- **Auth Service:** http://localhost:8001/docs
- **Product Service:** http://localhost:8002/docs
- **Cart Service:** http://localhost:8003/docs
- **Payment Service:** http://localhost:8004/docs
- **Analytics Service:** http://localhost:8005/docs
- **AI Search Service:** http://localhost:8006/docs

## Step 7: Database Access

If you need to access the databases directly:

```bash
# Auth Database
docker-compose exec auth-db psql -U postgres -d auth_db

# Product Database
docker-compose exec product-db psql -U postgres -d product_db

# Redis
docker-compose exec redis redis-cli
```

## Step 8: Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

## 🔧 Local Development (Without Docker)

### Setup Auth Service

```bash
cd services/auth-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database (make sure PostgreSQL is running)
# Update .env with your local database URL

# Run migrations (if using Alembic)
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8001
```

### Setup Product Service

```bash
cd services/product-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn src.main:app --reload --port 8002
```

## 🧪 Running Tests

```bash
# Test a specific service
cd services/auth-service
pytest -v --cov=src

# Test all services
./scripts/run-all-tests.sh
```

## 📊 Monitoring

### View Service Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f auth-service

# Last 100 lines
docker-compose logs --tail=100 product-service
```

### Check Container Health

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

## 🐛 Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose logs service-name

# Restart specific service
docker-compose restart service-name

# Rebuild if code changed
docker-compose up -d --build service-name
```

### Database connection issues

```bash
# Check if database is running
docker-compose ps | grep db

# Check database logs
docker-compose logs auth-db
```

### Port conflicts

If you get port binding errors:
1. Check what's using the port: `netstat -ano | findstr :8001` (Windows) or `lsof -i :8001` (Mac/Linux)
2. Either stop the conflicting process or change the port in `docker-compose.yml`

### Clear everything and restart

```bash
# Stop and remove all containers, networks, volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Restart fresh
docker-compose up -d --build
```

## 📝 Next Steps

1. ✅ Verify all services are running
2. ✅ Test authentication flow
3. ✅ Create some products
4. ✅ Test cart operations
5. ✅ Review API documentation
6. 🔜 Setup frontend application
7. 🔜 Configure AWS S3 for production
8. 🔜 Deploy to AWS ECS

## 🆘 Getting Help

- Check service logs: `docker-compose logs service-name`
- Review API docs: http://localhost:800X/docs
- Check this README: [README-ECOMMERCE.md](./README-ECOMMERCE.md)
- Review service-specific README in `services/[service-name]/README.md`

---

**Happy Coding! 🚀**

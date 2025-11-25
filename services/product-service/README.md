# Product Service

Microservice for managing product catalog with image storage on AWS S3.

## 🚀 Features

- ✅ Full CRUD operations for products
- ✅ AWS S3 integration for product images
- ✅ Advanced search and filtering
- ✅ Category management
- ✅ Pagination support
- ✅ Stock management
- ✅ Price validation
- ✅ Clean architecture

## 📁 Project Structure

```
product-service/
├── src/
│   ├── domain/
│   │   ├── models/
│   │   │   ├── product.py
│   │   │   └── category.py
│   │   └── interfaces/
│   │       └── product_repository.py
│   ├── application/
│   │   ├── services/
│   │   │   ├── product_service.py
│   │   │   └── s3_service.py
│   │   └── dtos/
│   │       └── product_schemas.py
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── product_repository.py
│   │   └── storage/
│   │       └── s3_client.py
│   ├── presentation/
│   │   ├── routes/
│   │   │   └── product_routes.py
│   │   └── middlewares/
│   │       └── auth_middleware.py
│   ├── config/
│   │   └── settings.py
│   └── main.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔌 API Endpoints

### Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/products` | Create product | ✅ Admin |
| GET | `/products` | List products with filters | ❌ |
| GET | `/products/{id}` | Get product details | ❌ |
| PUT | `/products/{id}` | Update product | ✅ Admin |
| DELETE | `/products/{id}` | Delete product | ✅ Admin |
| POST | `/products/{id}/images` | Upload images | ✅ Admin |
| DELETE | `/products/{id}/images/{image_id}` | Delete image | ✅ Admin |
| GET | `/products/search` | Search products | ❌ |

### Categories

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/categories` | Create category | ✅ Admin |
| GET | `/categories` | List categories | ❌ |
| GET | `/categories/{id}` | Get category | ❌ |
| PUT | `/categories/{id}` | Update category | ✅ Admin |
| DELETE | `/categories/{id}` | Delete category | ✅ Admin |

## 🔧 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/product_db

# Redis
REDIS_URL=redis://localhost:6379/1

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=ecommerce-products
S3_ENDPOINT_URL=  # Optional, for LocalStack

# Application
APP_NAME=ProductService
LOG_LEVEL=INFO
```

## 🏃 Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn src.main:app --reload --port 8002
```

## 📊 Database Schema

```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE products (
    id UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    category_id UUID REFERENCES categories(id),
    metadata JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE product_images (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_created ON products(created_at);
CREATE INDEX idx_product_images_product ON product_images(product_id);
```

## 🔍 Search & Filtering

The service supports advanced querying:

```
GET /products?category=electronics&min_price=100&max_price=500&search=laptop&page=1&limit=20&sort=price_asc
```

**Supported filters:**
- `category`: Filter by category slug
- `min_price`, `max_price`: Price range
- `search`: Text search in title and description
- `in_stock`: Boolean for stock availability
- `page`, `limit`: Pagination
- `sort`: price_asc, price_desc, newest, oldest

## 📝 License

MIT License © 2025

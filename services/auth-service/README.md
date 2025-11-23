# Authentication Service

JWT-based authentication microservice for the e-commerce platform.

## 🚀 Features

- ✅ User registration with email validation
- ✅ Secure login with JWT tokens
- ✅ Password hashing using bcrypt
- ✅ Access & refresh token management
- ✅ Token validation middleware
- ✅ PostgreSQL database
- ✅ Clean architecture (Domain, Application, Infrastructure, Presentation)

## 📁 Project Structure

```
auth-service/
├── src/
│   ├── domain/              # Core business entities
│   │   ├── models/
│   │   │   └── user.py
│   │   └── interfaces/
│   │       └── user_repository.py
│   ├── application/         # Business logic
│   │   ├── services/
│   │   │   └── auth_service.py
│   │   └── dtos/
│   │       ├── auth_schemas.py
│   │       └── user_schemas.py
│   ├── infrastructure/      # External dependencies
│   │   ├── database/
│   │   │   ├── connection.py
│   │   │   └── user_repository.py
│   │   └── security/
│   │       └── jwt_handler.py
│   ├── presentation/        # API layer
│   │   ├── routes/
│   │   │   ├── auth_routes.py
│   │   │   └── user_routes.py
│   │   └── middlewares/
│   │       └── auth_middleware.py
│   ├── config/
│   │   └── settings.py
│   └── main.py              # Application entry point
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/                 # Database migrations
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Environment Variables

Create a `.env` file:

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/auth_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=AuthService
APP_ENV=development
LOG_LEVEL=INFO
```

## 🐳 Running with Docker

```bash
# Build image
docker build -t auth-service .

# Run container
docker run -p 8001:8000 --env-file .env auth-service
```

## 🏃 Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8001
```

Visit API docs: http://localhost:8001/docs

## 🔌 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login and get tokens | ❌ |
| POST | `/auth/refresh` | Refresh access token | ❌ |
| POST | `/auth/logout` | Logout (invalidate tokens) | ✅ |
| GET | `/auth/me` | Get current user info | ✅ |

### Example Requests

**Register:**
```json
POST /auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Login:**
```json
POST /auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🔐 Security Features

- Password hashing with bcrypt (cost factor 12)
- JWT tokens with short expiration (15min access, 7d refresh)
- Secure token storage in HTTP-only cookies (optional)
- Rate limiting on auth endpoints
- Input validation with Pydantic
- SQL injection prevention

## 📊 Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token ON refresh_tokens(token);
```

## 🚀 Deployment

### Docker Compose

```bash
docker-compose up auth-service
```

### AWS ECS

See main project documentation for ECS deployment instructions.

## 📝 License

MIT License © 2025

# 🎨 Service Template Generator

This document serves as a template for creating new microservices following the same clean architecture pattern as the Auth Service.

## 📋 Template Structure

Every service should follow this structure:

```
service-name/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                 # Pydantic settings
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── [model_name].py        # SQLAlchemy models
│   │   └── interfaces/
│   │       ├── __init__.py
│   │       └── [repo_name].py         # Repository interfaces
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── [service_name].py      # Business logic
│   │   └── dtos/
│   │       ├── __init__.py
│   │       └── [dto_name].py          # Pydantic schemas
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py           # DB connection
│   │   │   └── [repo_impl].py         # Repository implementation
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   └── redis_client.py        # Redis client (copy from auth)
│   │   └── external/                   # Optional: for API clients
│   │       ├── __init__.py
│   │       └── [api_client].py
│   ├── presentation/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── [route_name].py        # API endpoints
│   │   └── middlewares/
│   │       ├── __init__.py
│   │       ├── auth_middleware.py      # Copy from shared/auth_utils.py
│   │       └── rate_limit.py           # Copy from auth service
│   └── main.py                         # FastAPI app
├── tests/
│   ├── __init__.py
│   ├── unit/
│   └── integration/
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 Standard Files for Every Service

### 1. `requirements.txt` (Base Dependencies)

```txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9

# Security (for auth validation)
python-jose[cryptography]>=3.3.0

# HTTP Client
httpx>=0.25.0

# Redis
redis>=5.0.0

# Rate Limiting
slowapi>=0.1.9

# Logging
python-json-logger>=2.0.7

# Environment
python-dotenv>=1.0.0

# [Add service-specific dependencies here]
```

### 2. `src/config/settings.py` (Template)

```python
"""
Configuration settings for [Service Name].
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "[ServiceName]"
    app_env: str = "development"
    log_level: str = "INFO"
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/[N]"  # Change N for each service
    
    # JWT (for auth validation)
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # [Add service-specific settings here]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
```

### 3. `src/infrastructure/database/connection.py` (Template)

```python
"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from src.config.settings import settings

# Create engine
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.log_level == "DEBUG"
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    Yields:
        SQLAlchemy Session object
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables - USE WITH CAUTION"""
    Base.metadata.drop_all(bind=engine)
```

### 4. `src/main.py` (Template)

```python
"""
Main FastAPI application for [Service Name].
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from src.config.settings import settings
from src.infrastructure.database.connection import create_tables
from src.presentation.routes import [your_routes]
from src.presentation.middlewares.rate_limit import limiter

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name}...")
    
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Test Redis connection
    try:
        from src.infrastructure.cache.redis_client import redis_client
        if redis_client.is_available():
            logger.info("Redis connection established")
        else:
            logger.warning("Redis unavailable")
    except Exception as e:
        logger.warning(f"Redis warning: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="[Service Description]",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router([your_routes].router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from src.infrastructure.cache.redis_client import redis_client
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "redis": "healthy" if redis_client.is_available() else "unavailable"
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
```

### 5. `Dockerfile` (Standard)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 6. `.env.example` (Template)

```bash
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:543X/[service]_db

# Redis
REDIS_URL=redis://localhost:6379/[N]

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256

# Application
APP_NAME=[ServiceName]
APP_ENV=development
LOG_LEVEL=INFO

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# [Service-specific env vars]
```

### 7. `.gitignore` (Standard)

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
.venv
*.log
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
```

## 🔐 Auth Middleware (For All Services)

Copy this to `src/presentation/middlewares/auth_middleware.py`:

```python
"""
Authentication middleware for validating JWT tokens.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt
from src.config.settings import settings

security = HTTPBearer()


def verify_access_token(token: str) -> Optional[str]:
    """Verify JWT access token and return user_id"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        if payload.get("type") != "access":
            return None
        
        return payload.get("sub")
    except JWTError:
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Extract and verify user ID from JWT token.
    Use this for protected endpoints.
    """
    token = credentials.credentials
    user_id_str = verify_access_token(token)
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[UUID]:
    """
    Optionally extract user ID from JWT token.
    Use for endpoints that work for both authenticated and anonymous users.
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None
```

## 📝 Quick Checklist for New Service

- [ ] Create folder structure
- [ ] Copy `requirements.txt` and add service-specific deps
- [ ] Create `settings.py` with service config
- [ ] Create database connection (`connection.py`)
- [ ] Define domain models (SQLAlchemy)
- [ ] Create repository interfaces
- [ ] Implement repositories
- [ ] Create DTOs (Pydantic schemas)
- [ ] Implement service layer (business logic)
- [ ] Create API routes
- [ ] Copy auth middleware
- [ ] Copy rate limit middleware
- [ ] Copy Redis client
- [ ] Create `main.py`
- [ ] Create `Dockerfile`
- [ ] Create `.env.example`
- [ ] Create `README.md`
- [ ] Add all `__init__.py` files
- [ ] Test endpoints

## 🎯 Service-Specific Adaptations

### Cart Service
- Add HTTP client for Product Service calls
- Implement cart item validation
- Add stock checking logic

### Payment Service
- Add Stripe SDK or payment provider
- Implement webhook handlers
- Add transaction models

### Analytics Service
- Optimize for write-heavy operations
- Add aggregation queries
- Consider TimescaleDB for time-series data

### AI Search Service
- Add sentence-transformers for embeddings
- Install pgvector extension
- Implement vector similarity search

---

**Use this template as your blueprint for all remaining services!** 🚀

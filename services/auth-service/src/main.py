"""
Main FastAPI application for the Authentication Service.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from src.config.settings import settings
from src.infrastructure.database.connection import create_tables
from src.presentation.routes import auth_routes
from src.presentation.middlewares.rate_limit import limiter


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name}...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Test Redis connection
    try:
        from src.infrastructure.cache.redis_client import redis_client
        if redis_client.is_available():
            logger.info("Redis connection established successfully")
        else:
            logger.warning("Redis is not available - caching and rate limiting will be limited")
    except Exception as e:
        logger.warning(f"Redis connection warning: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Authentication Service - JWT-based authentication for e-commerce platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting state
app.state.limiter = limiter

# Add rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint with Redis status"""
    from src.infrastructure.cache.redis_client import redis_client
    
    redis_status = "healthy" if redis_client.is_available() else "unavailable"
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "redis": redis_status
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

"""
Main FastAPI application for Product Service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from src.config.settings import settings
from src.infrastructure.database.connection import create_tables
from src.presentation.routes import product_routes
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
    
    # Test S3 connection
    try:
        from src.infrastructure.storage.s3_client import s3_client
        if s3_client.is_available():
            logger.info("S3 connection established")
        else:
            logger.warning("S3 unavailable - image uploads will fail")
    except Exception as e:
        logger.warning(f"S3 warning: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Product Service - Product catalog management with image uploads",
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
app.include_router(product_routes.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from src.infrastructure.storage.s3_client import s3_client
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0",
        "s3": "healthy" if s3_client.is_available() else "unavailable"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

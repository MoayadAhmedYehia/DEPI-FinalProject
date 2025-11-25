"""
Rate limiting middleware using slowapi.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from src.config.settings import settings


def get_user_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    Uses user ID from token if authenticated, otherwise uses IP address.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User identifier string
    """
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"] if settings.rate_limit_enabled else [],
    enabled=settings.rate_limit_enabled,
    storage_uri=settings.redis_url if settings.rate_limit_enabled else None,
)


# Rate limit decorators for common use cases
def strict_rate_limit():
    """Strict rate limit for sensitive operations (e.g., login)"""
    return limiter.limit("5/minute")


def moderate_rate_limit():
    """Moderate rate limit for normal operations"""
    return limiter.limit("20/minute")


def permissive_rate_limit():
    """Permissive rate limit for public endpoints"""
    return limiter.limit("100/minute")

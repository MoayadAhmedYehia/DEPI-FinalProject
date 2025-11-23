"""
Rate limiting middleware using slowapi.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from src.config.settings import settings


def get_user_identifier(request: Request) -> str:
    """
    Get identifier for rate limiting.
    Uses user ID from token if authenticated, otherwise uses IP address.
    """
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"
    
    return get_remote_address(request)


# Create limiter instance
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"] if settings.rate_limit_enabled else [],
    enabled=settings.rate_limit_enabled,
    storage_uri=settings.redis_url if settings.rate_limit_enabled else None,
)

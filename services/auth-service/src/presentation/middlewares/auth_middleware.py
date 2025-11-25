"""
Authentication middleware for protecting routes.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from src.infrastructure.security.jwt_handler import verify_access_token
from src.infrastructure.cache.redis_client import redis_client

security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    FastAPI dependency to extract and verify the current user from JWT token.
    Also checks if token is blacklisted.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        User ID from token payload
        
    Raises:
        HTTPException: If token is invalid, expired, or blacklisted
    """
    token = credentials.credentials
    
    # Check if token is blacklisted
    if redis_client.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token
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
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[UUID]:
    """
    FastAPI dependency to optionally extract user from JWT token.
    
    Args:
        credentials: HTTP Authorization header with Bearer token (optional)
        
    Returns:
        User ID from token payload or None if no token provided
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None

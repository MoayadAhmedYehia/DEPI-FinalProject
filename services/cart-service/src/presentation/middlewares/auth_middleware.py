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
    """Extract and verify user ID from JWT token"""
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

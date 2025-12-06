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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type must be 'access'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload.get("sub")
    except JWTError as e:
        # DEBUG: Expose specific error for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Extract and verify user ID from JWT token.
    Use this for protected endpoints.
    """
    token = credentials.credentials
    # verify_access_token now raises HTTPException directly with details
    user_id_str = verify_access_token(token)
    
    try:
        return UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token",
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

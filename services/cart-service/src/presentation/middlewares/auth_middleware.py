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
        # DEBUG LOGGING
        print(f"[AUTH DEBUG] Verifying token: {token[:20]}...")
        print(f"[AUTH DEBUG] Using Secret: {settings.jwt_secret_key[:5]}...")
        print(f"[AUTH DEBUG] Algorithm: {settings.jwt_algorithm}")
        
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        
        if payload.get("type") != "access":
            print(f"[AUTH DEBUG] Invalid token type: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token type must be 'access'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload.get("sub")
    except JWTError as e:
        print(f"[AUTH DEBUG] JWT Error: {str(e)}")
        # DEBUG: Expose specific error for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """Extract and verify user ID from JWT token"""
    token = credentials.credentials
    print(f"[AUTH DEBUG] Middleware received token: {token[:20]}...")
    
    # verify_access_token now raises HTTPException directly with details
    user_id_str = verify_access_token(token)
    
    try:
        return UUID(user_id_str)
    except ValueError:
        print(f"[AUTH DEBUG] Invalid UUID format: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )

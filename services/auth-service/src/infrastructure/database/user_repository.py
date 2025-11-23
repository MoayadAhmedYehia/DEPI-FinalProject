"""
User repository implementation with database operations.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.domain.models.user import User, RefreshToken
from src.domain.interfaces.user_repository import IUserRepository
from datetime import datetime, timedelta


class UserRepository(IUserRepository):
    """Concrete implementation of user repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, email: str, password_hash: str, full_name: str) -> User:
        """Create a new user"""
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"User with email {email} already exists")
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email.lower()).first()
    
    async def update(self, user: User) -> User:
        """Update user"""
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        user = await self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        return self.db.query(User).filter(User.email == email.lower()).count() > 0
    
    # Refresh token operations
    async def create_refresh_token(self, user_id: UUID, token: str, expires_days: int) -> RefreshToken:
        """Create a new refresh token"""
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=expires_days)
        )
        
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token
    
    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
    
    async def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        refresh_token = await self.get_refresh_token(token)
        if refresh_token:
            refresh_token.is_revoked = True
            self.db.commit()
            return True
        return False
    
    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user"""
        count = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        
        self.db.commit()
        return count

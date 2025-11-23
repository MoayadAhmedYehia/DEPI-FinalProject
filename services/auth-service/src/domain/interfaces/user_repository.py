"""
Repository interface for user operations (following Repository pattern).
"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from src.domain.models.user import User


class IUserRepository(ABC):
    """Interface defining user repository operations"""
    
    @abstractmethod
    async def create(self, email: str, password_hash: str, full_name: str) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        pass

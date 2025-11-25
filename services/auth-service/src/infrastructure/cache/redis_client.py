"""
Redis client for caching and token management.
"""
import redis
from typing import Optional
import json
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper for caching and token blacklist operations"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    def is_available(self) -> bool:
        """Check if Redis is available"""
        if self.redis is None:
            return False
        try:
            self.redis.ping()
            return True
        except:
            return False
    
    # Token Blacklist Operations
    def blacklist_token(self, token: str, expires_in: int) -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            token: JWT token to blacklist
            expires_in: Time in seconds until token expires
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("Redis unavailable, token blacklisting skipped")
            return False
        
        try:
            key = f"blacklist:{token}"
            self.redis.setex(key, expires_in, "1")
            logger.info(f"Token blacklisted successfully")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False
    
    def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if blacklisted, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            key = f"blacklist:{token}"
            return self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            return False
    
    # Caching Operations
    def set_cache(self, key: str, value: any, ttl: int = 3600) -> bool:
        """
        Set a cache value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis.setex(f"cache:{key}", ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[any]:
        """
        Get a cached value.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.is_available():
            return None
        
        try:
            value = self.redis.get(f"cache:{key}")
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting cache: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """
        Delete a cached value.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.redis.delete(f"cache:{key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache: {e}")
            return False
    
    def invalidate_user_cache(self, user_id: str) -> bool:
        """
        Invalidate all cache entries for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            pattern = f"cache:user:{user_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Error invalidating user cache: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()

"""
PHASE 6: Authentication Middleware
JWT validation and user context injection for protected endpoints.

Features:
- Extract JWT from Authorization header
- Validate token signature and expiration
- Inject user context into requests
- Per-user rate limiting
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import time

from .auth import get_auth_service, AuthenticationError

logger = logging.getLogger(__name__)

# Track user request counts for rate limiting
_user_requests: Dict[str, list] = {}  # {user_id: [timestamp, timestamp, ...]}


class AuthenticationMiddleware:
    """Middleware for JWT authentication and rate limiting"""
    
    def __init__(self):
        """Initialize middleware"""
        self.security = HTTPBearer()
    
    async def get_current_user(self, request: Request) -> Dict[str, Any]:
        """
        Extract and validate JWT from request.
        
        Expected: Authorization: Bearer <token>
        
        Args:
            request: FastAPI request object
        
        Returns:
            User dict with id, email
        
        Raises:
            HTTPException: If token missing or invalid
        """
        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Extract token
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = parts[1]
        
        # Verify token
        try:
            auth_service = get_auth_service()
            user = await auth_service.get_user_from_token(token)
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            logger.debug(f"User authenticated: {user['email']}")
            return user
            
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def check_rate_limit(self, user_id: str, limit: int, window_seconds: int) -> bool:
        """
        Check per-user rate limit.
        
        Args:
            user_id: User identifier
            limit: Max requests per window
            window_seconds: Time window in seconds
        
        Returns:
            True if within limit, False otherwise
        """
        now = time.time()
        cutoff = now - window_seconds
        
        # Initialize user request history if needed
        if user_id not in _user_requests:
            _user_requests[user_id] = []
        
        # Remove old requests outside window
        _user_requests[user_id] = [t for t in _user_requests[user_id] if t > cutoff]
        
        # Check if within limit
        if len(_user_requests[user_id]) >= limit:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Record this request
        _user_requests[user_id].append(now)
        return True
    
    def get_rate_limit_info(self, user_id: str, window_seconds: int) -> Dict[str, Any]:
        """
        Get rate limit information for user.
        
        Args:
            user_id: User identifier
            window_seconds: Time window
        
        Returns:
            Dict with requests_remaining, requests_used, reset_time
        """
        now = time.time()
        cutoff = now - window_seconds
        
        if user_id not in _user_requests:
            return {
                "requests_used": 0,
                "requests_remaining": "unlimited",
                "reset_time": now + window_seconds
            }
        
        recent_requests = [t for t in _user_requests[user_id] if t > cutoff]
        
        return {
            "requests_used": len(recent_requests),
            "requests_remaining": f"(see response headers)",
            "reset_time": max(recent_requests) + window_seconds if recent_requests else now + window_seconds
        }


# Global middleware instance
_middleware: Optional[AuthenticationMiddleware] = None


def init_auth_middleware() -> AuthenticationMiddleware:
    """Initialize and return global middleware"""
    global _middleware
    _middleware = AuthenticationMiddleware()
    return _middleware


def get_auth_middleware() -> AuthenticationMiddleware:
    """Get global middleware instance"""
    if _middleware is None:
        raise RuntimeError("Auth middleware not initialized. Call init_auth_middleware() first.")
    return _middleware


def clear_rate_limit_cache() -> int:
    """Clear rate limit cache (for testing)"""
    count = len(_user_requests)
    _user_requests.clear()
    logger.info(f"Cleared rate limit cache for {count} users")
    return count

"""
PHASE 6: Supabase Authentication Module
Email-only authentication with JWT token generation.

Features:
- Signup with email (auto-creates user, no verification required)
- Login with email (returns JWT token)
- User profile retrieval
- Password-less auth flow
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from supabase import Client

from .config import settings

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class AuthService:
    """Supabase authentication service"""
    
    def __init__(self, supabase_client: Client):
        """Initialize auth service with Supabase client"""
        self.client = supabase_client
    
    async def signup(self, email: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Sign up a new user with email only.
        
        PHASE 6: Password-less signup (no password verification)
        Creates user automatically, no email verification required.
        
        Args:
            email: User email address
            password: Optional password (for compatibility, not used)
        
        Returns:
            User dict with id, email, created_at
        
        Raises:
            AuthenticationError: If signup fails
        """
        if not email or "@" not in email:
            raise AuthenticationError("Invalid email address")
        
        try:
            # Use Supabase Auth - auto-creates user with no verification
            # Password-less mode: set random password for compatibility
            temp_password = f"temp_{email.split('@')[0]}_{int(datetime.now().timestamp())}"
            
            response = self.client.auth.sign_up({
                "email": email,
                "password": temp_password,
                "options": {
                    "data": {
                        "email": email,
                        "created_at": datetime.now().isoformat(),
                        "auth_method": "email_passwordless"
                    }
                }
            })
            
            logger.info(f"User signed up: {email}")
            
            return {
                "id": response.user.id,
                "email": response.user.email,
                "created_at": datetime.now().isoformat(),
                "verified": False  # No verification in PHASE 6
            }
            
        except Exception as e:
            logger.error(f"Signup failed for {email}: {str(e)}")
            raise AuthenticationError(f"Signup failed: {str(e)}")
    
    async def login(self, email: str, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Login with email.
        
        PHASE 6: Password-less login - returns JWT for any valid email
        
        Args:
            email: User email address
            password: Optional (not used in password-less mode)
        
        Returns:
            Token dict with access_token, user info, expires_in
        
        Raises:
            AuthenticationError: If login fails
        """
        if not email or "@" not in email:
            raise AuthenticationError("Invalid email address")
        
        try:
            # PHASE 6: Password-less auth - generate JWT directly
            # Production: Would use Supabase Auth session tokens
            
            user_id = self._generate_user_id(email)
            access_token = self._generate_jwt_token(user_id, email)
            
            logger.info(f"User logged in: {email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_EXPIRATION_SECONDS,
                "user": {
                    "id": user_id,
                    "email": email
                }
            }
            
        except Exception as e:
            logger.error(f"Login failed for {email}: {str(e)}")
            raise AuthenticationError(f"Login failed: {str(e)}")
    
    def _generate_user_id(self, email: str) -> str:
        """
        Generate consistent user ID from email.
        
        PHASE 6: For development, use email-based ID.
        Production: Would fetch from Supabase users table.
        """
        import hashlib
        return hashlib.sha256(email.encode()).hexdigest()[:32]
    
    def _generate_jwt_token(self, user_id: str, email: str) -> str:
        """
        Generate JWT token for authenticated user.
        
        Args:
            user_id: Unique user identifier
            email: User email
        
        Returns:
            Signed JWT token
        """
        now = datetime.utcnow()
        expiration = now + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "iat": now,
            "exp": expiration,
            "sub": user_id,
            "aud": "authenticated"
        }
        
        token = jwt.encode(
            payload,
            settings.SUPABASE_SERVICE_ROLE_KEY or "dev-secret-key",
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.debug(f"JWT token generated for {email}")
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload with user_id, email, etc.
        
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_SERVICE_ROLE_KEY or "dev-secret-key",
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            logger.debug(f"Token verified for user {payload.get('email')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning(f"Token expired")
            raise AuthenticationError("Token has expired")
        
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            raise AuthenticationError(f"Invalid token: {str(e)}")
        
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise AuthenticationError(f"Token verification failed: {str(e)}")
    
    async def get_user_from_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract user info from valid token.
        
        Args:
            token: JWT token string
        
        Returns:
            User dict with id, email, etc.
            None if token invalid
        """
        try:
            payload = self.verify_token(token)
            return {
                "id": payload.get("user_id"),
                "email": payload.get("email"),
                "verified": True
            }
        except AuthenticationError:
            return None


# Global auth service instance
_auth_service: Optional[AuthService] = None


def init_auth_service(supabase_client: Client) -> AuthService:
    """Initialize and return global auth service"""
    global _auth_service
    _auth_service = AuthService(supabase_client)
    return _auth_service


def get_auth_service() -> AuthService:
    """Get global auth service instance"""
    if _auth_service is None:
        raise RuntimeError("Auth service not initialized. Call init_auth_service() first.")
    return _auth_service

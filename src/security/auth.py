import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
import redis
import hashlib
from .config import SecurityConfig

class AuthManager:
    """Secure authentication and authorization"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
        self.config = SecurityConfig()
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=self.config.PASSWORD_HASH_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def generate_tokens(self, user_id: int, username: str) -> Dict[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            'user_id': user_id,
            'username': username,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(minutes=self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': user_id,
            'username': username,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=self.config.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            'jti': secrets.token_urlsafe(16)
        }
        
        access_token = jwt.encode(access_payload, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM)
        
        # Store tokens in Redis for revocation tracking
        self.redis_client.setex(
            f"access_token:{access_payload['jti']}", 
            self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id
        )
        self.redis_client.setex(
            f"refresh_token:{refresh_payload['jti']}", 
            self.config.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            user_id
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=[self.config.JWT_ALGORITHM])
            
            # Check if token is revoked
            jti = payload.get('jti')
            token_type = payload.get('type', 'access')
            
            if not self.redis_client.exists(f"{token_type}_token:{jti}"):
                return None  # Token revoked
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a JWT token"""
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=[self.config.JWT_ALGORITHM])
            jti = payload.get('jti')
            token_type = payload.get('type', 'access')
            
            self.redis_client.delete(f"{token_type}_token:{jti}")
            return True
            
        except Exception:
            return False
    
    def generate_api_key(self, user_id: int) -> str:
        """Generate secure API key"""
        api_key = secrets.token_urlsafe(self.config.API_KEY_LENGTH)
        
        # Store API key with expiration
        self.redis_client.setex(
            f"api_key:{api_key}",
            self.config.API_KEY_EXPIRE_DAYS * 24 * 60 * 60,
            user_id
        )
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[int]:
        """Verify API key and return user ID"""
        user_id = self.redis_client.get(f"api_key:{api_key}")
        return int(user_id) if user_id else None
    
    def track_failed_login(self, identifier: str) -> bool:
        """Track failed login attempts"""
        key = f"failed_login:{hashlib.sha256(identifier.encode()).hexdigest()}"
        
        # Increment counter
        current = self.redis_client.incr(key)
        
        # Set expiration on first attempt
        if current == 1:
            self.redis_client.expire(key, self.config.ACCOUNT_LOCKOUT_DURATION_MINUTES * 60)
        
        return current >= self.config.FAILED_LOGIN_THRESHOLD
    
    def is_account_locked(self, identifier: str) -> bool:
        """Check if account is locked due to failed attempts"""
        key = f"failed_login:{hashlib.sha256(identifier.encode()).hexdigest()}"
        attempts = self.redis_client.get(key)
        
        if attempts:
            return int(attempts) >= self.config.FAILED_LOGIN_THRESHOLD
        
        return False
    
    def clear_failed_attempts(self, identifier: str):
        """Clear failed login attempts after successful login"""
        key = f"failed_login:{hashlib.sha256(identifier.encode()).hexdigest()}"
        self.redis_client.delete(key)

class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=0)
    
    def is_allowed(self, identifier: str, limit: int, window: int = 60) -> bool:
        """Check if request is within rate limit"""
        key = f"rate_limit:{hashlib.sha256(identifier.encode()).hexdigest()}"
        
        current = self.redis_client.incr(key)
        
        if current == 1:
            self.redis_client.expire(key, window)
        
        return current <= limit
    
    def get_remaining(self, identifier: str, limit: int) -> int:
        """Get remaining requests in current window"""
        key = f"rate_limit:{hashlib.sha256(identifier.encode()).hexdigest()}"
        current = self.redis_client.get(key)
        
        if current:
            return max(0, limit - int(current))
        
        return limit

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implementation depends on framework (FastAPI, Flask, etc.)
        # This is a template
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check user permissions
            return f(*args, **kwargs)
        return decorated_function
    return decorator
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import hashlib
from typing import Optional
import redis
from sqlalchemy.orm import Session

from src.security.config import SecurityConfig
from src.security.auth import AuthManager, RateLimiter
from src.security.validation import InputValidator
from src.security.audit import SecurityMonitor, AuditEventType
from src.database.database import get_db

# Initialize security components
security_config = SecurityConfig()
auth_manager = AuthManager()
rate_limiter = RateLimiter()
security_bearer = HTTPBearer()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Create FastAPI app with security settings
app = FastAPI(
    title="ZipIt MLOps Platform API",
    description="Secure MLOps Platform API",
    version="1.0.0",
    docs_url="/docs" if not security_config.PRODUCTION else None,  # Disable docs in production
    redoc_url="/redoc" if not security_config.PRODUCTION else None
)

# Security Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    for header, value in security_config.SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response

@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    
    # Different limits for different endpoints
    if request.url.path.startswith("/auth/login"):
        limit = security_config.LOGIN_RATE_LIMIT_PER_MINUTE
    elif request.url.path.startswith("/api/"):
        limit = security_config.API_RATE_LIMIT_PER_MINUTE
    else:
        limit = security_config.RATE_LIMIT_PER_MINUTE
    
    if not rate_limiter.is_allowed(client_ip, limit):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining(client_ip, limit)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response

@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    """Audit logging middleware"""
    start_time = time.time()
    
    # Generate request ID
    request_id = hashlib.sha256(f"{time.time()}{request.client.host}".encode()).hexdigest()[:16]
    
    response = await call_next(request)
    
    # Log API access
    db = next(get_db())
    monitor = SecurityMonitor(db)
    
    monitor.log_event(
        event_type=AuditEventType.API_ACCESS,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        resource=str(request.url.path),
        action=request.method,
        success=response.status_code < 400,
        details={
            "status_code": response.status_code,
            "response_time": time.time() - start_time,
            "request_size": request.headers.get("content-length", 0)
        },
        request_id=request_id
    )
    
    return response

# CORS with strict settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["zipit.com", "www.zipit.com", "localhost", "127.0.0.1"]
)

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    token = credentials.credentials
    
    # Verify token
    payload = auth_manager.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload

# Input validation dependency
def validate_request_data(data: dict):
    """Validate request data"""
    result = InputValidator.validate_json_input(data)
    if not result.get('valid', True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get('error', 'Invalid input data')
        )
    return result.get('data', data)

# API Routes with security
@app.post("/auth/register")
async def register_user(request: Request, user_data: dict, db: Session = Depends(get_db)):
    """Register new user with validation"""
    
    # Validate input
    validated_data = validate_request_data(user_data)
    
    # Validate email
    if not InputValidator.validate_email(validated_data.get('email', '')):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Validate username
    if not InputValidator.validate_username(validated_data.get('username', '')):
        raise HTTPException(status_code=400, detail="Invalid username format")
    
    # Validate password
    password_check = InputValidator.validate_password(validated_data.get('password', ''))
    if not password_check['valid']:
        raise HTTPException(status_code=400, detail=password_check['errors'])
    
    # Check if user exists
    from src.database.models import User
    existing_user = db.query(User).filter(
        (User.email == validated_data['email']) | 
        (User.username == validated_data['username'])
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    hashed_password = auth_manager.hash_password(validated_data['password'])
    
    new_user = User(
        username=validated_data['username'],
        email=validated_data['email'],
        hashed_password=hashed_password,
        full_name=validated_data.get('full_name', '')
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log event
    monitor = SecurityMonitor(db)
    monitor.log_event(
        event_type=AuditEventType.ACCOUNT_CREATED,
        user_id=new_user.id,
        username=new_user.username,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        success=True
    )
    
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/auth/login")
async def login_user(request: Request, login_data: dict, db: Session = Depends(get_db)):
    """Login user with security checks"""
    
    # Validate input
    validated_data = validate_request_data(login_data)
    
    username = validated_data.get('username', '')
    password = validated_data.get('password', '')
    
    # Check account lockout
    if auth_manager.is_account_locked(username):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to failed login attempts"
        )
    
    # Find user
    from src.database.models import User
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not auth_manager.verify_password(password, user.hashed_password):
        # Track failed attempt
        auth_manager.track_failed_login(username)
        
        # Log failed login
        monitor = SecurityMonitor(db)
        monitor.log_event(
            event_type=AuditEventType.LOGIN_FAILED,
            username=username,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=False
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Clear failed attempts
    auth_manager.clear_failed_attempts(username)
    
    # Generate tokens
    tokens = auth_manager.generate_tokens(user.id, user.username)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Log successful login
    monitor = SecurityMonitor(db)
    monitor.log_event(
        event_type=AuditEventType.LOGIN_SUCCESS,
        user_id=user.id,
        username=user.username,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        success=True
    )
    
    return tokens

@app.post("/auth/logout")
async def logout_user(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user and revoke token"""
    
    # Revoke token (implementation depends on token storage)
    # auth_manager.revoke_token(token)
    
    # Log logout
    monitor = SecurityMonitor(db)
    monitor.log_event(
        event_type=AuditEventType.LOGOUT,
        user_id=current_user['user_id'],
        username=current_user['username'],
        ip_address=request.client.host,
        success=True
    )
    
    return {"message": "Logged out successfully"}

@app.get("/api/user/profile")
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile (protected endpoint)"""
    
    from src.database.models import User
    user = db.query(User).filter(User.id == current_user['user_id']).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "subscription_tier": user.subscription_tier.value,
        "created_at": user.created_at
    }

@app.get("/api/security/audit")
async def get_security_audit(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get security audit information (admin only)"""
    
    # Check admin permission
    from src.database.models import User, SubscriptionTier
    user = db.query(User).filter(User.id == current_user['user_id']).first()
    
    if user.subscription_tier != SubscriptionTier.ELITE:  # Assuming admin is elite
        raise HTTPException(status_code=403, detail="Admin access required")
    
    monitor = SecurityMonitor(db)
    report = monitor.generate_security_report()
    
    return report

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    # Log error
    import logging
    logging.error(f"Unhandled exception: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="ssl/private.key",
        ssl_certfile="ssl/certificate.crt"
    )
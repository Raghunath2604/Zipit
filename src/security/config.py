import os
import secrets
from datetime import timedelta

class SecurityConfig:
    """Enterprise-grade security configuration"""
    
    # JWT Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(64))
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    # Password Security
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
    PASSWORD_HASH_ROUNDS = 12
    
    # Session Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SESSION_TIMEOUT_MINUTES = 60
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 60
    LOGIN_RATE_LIMIT_PER_MINUTE = 5
    API_RATE_LIMIT_PER_MINUTE = 100
    
    # Input Validation
    MAX_UPLOAD_SIZE_MB = 100
    ALLOWED_FILE_EXTENSIONS = {'.pkl', '.joblib', '.h5', '.pt', '.onnx'}
    MAX_STRING_LENGTH = 1000
    
    # Database Security
    DB_CONNECTION_TIMEOUT = 30
    DB_MAX_CONNECTIONS = 20
    DB_SSL_REQUIRED = True
    
    # API Security
    API_KEY_LENGTH = 32
    API_KEY_EXPIRE_DAYS = 90
    CORS_ALLOWED_ORIGINS = ['https://zipit.com', 'https://www.zipit.com']
    
    # Encryption
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', secrets.token_bytes(32))
    
    # Audit Logging
    AUDIT_LOG_ENABLED = True
    AUDIT_LOG_RETENTION_DAYS = 365
    
    # Security Headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # IP Whitelist (for admin access)
    ADMIN_IP_WHITELIST = os.getenv('ADMIN_IP_WHITELIST', '').split(',')
    
    # Monitoring
    FAILED_LOGIN_THRESHOLD = 5
    ACCOUNT_LOCKOUT_DURATION_MINUTES = 30
    SUSPICIOUS_ACTIVITY_THRESHOLD = 10
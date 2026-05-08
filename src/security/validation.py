import re
import html
import bleach
from typing import Any, Dict, List, Optional
from pathlib import Path
import magic
import hashlib

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    PASSWORD_PATTERN = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    
    # Allowed HTML tags for rich text
    ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        return bool(InputValidator.USERNAME_PATTERN.match(username))
    
    @staticmethod
    def validate_password(password: str) -> Dict[str, bool]:
        """Validate password strength"""
        if not password:
            return {'valid': False, 'errors': ['Password is required']}
        
        errors = []
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters')
        
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain lowercase letters')
        
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain uppercase letters')
        
        if not re.search(r'\d', password):
            errors.append('Password must contain numbers')
        
        if not re.search(r'[@$!%*?&]', password):
            errors.append('Password must contain special characters')
        
        return {'valid': len(errors) == 0, 'errors': errors}
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not text:
            return ""
        
        # Truncate if too long
        text = text[:max_length]
        
        # HTML escape
        text = html.escape(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        return text.strip()
    
    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """Sanitize HTML content"""
        if not html_content:
            return ""
        
        return bleach.clean(
            html_content,
            tags=InputValidator.ALLOWED_TAGS,
            attributes=InputValidator.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    @staticmethod
    def validate_file_upload(file_path: str, allowed_extensions: set) -> Dict[str, Any]:
        """Validate uploaded file"""
        try:
            path = Path(file_path)
            
            # Check extension
            if path.suffix.lower() not in allowed_extensions:
                return {'valid': False, 'error': 'File type not allowed'}
            
            # Check file size (100MB max)
            if path.stat().st_size > 100 * 1024 * 1024:
                return {'valid': False, 'error': 'File too large (max 100MB)'}
            
            # Check MIME type
            mime_type = magic.from_file(file_path, mime=True)
            allowed_mimes = {
                '.pkl': 'application/octet-stream',
                '.joblib': 'application/octet-stream',
                '.h5': 'application/x-hdf',
                '.pt': 'application/octet-stream',
                '.onnx': 'application/octet-stream'
            }
            
            expected_mime = allowed_mimes.get(path.suffix.lower())
            if expected_mime and mime_type != expected_mime:
                return {'valid': False, 'error': 'File content does not match extension'}
            
            # Calculate file hash for integrity
            file_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
            
            return {
                'valid': True,
                'size': path.stat().st_size,
                'mime_type': mime_type,
                'hash': file_hash.hexdigest()
            }
            
        except Exception as e:
            return {'valid': False, 'error': f'File validation error: {str(e)}'}
    
    @staticmethod
    def validate_json_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize JSON input"""
        if not isinstance(data, dict):
            return {'valid': False, 'error': 'Invalid JSON format'}
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            clean_key = InputValidator.sanitize_string(str(key), 100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[clean_key] = InputValidator.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[clean_key] = value
            elif isinstance(value, list):
                sanitized[clean_key] = [
                    InputValidator.sanitize_string(str(item)) if isinstance(item, str) else item
                    for item in value[:100]  # Limit array size
                ]
            elif isinstance(value, dict):
                # Recursive validation for nested objects
                nested_result = InputValidator.validate_json_input(value)
                if nested_result.get('valid', True):
                    sanitized[clean_key] = nested_result.get('data', value)
        
        return {'valid': True, 'data': sanitized}
    
    @staticmethod
    def validate_sql_input(query: str) -> bool:
        """Check for SQL injection patterns"""
        if not query:
            return True
        
        # Dangerous SQL keywords
        dangerous_patterns = [
            r'\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|EXECUTE)\b',
            r'--',
            r'/\*.*\*/',
            r'\bunion\b.*\bselect\b',
            r'\bor\b.*=.*\bor\b',
            r"'.*'.*=.*'.*'",
        ]
        
        query_lower = query.lower()
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return False
        
        return True
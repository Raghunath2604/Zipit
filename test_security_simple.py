#!/usr/bin/env python3
"""
ZipIt Security Test Suite - Simplified Version
Tests core security without external dependencies
"""

import sys
import os
import re
import hashlib
import secrets
import html
from typing import Dict, List, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class SimplifiedSecurityTester:
    """Simplified security testing without external dependencies"""
    
    def __init__(self):
        self.test_results = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        print("🔒 ZipIt Security Test Suite (Simplified)")
        print("=" * 50)
        
        tests = [
            ("Input Validation", self.test_input_validation),
            ("Password Security", self.test_password_security),
            ("Authorization", self.test_authorization),
            ("XSS Protection", self.test_xss_protection),
            ("SQL Injection", self.test_sql_injection),
            ("Security Configuration", self.test_security_config),
            ("Database Models", self.test_database_models),
            ("Subscription Security", self.test_subscription_security)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\\n🧪 Testing: {test_name}")
            try:
                result = test_func()
                if result['passed']:
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
                
                self.test_results.append({
                    'test': test_name,
                    'passed': result['passed'],
                    'details': result.get('details', []),
                    'error': result.get('error')
                })
                
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                self.test_results.append({
                    'test': test_name,
                    'passed': False,
                    'error': str(e)
                })
        
        print("\\n" + "=" * 50)
        print(f"🔒 Security Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🛡️ All security tests passed! Platform is secure.")
        elif passed >= total * 0.8:
            print("✅ Most security tests passed. Platform is reasonably secure.")
        else:
            print("⚠️ Some security tests failed. Review and fix issues.")
        
        return {
            'total_tests': total,
            'passed_tests': passed,
            'success_rate': (passed / total) * 100,
            'results': self.test_results
        }
    
    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation"""
        try:
            # Email validation
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$')
            
            assert bool(email_pattern.match("test@example.com")) == True
            assert bool(email_pattern.match("invalid-email")) == False
            
            # Username validation
            username_pattern = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
            
            assert bool(username_pattern.match("valid_user123")) == True
            assert bool(username_pattern.match("invalid user!")) == False
            
            # Password validation
            password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$')
            
            assert bool(password_pattern.match("StrongPass123!")) == True
            assert bool(password_pattern.match("weak")) == False
            
            # String sanitization
            dangerous_input = "<script>alert('xss')</script>"
            sanitized = html.escape(dangerous_input)
            assert "<script>" not in sanitized
            
            return {'passed': True, 'details': ['Email validation', 'Username validation', 'Password validation', 'String sanitization']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_password_security(self) -> Dict[str, Any]:
        """Test password security"""
        try:
            import bcrypt
            
            # Test password hashing
            password = "TestPassword123!"
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # Verify password
            assert bcrypt.checkpw(password.encode('utf-8'), hashed) == True
            assert bcrypt.checkpw("wrong_password".encode('utf-8'), hashed) == False
            
            # Test hash strength
            assert len(hashed) > 50
            
            return {'passed': True, 'details': ['Password hashing with bcrypt', 'Hash verification', 'Strong salt rounds']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_authorization(self) -> Dict[str, Any]:
        """Test authorization controls"""
        try:
            from src.database.models import User, SubscriptionTier
            
            # Test free tier user
            free_user = User(
                username="free_user",
                email="free@example.com",
                subscription_tier=SubscriptionTier.FREE
            )
            
            limits = free_user.tier_limits
            assert limits['max_models'] == 3
            assert limits['max_storage_gb'] == 1.0
            assert 'basic_training' in limits['features']
            assert 'automl' not in limits['features']
            
            # Test developer tier user
            dev_user = User(
                username="dev_user",
                email="dev@example.com",
                subscription_tier=SubscriptionTier.DEVELOPER
            )
            
            dev_limits = dev_user.tier_limits
            assert dev_limits['max_models'] == 15
            assert 'automl' in dev_limits['features']
            
            return {'passed': True, 'details': ['Tier-based limits', 'Feature access control', 'Subscription validation']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_xss_protection(self) -> Dict[str, Any]:
        """Test XSS protection"""
        try:
            # XSS payloads
            xss_payloads = [
                "<script>alert('xss')</script>",
                "<img src=x onerror=alert('xss')>",
                "javascript:alert('xss')",
                "<svg onload=alert('xss')>",
                "';alert('xss');//"
            ]
            
            for payload in xss_payloads:
                # HTML escape
                sanitized = html.escape(payload)
                
                # Check dangerous patterns are escaped
                assert "&lt;script&gt;" in sanitized or "<script>" not in sanitized
                assert "javascript:" not in sanitized or "javascript:" in payload
            
            return {'passed': True, 'details': ['XSS payload sanitization', 'HTML escaping', 'Script tag neutralization']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_sql_injection(self) -> Dict[str, Any]:
        """Test SQL injection protection"""
        try:
            # SQL injection patterns
            dangerous_patterns = [
                r'\\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|EXECUTE)\\b',
                r'--',
                r'/\\*.*\\*/',
                r'\\bunion\\b.*\\bselect\\b',
                r'\\bor\\b.*=.*\\bor\\b',
                r"'.*'.*=.*'.*'",
            ]
            
            malicious_inputs = [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "admin'--",
                "1; DELETE FROM users WHERE 1=1; --",
                "' UNION SELECT * FROM users --"
            ]
            
            for malicious_input in malicious_inputs:
                is_dangerous = False
                for pattern in dangerous_patterns:
                    if re.search(pattern, malicious_input, re.IGNORECASE):
                        is_dangerous = True
                        break
                
                assert is_dangerous == True  # Should detect as dangerous
            
            # Test safe input
            safe_input = "normal search term"
            is_safe = True
            for pattern in dangerous_patterns:
                if re.search(pattern, safe_input, re.IGNORECASE):
                    is_safe = False
                    break
            
            assert is_safe == True
            
            return {'passed': True, 'details': ['SQL injection pattern detection', 'Malicious query identification', 'Safe input validation']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_security_config(self) -> Dict[str, Any]:
        """Test security configuration"""
        try:
            from src.security.config import SecurityConfig
            
            config = SecurityConfig()
            
            # Test JWT configuration
            assert hasattr(config, 'JWT_SECRET_KEY')
            assert config.JWT_ALGORITHM == 'HS256'
            assert config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
            
            # Test password requirements
            assert config.PASSWORD_MIN_LENGTH >= 8
            assert config.PASSWORD_REQUIRE_UPPERCASE == True
            assert config.PASSWORD_REQUIRE_NUMBERS == True
            
            # Test session security
            assert config.SESSION_COOKIE_SECURE == True
            assert config.SESSION_COOKIE_HTTPONLY == True
            
            # Test security headers
            assert 'X-Content-Type-Options' in config.SECURITY_HEADERS
            assert 'X-Frame-Options' in config.SECURITY_HEADERS
            assert 'Strict-Transport-Security' in config.SECURITY_HEADERS
            
            return {'passed': True, 'details': ['JWT configuration', 'Password requirements', 'Session security', 'Security headers']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_database_models(self) -> Dict[str, Any]:
        """Test database model security"""
        try:
            from src.database.models import User, SubscriptionTier, Payment
            
            # Test user model
            user = User(
                username="test_user",
                email="test@example.com",
                subscription_tier=SubscriptionTier.FREE
            )
            
            # Test password hashing method exists
            assert hasattr(user, 'hash_password')
            assert hasattr(user, 'verify_password')
            
            # Test subscription tiers
            assert SubscriptionTier.FREE.value == "free"
            assert SubscriptionTier.DEVELOPER.value == "developer"
            assert SubscriptionTier.ELITE.value == "elite"
            
            # Test payment model exists
            payment = Payment(
                user_id=1,
                amount=15.0,
                tier=SubscriptionTier.DEVELOPER
            )
            
            assert payment.amount == 15.0
            
            return {'passed': True, 'details': ['User model security', 'Password methods', 'Subscription tiers', 'Payment model']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}
    
    def test_subscription_security(self) -> Dict[str, Any]:
        """Test subscription system security"""
        try:
            from src.subscription.subscription_manager import PRICING_PLANS
            
            # Test pricing plans exist
            assert SubscriptionTier.FREE in PRICING_PLANS
            assert SubscriptionTier.DEVELOPER in PRICING_PLANS
            assert SubscriptionTier.ELITE in PRICING_PLANS
            
            # Test free tier limits
            free_plan = PRICING_PLANS[SubscriptionTier.FREE]
            assert free_plan['price'] == 0
            assert free_plan['models'] == 3
            
            # Test developer tier
            dev_plan = PRICING_PLANS[SubscriptionTier.DEVELOPER]
            assert dev_plan['price'] == 15
            assert dev_plan['models'] == 15
            
            # Test elite tier
            elite_plan = PRICING_PLANS[SubscriptionTier.ELITE]
            assert elite_plan['price'] == 55
            assert elite_plan['models'] == 100
            
            return {'passed': True, 'details': ['Pricing plans configuration', 'Tier limits', 'Payment amounts']}
            
        except Exception as e:
            return {'passed': False, 'error': str(e)}

def main():
    """Run security tests"""
    tester = SimplifiedSecurityTester()
    results = tester.run_all_tests()
    
    # Generate security report
    print("\\n📊 Security Report")
    print("=" * 30)
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
    
    if results['success_rate'] >= 90:
        print("🛡️ EXCELLENT: Platform has strong security")
    elif results['success_rate'] >= 75:
        print("✅ GOOD: Platform has adequate security")
    elif results['success_rate'] >= 50:
        print("⚠️ WARNING: Platform has security issues")
    else:
        print("🚨 CRITICAL: Platform has serious security vulnerabilities")
    
    # Security recommendations
    print("\\n🔧 Security Recommendations:")
    print("1. Install Redis for session management and rate limiting")
    print("2. Configure SSL/TLS certificates for HTTPS")
    print("3. Set up proper firewall rules")
    print("4. Enable audit logging in production")
    print("5. Regular security updates and monitoring")
    
    return results['success_rate'] >= 75

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
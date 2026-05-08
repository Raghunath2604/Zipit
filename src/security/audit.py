import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import hashlib
import geoip2.database
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AuditEventType(Enum):
    """Types of audit events"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DELETED = "account_deleted"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    API_ACCESS = "api_access"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_VIOLATION = "security_violation"

class AuditLog(Base):
    """Audit log database model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String(100), index=True)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    resource = Column(String(255))
    action = Column(String(100))
    success = Column(Boolean, default=True)
    details = Column(Text)  # JSON string
    risk_score = Column(Integer, default=0)
    session_id = Column(String(255))
    request_id = Column(String(255))

class SecurityMonitor:
    """Security monitoring and audit logging"""
    
    def __init__(self, db_session, geoip_db_path: Optional[str] = None):
        self.db = db_session
        self.logger = self._setup_logger()
        self.geoip_reader = None
        
        if geoip_db_path:
            try:
                self.geoip_reader = geoip2.database.Reader(geoip_db_path)
            except Exception:
                pass
    
    def _setup_logger(self) -> logging.Logger:
        """Setup structured logging"""
        logger = logging.getLogger('security_audit')
        logger.setLevel(logging.INFO)
        
        # File handler for audit logs
        handler = logging.FileHandler('logs/security_audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log_event(self, 
                  event_type: AuditEventType,
                  user_id: Optional[int] = None,
                  username: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  resource: Optional[str] = None,
                  action: Optional[str] = None,
                  success: bool = True,
                  details: Optional[Dict[str, Any]] = None,
                  session_id: Optional[str] = None,
                  request_id: Optional[str] = None) -> None:
        """Log security event"""
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(event_type, ip_address, details)
        
        # Get location info
        location_info = self._get_location_info(ip_address) if ip_address else {}
        
        # Prepare details
        event_details = {
            **(details or {}),
            **location_info
        }
        
        # Create audit log entry
        audit_entry = AuditLog(
            event_type=event_type.value,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            success=success,
            details=json.dumps(event_details),
            risk_score=risk_score,
            session_id=session_id,
            request_id=request_id
        )
        
        # Save to database
        try:
            self.db.add(audit_entry)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to save audit log: {e}")
        
        # Log to file
        log_message = {
            'event_type': event_type.value,
            'user_id': user_id,
            'username': username,
            'ip_address': ip_address,
            'success': success,
            'risk_score': risk_score,
            'details': event_details
        }
        
        if risk_score >= 7:
            self.logger.critical(f"HIGH RISK EVENT: {json.dumps(log_message)}")
        elif risk_score >= 5:
            self.logger.warning(f"MEDIUM RISK EVENT: {json.dumps(log_message)}")
        else:
            self.logger.info(f"AUDIT EVENT: {json.dumps(log_message)}")
    
    def _calculate_risk_score(self, 
                            event_type: AuditEventType, 
                            ip_address: Optional[str],
                            details: Optional[Dict[str, Any]]) -> int:
        """Calculate risk score for event (0-10)"""
        score = 0
        
        # Base scores by event type
        risk_scores = {
            AuditEventType.LOGIN_FAILED: 3,
            AuditEventType.SUSPICIOUS_ACTIVITY: 8,
            AuditEventType.SECURITY_VIOLATION: 9,
            AuditEventType.PERMISSION_GRANTED: 4,
            AuditEventType.ACCOUNT_CREATED: 2,
            AuditEventType.PASSWORD_CHANGE: 3,
            AuditEventType.DATA_MODIFICATION: 4,
            AuditEventType.FILE_UPLOAD: 3,
        }
        
        score += risk_scores.get(event_type, 1)
        
        # IP-based risk factors
        if ip_address:
            # Check for suspicious patterns
            if self._is_suspicious_ip(ip_address):
                score += 3
            
            # Check for unusual location
            if self._is_unusual_location(ip_address):
                score += 2
        
        # Details-based risk factors
        if details:
            if details.get('multiple_failed_attempts'):
                score += 2
            if details.get('unusual_user_agent'):
                score += 1
            if details.get('off_hours_access'):
                score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _get_location_info(self, ip_address: str) -> Dict[str, Any]:
        """Get location information for IP address"""
        if not self.geoip_reader:
            return {}
        
        try:
            response = self.geoip_reader.city(ip_address)
            return {
                'country': response.country.name,
                'city': response.city.name,
                'latitude': float(response.location.latitude) if response.location.latitude else None,
                'longitude': float(response.location.longitude) if response.location.longitude else None
            }
        except Exception:
            return {}
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP address is suspicious"""
        # Check against known malicious IP lists
        # This would integrate with threat intelligence feeds
        
        # For now, check for common suspicious patterns
        suspicious_patterns = [
            '10.0.0.',  # Internal networks from external
            '192.168.',  # Private networks
            '172.16.',   # Private networks
        ]
        
        # In production, you'd check against:
        # - Tor exit nodes
        # - Known malicious IPs
        # - VPN/Proxy services
        # - Geolocation anomalies
        
        return any(ip_address.startswith(pattern) for pattern in suspicious_patterns)
    
    def _is_unusual_location(self, ip_address: str) -> bool:
        """Check if location is unusual for user"""
        # This would check against user's typical locations
        # For now, return False
        return False
    
    def detect_anomalies(self, user_id: int, time_window_hours: int = 24) -> List[Dict[str, Any]]:
        """Detect anomalous behavior patterns"""
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Query recent events for user
        recent_events = self.db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff_time
        ).all()
        
        anomalies = []
        
        # Check for rapid successive logins
        login_events = [e for e in recent_events if e.event_type == AuditEventType.LOGIN_SUCCESS.value]
        if len(login_events) > 10:  # More than 10 logins in time window
            anomalies.append({
                'type': 'excessive_logins',
                'count': len(login_events),
                'severity': 'medium'
            })
        
        # Check for failed login patterns
        failed_logins = [e for e in recent_events if e.event_type == AuditEventType.LOGIN_FAILED.value]
        if len(failed_logins) > 5:
            anomalies.append({
                'type': 'multiple_failed_logins',
                'count': len(failed_logins),
                'severity': 'high'
            })
        
        # Check for unusual IP addresses
        unique_ips = set(e.ip_address for e in recent_events if e.ip_address)
        if len(unique_ips) > 5:
            anomalies.append({
                'type': 'multiple_ip_addresses',
                'count': len(unique_ips),
                'severity': 'medium'
            })
        
        return anomalies
    
    def generate_security_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate security summary report"""
        from datetime import timedelta
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        # Query events in time period
        events = self.db.query(AuditLog).filter(
            AuditLog.timestamp >= cutoff_time
        ).all()
        
        # Aggregate statistics
        total_events = len(events)
        failed_logins = len([e for e in events if e.event_type == AuditEventType.LOGIN_FAILED.value])
        high_risk_events = len([e for e in events if e.risk_score >= 7])
        unique_users = len(set(e.user_id for e in events if e.user_id))
        unique_ips = len(set(e.ip_address for e in events if e.ip_address))
        
        return {
            'period_days': days,
            'total_events': total_events,
            'failed_logins': failed_logins,
            'high_risk_events': high_risk_events,
            'unique_users': unique_users,
            'unique_ips': unique_ips,
            'security_score': max(0, 100 - (failed_logins * 2) - (high_risk_events * 5))
        }
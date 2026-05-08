from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import bcrypt
import enum

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    FREE = "free"
    DEVELOPER = "developer"
    ELITE = "elite"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    
    # Subscription Management
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE)
    subscription_expires = Column(DateTime)
    subscription_active = Column(Boolean, default=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    models = relationship("MLModel", back_populates="owner")
    projects = relationship("Project", back_populates="owner")
    payments = relationship("Payment", back_populates="user")
    
    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @property
    def tier_limits(self):
        limits = {
            SubscriptionTier.FREE: {
                'max_models': 3,
                'max_storage_gb': 1.0,
                'max_compute_hours': 5,
                'features': ['basic_training', 'model_upload']
            },
            SubscriptionTier.DEVELOPER: {
                'max_models': 15,
                'max_storage_gb': 25.0,
                'max_compute_hours': 100,
                'features': ['automl', 'advanced_monitoring', 'api_access', 'collaboration']
            },
            SubscriptionTier.ELITE: {
                'max_models': 100,
                'max_storage_gb': 500.0,
                'max_compute_hours': 1000,
                'features': ['all_features', 'priority_support', 'custom_deployment', 'white_label']
            }
        }
        return limits.get(self.subscription_tier, limits[SubscriptionTier.FREE])
    
    def can_create_model(self):
        current_models = len(self.models)
        return current_models < self.tier_limits['max_models']
    
    def has_feature(self, feature: str):
        return feature in self.tier_limits['features'] or 'all_features' in self.tier_limits['features']

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    model_type = Column(String(50))  # classification, regression, clustering
    framework = Column(String(50))   # sklearn, tensorflow, pytorch
    version = Column(String(20), default="1.0.0")
    status = Column(String(20), default="training")  # training, deployed, stopped
    accuracy = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    # Relationships
    owner = relationship("User", back_populates="models")
    project = relationship("Project", back_populates="models")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    models = relationship("MLModel", back_populates="project")

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_token = Column(String(255), unique=True, index=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    tier = Column(Enum(SubscriptionTier))
    duration_months = Column(Integer)  # 3 for developer, 12 for elite
    payment_method = Column(String(50))  # stripe, paypal, etc
    transaction_id = Column(String(255), unique=True)
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="payments")

class FeatureUsage(Base):
    __tablename__ = "feature_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    feature_name = Column(String(100))
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, default=datetime.utcnow)
    month_year = Column(String(7))  # "2024-01" format for monthly tracking
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from .models import Base

# Database URL - supports PostgreSQL, SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://zipit_user:zipit_pass@localhost:5432/zipit_db"
)

# For development, fallback to SQLite
if "postgresql" not in DATABASE_URL and not os.path.exists("data"):
    os.makedirs("data", exist_ok=True)
    DATABASE_URL = "sqlite:///./data/zipit.db"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_admin_user():
    """Initialize admin user if not exists"""
    from .models import User, SubscriptionTier
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@zipit.com",
                hashed_password=User.hash_password("zip@2604"),
                full_name="ZipIt Administrator",
                subscription_tier=SubscriptionTier.ELITE,
                subscription_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ Admin user created: admin / zip@2604")
    finally:
        db.close()
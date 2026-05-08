#!/usr/bin/env python3
"""
ZipIt Database Initialization Script
Creates tables and sets up admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.database import create_tables, init_admin_user, engine
from src.database.models import Base

def main():
    print("🗄️  Initializing ZipIt Database...")
    
    try:
        # Create all tables
        print("📋 Creating database tables...")
        create_tables()
        print("✅ Tables created successfully")
        
        # Initialize admin user
        print("👤 Setting up admin user...")
        init_admin_user()
        print("✅ Admin user initialized")
        
        print("🎉 Database initialization complete!")
        print("📊 Admin Login: admin / zip@2604")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
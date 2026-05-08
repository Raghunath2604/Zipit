import json
import bcrypt
from datetime import datetime
import os

class UserManager:
    """Manage users and their model access"""
    
    def __init__(self, users_file="users.json"):
        self.users_file = users_file
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {"users": {}}
    
    def save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def hash_password(self, password):
        """Hash password with bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def add_user(self, username, email, name, password, aws_account, models=None):
        """Add new user"""
        if models is None:
            models = []
        
        if username in self.users["users"]:
            return False, "User already exists"
        
        self.users["users"][username] = {
            "email": email,
            "name": name,
            "password": self.hash_password(password),
            "aws_account": aws_account,
            "models": models,
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        self.save_users()
        return True, "User created successfully"
    
    def add_model_to_user(self, username, model_name):
        """Add model to user's monitoring list"""
        if username not in self.users["users"]:
            return False, "User not found"
        
        if model_name not in self.users["users"][username]["models"]:
            self.users["users"][username]["models"].append(model_name)
            self.save_users()
            return True, f"Model {model_name} added"
        
        return False, "Model already exists"

def setup_demo_users():
    """Setup demo users"""
    user_manager = UserManager()
    
    user_manager.add_user(
        username="demo_user",
        email="demo@company.com", 
        name="Demo User",
        password="demo123",
        aws_account="123456789012",
        models=["fraud-detection-v1", "churn-prediction-v2"]
    )
    
    user_manager.add_user(
        username="john_doe",
        email="john@company.com",
        name="John Doe", 
        password="demo123",
        aws_account="987654321098",
        models=["recommendation-engine", "price-optimizer"]
    )
    
    print("✅ Demo users created")

if __name__ == "__main__":
    setup_demo_users()
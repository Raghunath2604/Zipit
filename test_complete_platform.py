#!/usr/bin/env python3
"""
Comprehensive MLOps Platform Test Suite
Tests all routes, visualization, and deployment functionality
"""

import requests
import json
import time
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
import joblib
import os

# Configuration
BASE_URL = "http://localhost:8002"
API_BASE = f"{BASE_URL}/api"

class MLOpsPlatformTester:
    def __init__(self):
        self.token = None
        self.api_key = None
        self.user_id = None
        self.model_name = "test-fraud-detector"
        
    def test_user_registration(self):
        """Test user registration"""
        print("🔐 Testing user registration...")
        
        user_data = {
            "username": "test_user_" + str(int(time.time())),
            "email": f"test_{int(time.time())}@example.com",
            "full_name": "Test User",
            "password": "test_password_123"
        }
        
        response = requests.post(f"{API_BASE}/users/register", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.api_key = data["api_key"]
            self.user_id = data["user_id"]
            print(f"✅ User registered successfully! User ID: {self.user_id}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    
    def test_user_login(self):
        """Test user login"""
        print("🔑 Testing user login...")
        
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        
        response = requests.post(f"{API_BASE}/users/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print(f"⚠️ Login failed (expected for new user): {response.text}")
            return False
    
    def test_model_registration(self):
        """Test model registration"""
        print("🤖 Testing model registration...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        model_data = {
            "model_name": self.model_name,
            "model_type": "classification",
            "framework": "sklearn",
            "deployment_platform": "local"
        }
        
        response = requests.post(f"{API_BASE}/models/register", json=model_data, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Model '{self.model_name}' registered successfully!")
            return True
        else:
            print(f"❌ Model registration failed: {response.text}")
            return False
    
    def create_and_upload_model(self):
        """Create a sample model and upload it"""
        print("📁 Creating and uploading sample model...")
        
        # Create sample model
        X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        # Save model
        model_path = f"test_{self.model_name}.joblib"
        joblib.dump(model, model_path)
        
        # Upload model
        headers = {"Authorization": f"Bearer {self.token}"}
        
        with open(model_path, 'rb') as f:
            files = {'file': (model_path, f, 'application/octet-stream')}
            response = requests.post(f"{API_BASE}/models/{self.model_name}/upload", 
                                   files=files, headers=headers)
        
        # Clean up
        os.remove(model_path)
        
        if response.status_code == 200:
            print("✅ Model uploaded successfully!")
            return True
        else:
            print(f"❌ Model upload failed: {response.text}")
            return False
    
    def test_model_deployment(self):
        """Test model deployment"""
        print("🚀 Testing model deployment...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(f"{API_BASE}/models/{self.model_name}/deploy", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Model deployed successfully! URL: {data['deployment_url']}")
            return True
        else:
            print(f"❌ Model deployment failed: {response.text}")
            return False
    
    def test_model_prediction(self):
        """Test model prediction"""
        print("🎯 Testing model prediction...")
        
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Test prediction with sample features
        features = {
            "feature_0": 1.5,
            "feature_1": -0.8,
            "feature_2": 2.1,
            "feature_3": 0.3,
            "feature_4": -1.2,
            "feature_5": 0.9,
            "feature_6": 1.8,
            "feature_7": -0.5,
            "feature_8": 0.7,
            "feature_9": 1.1
        }
        
        response = requests.post(f"{API_BASE}/models/{self.model_name}/predict", 
                               json=features, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful! Result: {data['prediction']}")
            return True
        else:
            print(f"❌ Prediction failed: {response.text}")
            return False
    
    def test_prediction_logging(self):
        """Test prediction logging"""
        print("📊 Testing prediction logging...")
        
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Generate sample predictions
        predictions_data = {
            "model_name": self.model_name,
            "predictions": [0.8, 0.3, 0.9, 0.1, 0.7],
            "features": [
                {"feature_0": 1.5, "feature_1": -0.8},
                {"feature_0": 0.3, "feature_1": 1.2},
                {"feature_0": 2.1, "feature_1": -1.5},
                {"feature_0": -0.5, "feature_1": 0.9},
                {"feature_0": 1.8, "feature_1": 0.2}
            ],
            "actuals": [1, 0, 1, 0, 1]
        }
        
        response = requests.post(f"{API_BASE}/models/{self.model_name}/predictions", 
                               json=predictions_data, headers=headers)
        
        if response.status_code == 200:
            print("✅ Predictions logged successfully!")
            return True
        else:
            print(f"❌ Prediction logging failed: {response.text}")
            return False
    
    def test_drift_detection(self):
        """Test drift detection"""
        print("🔍 Testing drift detection...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/models/{self.model_name}/drift", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Drift detection successful! Drift detected: {data.get('drift_detected', 'N/A')}")
            return True
        else:
            print(f"❌ Drift detection failed: {response.text}")
            return False
    
    def test_metrics_calculation(self):
        """Test metrics calculation"""
        print("📈 Testing metrics calculation...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/models/{self.model_name}/metrics", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Metrics calculated successfully! Accuracy: {data.get('accuracy', 'N/A')}")
            return True
        else:
            print(f"❌ Metrics calculation failed: {response.text}")
            return False
    
    def test_dashboard_data(self):
        """Test dashboard data retrieval"""
        print("📊 Testing dashboard data...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/dashboard/{self.model_name}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data retrieved successfully! Model: {data['model_info']['name']}")
            return True
        else:
            print(f"❌ Dashboard data retrieval failed: {response.text}")
            return False
    
    def test_visualization_data(self):
        """Test visualization data retrieval"""
        print("📊 Testing visualization data...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/models/{self.model_name}/visualize", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Visualization data retrieved successfully! Predictions: {len(data['predictions'])}")
            return True
        else:
            print(f"❌ Visualization data retrieval failed: {response.text}")
            return False
    
    def test_user_models(self):
        """Test user models listing"""
        print("📋 Testing user models listing...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(f"{API_BASE}/user/models", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User models retrieved successfully! Count: {len(data)}")
            return True
        else:
            print(f"❌ User models retrieval failed: {response.text}")
            return False
    
    def test_web_interfaces(self):
        """Test web interface accessibility"""
        print("🌐 Testing web interfaces...")
        
        # Test home page
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("✅ Home page accessible!")
        else:
            print(f"❌ Home page failed: {response.status_code}")
        
        # Test dashboard page
        response = requests.get(f"{BASE_URL}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard page accessible!")
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
        
        # Test model visualization page
        response = requests.get(f"{BASE_URL}/models/{self.model_name}/visualize")
        if response.status_code == 200:
            print("✅ Model visualization page accessible!")
            return True
        else:
            print(f"❌ Model visualization page failed: {response.status_code}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting MLOps Platform Comprehensive Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_user_registration,
            self.test_model_registration,
            self.create_and_upload_model,
            self.test_model_deployment,
            self.test_model_prediction,
            self.test_prediction_logging,
            self.test_drift_detection,
            self.test_metrics_calculation,
            self.test_dashboard_data,
            self.test_visualization_data,
            self.test_user_models,
            self.test_web_interfaces
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
            print("-" * 40)
        
        print(f"\n🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Platform is working correctly.")
        else:
            print(f"⚠️ {total - passed} tests failed. Check the logs above.")
        
        return passed == total

def main():
    """Main test function"""
    print("MLOps Platform - Comprehensive Test Suite")
    print("Make sure the platform is running on http://localhost:8002")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running!")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the platform first:")
        print("   python mlops_platform.py")
        return False
    
    # Run tests
    tester = MLOpsPlatformTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
#!/usr/bin/env python3
"""
Open Source MLOps Monitoring Platform - User Example
Shows how any user can login and monitor their own ML models
"""

import requests
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from mlops_connector import MLOpsConnector

def register_user():
    """User registers on the platform"""
    print("👤 Registering on MLOps Platform...")
    
    user_data = {
        "username": "ml_engineer_john",
        "email": "john@mycompany.com",
        "full_name": "John Smith",
        "password": "mypassword123"
    }
    
    response = requests.post("http://localhost:8002/api/users/register", json=user_data)
    if response.status_code == 200:
        token = response.json()['token']
        print("✅ Successfully registered on platform")
        return token
    else:
        # Try login if already exists
        login_data = {"username": user_data["username"], "password": user_data["password"]}
        response = requests.post("http://localhost:8002/api/users/login", json=login_data)
        if response.status_code == 200:
            token = response.json()['token']
            print("✅ Successfully logged into platform")
            return token
    return None

def monitor_my_model():
    """User monitors their own ML model"""
    print("\n🤖 Monitoring My ML Model")
    print("=" * 40)
    
    # Get platform access
    token = register_user()
    if not token:
        print("❌ Failed to access platform")
        return
    
    # Initialize connector
    connector = MLOpsConnector(token)
    
    # User has their own model (any model they built)
    print("📊 Training my model...")
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # User's model
    my_model = RandomForestClassifier(n_estimators=100, random_state=42)
    my_model.fit(X_train, y_train)
    
    # Register model on platform
    print("📝 Registering my model on platform...")
    connector.register_model(
        model_name="my-customer-model",
        model_type="classification",
        framework="sklearn",
        deployment_platform="aws"
    )
    
    # Make predictions with my model
    predictions = my_model.predict_proba(X_test)[:, 1]
    features = X_test.tolist()
    actuals = y_test.tolist()
    
    # Log predictions to platform
    print("📈 Logging my model predictions...")
    connector.log_predictions("my-customer-model", predictions.tolist(), features, actuals)
    
    # Check my model performance
    print("📊 Checking my model metrics...")
    metrics = connector.get_metrics("my-customer-model")
    print(f"   Accuracy: {metrics.get('accuracy', 0):.3f}")
    print(f"   Precision: {metrics.get('precision', 0):.3f}")
    print(f"   Recall: {metrics.get('recall', 0):.3f}")
    print(f"   F1-Score: {metrics.get('f1_score', 0):.3f}")
    
    # Check for drift
    print("🔍 Checking for drift...")
    drift_status = connector.check_drift("my-customer-model")
    if drift_status.get('drift_detected'):
        print(f"   ⚠️ Drift detected: {drift_status.get('severity', 'unknown')} severity")
    else:
        print("   ✅ No drift detected")
    
    # View dashboard
    dashboard_url = connector.get_dashboard_url("my-customer-model")
    print(f"🌐 View my model dashboard: {dashboard_url}")
    
    return "my-customer-model"

def simulate_model_usage(connector, model_name):
    """Simulate ongoing model usage"""
    print(f"\n🔄 Simulating ongoing usage of {model_name}...")
    
    # Simulate new data coming in
    for batch in range(3):
        # Generate new batch of data
        X_new, y_new = make_classification(n_samples=50, n_features=10, n_classes=2, 
                                         random_state=42+batch)
        
        # Simulate model predictions (user's production model)
        predictions = np.random.uniform(0.2, 0.8, 50)  # Simulated predictions
        features = X_new.tolist()
        actuals = y_new.tolist()
        
        # Log to platform
        connector.log_predictions(model_name, predictions.tolist(), features, actuals)
        print(f"   Batch {batch+1}: Logged 50 predictions")
    
    # Check updated metrics
    metrics = connector.get_metrics(model_name)
    print(f"📊 Updated metrics: Accuracy {metrics.get('accuracy', 0):.3f}")

def main():
    """Main example - User monitoring their own model"""
    print("🚀 Open Source MLOps Monitoring Platform")
    print("Monitor Your Own ML Models")
    print("=" * 50)
    
    # User monitors their model
    model_name = monitor_my_model()
    
    if model_name:
        # Get connector for ongoing monitoring
        user_data = {"username": "ml_engineer_john", "password": "mypassword123"}
        response = requests.post("http://localhost:8002/api/users/login", json=user_data)
        token = response.json()['token']
        connector = MLOpsConnector(token)
        
        # Simulate ongoing usage
        simulate_model_usage(connector, model_name)
        
        # Show final dashboard
        print(f"\n🎯 Platform Features Available:")
        print(f"   📊 Real-time metrics (accuracy, precision, recall)")
        print(f"   🔍 Drift detection with alerts")
        print(f"   📈 Performance trends over time")
        print(f"   ⚠️ Error analysis and debugging")
        print(f"   🌐 Professional dashboard")
        
        print(f"\n🌐 Access Your Dashboard:")
        print(f"   Model Dashboard: http://localhost:8002/dashboard?model={model_name}")
        print(f"   Main Dashboard: http://localhost:8002/dashboard")
        
        print(f"\n✅ Your model is now monitored 24/7!")
        print(f"🎉 Get alerts when performance drops or drift occurs")

if __name__ == "__main__":
    main()
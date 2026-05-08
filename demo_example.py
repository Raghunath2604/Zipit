#!/usr/bin/env python3
"""
MLOps Monitoring Platform - Complete Example
Demonstrates monitoring for sklearn, tensorflow, and pytorch models
"""

import numpy as np
import pandas as pd
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import requests
import time
from mlops_connector import MLOpsConnector, FrameworkIntegrations

def create_sample_data():
    """Create sample datasets for demonstration"""
    print("📊 Creating sample datasets...")
    
    # Classification dataset (fraud detection)
    X_class, y_class = make_classification(
        n_samples=1000, n_features=20, n_informative=15, 
        n_redundant=5, n_classes=2, random_state=42
    )
    
    # Regression dataset (price prediction)
    X_reg, y_reg = make_regression(
        n_samples=1000, n_features=15, noise=0.1, random_state=42
    )
    
    return (X_class, y_class), (X_reg, y_reg)

def register_demo_user():
    """Register a demo user and return API key"""
    print("👤 Registering demo user...")
    
    user_data = {
        "username": f"demo_user_{int(time.time())}",
        "email": f"demo_{int(time.time())}@example.com",
        "full_name": "Demo User",
        "password": "demo_password_123"
    }
    
    try:
        response = requests.post("http://localhost:8000/api/users/register", json=user_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User registered successfully!")
            print(f"🔑 API Key: {result['api_key']}")
            return result['api_key']
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("Make sure the MLOps platform is running: python mlops_platform.py")
        return None

def demo_sklearn_classification(connector, X, y):
    """Demonstrate sklearn classification monitoring"""
    print("\n🔬 Demo: Scikit-learn Classification Model")
    print("=" * 50)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Auto-integration with MLOps platform
    result = FrameworkIntegrations.sklearn_integration(
        model=model,
        X_test=X_test,
        y_test=y_test,
        connector=connector,
        model_name="fraud-detector-rf"
    )
    
    print(f"📈 Integration Result: {result}")
    
    # Simulate real-time predictions
    print("\n🔄 Simulating real-time predictions...")
    for i in range(5):
        # Generate new batch of data (simulating production data)
        batch_X = X_test[i*10:(i+1)*10]
        batch_y = y_test[i*10:(i+1)*10]
        
        predictions = model.predict_proba(batch_X)[:, 1].tolist()
        features = batch_X.tolist()
        actuals = batch_y.tolist()
        
        # Log to platform
        connector.log_predictions("fraud-detector-rf", predictions, features, actuals)
        print(f"  Batch {i+1}: Logged {len(predictions)} predictions")
        time.sleep(1)
    
    # Check drift and metrics
    print("\n📊 Checking model performance...")
    metrics = connector.get_metrics("fraud-detector-rf")
    drift = connector.check_drift("fraud-detector-rf")
    
    print(f"📈 Current Metrics: {metrics}")
    print(f"🔍 Drift Status: {drift}")
    
    return "fraud-detector-rf"

def demo_sklearn_regression(connector, X, y):
    """Demonstrate sklearn regression monitoring"""
    print("\n📈 Demo: Scikit-learn Regression Model")
    print("=" * 50)
    
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    
    # Split and scale data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    # Manual registration and monitoring
    connector.register_model("price-predictor", "regression", "sklearn", "local")
    
    # Make predictions
    predictions = model.predict(X_test_scaled).tolist()
    features = X_test_scaled.tolist()
    actuals = y_test.tolist()
    
    # Log predictions
    connector.log_predictions("price-predictor", predictions, features, actuals)
    
    # Get metrics
    metrics = connector.get_metrics("price-predictor")
    print(f"📊 Regression Metrics: {metrics}")
    
    return "price-predictor"

def demo_tensorflow_model(connector):
    """Demonstrate TensorFlow model monitoring"""
    print("\n🧠 Demo: TensorFlow/Keras Model")
    print("=" * 50)
    
    try:
        import tensorflow as tf
        from tensorflow import keras
        
        # Create simple dataset
        X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Build simple neural network
        model = keras.Sequential([
            keras.layers.Dense(64, activation='relu', input_shape=(10,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        
        # Train model (quietly)
        model.fit(X_train, y_train, epochs=10, batch_size=32, verbose=0, validation_split=0.2)
        
        # Auto-integration
        result = FrameworkIntegrations.tensorflow_integration(
            model=model,
            X_test=X_test,
            y_test=y_test,
            connector=connector,
            model_name="neural-classifier"
        )
        
        print(f"🧠 TensorFlow Integration: {result}")
        return "neural-classifier"
        
    except ImportError:
        print("⚠️  TensorFlow not installed. Skipping TensorFlow demo.")
        print("   Install with: pip install tensorflow")
        return None

def demo_pytorch_model(connector):
    """Demonstrate PyTorch model monitoring"""
    print("\n🔥 Demo: PyTorch Model")
    print("=" * 50)
    
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        
        # Create dataset
        X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)
        X_test_tensor = torch.FloatTensor(X_test)
        
        # Simple neural network
        class SimpleNet(nn.Module):
            def __init__(self):
                super(SimpleNet, self).__init__()
                self.fc1 = nn.Linear(10, 64)
                self.fc2 = nn.Linear(64, 32)
                self.fc3 = nn.Linear(32, 1)
                self.relu = nn.ReLU()
                self.sigmoid = nn.Sigmoid()
                
            def forward(self, x):
                x = self.relu(self.fc1(x))
                x = self.relu(self.fc2(x))
                x = self.sigmoid(self.fc3(x))
                return x
        
        # Train model
        model = SimpleNet()
        criterion = nn.BCELoss()
        optimizer = optim.Adam(model.parameters())
        
        # Quick training
        for epoch in range(50):
            optimizer.zero_grad()
            outputs = model(X_train_tensor)
            loss = criterion(outputs, y_train_tensor)
            loss.backward()
            optimizer.step()
        
        # Auto-integration
        result = FrameworkIntegrations.pytorch_integration(
            model=model,
            X_test=X_test_tensor,
            y_test=y_test,
            connector=connector,
            model_name="pytorch-classifier"
        )
        
        print(f"🔥 PyTorch Integration: {result}")
        return "pytorch-classifier"
        
    except ImportError:
        print("⚠️  PyTorch not installed. Skipping PyTorch demo.")
        print("   Install with: pip install torch")
        return None

def demo_drift_simulation(connector, model_name):
    """Simulate data drift and show detection"""
    print(f"\n🔍 Demo: Drift Detection for {model_name}")
    print("=" * 50)
    
    # Generate drifted data (different distribution)
    X_drift, _ = make_classification(
        n_samples=100, n_features=20, n_informative=10,
        n_redundant=10, n_classes=2, random_state=999  # Different seed
    )
    
    # Simulate predictions on drifted data
    fake_predictions = np.random.uniform(0.3, 0.8, 100).tolist()  # Different distribution
    features = X_drift.tolist()
    
    print("📊 Logging drifted predictions...")
    connector.log_predictions(model_name, fake_predictions, features)
    
    # Check for drift
    time.sleep(2)  # Wait a moment
    drift_result = connector.check_drift(model_name)
    
    print(f"🔍 Drift Detection Result: {drift_result}")
    
    if drift_result.get('drift_detected'):
        print("⚠️  Drift detected! Model may need retraining.")
    else:
        print("✅ No significant drift detected.")

def show_dashboard_info(connector, model_names):
    """Show dashboard information"""
    print("\n📊 Dashboard Information")
    print("=" * 50)
    
    print("🌐 Access your models at:")
    for model_name in model_names:
        if model_name:
            dashboard_url = connector.get_dashboard_url(model_name)
            print(f"  • {model_name}: {dashboard_url}")
    
    print(f"\n🏠 Main Dashboard: http://localhost:8000/dashboard")
    print(f"🏡 Home Page: http://localhost:8000/")
    
    # Show summary data
    print("\n📈 Model Summary:")
    models = connector.list_models()
    for model in models:
        print(f"  • {model['name']} ({model['framework']}) - {model['total_predictions']} predictions")

def main():
    """Main demo function"""
    print("🚀 MLOps Monitoring Platform - Complete Demo")
    print("=" * 60)
    
    # Register user
    api_key = register_demo_user()
    if not api_key:
        return
    
    # Initialize connector
    connector = MLOpsConnector(api_key)
    
    # Create sample data
    (X_class, y_class), (X_reg, y_reg) = create_sample_data()
    
    # Demo different frameworks
    model_names = []
    
    # Sklearn classification
    model_name = demo_sklearn_classification(connector, X_class, y_class)
    model_names.append(model_name)
    
    # Sklearn regression
    model_name = demo_sklearn_regression(connector, X_reg, y_reg)
    model_names.append(model_name)
    
    # TensorFlow (if available)
    model_name = demo_tensorflow_model(connector)
    model_names.append(model_name)
    
    # PyTorch (if available)
    model_name = demo_pytorch_model(connector)
    model_names.append(model_name)
    
    # Drift simulation
    if model_names[0]:  # Use first model for drift demo
        demo_drift_simulation(connector, model_names[0])
    
    # Show dashboard info
    show_dashboard_info(connector, model_names)
    
    print("\n✅ Demo completed successfully!")
    print("🎉 Your models are now being monitored in real-time!")
    print("\n💡 Next steps:")
    print("   1. Open the dashboard in your browser")
    print("   2. Explore the monitoring features")
    print("   3. Integrate with your production models")
    print("   4. Set up alerts and notifications")

if __name__ == "__main__":
    main()
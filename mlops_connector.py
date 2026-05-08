#!/usr/bin/env python3
"""
MLOps Connector - Python SDK for Open Source MLOps Monitoring Platform
Easy integration for any ML framework
"""

import requests
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
import warnings

class MLOpsConnector:
    """
    Universal ML model monitoring connector
    Works with any ML framework - sklearn, tensorflow, pytorch, xgboost, etc.
    """
    
    def __init__(self, api_key: str, base_url: str = "http://localhost:8002"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def register_model(self, model_name: str, model_type: str, framework: str, deployment_platform: str = "local") -> Dict:
        """
        Register a new ML model for monitoring
        
        Args:
            model_name: Unique name for your model
            model_type: 'classification', 'regression', or 'ranking'
            framework: 'sklearn', 'tensorflow', 'pytorch', 'xgboost', etc.
            deployment_platform: 'aws', 'gcp', 'azure', 'kubernetes', 'local'
        """
        data = {
            "model_name": model_name,
            "model_type": model_type,
            "framework": framework,
            "deployment_platform": deployment_platform
        }
        
        response = requests.post(f"{self.base_url}/api/models/register", json=data, headers=self.headers)
        
        if response.status_code == 200:
            print(f"✅ Model '{model_name}' registered successfully!")
            return response.json()
        else:
            print(f"❌ Failed to register model: {response.text}")
            return {"error": response.text}
    
    def log_predictions(self, model_name: str, predictions: List[float], features: List[List[float]], actuals: Optional[List[float]] = None) -> Dict:
        """
        Log model predictions for monitoring
        
        Args:
            model_name: Name of the registered model
            predictions: List of model predictions
            features: List of feature vectors used for predictions
            actuals: Optional list of actual/true values (for performance calculation)
        """
        data = {
            "model_name": model_name,
            "predictions": predictions,
            "features": features,
            "actuals": actuals
        }
        
        response = requests.post(f"{self.base_url}/api/models/{model_name}/predictions", json=data, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to log predictions: {response.text}")
            return {"error": response.text}
    
    def check_drift(self, model_name: str) -> Dict:
        """
        Check for data/concept drift in model predictions
        
        Args:
            model_name: Name of the registered model
            
        Returns:
            Dict with drift detection results
        """
        response = requests.get(f"{self.base_url}/api/models/{model_name}/drift", headers=self.headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("drift_detected"):
                severity = result.get("severity", "unknown")
                print(f"⚠️  Drift detected for '{model_name}' - Severity: {severity}")
            else:
                print(f"✅ No drift detected for '{model_name}'")
            return result
        else:
            print(f"❌ Failed to check drift: {response.text}")
            return {"error": response.text}
    
    def get_metrics(self, model_name: str) -> Dict:
        """
        Get current performance metrics for the model
        
        Args:
            model_name: Name of the registered model
            
        Returns:
            Dict with performance metrics
        """
        response = requests.get(f"{self.base_url}/api/models/{model_name}/metrics", headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get metrics: {response.text}")
            return {"error": response.text}
    
    def get_dashboard_url(self, model_name: str) -> str:
        """Get the dashboard URL for the model"""
        return f"{self.base_url}/dashboard?model={model_name}"
    
    def get_dashboard_data(self, model_name: str) -> Dict:
        """
        Get comprehensive dashboard data for the model
        
        Args:
            model_name: Name of the registered model
            
        Returns:
            Dict with dashboard data including metrics, drift status, etc.
        """
        response = requests.get(f"{self.base_url}/api/dashboard/{model_name}", headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get dashboard data: {response.text}")
            return {"error": response.text}
    
    def list_models(self) -> List[Dict]:
        """Get list of all registered models for the user"""
        response = requests.get(f"{self.base_url}/api/user/models", headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get models: {response.text}")
            return []


class FrameworkIntegrations:
    """
    Pre-built integrations for popular ML frameworks
    """
    
    @staticmethod
    def sklearn_integration(model, X_test, y_test, connector: MLOpsConnector, model_name: str) -> Dict:
        """
        Auto-integration for scikit-learn models
        
        Args:
            model: Trained sklearn model
            X_test: Test features
            y_test: Test labels
            connector: MLOpsConnector instance
            model_name: Name for the model
        """
        try:
            # Make predictions
            if hasattr(model, 'predict_proba'):
                predictions = model.predict_proba(X_test)[:, 1].tolist()  # Binary classification
            else:
                predictions = model.predict(X_test).tolist()
            
            # Convert features to list
            features = X_test.tolist() if hasattr(X_test, 'tolist') else X_test
            actuals = y_test.tolist() if hasattr(y_test, 'tolist') else y_test
            
            # Determine model type
            model_type = "classification" if hasattr(model, 'predict_proba') else "regression"
            
            # Register model
            connector.register_model(model_name, model_type, "sklearn")
            
            # Log predictions
            result = connector.log_predictions(model_name, predictions, features, actuals)
            
            # Get metrics
            metrics = connector.get_metrics(model_name)
            
            print(f"✅ sklearn model '{model_name}' integrated successfully!")
            print(f"📊 Dashboard: {connector.get_dashboard_url(model_name)}")
            
            return {"status": "success", "metrics": metrics, "predictions_logged": len(predictions)}
            
        except Exception as e:
            print(f"❌ sklearn integration failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def tensorflow_integration(model, X_test, y_test, connector: MLOpsConnector, model_name: str) -> Dict:
        """
        Auto-integration for TensorFlow/Keras models
        """
        try:
            import tensorflow as tf
            
            # Make predictions
            predictions = model.predict(X_test)
            
            # Handle different output shapes
            if len(predictions.shape) > 1 and predictions.shape[1] > 1:
                predictions = predictions[:, 1].tolist()  # Binary classification
            else:
                predictions = predictions.flatten().tolist()
            
            # Convert to lists
            features = X_test.tolist() if hasattr(X_test, 'tolist') else X_test
            actuals = y_test.tolist() if hasattr(y_test, 'tolist') else y_test
            
            # Determine model type (simplified)
            model_type = "classification" if len(set(actuals)) <= 10 else "regression"
            
            # Register and log
            connector.register_model(model_name, model_type, "tensorflow")
            result = connector.log_predictions(model_name, predictions, features, actuals)
            metrics = connector.get_metrics(model_name)
            
            print(f"✅ TensorFlow model '{model_name}' integrated successfully!")
            print(f"📊 Dashboard: {connector.get_dashboard_url(model_name)}")
            
            return {"status": "success", "metrics": metrics, "predictions_logged": len(predictions)}
            
        except Exception as e:
            print(f"❌ TensorFlow integration failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def pytorch_integration(model, X_test, y_test, connector: MLOpsConnector, model_name: str) -> Dict:
        """
        Auto-integration for PyTorch models
        """
        try:
            import torch
            
            model.eval()
            with torch.no_grad():
                if isinstance(X_test, np.ndarray):
                    X_test = torch.FloatTensor(X_test)
                
                predictions = model(X_test)
                
                # Handle different output types
                if hasattr(predictions, 'numpy'):
                    predictions = predictions.numpy()
                
                if len(predictions.shape) > 1 and predictions.shape[1] > 1:
                    predictions = predictions[:, 1].tolist()  # Binary classification
                else:
                    predictions = predictions.flatten().tolist()
            
            # Convert to lists
            features = X_test.numpy().tolist() if hasattr(X_test, 'numpy') else X_test.tolist()
            actuals = y_test.tolist() if hasattr(y_test, 'tolist') else y_test
            
            # Determine model type
            model_type = "classification" if len(set(actuals)) <= 10 else "regression"
            
            # Register and log
            connector.register_model(model_name, model_type, "pytorch")
            result = connector.log_predictions(model_name, predictions, features, actuals)
            metrics = connector.get_metrics(model_name)
            
            print(f"✅ PyTorch model '{model_name}' integrated successfully!")
            print(f"📊 Dashboard: {connector.get_dashboard_url(model_name)}")
            
            return {"status": "success", "metrics": metrics, "predictions_logged": len(predictions)}
            
        except Exception as e:
            print(f"❌ PyTorch integration failed: {str(e)}")
            return {"status": "error", "message": str(e)}


# Example usage
if __name__ == "__main__":
    # Example: Register user and get API key
    print("🚀 MLOps Monitoring Platform - Python SDK")
    print("=" * 50)
    
    # Register new user (one-time)
    register_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "full_name": "Demo User",
        "password": "demo_password"
    }
    
    response = requests.post("http://localhost:8002/api/users/register", json=register_data)
    if response.status_code == 200:
        api_key = response.json()["api_key"]
        print(f"✅ User registered! API Key: {api_key}")
        
        # Initialize connector
        connector = MLOpsConnector(api_key)
        
        # Example: Register a model
        connector.register_model("demo-fraud-detector", "classification", "sklearn", "aws")
        
        # Example: Log some predictions
        sample_predictions = [0.8, 0.2, 0.9, 0.1, 0.7]
        sample_features = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]
        sample_actuals = [1, 0, 1, 0, 1]
        
        connector.log_predictions("demo-fraud-detector", sample_predictions, sample_features, sample_actuals)
        
        # Check metrics and drift
        metrics = connector.get_metrics("demo-fraud-detector")
        drift = connector.check_drift("demo-fraud-detector")
        
        print(f"📊 Metrics: {metrics}")
        print(f"🔍 Drift Status: {drift}")
        print(f"🌐 Dashboard: {connector.get_dashboard_url('demo-fraud-detector')}")
        
    else:
        print(f"❌ Registration failed: {response.text}")
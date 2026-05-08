#!/usr/bin/env python3
"""
Real-World Production Integration Examples
Shows how to integrate MLOps monitoring with existing production systems
"""

import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import threading
from mlops_connector import MLOpsConnector

class ProductionFraudDetectionService:
    """Real fraud detection service with MLOps monitoring"""
    
    def __init__(self, mlops_token):
        self.connector = MLOpsConnector(mlops_token)
        self.model_name = "production-fraud-detector"
        
        # Register model
        self.connector.register_model(
            model_name=self.model_name,
            model_type="classification",
            framework="sklearn",
            deployment_platform="aws"
        )
        print(f"✅ Fraud detection service initialized with MLOps monitoring")
    
    def process_transaction(self, transaction_data):
        """Process a single transaction and detect fraud"""
        # Simulate fraud detection logic
        features = [
            transaction_data['amount'],
            transaction_data['merchant_category'],
            transaction_data['hour_of_day'],
            transaction_data['day_of_week'],
            transaction_data['user_age'],
            transaction_data['account_balance']
        ]
        
        # Simulate model prediction (in real system, this would be your trained model)
        fraud_score = self._calculate_fraud_score(features)
        
        # Log prediction to MLOps platform
        self.connector.log_predictions(
            self.model_name, 
            [float(fraud_score)], 
            [list(map(float, features))],
            [int(transaction_data.get('is_fraud', 0))] if transaction_data.get('is_fraud') is not None else None
        )
        
        return {
            'transaction_id': transaction_data['transaction_id'],
            'fraud_score': fraud_score,
            'is_fraud': fraud_score > 0.5,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_fraud_score(self, features):
        """Simulate fraud score calculation"""
        # Simple heuristic-based fraud detection
        amount, merchant_cat, hour, day, age, balance = features
        
        score = 0.1  # base score
        
        # High amount transactions
        if amount > 1000:
            score += 0.3
        
        # Unusual hours (late night/early morning)
        if hour < 6 or hour > 22:
            score += 0.2
        
        # High-risk merchant categories
        if merchant_cat in [7995, 5993, 5912]:  # gambling, cigar stores, drug stores
            score += 0.25
        
        # Young users with high amounts
        if age < 25 and amount > 500:
            score += 0.15
        
        # Low balance with high transaction
        if balance < amount * 2:
            score += 0.2
        
        return min(score + np.random.normal(0, 0.1), 1.0)
    
    def check_model_health(self):
        """Check model health and drift"""
        drift_status = self.connector.check_drift(self.model_name)
        metrics = self.connector.get_metrics(self.model_name)
        
        return {
            'drift_detected': drift_status.get('drift_detected', False),
            'drift_severity': drift_status.get('severity', 'unknown'),
            'current_metrics': metrics
        }

class ProductionRecommendationService:
    """Real recommendation service with MLOps monitoring"""
    
    def __init__(self, mlops_token):
        self.connector = MLOpsConnector(mlops_token)
        self.model_name = "production-recommender"
        
        # Register model
        self.connector.register_model(
            model_name=self.model_name,
            model_type="ranking",
            framework="tensorflow",
            deployment_platform="gcp"
        )
        print(f"✅ Recommendation service initialized with MLOps monitoring")
    
    def get_recommendations(self, user_data, num_recommendations=5):
        """Get product recommendations for user"""
        features = [
            user_data['age'],
            user_data['gender'],
            user_data['location_code'],
            user_data['purchase_history_length'],
            user_data['avg_order_value'],
            user_data['days_since_last_purchase']
        ]
        
        # Simulate recommendation scores
        recommendations = []
        recommendation_scores = []
        
        for i in range(num_recommendations):
            product_id = f"product_{np.random.randint(1000, 9999)}"
            score = self._calculate_recommendation_score(features, i)
            
            recommendations.append(product_id)
            recommendation_scores.append(score)
        
        # Log to MLOps platform
        self.connector.log_predictions(
            self.model_name,
            list(map(float, recommendation_scores)),
            [list(map(float, features))] * num_recommendations
        )
        
        return {
            'user_id': user_data['user_id'],
            'recommendations': list(zip(recommendations, recommendation_scores)),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_recommendation_score(self, user_features, item_index):
        """Simulate recommendation score calculation"""
        age, gender, location, history_len, avg_order, days_since = user_features
        
        # Base score with some randomness
        score = 0.5 + np.random.normal(0, 0.1)
        
        # Adjust based on user characteristics
        if age > 30:
            score += 0.1
        if history_len > 10:
            score += 0.15
        if days_since < 7:
            score += 0.1
        
        return max(0, min(1, score))

class ProductionModelMonitor:
    """Production monitoring service that runs continuously"""
    
    def __init__(self, mlops_token):
        self.connector = MLOpsConnector(mlops_token)
        self.monitoring_active = True
        
    def start_monitoring(self, model_names, check_interval=300):  # 5 minutes
        """Start continuous monitoring of production models"""
        print(f"🔄 Starting continuous monitoring for {len(model_names)} models")
        
        def monitor_loop():
            while self.monitoring_active:
                for model_name in model_names:
                    try:
                        # Check drift
                        drift_status = self.connector.check_drift(model_name)
                        
                        # Check metrics
                        metrics = self.connector.get_metrics(model_name)
                        
                        # Get dashboard data
                        dashboard_data = self.connector.get_dashboard_data(model_name)
                        
                        # Alert if issues detected
                        if drift_status.get('drift_detected'):
                            self._send_alert(model_name, 'drift', drift_status)
                        
                        if metrics.get('accuracy', 1.0) < 0.8:  # Accuracy threshold
                            self._send_alert(model_name, 'performance', metrics)
                        
                        print(f"✅ {model_name}: Health check completed")
                        
                    except Exception as e:
                        print(f"❌ {model_name}: Monitoring error - {e}")
                
                time.sleep(check_interval)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def _send_alert(self, model_name, alert_type, data):
        """Send alert for model issues"""
        alert = {
            'model': model_name,
            'type': alert_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        print(f"🚨 ALERT: {alert_type.upper()} detected in {model_name}")
        print(f"   Details: {data}")
        
        # In production, send to Slack, email, PagerDuty, etc.
        # self._send_to_slack(alert)
        # self._send_email_alert(alert)
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        print("🛑 Monitoring stopped")

def simulate_production_traffic(fraud_service, recommendation_service, duration_minutes=5):
    """Simulate real production traffic"""
    print(f"🚀 Simulating production traffic for {duration_minutes} minutes...")
    
    start_time = time.time()
    transaction_count = 0
    recommendation_count = 0
    
    while time.time() - start_time < duration_minutes * 60:
        # Simulate fraud detection requests
        if np.random.random() < 0.7:  # 70% fraud detection traffic
            transaction = {
                'transaction_id': f"txn_{transaction_count:06d}",
                'amount': np.random.exponential(200),
                'merchant_category': np.random.choice([5411, 5812, 5999, 7995, 5993]),
                'hour_of_day': np.random.randint(0, 24),
                'day_of_week': np.random.randint(0, 7),
                'user_age': np.random.randint(18, 80),
                'account_balance': np.random.exponential(5000),
                'is_fraud': np.random.random() < 0.05  # 5% actual fraud rate
            }
            
            result = fraud_service.process_transaction(transaction)
            transaction_count += 1
            
            if transaction_count % 50 == 0:
                print(f"   Processed {transaction_count} transactions")
        
        # Simulate recommendation requests
        if np.random.random() < 0.3:  # 30% recommendation traffic
            user = {
                'user_id': f"user_{recommendation_count:06d}",
                'age': np.random.randint(18, 70),
                'gender': np.random.choice([0, 1]),
                'location_code': np.random.randint(1, 100),
                'purchase_history_length': np.random.randint(0, 50),
                'avg_order_value': np.random.exponential(100),
                'days_since_last_purchase': np.random.randint(0, 365)
            }
            
            recommendations = recommendation_service.get_recommendations(user)
            recommendation_count += 1
            
            if recommendation_count % 20 == 0:
                print(f"   Generated {recommendation_count} recommendation sets")
        
        # Small delay to simulate realistic traffic
        time.sleep(np.random.exponential(0.1))
    
    print(f"✅ Traffic simulation completed:")
    print(f"   Transactions processed: {transaction_count}")
    print(f"   Recommendations generated: {recommendation_count}")

def main():
    """Main production integration example"""
    print("🏭 Real-World Production Integration")
    print("=" * 60)
    
    # Setup production user (reuse from previous example)
    user_data = {
        "username": "production_integration_user",
        "email": "integration@company.com",
        "full_name": "Production Integration User",
        "password": "SecureIntegration2024!"
    }
    
    try:
        response = requests.post("http://localhost:8002/api/users/register", json=user_data)
        if response.status_code == 200:
            token = response.json()['token']
            print("✅ Production integration user registered")
        else:
            # Try to login if user already exists
            login_data = {"username": user_data["username"], "password": user_data["password"]}
            response = requests.post("http://localhost:8002/api/users/login", json=login_data)
            if response.status_code == 200:
                token = response.json()['token']
                print("✅ Production integration user logged in")
            else:
                print(f"❌ User registration/login failed: {response.text}")
                return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Initialize production services
    print("\n🔧 Initializing production services...")
    fraud_service = ProductionFraudDetectionService(token)
    recommendation_service = ProductionRecommendationService(token)
    
    # Start monitoring
    monitor = ProductionModelMonitor(token)
    model_names = ["production-fraud-detector", "production-recommender"]
    monitor_thread = monitor.start_monitoring(model_names, check_interval=30)  # Check every 30 seconds
    
    # Simulate production traffic
    simulate_production_traffic(fraud_service, recommendation_service, duration_minutes=2)
    
    # Check model health
    print("\n📊 Production Model Health Check:")
    fraud_health = fraud_service.check_model_health()
    print(f"Fraud Detection Model:")
    print(f"   Drift Detected: {fraud_health['drift_detected']}")
    print(f"   Current Metrics: {fraud_health['current_metrics']}")
    
    # Show dashboard links
    print(f"\n🌐 Production Dashboards:")
    print(f"   Fraud Detection: http://localhost:8002/dashboard?model=production-fraud-detector")
    print(f"   Recommendations: http://localhost:8002/dashboard?model=production-recommender")
    print(f"   Main Dashboard: http://localhost:8002/dashboard")
    
    # Stop monitoring
    time.sleep(5)  # Let monitoring run for a bit
    monitor.stop_monitoring()
    
    print("\n✅ Production integration example completed!")
    print("🎯 Your production services are now monitored with real-time MLOps")

if __name__ == "__main__":
    main()
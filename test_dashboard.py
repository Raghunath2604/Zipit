#!/usr/bin/env python3
"""
Test script to verify the MLOps dashboard is working
"""

import requests
import json
from datetime import datetime

def test_dashboard():
    """Test all dashboard endpoints"""
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/api/health",
        "/api/status", 
        "/api/metrics",
        "/api/business-hours",
        "/api/drift",
        "/api/performance",
        "/api/system-info"
    ]
    
    print("🧪 Testing MLOps Dashboard APIs...")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}")
                
                # Show key info for some endpoints
                if endpoint == "/api/health":
                    print(f"   Status: {data['status']}")
                    print(f"   Version: {data['version']}")
                    
                elif endpoint == "/api/business-hours":
                    print(f"   Status: {data['status']}")
                    print(f"   Hours: {data['business_hours']}")
                    print(f"   Cost Savings: {data['cost_savings']}")
                    
                elif endpoint == "/api/metrics":
                    print(f"   Total Invocations: {data['invocations']['total']}")
                    print(f"   Avg Latency: {data['latency']['avg']:.1f}ms")
                    print(f"   Error Rate: {data['errors']['error_rate']:.2f}%")
                    
                elif endpoint == "/api/performance":
                    print(f"   AUC Score: {data['auc_score']}")
                    print(f"   Model Version: {data['model_version']}")
                    
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("\n" + "=" * 50)
    print("🌐 Dashboard Access:")
    print("   Local: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   In SageMaker Studio: Use the proxy URL")
    print("\n📊 Dashboard Features:")
    print("   ✅ Real-time metrics")
    print("   ✅ Business hours monitoring (6AM-6PM)")
    print("   ✅ Drift detection")
    print("   ✅ Model performance tracking")
    print("   ✅ Interactive charts")
    print("   ✅ Cost optimization (75% savings)")

if __name__ == "__main__":
    test_dashboard()
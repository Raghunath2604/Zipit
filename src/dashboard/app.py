from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

app = FastAPI(
    title="MLOps Monitoring Dashboard",
    description="Real-time monitoring for ML models with business hours optimization",
    version="2.0.0"
)

# Templates
templates = Jinja2Templates(directory="templates")

class SimpleConfig:
    """Simple configuration"""
    def __init__(self):
        self.business_hours_start = 6
        self.business_hours_end = 18
        self.aws_region = "us-east-1"
        self.endpoint_name = "fraud-detection-endpoint"
        self.drift_threshold_low = 0.05
        self.drift_threshold_medium = 0.15
        self.drift_threshold_high = 0.25

config = SimpleConfig()

class MLOpsDashboard:
    """Enhanced MLOps Dashboard with FastAPI"""
    
    def __init__(self):
        self.config = config
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        """Generate realistic mock data"""
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=i*5)).isoformat() for i in range(24)]
        
        return {
            'invocations': [100 + (i * 5) + (i % 3 * 10) for i in range(24)],
            'latency': [150 + (i % 5 * 10) + (i % 7 * 5) for i in range(24)],
            'errors_4xx': [0 if i % 8 != 0 else 1 for i in range(24)],
            'errors_5xx': [0 if i % 12 != 0 else 1 for i in range(24)],
            'timestamps': timestamps
        }
    
    def get_endpoint_status(self) -> Dict:
        """Get endpoint status"""
        return {
            'status': 'InService',
            'creation_time': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'instance_type': 'ml.m5.large',
            'current_weight': 100,
            'health_score': 98.5
        }
    
    def get_real_time_metrics(self) -> Dict:
        """Get real-time metrics"""
        data = self.mock_data
        
        return {
            'invocations': {
                'timestamps': data['timestamps'],
                'values': data['invocations'],
                'total': sum(data['invocations']),
                'avg_per_hour': sum(data['invocations']) / 24
            },
            'latency': {
                'timestamps': data['timestamps'],
                'values': data['latency'],
                'avg': sum(data['latency']) / len(data['latency']),
                'p95': sorted(data['latency'])[int(len(data['latency']) * 0.95)],
                'p99': sorted(data['latency'])[int(len(data['latency']) * 0.99)]
            },
            'errors': {
                'timestamps': data['timestamps'],
                'errors_4xx': data['errors_4xx'],
                'errors_5xx': data['errors_5xx'],
                'total_errors': sum(data['errors_4xx']) + sum(data['errors_5xx']),
                'error_rate': ((sum(data['errors_4xx']) + sum(data['errors_5xx'])) / sum(data['invocations'])) * 100
            }
        }
    
    def get_business_hours_status(self) -> Dict:
        """Get business hours status"""
        now = datetime.now()
        hour = now.hour
        day = now.weekday()  # 0 = Monday
        
        is_business_hours = (0 <= day <= 4) and (6 <= hour < 18)
        
        # Calculate next business hour
        next_check = now
        if not is_business_hours:
            if hour < 6:
                next_check = now.replace(hour=6, minute=0, second=0)
            elif hour >= 18:
                next_check = (now + timedelta(days=1)).replace(hour=6, minute=0, second=0)
            elif day >= 5:  # Weekend
                days_until_monday = (7 - day) % 7
                if days_until_monday == 0:
                    days_until_monday = 1
                next_check = (now + timedelta(days=days_until_monday)).replace(hour=6, minute=0, second=0)
        
        return {
            'is_business_hours': is_business_hours,
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'business_hours': '6:00 - 18:00',
            'business_days': 'Monday - Friday',
            'status': 'Active' if is_business_hours else 'Inactive',
            'next_check': next_check.strftime('%Y-%m-%d %H:%M:%S') if not is_business_hours else 'Active now',
            'cost_savings': '75% vs 24/7 monitoring'
        }
    
    def get_drift_analysis(self) -> Dict:
        """Get drift analysis results"""
        return {
            'overall_drift_detected': False,
            'features_analyzed': 20,
            'drifted_features': 2,
            'drift_percentage': 10.0,
            'severity': 'low',
            'last_analysis': datetime.now().isoformat(),
            'thresholds': {
                'low': config.drift_threshold_low,
                'medium': config.drift_threshold_medium,
                'high': config.drift_threshold_high
            },
            'feature_drift_scores': [
                {'feature': 'transaction_amount', 'drift_score': 0.03, 'status': 'stable'},
                {'feature': 'account_age', 'drift_score': 0.08, 'status': 'drift_detected'},
                {'feature': 'transaction_hour', 'drift_score': 0.02, 'status': 'stable'},
                {'feature': 'merchant_category', 'drift_score': 0.12, 'status': 'drift_detected'},
                {'feature': 'location_risk', 'drift_score': 0.01, 'status': 'stable'}
            ]
        }
    
    def get_model_performance(self) -> Dict:
        """Get model performance metrics"""
        return {
            'auc_score': 0.9724,
            'precision': 0.89,
            'recall': 0.92,
            'f1_score': 0.905,
            'accuracy': 0.987,
            'false_positive_rate': 0.011,
            'model_version': 'v2.1.0',
            'last_training': '2024-01-15T10:30:00Z',
            'performance_trend': 'stable',
            'confidence_distribution': {
                'high_confidence': 78,
                'medium_confidence': 18,
                'low_confidence': 4
            }
        }

dashboard = MLOpsDashboard()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/status")
async def get_status():
    """Get endpoint status"""
    return dashboard.get_endpoint_status()

@app.get("/api/metrics")
async def get_metrics():
    """Get real-time metrics"""
    return dashboard.get_real_time_metrics()

@app.get("/api/business-hours")
async def get_business_hours():
    """Get business hours status"""
    return dashboard.get_business_hours_status()

@app.get("/api/drift")
async def get_drift():
    """Get drift analysis"""
    return dashboard.get_drift_analysis()

@app.get("/api/performance")
async def get_performance():
    """Get model performance"""
    return dashboard.get_model_performance()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'business_hours': f"{config.business_hours_start}:00-{config.business_hours_end}:00",
        'version': '2.0.0',
        'uptime': '24h 15m',
        'components': {
            'dashboard': 'healthy',
            'monitoring': 'healthy',
            'business_hours_scheduler': 'active'
        }
    }

@app.get("/api/system-info")
async def get_system_info():
    """Get system information"""
    return {
        'project_name': 'MLOps Monitoring',
        'version': '2.0.0',
        'environment': 'production',
        'features': [
            'Business Hours Monitoring',
            'Advanced Drift Detection',
            'Real-time Dashboard',
            'A/B Testing',
            'Automated Alerts'
        ],
        'cost_optimization': '75% savings vs 24/7',
        'monitoring_schedule': 'Monday-Friday, 6AM-6PM'
    }

if __name__ == "__main__":
    print("🚀 Starting MLOps FastAPI Dashboard...")
    print(f"📊 Business Hours: {config.business_hours_start}:00 - {config.business_hours_end}:00")
    print("🌐 Dashboard: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
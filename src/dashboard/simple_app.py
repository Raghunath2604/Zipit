from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import json
from datetime import datetime, timedelta

app = FastAPI(title="MLOps Monitoring Dashboard", version="2.0.0")

class MLOpsDashboard:
    def __init__(self):
        self.mock_data = self._generate_mock_data()
    
    def _generate_mock_data(self):
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=i*5)).isoformat() for i in range(24)]
        return {
            'invocations': [100 + (i * 5) + (i % 3 * 10) for i in range(24)],
            'latency': [150 + (i % 5 * 10) + (i % 7 * 5) for i in range(24)],
            'errors_4xx': [0 if i % 8 != 0 else 1 for i in range(24)],
            'errors_5xx': [0 if i % 12 != 0 else 1 for i in range(24)],
            'timestamps': timestamps
        }
    
    def get_status(self):
        return {
            'status': 'InService',
            'health_score': 98.5,
            'instance_type': 'ml.m5.large'
        }
    
    def get_metrics(self):
        data = self.mock_data
        return {
            'invocations': {
                'total': sum(data['invocations']),
                'values': data['invocations'],
                'timestamps': data['timestamps']
            },
            'latency': {
                'avg': sum(data['latency']) / len(data['latency']),
                'values': data['latency'],
                'timestamps': data['timestamps']
            },
            'errors': {
                'total_errors': sum(data['errors_4xx']) + sum(data['errors_5xx']),
                'error_rate': ((sum(data['errors_4xx']) + sum(data['errors_5xx'])) / sum(data['invocations'])) * 100
            }
        }
    
    def get_business_hours(self):
        now = datetime.now()
        hour = now.hour
        day = now.weekday()
        is_business_hours = (0 <= day <= 4) and (6 <= hour < 18)
        
        return {
            'is_business_hours': is_business_hours,
            'status': 'Active' if is_business_hours else 'Inactive',
            'business_hours': '6:00 - 18:00',
            'cost_savings': '75% vs 24/7 monitoring'
        }

dashboard = MLOpsDashboard()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MLOps Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            .header { text-align: center; color: #2563eb; margin-bottom: 30px; }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            .metric-card { background: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid #2563eb; }
            .metric-value { font-size: 2rem; font-weight: bold; color: #1f2937; }
            .metric-label { color: #6b7280; margin-bottom: 10px; }
            .status-active { color: #10b981; }
            .status-inactive { color: #ef4444; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 MLOps Monitoring Dashboard</h1>
                <p>Business Hours Optimized ML Monitoring</p>
            </div>
            
            <div class="metrics" id="metrics">
                <div class="metric-card">
                    <div class="metric-label">Loading...</div>
                    <div class="metric-value">Please wait</div>
                </div>
            </div>
            
            <div style="margin-top: 30px; text-align: center;">
                <h3>🔗 API Endpoints</h3>
                <p><a href="/api/health">Health Check</a> | <a href="/api/status">Status</a> | <a href="/api/metrics">Metrics</a> | <a href="/api/business-hours">Business Hours</a></p>
                <p><a href="/docs">📖 API Documentation</a></p>
            </div>
        </div>
        
        <script>
            async function loadData() {
                try {
                    const [status, metrics, businessHours] = await Promise.all([
                        fetch('/api/status').then(r => r.json()),
                        fetch('/api/metrics').then(r => r.json()),
                        fetch('/api/business-hours').then(r => r.json())
                    ]);
                    
                    document.getElementById('metrics').innerHTML = `
                        <div class="metric-card">
                            <div class="metric-label">Endpoint Status</div>
                            <div class="metric-value">${status.status}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Total Invocations</div>
                            <div class="metric-value">${metrics.invocations.total.toLocaleString()}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Avg Latency</div>
                            <div class="metric-value">${Math.round(metrics.latency.avg)} ms</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Business Hours</div>
                            <div class="metric-value ${businessHours.is_business_hours ? 'status-active' : 'status-inactive'}">
                                ${businessHours.status}
                            </div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Error Rate</div>
                            <div class="metric-value">${metrics.errors.error_rate.toFixed(2)}%</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Cost Savings</div>
                            <div class="metric-value status-active">75%</div>
                        </div>
                    `;
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }
            
            loadData();
            setInterval(loadData, 30000);
        </script>
    </body>
    </html>
    """

@app.get("/api/health")
async def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'business_hours': '6:00-18:00'
    }

@app.get("/api/status")
async def status():
    return dashboard.get_status()

@app.get("/api/metrics")
async def metrics():
    return dashboard.get_metrics()

@app.get("/api/business-hours")
async def business_hours():
    return dashboard.get_business_hours()

if __name__ == "__main__":
    print("🚀 Starting MLOps Dashboard on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
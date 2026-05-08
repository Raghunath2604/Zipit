#!/usr/bin/env python3
"""
Prometheus Integration for MLOps Platform
Metrics collection, monitoring, and alerting
"""

from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
from prometheus_client.exposition import MetricsHandler
from prometheus_client.core import REGISTRY
import time
import threading
from datetime import datetime
import json

class PrometheusManager:
    """Prometheus metrics collection and monitoring"""
    
    def __init__(self):
        # Create custom registry
        self.registry = CollectorRegistry()
        
        # Model prediction metrics
        self.prediction_counter = Counter(
            'mlops_predictions_total',
            'Total number of predictions made',
            ['model_name', 'user_id', 'model_type'],
            registry=self.registry
        )
        
        self.prediction_latency = Histogram(
            'mlops_prediction_duration_seconds',
            'Time spent on predictions',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        # Model performance metrics
        self.model_accuracy = Gauge(
            'mlops_model_accuracy',
            'Current model accuracy',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        self.model_precision = Gauge(
            'mlops_model_precision',
            'Current model precision',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        self.model_recall = Gauge(
            'mlops_model_recall',
            'Current model recall',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        self.model_f1_score = Gauge(
            'mlops_model_f1_score',
            'Current model F1 score',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        # Drift detection metrics
        self.drift_detected = Gauge(
            'mlops_drift_detected',
            'Whether drift is detected (1 = drift, 0 = no drift)',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        self.drift_score = Gauge(
            'mlops_drift_score',
            'Current drift score',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        # System metrics
        self.active_models = Gauge(
            'mlops_active_models_total',
            'Total number of active models',
            ['user_id'],
            registry=self.registry
        )
        
        self.api_requests = Counter(
            'mlops_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status_code'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'mlops_api_request_duration_seconds',
            'API request duration',
            ['endpoint', 'method'],
            registry=self.registry
        )
        
        # Data quality metrics
        self.data_quality_score = Gauge(
            'mlops_data_quality_score',
            'Data quality score (0-100)',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        self.missing_values_count = Gauge(
            'mlops_missing_values_total',
            'Number of missing values in data',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        # Business metrics
        self.model_uptime = Gauge(
            'mlops_model_uptime_seconds',
            'Model uptime in seconds',
            ['model_name', 'user_id'],
            registry=self.registry
        )
        
        self.cost_savings = Gauge(
            'mlops_cost_savings_dollars',
            'Cost savings from optimization',
            ['user_id'],
            registry=self.registry
        )
    
    def record_prediction(self, model_name, user_id, model_type, latency=None):
        """Record a prediction event"""
        self.prediction_counter.labels(
            model_name=model_name,
            user_id=str(user_id),
            model_type=model_type
        ).inc()
        
        if latency:
            self.prediction_latency.labels(
                model_name=model_name,
                user_id=str(user_id)
            ).observe(latency)
    
    def update_model_metrics(self, model_name, user_id, metrics):
        """Update model performance metrics"""
        user_id_str = str(user_id)
        
        if 'accuracy' in metrics:
            self.model_accuracy.labels(
                model_name=model_name,
                user_id=user_id_str
            ).set(metrics['accuracy'])
        
        if 'precision' in metrics:
            self.model_precision.labels(
                model_name=model_name,
                user_id=user_id_str
            ).set(metrics['precision'])
        
        if 'recall' in metrics:
            self.model_recall.labels(
                model_name=model_name,
                user_id=user_id_str
            ).set(metrics['recall'])
        
        if 'f1_score' in metrics:
            self.model_f1_score.labels(
                model_name=model_name,
                user_id=user_id_str
            ).set(metrics['f1_score'])
    
    def update_drift_metrics(self, model_name, user_id, drift_detected, drift_score):
        """Update drift detection metrics"""
        user_id_str = str(user_id)
        
        self.drift_detected.labels(
            model_name=model_name,
            user_id=user_id_str
        ).set(1 if drift_detected else 0)
        
        self.drift_score.labels(
            model_name=model_name,
            user_id=user_id_str
        ).set(drift_score)
    
    def update_data_quality_metrics(self, model_name, user_id, quality_score, missing_values):
        """Update data quality metrics"""
        user_id_str = str(user_id)
        
        self.data_quality_score.labels(
            model_name=model_name,
            user_id=user_id_str
        ).set(quality_score)
        
        self.missing_values_count.labels(
            model_name=model_name,
            user_id=user_id_str
        ).set(missing_values)
    
    def record_api_request(self, endpoint, method, status_code, duration=None):
        """Record API request metrics"""
        self.api_requests.labels(
            endpoint=endpoint,
            method=method,
            status_code=str(status_code)
        ).inc()
        
        if duration:
            self.api_request_duration.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
    
    def update_system_metrics(self, user_id, active_models_count, cost_savings=None):
        """Update system-level metrics"""
        user_id_str = str(user_id)
        
        self.active_models.labels(user_id=user_id_str).set(active_models_count)
        
        if cost_savings is not None:
            self.cost_savings.labels(user_id=user_id_str).set(cost_savings)
    
    def update_model_uptime(self, model_name, user_id, uptime_seconds):
        """Update model uptime"""
        self.model_uptime.labels(
            model_name=model_name,
            user_id=str(user_id)
        ).set(uptime_seconds)
    
    def get_metrics(self):
        """Get all metrics in Prometheus format"""
        return generate_latest(self.registry)
    
    def create_alert_rules(self):
        """Create Prometheus alert rules"""
        alert_rules = {
            "groups": [
                {
                    "name": "mlops_alerts",
                    "rules": [
                        {
                            "alert": "ModelAccuracyLow",
                            "expr": "mlops_model_accuracy < 0.8",
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "Model accuracy is below 80%",
                                "description": "Model {{ $labels.model_name }} for user {{ $labels.user_id }} has accuracy {{ $value }}"
                            }
                        },
                        {
                            "alert": "DriftDetected",
                            "expr": "mlops_drift_detected == 1",
                            "for": "1m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "Data drift detected",
                                "description": "Drift detected for model {{ $labels.model_name }} (user {{ $labels.user_id }})"
                            }
                        },
                        {
                            "alert": "HighPredictionLatency",
                            "expr": "histogram_quantile(0.95, mlops_prediction_duration_seconds_bucket) > 1.0",
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "High prediction latency",
                                "description": "95th percentile latency is {{ $value }}s for model {{ $labels.model_name }}"
                            }
                        },
                        {
                            "alert": "DataQualityLow",
                            "expr": "mlops_data_quality_score < 70",
                            "for": "10m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "Low data quality score",
                                "description": "Data quality score is {{ $value }} for model {{ $labels.model_name }}"
                            }
                        },
                        {
                            "alert": "ModelDown",
                            "expr": "up{job=\"mlops-platform\"} == 0",
                            "for": "1m",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "MLOps platform is down",
                                "description": "MLOps platform has been down for more than 1 minute"
                            }
                        }
                    ]
                }
            ]
        }
        return alert_rules
    
    def create_grafana_dashboard(self):
        """Create Grafana dashboard configuration"""
        dashboard = {
            "dashboard": {
                "title": "MLOps Platform Monitoring",
                "panels": [
                    {
                        "title": "Model Accuracy",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "mlops_model_accuracy",
                                "legendFormat": "{{model_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Predictions per Second",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(mlops_predictions_total[5m])",
                                "legendFormat": "{{model_name}}"
                            }
                        ]
                    },
                    {
                        "title": "Drift Detection",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "mlops_drift_detected",
                                "legendFormat": "{{model_name}}"
                            }
                        ]
                    },
                    {
                        "title": "API Request Duration",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "histogram_quantile(0.95, mlops_api_request_duration_seconds_bucket)",
                                "legendFormat": "95th percentile"
                            }
                        ]
                    },
                    {
                        "title": "Data Quality Score",
                        "type": "gauge",
                        "targets": [
                            {
                                "expr": "mlops_data_quality_score",
                                "legendFormat": "{{model_name}}"
                            }
                        ]
                    }
                ]
            }
        }
        return dashboard

# Middleware for automatic metrics collection
class PrometheusMiddleware:
    """FastAPI middleware for automatic Prometheus metrics collection"""
    
    def __init__(self, prometheus_manager):
        self.prometheus = prometheus_manager
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record API metrics
        duration = time.time() - start_time
        self.prometheus.record_api_request(
            endpoint=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration=duration
        )
        
        return response

# Integration with main platform
def integrate_prometheus_with_platform():
    """Add Prometheus endpoints to main platform"""
    from fastapi import APIRouter, Response
    
    router = APIRouter(prefix="/api/prometheus", tags=["Prometheus"])
    prometheus_manager = PrometheusManager()
    
    @router.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint"""
        metrics = prometheus_manager.get_metrics()
        return Response(content=metrics, media_type="text/plain")
    
    @router.get("/alerts")
    async def get_alert_rules():
        """Get Prometheus alert rules"""
        return prometheus_manager.create_alert_rules()
    
    @router.get("/dashboard")
    async def get_grafana_dashboard():
        """Get Grafana dashboard configuration"""
        return prometheus_manager.create_grafana_dashboard()
    
    @router.post("/metrics/prediction")
    async def record_prediction_metric(model_name: str, user_id: int, model_type: str, latency: float = None):
        """Record prediction metrics"""
        prometheus_manager.record_prediction(model_name, user_id, model_type, latency)
        return {"status": "recorded"}
    
    @router.post("/metrics/performance")
    async def update_performance_metrics(model_name: str, user_id: int, metrics: dict):
        """Update model performance metrics"""
        prometheus_manager.update_model_metrics(model_name, user_id, metrics)
        return {"status": "updated"}
    
    return router, prometheus_manager
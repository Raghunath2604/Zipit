import boto3
import json
from datetime import datetime, timedelta

def create_comprehensive_dashboard(endpoint_name, region='us-east-1'):
    """Create comprehensive CloudWatch dashboard for MLOps monitoring"""
    
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "Invocations", "EndpointName", endpoint_name],
                        [".", "InvocationsPerInstance", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": region,
                    "title": "🚀 Endpoint Invocations",
                    "yAxis": {"left": {"min": 0}}
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "ModelLatency", "EndpointName", endpoint_name, {"stat": "Average"}],
                        [".", ".", ".", ".", {"stat": "p99"}],
                        [".", ".", ".", ".", {"stat": "p95"}]
                    ],
                    "period": 300,
                    "region": region,
                    "title": "⏱️ Model Latency (ms)",
                    "yAxis": {"left": {"min": 0}}
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6,
                "width": 8, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "Invocation4XXErrors", "EndpointName", endpoint_name],
                        [".", "Invocation5XXErrors", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": region,
                    "title": "❌ Error Rates",
                    "yAxis": {"left": {"min": 0}}
                }
            },
            {
                "type": "metric",
                "x": 8, "y": 6,
                "width": 8, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "CPUUtilization", "EndpointName", endpoint_name],
                        [".", "MemoryUtilization", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": region,
                    "title": "💻 Resource Utilization (%)",
                    "yAxis": {"left": {"min": 0, "max": 100}}
                }
            },
            {
                "type": "metric",
                "x": 16, "y": 6,
                "width": 8, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker/ModelMonitor", "feature_baseline_drift_distance", "MonitoringSchedule", f"{endpoint_name}-monitoring"]
                    ],
                    "period": 3600,
                    "stat": "Maximum",
                    "region": region,
                    "title": "📊 Data Drift Distance",
                    "annotations": {
                        "horizontal": [{
                            "label": "Drift Threshold",
                            "value": 0.1
                        }]
                    }
                }
            },
            {
                "type": "log",
                "x": 0, "y": 12,
                "width": 24, "height": 6,
                "properties": {
                    "query": f"SOURCE '/aws/sagemaker/Endpoints/{endpoint_name}'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 100",
                    "region": region,
                    "title": "🔍 Recent Errors",
                    "view": "table"
                }
            }
        ]
    }
    
    dashboard_name = f"MLOps-Fraud-Detection-{endpoint_name}"
    
    try:
        cloudwatch.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(dashboard_body)
        )
        print(f"✅ Dashboard created: {dashboard_name}")
        return dashboard_name
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        return None

def create_business_metrics_dashboard(endpoint_name, region='us-east-1'):
    """Create business-specific metrics dashboard"""
    
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    # Custom business metrics dashboard
    business_dashboard = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["MLOps/FraudDetection", "FraudDetectionRate", "EndpointName", endpoint_name],
                        [".", "FalsePositiveRate", ".", "."]
                    ],
                    "period": 3600,
                    "stat": "Average",
                    "region": region,
                    "title": "🎯 Fraud Detection Performance",
                    "yAxis": {"left": {"min": 0, "max": 1}}
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["MLOps/FraudDetection", "ModelConfidenceHigh", "EndpointName", endpoint_name],
                        [".", "ModelConfidenceMedium", ".", "."],
                        [".", "ModelConfidenceLow", ".", "."]
                    ],
                    "period": 3600,
                    "stat": "Sum",
                    "region": region,
                    "title": "🎲 Model Confidence Distribution"
                }
            },
            {
                "type": "metric",
                "x": 0, "y": 6,
                "width": 24, "height": 6,
                "properties": {
                    "metrics": [
                        ["MLOps/FraudDetection", "TransactionVolume", "EndpointName", endpoint_name],
                        [".", "FraudTransactionVolume", ".", "."]
                    ],
                    "period": 3600,
                    "stat": "Sum",
                    "region": region,
                    "title": "💰 Transaction Volume Analysis"
                }
            }
        ]
    }
    
    business_dashboard_name = f"MLOps-Business-Metrics-{endpoint_name}"
    
    try:
        cloudwatch.put_dashboard(
            DashboardName=business_dashboard_name,
            DashboardBody=json.dumps(business_dashboard)
        )
        print(f"✅ Business dashboard created: {business_dashboard_name}")
        return business_dashboard_name
    except Exception as e:
        print(f"❌ Error creating business dashboard: {e}")
        return None

if __name__ == "__main__":
    endpoint_name = "fraud-detection-endpoint"  # Replace with actual endpoint name
    
    # Create dashboards
    tech_dashboard = create_comprehensive_dashboard(endpoint_name)
    business_dashboard = create_business_metrics_dashboard(endpoint_name)
    
    print(f"\n🎯 Dashboards created:")
    print(f"Technical: {tech_dashboard}")
    print(f"Business: {business_dashboard}")
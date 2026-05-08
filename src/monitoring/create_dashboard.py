import boto3
import json

def create_cloudwatch_dashboard(endpoint_name):
    """Create CloudWatch dashboard for MLOps monitoring"""
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "Invocations", "EndpointName", endpoint_name],
                        [".", "InvocationErrors", ".", "."],
                        [".", "ModelLatency", ".", "."]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Model Performance Metrics"
                }
            },
            {
                "type": "metric",
                "x": 12, "y": 0,
                "width": 12, "height": 6,
                "properties": {
                    "metrics": [
                        ["aws/sagemaker/Endpoints/data-metrics", "feature_baseline_drift_distance", "Endpoint", endpoint_name]
                    ],
                    "period": 3600,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Data Drift Detection"
                }
            },
            {
                "type": "log",
                "x": 0, "y": 6,
                "width": 24, "height": 6,
                "properties": {
                    "query": f"SOURCE '/aws/sagemaker/Endpoints/{endpoint_name}'\n| fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 100",
                    "region": "us-east-1",
                    "title": "Recent Errors"
                }
            }
        ]
    }
    
    cloudwatch.put_dashboard(
        DashboardName=f'MLOps-{endpoint_name}',
        DashboardBody=json.dumps(dashboard_body)
    )
    
    print(f"Dashboard created: MLOps-{endpoint_name}")
    return f'MLOps-{endpoint_name}'

def create_fraud_specific_dashboard(endpoint_name):
    """Create fraud detection specific dashboard"""
    cloudwatch = boto3.client('cloudwatch')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "x": 0, "y": 0,
                "width": 8, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "Invocations", "EndpointName", endpoint_name]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Total Predictions"
                }
            },
            {
                "type": "metric",
                "x": 8, "y": 0,
                "width": 8, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "ModelLatency", "EndpointName", endpoint_name]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "Prediction Latency"
                }
            },
            {
                "type": "metric",
                "x": 16, "y": 0,
                "width": 8, "height": 6,
                "properties": {
                    "metrics": [
                        ["AWS/SageMaker", "InvocationErrors", "EndpointName", endpoint_name]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Prediction Errors"
                }
            }
        ]
    }
    
    cloudwatch.put_dashboard(
        DashboardName=f'FraudDetection-{endpoint_name}',
        DashboardBody=json.dumps(dashboard_body)
    )
    
    print(f"Fraud detection dashboard created: FraudDetection-{endpoint_name}")

if __name__ == "__main__":
    # Create dashboard
    endpoint_name = 'your-endpoint-name'  # Replace
    create_cloudwatch_dashboard(endpoint_name)
    create_fraud_specific_dashboard(endpoint_name)
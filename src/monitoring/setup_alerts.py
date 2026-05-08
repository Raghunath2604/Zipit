import boto3
import json

def create_sns_topic_and_subscription(email):
    """Create SNS topic and email subscription"""
    sns = boto3.client('sns')
    
    # Create SNS topic
    topic_response = sns.create_topic(Name='MLOpsModelAlerts')
    topic_arn = topic_response['TopicArn']
    
    # Subscribe email
    sns.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=email
    )
    
    print(f"SNS topic created: {topic_arn}")
    print(f"Email subscription added for: {email}")
    return topic_arn

def create_cloudwatch_alarms(endpoint_name, topic_arn):
    """Create CloudWatch alarms for model monitoring"""
    cloudwatch = boto3.client('cloudwatch')
    
    # Model quality alarm
    cloudwatch.put_metric_alarm(
        AlarmName=f'{endpoint_name}-ModelQuality',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='feature_baseline_drift_distance',
        Namespace='aws/sagemaker/Endpoints/data-metrics',
        Period=3600,
        Statistic='Average',
        Threshold=0.1,
        ActionsEnabled=True,
        AlarmActions=[topic_arn],
        AlarmDescription='Alert when model drift detected',
        Dimensions=[
            {
                'Name': 'Endpoint',
                'Value': endpoint_name
            }
        ]
    )
    
    # Invocation errors alarm
    cloudwatch.put_metric_alarm(
        AlarmName=f'{endpoint_name}-InvocationErrors',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='ModelInvocation4XXErrors',
        Namespace='AWS/SageMaker',
        Period=300,
        Statistic='Sum',
        Threshold=5,
        ActionsEnabled=True,
        AlarmActions=[topic_arn],
        AlarmDescription='Alert on model invocation errors',
        Dimensions=[
            {
                'Name': 'EndpointName',
                'Value': endpoint_name
            }
        ]
    )
    
    print(f"CloudWatch alarms created for endpoint: {endpoint_name}")

def setup_alerts(endpoint_name, email):
    """Complete alert setup"""
    topic_arn = create_sns_topic_and_subscription(email)
    create_cloudwatch_alarms(endpoint_name, topic_arn)
    return topic_arn

if __name__ == "__main__":
    # Setup alerts
    endpoint_name = 'your-endpoint-name'  # Replace
    email = 'your-email@example.com'  # Replace
    
    topic_arn = setup_alerts(endpoint_name, email)
    print(f"Alerts configured with topic: {topic_arn}")
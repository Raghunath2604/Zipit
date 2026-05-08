from sagemaker.model_monitor import CronExpressionGenerator
import time

def setup_monitoring_schedule(monitor, endpoint_name, bucket):
    """Setup automated monitoring schedule"""
    schedule_name = f'fraud-monitoring-{int(time.time())}'
    
    monitor.create_monitoring_schedule(
        monitor_schedule_name=schedule_name,
        endpoint_input=endpoint_name,
        output_s3_uri=f's3://{bucket}/monitoring-reports',
        statistics=f's3://{bucket}/baseline-results/statistics.json',
        constraints=f's3://{bucket}/baseline-results/constraints.json',
        schedule_cron_expression=CronExpressionGenerator.hourly(),
        enable_cloudwatch_metrics=True
    )
    
    return schedule_name

def get_monitoring_results(monitor):
    """Get latest monitoring execution results"""
    executions = monitor.list_executions()
    if executions:
        latest = executions[-1]
        return latest.describe()
    return None

if __name__ == "__main__":
    # Example usage
    from sagemaker.model_monitor import DefaultModelMonitor
    
    role = 'arn:aws:iam::YOUR_ACCOUNT:role/MLOpsMonitoringRole'
    bucket = 'your-mlops-monitoring-bucket'
    endpoint_name = 'your-endpoint-name'
    
    monitor = DefaultModelMonitor(role=role)
    schedule_name = setup_monitoring_schedule(monitor, endpoint_name, bucket)
    print(f"Monitoring schedule created: {schedule_name}")
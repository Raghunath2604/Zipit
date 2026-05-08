import boto3
import json
from datetime import datetime, time
import pytz

try:
    from config.config import config
except ImportError:
    # Fallback configuration
    class Config:
        business_hours_start = 6
        business_hours_end = 18
        business_days = [0, 1, 2, 3, 4]
        timezone = 'UTC'
        sagemaker_role = ''
    config = Config()

class BusinessHoursScheduler:
    """Manage monitoring activities during business hours only (6 AM - 6 PM)"""
    
    def __init__(self):
        self.events_client = boto3.client('events')
        self.lambda_client = boto3.client('lambda')
        self.tz = pytz.timezone(config.timezone)
        
    def is_business_hours(self, dt=None):
        """Check if current time is within business hours"""
        if dt is None:
            dt = datetime.now(self.tz)
        
        # Check if it's a business day
        if dt.weekday() not in config.business_days:
            return False
            
        # Check if it's within business hours
        current_hour = dt.hour
        return config.business_hours_start <= current_hour < config.business_hours_end
    
    def create_business_hours_rule(self, rule_name, target_function_arn):
        """Create EventBridge rule for business hours only"""
        
        # Create rule that runs every hour during business hours
        cron_expression = f"0 {config.business_hours_start}-{config.business_hours_end-1} ? * MON-FRI *"
        
        try:
            response = self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression=f"cron({cron_expression})",
                Description=f"MLOps monitoring during business hours ({config.business_hours_start}AM-{config.business_hours_end}PM)",
                State='ENABLED'
            )
            
            # Add target
            self.events_client.put_targets(
                Rule=rule_name,
                Targets=[
                    {
                        'Id': '1',
                        'Arn': target_function_arn,
                        'Input': json.dumps({
                            'source': 'business-hours-scheduler',
                            'detail-type': 'MLOps Monitoring Check'
                        })
                    }
                ]
            )
            
            print(f"✅ Business hours rule created: {rule_name}")
            print(f"📅 Schedule: {cron_expression}")
            return response['RuleArn']
            
        except Exception as e:
            print(f"❌ Error creating business hours rule: {e}")
            return None
    
    def create_monitoring_lambda(self):
        """Create Lambda function for business hours monitoring"""
        
        lambda_code = '''
import json
import boto3
from datetime import datetime
import pytz

def lambda_handler(event, context):
    """Lambda function to run monitoring checks during business hours"""
    
    # Initialize clients
    sagemaker = boto3.client('sagemaker')
    cloudwatch = boto3.client('cloudwatch')
    
    print(f"🕐 Running business hours monitoring check at {datetime.now()}")
    
    try:
        # Check endpoint health
        endpoint_name = "fraud-detection-endpoint"  # Replace with actual endpoint
        
        response = sagemaker.describe_endpoint(EndpointName=endpoint_name)
        endpoint_status = response['EndpointStatus']
        
        # Send custom metric
        cloudwatch.put_metric_data(
            Namespace='MLOps/BusinessHours',
            MetricData=[
                {
                    'MetricName': 'EndpointHealthCheck',
                    'Value': 1 if endpoint_status == 'InService' else 0,
                    'Unit': 'Count',
                    'Dimensions': [
                        {
                            'Name': 'EndpointName',
                            'Value': endpoint_name
                        }
                    ]
                }
            ]
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Business hours monitoring check completed',
                'endpoint_status': endpoint_status,
                'timestamp': datetime.now().isoformat()
            })
        }
        
    except Exception as e:
        print(f"❌ Error in monitoring check: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
'''
        
        # Create Lambda function
        try:
            response = self.lambda_client.create_function(
                FunctionName='mlops-business-hours-monitor',
                Runtime='python3.9',
                Role=config.sagemaker_role,  # Reuse SageMaker role
                Handler='index.lambda_handler',
                Code={'ZipFile': lambda_code.encode()},
                Description='MLOps monitoring during business hours',
                Timeout=300,
                Environment={
                    'Variables': {
                        'BUSINESS_HOURS_START': str(config.business_hours_start),
                        'BUSINESS_HOURS_END': str(config.business_hours_end)
                    }
                }
            )
            
            function_arn = response['FunctionArn']
            print(f"✅ Lambda function created: {function_arn}")
            
            # Add permission for EventBridge to invoke Lambda
            self.lambda_client.add_permission(
                FunctionName='mlops-business-hours-monitor',
                StatementId='allow-eventbridge',
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com'
            )
            
            return function_arn
            
        except Exception as e:
            print(f"❌ Error creating Lambda function: {e}")
            return None
    
    def setup_business_hours_monitoring(self):
        """Setup complete business hours monitoring"""
        
        print("🚀 Setting up business hours monitoring...")
        
        # Create Lambda function
        function_arn = self.create_monitoring_lambda()
        if not function_arn:
            return False
        
        # Create EventBridge rule
        rule_arn = self.create_business_hours_rule(
            'mlops-business-hours-monitoring',
            function_arn
        )
        
        if rule_arn:
            print("✅ Business hours monitoring setup complete!")
            print(f"⏰ Active hours: {config.business_hours_start}:00 - {config.business_hours_end}:00")
            print(f"📅 Active days: Monday - Friday")
            return True
        
        return False
    
    def disable_24x7_monitoring(self):
        """Disable any existing 24x7 monitoring rules"""
        
        try:
            # List all rules
            response = self.events_client.list_rules(NamePrefix='mlops')
            
            for rule in response.get('Rules', []):
                rule_name = rule['Name']
                
                # Skip business hours rule
                if 'business-hours' in rule_name:
                    continue
                
                # Disable 24x7 rules
                if any(keyword in rule_name.lower() for keyword in ['24x7', 'continuous', 'always']):
                    self.events_client.disable_rule(Name=rule_name)
                    print(f"🚫 Disabled 24x7 rule: {rule_name}")
            
            print("✅ 24x7 monitoring rules disabled")
            
        except Exception as e:
            print(f"❌ Error disabling 24x7 monitoring: {e}")

def get_next_business_hour():
    """Get the next business hour for scheduling"""
    now = datetime.now(pytz.timezone(config.timezone))
    
    # If currently in business hours, return current time
    scheduler = BusinessHoursScheduler()
    if scheduler.is_business_hours(now):
        return now
    
    # Find next business hour
    next_hour = now.replace(minute=0, second=0, microsecond=0)
    
    while not scheduler.is_business_hours(next_hour):
        next_hour = next_hour.replace(hour=next_hour.hour + 1)
        
        # If past business hours today, move to next business day
        if next_hour.hour >= config.business_hours_end:
            next_hour = next_hour.replace(hour=config.business_hours_start)
            next_hour = next_hour.replace(day=next_hour.day + 1)
    
    return next_hour

if __name__ == "__main__":
    scheduler = BusinessHoursScheduler()
    
    # Setup business hours monitoring
    success = scheduler.setup_business_hours_monitoring()
    
    if success:
        # Disable any 24x7 monitoring
        scheduler.disable_24x7_monitoring()
        
        # Show next monitoring time
        next_check = get_next_business_hour()
        print(f"🕐 Next monitoring check: {next_check}")
    else:
        print("❌ Failed to setup business hours monitoring")
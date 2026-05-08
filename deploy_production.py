#!/usr/bin/env python3
"""
Production deployment automation script
Deploys the complete MLOps monitoring stack to AWS with validation
"""

import boto3
import json
import time
import sys
from datetime import datetime
from config.config import config
from src.monitoring.business_hours_scheduler import BusinessHoursScheduler

class ProductionDeployer:
    """Enhanced production deployment with validation"""
    
    def __init__(self):
        self.sm_client = boto3.client('sagemaker', region_name=config.aws_region)
        self.s3_client = boto3.client('s3', region_name=config.aws_region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=config.aws_region)
        self.scheduler = BusinessHoursScheduler()
        
    def validate_prerequisites(self):
        """Validate all prerequisites before deployment"""
        print("🔍 Validating prerequisites...")
        
        checks = [
            self._check_aws_credentials,
            self._check_s3_bucket,
            self._check_sagemaker_role,
            self._check_model_artifacts
        ]
        
        for check in checks:
            if not check():
                return False
        
        print("✅ All prerequisites validated")
        return True
    
    def _check_aws_credentials(self):
        """Check AWS credentials"""
        try:
            sts = boto3.client('sts')
            sts.get_caller_identity()
            print("✅ AWS credentials valid")
            return True
        except Exception as e:
            print(f"❌ AWS credentials invalid: {e}")
            return False
    
    def _check_s3_bucket(self):
        """Check S3 bucket exists and is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=config.s3_bucket)
            print(f"✅ S3 bucket accessible: {config.s3_bucket}")
            return True
        except Exception as e:
            print(f"❌ S3 bucket not accessible: {e}")
            return False
    
    def _check_sagemaker_role(self):
        """Check SageMaker execution role"""
        if not config.sagemaker_role:
            print("❌ SageMaker role not configured")
            return False
        
        try:
            iam = boto3.client('iam')
            role_name = config.sagemaker_role.split('/')[-1]
            iam.get_role(RoleName=role_name)
            print(f"✅ SageMaker role valid: {role_name}")
            return True
        except Exception as e:
            print(f"❌ SageMaker role invalid: {e}")
            return False
    
    def _check_model_artifacts(self):
        """Check model artifacts exist"""
        try:
            import os
            if os.path.exists('models/model.joblib'):
                print("✅ Model artifacts found")
                return True
            else:
                print("❌ Model artifacts not found")
                return False
        except Exception as e:
            print(f"❌ Error checking model artifacts: {e}")
            return False
    
    def deploy_model(self):
        """Deploy model with enhanced configuration"""
        print("🤖 Deploying SageMaker model...")
        
        timestamp = int(time.time())
        model_name = f"fraud-detection-{timestamp}"
        
        # Upload model artifacts
        print("📦 Uploading model artifacts...")
        self.s3_client.upload_file(
            'models/model.joblib',
            config.s3_bucket,
            f'models/{model_name}/model.joblib'
        )
        
        # Create model
        try:
            self.sm_client.create_model(
                ModelName=model_name,
                PrimaryContainer={
                    'Image': '246618743249.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:0.23-1-cpu-py3',
                    'ModelDataUrl': f's3://{config.s3_bucket}/models/{model_name}/model.joblib',
                    'Environment': {
                        'SAGEMAKER_PROGRAM': 'fraud_inference.py',
                        'SAGEMAKER_SUBMIT_DIRECTORY': f's3://{config.s3_bucket}/code/inference.tar.gz'
                    }
                },
                ExecutionRoleArn=config.sagemaker_role
            )
            print(f"✅ Model created: {model_name}")
            return model_name
        except Exception as e:
            print(f"❌ Error creating model: {e}")
            return None
    
    def deploy_endpoint(self, model_name):
        """Deploy endpoint with data capture"""
        print("🌐 Deploying endpoint...")
        
        timestamp = int(time.time())
        endpoint_config_name = f"fraud-detection-config-{timestamp}"
        endpoint_name = f"fraud-detection-endpoint-{timestamp}"
        
        try:
            # Create endpoint configuration
            self.sm_client.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[{
                    'VariantName': 'primary',
                    'ModelName': model_name,
                    'InitialInstanceCount': 1,
                    'InstanceType': 'ml.m5.large',
                    'InitialVariantWeight': 1
                }],
                DataCaptureConfig={
                    'EnableCapture': True,
                    'InitialSamplingPercentage': config.data_capture_percentage,
                    'DestinationS3Uri': f's3://{config.s3_bucket}/data-capture',
                    'CaptureOptions': [
                        {'CaptureMode': 'Input'},
                        {'CaptureMode': 'Output'}
                    ]
                }
            )
            
            # Create endpoint
            self.sm_client.create_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            
            print(f"✅ Endpoint deployment initiated: {endpoint_name}")
            return endpoint_name
            
        except Exception as e:
            print(f"❌ Error deploying endpoint: {e}")
            return None
    
    def wait_for_endpoint(self, endpoint_name, timeout_minutes=20):
        """Wait for endpoint to be in service"""
        print(f"⏳ Waiting for endpoint to be in service (timeout: {timeout_minutes}min)...")
        
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = self.sm_client.describe_endpoint(EndpointName=endpoint_name)
                status = response['EndpointStatus']
                
                if status == 'InService':
                    print(f"✅ Endpoint is in service: {endpoint_name}")
                    return True
                elif status == 'Failed':
                    print(f"❌ Endpoint deployment failed: {response.get('FailureReason', 'Unknown')}")
                    return False
                else:
                    print(f"⏳ Endpoint status: {status}")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"❌ Error checking endpoint status: {e}")
                return False
        
        print(f"❌ Endpoint deployment timeout after {timeout_minutes} minutes")
        return False
    
    def setup_business_hours_monitoring(self, endpoint_name):
        """Setup business hours monitoring"""
        print("📊 Setting up business hours monitoring...")
        
        try:
            success = self.scheduler.setup_business_hours_monitoring()
            if success:
                print("✅ Business hours monitoring configured")
                return True
            else:
                print("❌ Failed to setup business hours monitoring")
                return False
        except Exception as e:
            print(f"❌ Error setting up monitoring: {e}")
            return False
    
    def test_endpoint(self, endpoint_name):
        """Test endpoint with sample data"""
        print("🧪 Testing endpoint...")
        
        try:
            runtime = boto3.client('sagemaker-runtime')
            
            # Sample test data
            test_data = {
                'transaction_amount': 100.0,
                'account_age_days': 365,
                'transaction_hour': 14,
                'is_weekend': 0
            }
            
            response = runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/json',
                Body=json.dumps(test_data)
            )
            
            result = json.loads(response['Body'].read().decode())
            print(f"✅ Endpoint test successful: {result}")
            return True
            
        except Exception as e:
            print(f"❌ Endpoint test failed: {e}")
            return False
    
    def deploy_to_production(self):
        """Complete production deployment"""
        print("🚀 Starting production deployment...")
        print(f"📅 Deployment time: {datetime.now()}")
        
        # Validate prerequisites
        if not self.validate_prerequisites():
            print("❌ Prerequisites validation failed")
            return None
        
        # Deploy model
        model_name = self.deploy_model()
        if not model_name:
            print("❌ Model deployment failed")
            return None
        
        # Deploy endpoint
        endpoint_name = self.deploy_endpoint(model_name)
        if not endpoint_name:
            print("❌ Endpoint deployment failed")
            return None
        
        # Wait for endpoint
        if not self.wait_for_endpoint(endpoint_name):
            print("❌ Endpoint failed to come online")
            return None
        
        # Setup monitoring
        self.setup_business_hours_monitoring(endpoint_name)
        
        # Test endpoint
        self.test_endpoint(endpoint_name)
        
        # Save deployment info
        deployment_info = {
            'endpoint_name': endpoint_name,
            'model_name': model_name,
            'deployment_time': datetime.now().isoformat(),
            'business_hours': f"{config.business_hours_start}:00-{config.business_hours_end}:00",
            'monitoring_enabled': True
        }
        
        with open('deployment_info.json', 'w') as f:
            json.dump(deployment_info, f, indent=2)
        
        print("\n🎯 Deployment Summary:")
        print(f"📍 Endpoint: {endpoint_name}")
        print(f"🤖 Model: {model_name}")
        print(f"⏰ Business Hours: {config.business_hours_start}:00-{config.business_hours_end}:00")
        print(f"📊 Monitoring: Enabled")
        print("✅ Production deployment completed successfully!")
        
        return deployment_info

if __name__ == "__main__":
    deployer = ProductionDeployer()
    result = deployer.deploy_to_production()
    
    if result:
        print(f"\n🎉 Deployment successful!")
        sys.exit(0)
    else:
        print(f"\n💥 Deployment failed!")
        sys.exit(1)
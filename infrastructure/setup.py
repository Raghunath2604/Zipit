import boto3
import json
import time

def create_s3_bucket(bucket_name, region='us-east-1'):
    s3 = boto3.client('s3', region_name=region)
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket {bucket_name} created successfully")
        return bucket_name
    except Exception as e:
        print(f"Error creating bucket: {e}")
        return None

def create_sagemaker_role():
    iam = boto3.client('iam')
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "sagemaker.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role = iam.create_role(
            RoleName='MLOpsMonitoringRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for MLOps monitoring project'
        )
        
        # Attach necessary policies
        policies = [
            'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess',
            'arn:aws:iam::aws:policy/AmazonS3FullAccess',
            'arn:aws:iam::aws:policy/CloudWatchFullAccess'
        ]
        
        for policy in policies:
            iam.attach_role_policy(
                RoleName='MLOpsMonitoringRole',
                PolicyArn=policy
            )
        
        print(f"Role created: {role['Role']['Arn']}")
        return role['Role']['Arn']
    except Exception as e:
        print(f"Error creating role: {e}")
        return None

if __name__ == "__main__":
    # Run setup
    bucket_name = 'mlops-monitoring-bucket-' + str(int(time.time()))
    bucket = create_s3_bucket(bucket_name)
    role_arn = create_sagemaker_role()
    
    print(f"\nSetup complete:")
    print(f"Bucket: {bucket}")
    print(f"Role: {role_arn}")
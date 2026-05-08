import boto3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from sklearn.metrics import roc_auc_score, precision_recall_curve, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class ModelPerformanceTracker:
    """Track model performance over time with A/B testing capabilities"""
    
    def __init__(self, s3_bucket, region='us-east-1'):
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        
    def track_prediction_performance(self, predictions, ground_truth, model_version, timestamp=None):
        """Track model performance metrics"""
        
        if timestamp is None:
            timestamp = datetime.now()
            
        # Calculate metrics
        metrics = self._calculate_performance_metrics(predictions, ground_truth)
        
        # Store metrics
        performance_data = {
            'timestamp': timestamp.isoformat(),
            'model_version': model_version,
            'metrics': metrics,
            'sample_size': len(predictions)
        }
        
        # Save to S3
        self._save_performance_data(performance_data)
        
        # Send to CloudWatch
        self._send_cloudwatch_metrics(metrics, model_version)
        
        return performance_data
    
    def _calculate_performance_metrics(self, predictions, ground_truth):
        """Calculate comprehensive performance metrics"""
        
        # Convert to numpy arrays
        y_true = np.array(ground_truth)
        y_pred_proba = np.array(predictions)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Basic metrics
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        metrics = {
            'auc_score': float(roc_auc_score(y_true, y_pred_proba)),
            'precision': float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0,
            'recall': float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0,
            'specificity': float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0,
            'f1_score': float(2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) > 0 else 0.0,
            'accuracy': float((tp + tn) / (tp + tn + fp + fn)),
            'false_positive_rate': float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0,
            'false_negative_rate': float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0,
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn)
        }
        
        return metrics
    
    def _save_performance_data(self, performance_data):
        """Save performance data to S3"""
        timestamp = performance_data['timestamp'].replace(':', '-')
        key = f"performance_tracking/{timestamp}_{performance_data['model_version']}.json"
        
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(performance_data, indent=2),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error saving performance data: {e}")
    
    def _send_cloudwatch_metrics(self, metrics, model_version):
        """Send metrics to CloudWatch"""
        
        metric_data = []
        
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)):
                metric_data.append({
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': 'None',
                    'Dimensions': [
                        {'Name': 'ModelVersion', 'Value': model_version}
                    ]
                })
        
        try:
            self.cloudwatch.put_metric_data(
                Namespace='MLOps/ModelPerformance',
                MetricData=metric_data
            )
        except Exception as e:
            print(f"Error sending CloudWatch metrics: {e}")
    
    def get_performance_history(self, model_version=None, days=30):
        """Get performance history from S3"""
        
        prefix = "performance_tracking/"
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=prefix
            )
            
            performance_history = []
            
            for obj in response.get('Contents', []):
                # Filter by model version if specified
                if model_version and model_version not in obj['Key']:
                    continue
                
                # Filter by date
                if obj['LastModified'] < datetime.now() - timedelta(days=days):
                    continue
                
                # Load performance data
                try:
                    obj_response = self.s3_client.get_object(
                        Bucket=self.s3_bucket,
                        Key=obj['Key']
                    )
                    data = json.loads(obj_response['Body'].read())
                    performance_history.append(data)
                except Exception as e:
                    print(f"Error loading {obj['Key']}: {e}")
            
            return sorted(performance_history, key=lambda x: x['timestamp'])
            
        except Exception as e:
            print(f"Error retrieving performance history: {e}")
            return []

class ABTestManager:
    """Manage A/B testing for model versions"""
    
    def __init__(self, s3_bucket, region='us-east-1'):
        self.s3_bucket = s3_bucket
        self.sagemaker = boto3.client('sagemaker', region_name=region)
        self.performance_tracker = ModelPerformanceTracker(s3_bucket, region)
        
    def setup_ab_test(self, endpoint_name, model_a_name, model_b_name, traffic_split=50):
        """Setup A/B test between two model versions"""
        
        endpoint_config_name = f"{endpoint_name}-ab-test-{int(datetime.now().timestamp())}"
        
        try:
            self.sagemaker.create_endpoint_config(
                EndpointConfigName=endpoint_config_name,
                ProductionVariants=[
                    {
                        'VariantName': 'model-a',
                        'ModelName': model_a_name,
                        'InitialInstanceCount': 1,
                        'InstanceType': 'ml.m5.large',
                        'InitialVariantWeight': traffic_split
                    },
                    {
                        'VariantName': 'model-b',
                        'ModelName': model_b_name,
                        'InitialInstanceCount': 1,
                        'InstanceType': 'ml.m5.large',
                        'InitialVariantWeight': 100 - traffic_split
                    }
                ],
                DataCaptureConfig={
                    'EnableCapture': True,
                    'InitialSamplingPercentage': 100,
                    'DestinationS3Uri': f's3://{self.s3_bucket}/ab-test-data-capture',
                    'CaptureOptions': [
                        {'CaptureMode': 'Input'},
                        {'CaptureMode': 'Output'}
                    ]
                }
            )
            
            # Update endpoint
            self.sagemaker.update_endpoint(
                EndpointName=endpoint_name,
                EndpointConfigName=endpoint_config_name
            )
            
            # Save A/B test configuration
            ab_test_config = {
                'endpoint_name': endpoint_name,
                'endpoint_config_name': endpoint_config_name,
                'model_a': model_a_name,
                'model_b': model_b_name,
                'traffic_split': traffic_split,
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self._save_ab_test_config(ab_test_config)
            
            print(f"✅ A/B test setup complete: {traffic_split}% to {model_a_name}, {100-traffic_split}% to {model_b_name}")
            return endpoint_config_name
            
        except Exception as e:
            print(f"❌ Error setting up A/B test: {e}")
            return None
    
    def analyze_ab_test_results(self, endpoint_name, test_duration_hours=24):
        """Analyze A/B test results"""
        
        # Get A/B test configuration
        ab_config = self._get_ab_test_config(endpoint_name)
        if not ab_config:
            print("No A/B test configuration found")
            return None
        
        # Get performance data for both variants
        start_time = datetime.fromisoformat(ab_config['start_time'])
        end_time = start_time + timedelta(hours=test_duration_hours)
        
        # Analyze captured data
        results = self._analyze_captured_data(endpoint_name, start_time, end_time)
        
        # Statistical significance test
        significance_result = self._statistical_significance_test(results)
        
        analysis = {
            'test_config': ab_config,
            'test_duration_hours': test_duration_hours,
            'results': results,
            'statistical_significance': significance_result,
            'recommendation': self._generate_recommendation(results, significance_result)
        }
        
        # Save analysis
        self._save_ab_test_analysis(analysis)
        
        return analysis
    
    def _analyze_captured_data(self, endpoint_name, start_time, end_time):
        """Analyze captured data from A/B test"""
        
        # This would typically parse the captured data from S3
        # For now, we'll simulate the analysis
        
        results = {
            'model_a': {
                'total_requests': 1000,
                'avg_latency_ms': 150,
                'error_rate': 0.01,
                'avg_confidence': 0.85
            },
            'model_b': {
                'total_requests': 1000,
                'avg_latency_ms': 120,
                'error_rate': 0.008,
                'avg_confidence': 0.87
            }
        }
        
        return results
    
    def _statistical_significance_test(self, results):
        """Perform statistical significance test"""
        
        # Simplified significance test
        # In practice, you'd use proper statistical tests
        
        model_a_perf = results['model_a']['avg_confidence']
        model_b_perf = results['model_b']['avg_confidence']
        
        improvement = (model_b_perf - model_a_perf) / model_a_perf * 100
        
        return {
            'improvement_percentage': improvement,
            'is_significant': abs(improvement) > 2.0,  # Simplified threshold
            'confidence_level': 0.95 if abs(improvement) > 5.0 else 0.80
        }
    
    def _generate_recommendation(self, results, significance):
        """Generate recommendation based on A/B test results"""
        
        if significance['is_significant'] and significance['improvement_percentage'] > 0:
            return {
                'action': 'promote_model_b',
                'reason': f"Model B shows {significance['improvement_percentage']:.2f}% improvement",
                'confidence': significance['confidence_level']
            }
        elif significance['is_significant'] and significance['improvement_percentage'] < 0:
            return {
                'action': 'keep_model_a',
                'reason': f"Model A performs {abs(significance['improvement_percentage']):.2f}% better",
                'confidence': significance['confidence_level']
            }
        else:
            return {
                'action': 'continue_testing',
                'reason': "No statistically significant difference detected",
                'confidence': significance['confidence_level']
            }
    
    def _save_ab_test_config(self, config):
        """Save A/B test configuration"""
        key = f"ab_tests/{config['endpoint_name']}_config.json"
        
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(config, indent=2),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error saving A/B test config: {e}")
    
    def _get_ab_test_config(self, endpoint_name):
        """Get A/B test configuration"""
        key = f"ab_tests/{endpoint_name}_config.json"
        
        try:
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=key)
            return json.loads(response['Body'].read())
        except Exception as e:
            print(f"Error loading A/B test config: {e}")
            return None
    
    def _save_ab_test_analysis(self, analysis):
        """Save A/B test analysis"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"ab_tests/{analysis['test_config']['endpoint_name']}_analysis_{timestamp}.json"
        
        try:
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(analysis, indent=2, default=str),
                ContentType='application/json'
            )
        except Exception as e:
            print(f"Error saving A/B test analysis: {e}")

def create_performance_visualization(performance_history):
    """Create performance visualization charts"""
    
    if not performance_history:
        print("No performance history available")
        return
    
    # Convert to DataFrame
    df_data = []
    for record in performance_history:
        row = {
            'timestamp': pd.to_datetime(record['timestamp']),
            'model_version': record['model_version'],
            **record['metrics']
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Create visualizations
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # AUC Score over time
    for version in df['model_version'].unique():
        version_data = df[df['model_version'] == version]
        axes[0, 0].plot(version_data['timestamp'], version_data['auc_score'], 
                       marker='o', label=version)
    axes[0, 0].set_title('AUC Score Over Time')
    axes[0, 0].set_ylabel('AUC Score')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Precision and Recall
    for version in df['model_version'].unique():
        version_data = df[df['model_version'] == version]
        axes[0, 1].plot(version_data['timestamp'], version_data['precision'], 
                       marker='o', label=f'{version} - Precision')
        axes[0, 1].plot(version_data['timestamp'], version_data['recall'], 
                       marker='s', label=f'{version} - Recall')
    axes[0, 1].set_title('Precision and Recall Over Time')
    axes[0, 1].set_ylabel('Score')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # False Positive Rate
    for version in df['model_version'].unique():
        version_data = df[df['model_version'] == version]
        axes[1, 0].plot(version_data['timestamp'], version_data['false_positive_rate'], 
                       marker='o', label=version)
    axes[1, 0].set_title('False Positive Rate Over Time')
    axes[1, 0].set_ylabel('False Positive Rate')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # F1 Score
    for version in df['model_version'].unique():
        version_data = df[df['model_version'] == version]
        axes[1, 1].plot(version_data['timestamp'], version_data['f1_score'], 
                       marker='o', label=version)
    axes[1, 1].set_title('F1 Score Over Time')
    axes[1, 1].set_ylabel('F1 Score')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('/tmp/model_performance_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    # Example usage
    bucket = 'your-mlops-monitoring-bucket'
    
    # Initialize tracker
    tracker = ModelPerformanceTracker(bucket)
    
    # Example performance tracking
    predictions = np.random.random(1000)
    ground_truth = np.random.randint(0, 2, 1000)
    
    performance_data = tracker.track_prediction_performance(
        predictions, ground_truth, 'model_v1.0'
    )
    
    print("📊 Performance tracking completed:")
    print(json.dumps(performance_data, indent=2))
    
    # Initialize A/B test manager
    ab_manager = ABTestManager(bucket)
    
    # Example A/B test setup
    # ab_manager.setup_ab_test('fraud-endpoint', 'model-v1', 'model-v2', traffic_split=70)
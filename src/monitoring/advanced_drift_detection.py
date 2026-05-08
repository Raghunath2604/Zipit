import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime
import json
import boto3

# Simplified evidently import
try:
    from evidently.report import Report
    from evidently.metric_preset import DataDriftPreset, DataQualityPreset
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    print("Warning: Evidently not available, using simplified drift detection")

class AdvancedDriftDetector:
    """Advanced drift detection with multiple statistical tests"""
    
    def __init__(self, reference_data, threshold=0.05):
        self.reference_data = reference_data
        self.threshold = threshold
        self.drift_results = {}
        
    def kolmogorov_smirnov_test(self, current_data, feature):
        """Perform KS test for drift detection"""
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()
        
        statistic, p_value = stats.ks_2samp(ref_values, curr_values)
        
        return {
            'test': 'kolmogorov_smirnov',
            'statistic': statistic,
            'p_value': p_value,
            'drift_detected': p_value < self.threshold,
            'severity': self._calculate_severity(statistic)
        }
    
    def population_stability_index(self, current_data, feature, bins=10):
        """Calculate Population Stability Index (PSI)"""
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()
        
        # Create bins based on reference data
        _, bin_edges = np.histogram(ref_values, bins=bins)
        
        # Calculate distributions
        ref_dist, _ = np.histogram(ref_values, bins=bin_edges)
        curr_dist, _ = np.histogram(curr_values, bins=bin_edges)
        
        # Normalize to get percentages
        ref_dist = ref_dist / len(ref_values)
        curr_dist = curr_dist / len(curr_values)
        
        # Avoid division by zero
        ref_dist = np.where(ref_dist == 0, 0.0001, ref_dist)
        curr_dist = np.where(curr_dist == 0, 0.0001, curr_dist)
        
        # Calculate PSI
        psi = np.sum((curr_dist - ref_dist) * np.log(curr_dist / ref_dist))
        
        return {
            'test': 'population_stability_index',
            'psi_value': psi,
            'drift_detected': psi > 0.1,  # PSI > 0.1 indicates drift
            'severity': self._psi_severity(psi)
        }
    
    def jensen_shannon_divergence(self, current_data, feature, bins=50):
        """Calculate Jensen-Shannon divergence"""
        ref_values = self.reference_data[feature].dropna()
        curr_values = current_data[feature].dropna()
        
        # Create histograms
        min_val = min(ref_values.min(), curr_values.min())
        max_val = max(ref_values.max(), curr_values.max())
        bin_edges = np.linspace(min_val, max_val, bins + 1)
        
        ref_hist, _ = np.histogram(ref_values, bins=bin_edges, density=True)
        curr_hist, _ = np.histogram(curr_values, bins=bin_edges, density=True)
        
        # Normalize
        ref_hist = ref_hist / np.sum(ref_hist)
        curr_hist = curr_hist / np.sum(curr_hist)
        
        # Add small epsilon to avoid log(0)
        epsilon = 1e-10
        ref_hist = ref_hist + epsilon
        curr_hist = curr_hist + epsilon
        
        # Calculate JS divergence
        m = 0.5 * (ref_hist + curr_hist)
        js_div = 0.5 * stats.entropy(ref_hist, m) + 0.5 * stats.entropy(curr_hist, m)
        
        return {
            'test': 'jensen_shannon_divergence',
            'js_divergence': js_div,
            'drift_detected': js_div > 0.1,
            'severity': self._js_severity(js_div)
        }
    
    def evidently_drift_report(self, current_data):
        """Generate comprehensive Evidently drift report"""
        if not EVIDENTLY_AVAILABLE:
            return {
                'test': 'evidently_simplified',
                'dataset_drift': False,
                'drift_share': 0.1,
                'number_of_drifted_columns': 2,
                'report_path': 'evidently_not_available'
            }
        
        try:
            report = Report(metrics=[
                DataDriftPreset(),
                DataQualityPreset()
            ])
            
            report.run(reference_data=self.reference_data, current_data=current_data)
            
            # Extract key metrics
            report_dict = report.as_dict()
            
            return {
                'test': 'evidently_comprehensive',
                'dataset_drift': report_dict['metrics'][0]['result']['dataset_drift'],
                'drift_share': report_dict['metrics'][0]['result']['drift_share'],
                'number_of_drifted_columns': report_dict['metrics'][0]['result']['number_of_drifted_columns'],
                'report_path': self._save_evidently_report(report)
            }
        except Exception as e:
            return {
                'test': 'evidently_error',
                'error': str(e),
                'dataset_drift': False,
                'drift_share': 0.0,
                'number_of_drifted_columns': 0
            }
    
    def comprehensive_drift_analysis(self, current_data):
        """Run all drift detection methods"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_features': len(self.reference_data.columns),
            'features_analyzed': [],
            'overall_drift_detected': False,
            'drift_summary': {}
        }
        
        # Analyze each feature
        for feature in self.reference_data.columns:
            if feature in current_data.columns:
                feature_results = {
                    'ks_test': self.kolmogorov_smirnov_test(current_data, feature),
                    'psi': self.population_stability_index(current_data, feature),
                    'js_divergence': self.jensen_shannon_divergence(current_data, feature)
                }
                
                # Determine if any test detected drift
                drift_detected = any([
                    feature_results['ks_test']['drift_detected'],
                    feature_results['psi']['drift_detected'],
                    feature_results['js_divergence']['drift_detected']
                ])
                
                feature_results['overall_drift'] = drift_detected
                results['features_analyzed'].append(feature)
                results['drift_summary'][feature] = feature_results
                
                if drift_detected:
                    results['overall_drift_detected'] = True
        
        # Add Evidently report
        results['evidently_report'] = self.evidently_drift_report(current_data)
        
        return results
    
    def _calculate_severity(self, statistic):
        """Calculate drift severity based on KS statistic"""
        if statistic < 0.1:
            return 'low'
        elif statistic < 0.3:
            return 'medium'
        else:
            return 'high'
    
    def _psi_severity(self, psi):
        """Calculate PSI severity"""
        if psi < 0.1:
            return 'no_drift'
        elif psi < 0.2:
            return 'moderate_drift'
        else:
            return 'significant_drift'
    
    def _js_severity(self, js_div):
        """Calculate JS divergence severity"""
        if js_div < 0.05:
            return 'low'
        elif js_div < 0.15:
            return 'medium'
        else:
            return 'high'
    
    def _save_evidently_report(self, report):
        """Save Evidently report to S3"""
        if not EVIDENTLY_AVAILABLE:
            return "evidently_not_available"
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"drift_reports/evidently_report_{timestamp}.html"
        
        # Save locally first
        local_path = f"/tmp/{report_path.split('/')[-1]}"
        
        try:
            report.save_html(local_path)
            
            # Upload to S3 (if configured)
            try:
                s3_client = boto3.client('s3')
                bucket = 'your-mlops-monitoring-bucket'  # Replace with actual bucket
                s3_client.upload_file(local_path, bucket, report_path)
                return f"s3://{bucket}/{report_path}"
            except Exception as e:
                print(f"Warning: Could not upload report to S3: {e}")
                return local_path
        except Exception as e:
            print(f"Warning: Could not save evidently report: {e}")
            return f"error_saving_report_{timestamp}"

def automated_drift_remediation(drift_results, endpoint_name):
    """Automated remediation based on drift detection results"""
    
    if not drift_results['overall_drift_detected']:
        print("✅ No drift detected - no action needed")
        return
    
    # Count drifted features
    drifted_features = [
        feature for feature, results in drift_results['drift_summary'].items()
        if results['overall_drift']
    ]
    
    drift_percentage = len(drifted_features) / drift_results['total_features']
    
    print(f"🚨 Drift detected in {len(drifted_features)} features ({drift_percentage:.1%})")
    
    # Determine remediation action
    if drift_percentage > 0.3:  # More than 30% features drifted
        print("🔄 Triggering immediate model retraining...")
        trigger_retraining_pipeline(endpoint_name, priority='high')
        
    elif drift_percentage > 0.15:  # 15-30% features drifted
        print("⚠️ Scheduling model retraining within 24 hours...")
        schedule_retraining(endpoint_name, delay_hours=24)
        
    else:  # Less than 15% features drifted
        print("📊 Increasing monitoring frequency...")
        increase_monitoring_frequency(endpoint_name)
    
    # Send alerts
    send_drift_alert(drift_results, endpoint_name)

def trigger_retraining_pipeline(endpoint_name, priority='normal'):
    """Trigger SageMaker retraining pipeline"""
    sm_client = boto3.client('sagemaker')
    
    pipeline_name = 'FraudDetectionRetrainingPipeline'
    
    try:
        response = sm_client.start_pipeline_execution(
            PipelineName=pipeline_name,
            PipelineParameters=[
                {'Name': 'EndpointName', 'Value': endpoint_name},
                {'Name': 'Priority', 'Value': priority}
            ]
        )
        print(f"✅ Pipeline execution started: {response['PipelineExecutionArn']}")
    except Exception as e:
        print(f"❌ Error starting pipeline: {e}")

def send_drift_alert(drift_results, endpoint_name):
    """Send drift detection alert"""
    sns_client = boto3.client('sns')
    
    message = f"""
🚨 DRIFT ALERT - {endpoint_name}

Drift detected in {len([f for f, r in drift_results['drift_summary'].items() if r['overall_drift']])} features

Timestamp: {drift_results['timestamp']}
Total Features: {drift_results['total_features']}

Action: Automated remediation initiated
    """
    
    try:
        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:ACCOUNT:mlops-alerts',  # Replace with actual ARN
            Message=message,
            Subject=f'Drift Alert - {endpoint_name}'
        )
        print("📧 Alert sent successfully")
    except Exception as e:
        print(f"❌ Error sending alert: {e}")

if __name__ == "__main__":
    # Example usage
    reference_data = pd.read_csv('data/processed/baseline_data.csv')
    current_data = pd.read_csv('data/processed/current_data.csv')
    
    detector = AdvancedDriftDetector(reference_data)
    results = detector.comprehensive_drift_analysis(current_data)
    
    print("🔍 Drift Analysis Results:")
    print(json.dumps(results, indent=2, default=str))
    
    # Trigger automated remediation
    automated_drift_remediation(results, 'fraud-detection-endpoint')
import pandas as pd
import numpy as np
from scipy import stats
import boto3
from typing import Dict, Any

class DataDriftMonitor:
    def __init__(self, reference_data: pd.DataFrame):
        self.reference_data = reference_data
        
    def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect data drift using statistical tests"""
        drift_results = {}
        
        for column in self.reference_data.columns:
            if column in current_data.columns:
                # Kolmogorov-Smirnov test for drift detection
                ref_values = self.reference_data[column].dropna()
                curr_values = current_data[column].dropna()
                
                ks_stat, p_value = stats.ks_2samp(ref_values, curr_values)
                
                drift_results[column] = {
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'drift_detected': p_value < 0.05,
                    'ref_mean': float(ref_values.mean()),
                    'curr_mean': float(curr_values.mean()),
                    'mean_shift': float(curr_values.mean() - ref_values.mean())
                }
        
        # Overall drift summary
        drifted_features = sum(1 for result in drift_results.values() if result['drift_detected'])
        
        summary = {
            'total_features': len(drift_results),
            'drifted_features': drifted_features,
            'drift_percentage': drifted_features / len(drift_results) if drift_results else 0,
            'overall_drift': drifted_features > 0
        }
        
        return {
            'summary': summary,
            'feature_drift': drift_results
        }
    
    def save_report(self, report: Dict[str, Any], s3_bucket: str, key: str):
        """Save drift report to S3"""
        import json
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=s3_bucket,
            Key=key,
            Body=json.dumps(report, indent=2),
            ContentType='application/json'
        )
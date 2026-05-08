import pandas as pd
import numpy as np
from evidently import Report
from evidently.metrics import DataDriftPreset, DataQualityPreset
import boto3
from typing import Dict, Any

class DataDriftMonitor:
    def __init__(self, reference_data: pd.DataFrame):
        self.reference_data = reference_data
        
    def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect data drift between reference and current data"""
        report = Report(metrics=[
            DataDriftPreset(),
            DataQualityPreset()
        ])
        
        report.run(
            reference_data=self.reference_data,
            current_data=current_data
        )
        
        return report.as_dict()
    
    def save_report(self, report: Dict[str, Any], s3_bucket: str, key: str):
        """Save drift report to S3"""
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=s3_bucket,
            Key=key,
            Body=str(report),
            ContentType='application/json'
        )
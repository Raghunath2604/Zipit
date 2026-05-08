import os
from typing import List, Dict

class Config:
    """Enhanced configuration with business hours and thresholds"""
    
    def __init__(self):
        # AWS Configuration
        self.aws_region: str = os.getenv("AWS_REGION", "us-east-1")
        self.s3_bucket: str = os.getenv("S3_BUCKET", "mlops-monitoring-bucket")
        
        # SageMaker Configuration
        self.sagemaker_role: str = os.getenv("SAGEMAKER_EXECUTION_ROLE", "")
        self.model_name: str = os.getenv("MODEL_NAME", "ml-model")
        self.endpoint_name: str = os.getenv("ENDPOINT_NAME", "ml-endpoint")
        
        # Monitoring Configuration
        self.monitoring_schedule_name: str = "model-monitoring-schedule"
        self.data_capture_percentage: int = int(os.getenv("DATA_CAPTURE_PERCENTAGE", "100"))
        
        # Business Hours Configuration (6 AM to 6 PM)
        self.business_hours_start: int = int(os.getenv("BUSINESS_HOURS_START", "6"))
        self.business_hours_end: int = int(os.getenv("BUSINESS_HOURS_END", "18"))
        self.business_days: List[int] = [0, 1, 2, 3, 4]  # Monday to Friday
        self.timezone: str = os.getenv("TIMEZONE", "UTC")
        
        # Alert Configuration
        self.alert_email: str = os.getenv("ALERT_EMAIL", "")
        self.slack_webhook_url: str = os.getenv("SLACK_WEBHOOK_URL", "")
        
        # Drift Detection Thresholds
        self.drift_threshold_low: float = float(os.getenv("DRIFT_THRESHOLD_LOW", "0.05"))
        self.drift_threshold_medium: float = float(os.getenv("DRIFT_THRESHOLD_MEDIUM", "0.15"))
        self.drift_threshold_high: float = float(os.getenv("DRIFT_THRESHOLD_HIGH", "0.25"))
        
        # Performance Thresholds
        self.min_auc_score: float = float(os.getenv("MIN_AUC_SCORE", "0.8"))
        self.max_latency_ms: int = int(os.getenv("MAX_LATENCY_MS", "1000"))
        self.max_error_rate: float = float(os.getenv("MAX_ERROR_RATE", "0.01"))
        
        # Data Configuration
        self.raw_data_path: str = "data/raw/"
        self.processed_data_path: str = "data/processed/"
        
        # Model Configuration
        self.model_artifact_path: str = "models/"
        self.baseline_data_path: str = "baseline/"
        
        # UI Configuration
        self.dashboard_refresh_interval: int = 30  # seconds
        self.max_chart_points: int = 100

config = Config()
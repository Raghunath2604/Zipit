import boto3
import sagemaker
from sagemaker.model_monitor import DefaultModelMonitor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from config.config import config

class SageMakerMonitor:
    def __init__(self):
        self.sagemaker_session = sagemaker.Session()
        self.role = config.sagemaker_role
        self.monitor = DefaultModelMonitor(
            role=self.role,
            sagemaker_session=self.sagemaker_session
        )
    
    def create_baseline(self, baseline_data_uri: str, output_uri: str):
        """Create baseline for model monitoring"""
        baseline_job = self.monitor.suggest_baseline(
            baseline_dataset=baseline_data_uri,
            dataset_format=sagemaker.dataset_definition.DatasetFormat.csv(header=True),
            output_s3_uri=output_uri
        )
        return baseline_job
    
    def create_monitoring_schedule(self, endpoint_name: str, baseline_uri: str, output_uri: str):
        """Create monitoring schedule for endpoint"""
        self.monitor.create_monitoring_schedule(
            monitor_schedule_name=config.monitoring_schedule_name,
            endpoint_input=endpoint_name,
            output_s3_uri=output_uri,
            statistics=f"{baseline_uri}/statistics.json",
            constraints=f"{baseline_uri}/constraints.json",
            schedule_cron_expression="cron(0 * * * ? *)"  # Hourly
        )
    
    def get_monitoring_results(self):
        """Get latest monitoring execution results"""
        executions = self.monitor.list_executions()
        if executions:
            return executions[-1].describe()
        return None
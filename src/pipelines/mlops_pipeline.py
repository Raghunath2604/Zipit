import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.sklearn.estimator import SKLearn
from config.config import config

class MLOpsPipeline:
    def __init__(self):
        self.sagemaker_session = sagemaker.Session()
        self.role = config.sagemaker_role
        
    def create_processing_step(self, input_data_uri: str, output_data_uri: str):
        """Create data processing step"""
        processor = SKLearnProcessor(
            framework_version="1.2-1",
            role=self.role,
            instance_type="ml.m5.large",
            instance_count=1
        )
        
        step = ProcessingStep(
            name="DataProcessing",
            processor=processor,
            code="src/training/preprocess.py",
            inputs=[
                sagemaker.processing.ProcessingInput(
                    source=input_data_uri,
                    destination="/opt/ml/processing/input"
                )
            ],
            outputs=[
                sagemaker.processing.ProcessingOutput(
                    output_name="train",
                    source="/opt/ml/processing/train",
                    destination=f"{output_data_uri}/train"
                ),
                sagemaker.processing.ProcessingOutput(
                    output_name="validation",
                    source="/opt/ml/processing/validation", 
                    destination=f"{output_data_uri}/validation"
                )
            ]
        )
        return step
    
    def create_training_step(self, training_data_uri: str):
        """Create model training step"""
        estimator = SKLearn(
            entry_point="src/training/train.py",
            framework_version="1.2-1",
            py_version="py39",
            instance_type="ml.m5.large",
            role=self.role
        )
        
        step = TrainingStep(
            name="ModelTraining",
            estimator=estimator,
            inputs={
                "train": sagemaker.inputs.TrainingInput(
                    s3_data=training_data_uri,
                    content_type="text/csv"
                )
            }
        )
        return step
    
    def create_pipeline(self, input_data_uri: str, output_data_uri: str):
        """Create complete MLOps pipeline"""
        processing_step = self.create_processing_step(input_data_uri, output_data_uri)
        training_step = self.create_training_step(processing_step.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri)
        
        pipeline = Pipeline(
            name="MLOpsMonitoringPipeline",
            steps=[processing_step, training_step],
            sagemaker_session=self.sagemaker_session
        )
        
        return pipeline
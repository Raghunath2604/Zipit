from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet
from sagemaker.sklearn import SKLearnProcessor, SKLearn, SKLearnModel
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.inputs import TrainingInput
import sagemaker

def create_retraining_pipeline(role, bucket):
    """Create automated retraining pipeline"""
    
    # Processing step for data preparation
    processor = SKLearnProcessor(
        framework_version='0.23-1',
        role=role,
        instance_type='ml.m5.large',
        instance_count=1
    )
    
    processing_step = ProcessingStep(
        name='DataProcessing',
        processor=processor,
        code='../src/processing/prepare_data.py',
        inputs=[
            ProcessingInput(
                source=f's3://{bucket}/data/fraud_dataset.csv',
                destination='/opt/ml/processing/input'
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name='train_data',
                source='/opt/ml/processing/train'
            ),
            ProcessingOutput(
                output_name='validation_data', 
                source='/opt/ml/processing/validation'
            )
        ]
    )
    
    # Training step
    sklearn_estimator = SKLearn(
        entry_point='fraud_train.py',
        source_dir='../src/training',
        role=role,
        instance_type='ml.m5.large',
        framework_version='0.23-1',
        py_version='py3'
    )
    
    training_step = TrainingStep(
        name='ModelTraining',
        estimator=sklearn_estimator,
        inputs={
            'train': TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs['train_data'].S3Output.S3Uri
            ),
            'validation': TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs['validation_data'].S3Output.S3Uri
            )
        }
    )
    
    # Model evaluation step
    evaluation_processor = SKLearnProcessor(
        framework_version='0.23-1',
        role=role,
        instance_type='ml.m5.large',
        instance_count=1
    )
    
    evaluation_step = ProcessingStep(
        name='ModelEvaluation',
        processor=evaluation_processor,
        code='../src/evaluation/evaluate.py',
        inputs=[
            ProcessingInput(
                source=training_step.properties.ModelArtifacts.S3ModelArtifacts,
                destination='/opt/ml/processing/model'
            ),
            ProcessingInput(
                source=processing_step.properties.ProcessingOutputConfig.Outputs['validation_data'].S3Output.S3Uri,
                destination='/opt/ml/processing/test'
            )
        ],
        outputs=[
            ProcessingOutput(
                output_name='evaluation',
                source='/opt/ml/processing/evaluation'
            )
        ]
    )
    
    # Condition for model approval
    cond_gte = ConditionGreaterThanOrEqualTo(
        left=JsonGet(
            step_name=evaluation_step.name,
            property_file='evaluation.json',
            json_path='classification_metrics.auc.value'
        ),
        right=0.8  # Minimum AUC threshold
    )
    
    # Create model step (only if condition is met)
    model = SKLearnModel(
        model_data=training_step.properties.ModelArtifacts.S3ModelArtifacts,
        role=role,
        entry_point='fraud_inference.py',
        source_dir='../src/inference',
        framework_version='0.23-1'
    )
    
    create_model_step = CreateModelStep(
        name='CreateModel',
        model=model
    )
    
    # Conditional step
    condition_step = ConditionStep(
        name='CheckModelQuality',
        conditions=[cond_gte],
        if_steps=[create_model_step],
        else_steps=[]
    )
    
    # Create pipeline
    pipeline = Pipeline(
        name='FraudDetectionRetrainingPipeline',
        steps=[processing_step, training_step, evaluation_step, condition_step]
    )
    
    return pipeline

if __name__ == "__main__":
    # Create and start pipeline
    role = 'arn:aws:iam::YOUR_ACCOUNT:role/MLOpsMonitoringRole'
    bucket = 'your-mlops-monitoring-bucket'
    
    pipeline = create_retraining_pipeline(role, bucket)
    pipeline.upsert(role_arn=role)
    print("Retraining pipeline created successfully!")
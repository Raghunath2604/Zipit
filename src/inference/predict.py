import pandas as pd
import joblib
import boto3
from typing import Dict, Any, List
from config.config import config

class ModelInference:
    def __init__(self, model_path: str = None):
        self.model = None
        self.s3_client = boto3.client('s3')
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load model from local path or S3"""
        if model_path.startswith('s3://'):
            # Download from S3
            bucket, key = model_path.replace('s3://', '').split('/', 1)
            local_path = f"/tmp/{key.split('/')[-1]}"
            self.s3_client.download_file(bucket, key, local_path)
            self.model = joblib.load(local_path)
        else:
            self.model = joblib.load(model_path)
    
    def predict(self, input_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Make predictions and return with metadata"""
        predictions = self.model.predict(input_data)
        probabilities = self.model.predict_proba(input_data)
        
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append({
                'prediction': pred,
                'confidence': max(prob),
                'probabilities': prob.tolist(),
                'input_features': input_data.iloc[i].to_dict()
            })
        
        return results
    
    def batch_predict(self, data_path: str, output_path: str):
        """Batch prediction for large datasets"""
        data = pd.read_csv(data_path)
        predictions = self.predict(data)
        
        # Save predictions
        pd.DataFrame(predictions).to_csv(output_path, index=False)
        
        # Upload to S3
        self.s3_client.upload_file(
            output_path,
            config.s3_bucket,
            f"predictions/{output_path.split('/')[-1]}"
        )
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import boto3
from config.config import config

class ModelTrainer:
    def __init__(self):
        self.model = None
        self.s3_client = boto3.client('s3')
    
    def load_data(self, data_path: str) -> pd.DataFrame:
        """Load training data"""
        return pd.read_csv(data_path)
    
    def preprocess_data(self, df: pd.DataFrame, target_column: str):
        """Basic preprocessing"""
        X = df.drop(columns=[target_column])
        y = df[target_column]
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train the model"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        return self.model
    
    def evaluate_model(self, X_test: pd.DataFrame, y_test: pd.Series):
        """Evaluate model performance"""
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        report = classification_report(y_test, predictions)
        return {"accuracy": accuracy, "report": report}
    
    def save_model(self, model_path: str):
        """Save model locally and to S3"""
        joblib.dump(self.model, model_path)
        self.s3_client.upload_file(
            model_path, 
            config.s3_bucket, 
            f"{config.model_artifact_path}{model_path.split('/')[-1]}"
        )
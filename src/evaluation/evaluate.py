import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
import argparse
import os

def evaluate_model():
    """Evaluate model performance"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-path', type=str, default='/opt/ml/processing/model')
    parser.add_argument('--test-path', type=str, default='/opt/ml/processing/test')
    parser.add_argument('--output-path', type=str, default='/opt/ml/processing/evaluation')
    args = parser.parse_args()
    
    # Load model
    model = joblib.load(os.path.join(args.model_path, 'model.joblib'))
    
    # Load feature names
    with open(os.path.join(args.model_path, 'feature_names.txt'), 'r') as f:
        feature_names = [line.strip() for line in f.readlines()]
    
    # Load test data
    test_data = pd.read_csv(os.path.join(args.test_path, 'validation.csv'))
    
    X_test = test_data[feature_names]
    y_test = test_data['is_fraud']
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    auc_score = roc_auc_score(y_test, y_pred_proba)
    cm = confusion_matrix(y_test, y_pred)
    
    # Create evaluation report
    evaluation_report = {
        'classification_metrics': {
            'auc': {
                'value': float(auc_score)
            },
            'confusion_matrix': cm.tolist(),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    }
    
    # Save evaluation results
    os.makedirs(args.output_path, exist_ok=True)
    with open(os.path.join(args.output_path, 'evaluation.json'), 'w') as f:
        json.dump(evaluation_report, f, indent=2)
    
    print(f"AUC Score: {auc_score:.4f}")
    print(f"Confusion Matrix:\n{cm}")
    print("Evaluation complete!")

if __name__ == '__main__':
    evaluate_model()
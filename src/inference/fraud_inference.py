import joblib
import pandas as pd
import numpy as np
import json
import os
from io import StringIO

def model_fn(model_dir):
    """Load model for inference"""
    model = joblib.load(os.path.join(model_dir, 'model.joblib'))
    
    with open(os.path.join(model_dir, 'feature_names.txt'), 'r') as f:
        feature_names = [line.strip() for line in f.readlines()]
    
    return {'model': model, 'feature_names': feature_names}

def input_fn(request_body, request_content_type):
    """Parse input data"""
    if request_content_type == 'application/json':
        data = json.loads(request_body)
        return pd.DataFrame(data)
    elif request_content_type == 'text/csv':
        return pd.read_csv(StringIO(request_body))
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model_dict):
    """Make predictions"""
    model = model_dict['model']
    feature_names = model_dict['feature_names']
    
    # Ensure correct feature order
    input_data = input_data[feature_names]
    
    # Make predictions
    predictions = model.predict_proba(input_data)[:, 1]
    
    return predictions

def output_fn(prediction, content_type):
    """Format output"""
    if content_type == 'application/json':
        return json.dumps({'predictions': prediction.tolist()})
    else:
        return str(prediction)